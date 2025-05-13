from fastapi import FastAPI, HTTPException, status, Response, Depends
from core.entities import User, Appointment, Patient, Transaction
import datetime
from config.database import async_session_maker
from sqlalchemy import select, func
from models.models import predict_model
import asyncio
from core.use_cases.auth import get_password_hash, verify_password, create_access_token, get_current_user

app = FastAPI()


@app.get("/")
def home_page():
    return {"massage": "Информационная система прогнозирования посещений"}


@app.get("/get_appointments/{day}/{month}/{year}")
async def get_appointments(day: int, 
                           month: int, 
                           year: int, 
                           doctor_name: str | None = None, 
                           ) -> list[Appointment.AppointmentInDB]:
    
    # Проверка корректности даты
    try:
        target_date = datetime.date(year, month, day)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=f"Передана некорректная дата: {error}")
    
    # Обращение к базе
    async with async_session_maker() as session:
        # Запрос по дате записи
        query = select(Appointment.Appointment).filter(
            Appointment.Appointment.appointment_date == target_date
        )
        # Если передан doctor, добавляем соответствующий фильтр
        if doctor_name is not None:
            query = query.filter(Appointment.Appointment.doctor_name == doctor_name)

        result = await session.execute(query)
        appointments = result.scalars().all()

    if not appointments:
        raise HTTPException(status_code=404, detail="Записи не найдены")
    
    return appointments


@app.post("/registration/")
async def register_user(user_data: User.UserCreate) -> dict:
    # Проверка существования пользователя по email
    async with async_session_maker() as session:
        user = select(User.User).filter(User.User.email == user_data.email) 
        result = (await session.execute(user)).scalars().first()
    if result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    # Преобразуем модель Pydantic в словарь
    user_data = user_data.model_dump()
    async with async_session_maker() as session:
        async with session.begin():
            # Захешировать пароль, удалить открытый пароль из словаря
            user_data['hashed_password'] = get_password_hash(user_data['password'])
            del user_data['password']
            # Создаем экземпляр пользователя
            user_instance = User.User(**user_data)
            session.add(user_instance)
            await session.flush() #await session.commit()
            
            # Создаем транзакцию для нового пользователя
            transaction_instance = Transaction.Transaction(
                user_id=user_instance.user_id, 
                amount=100,
                status="completed"
            )
            session.add(transaction_instance)

    return {'message': 'Вы успешно зарегистрированы!'}


@app.post("/login/")
async def auth_user(response: Response, user_data: User.UserAuth):
    async with async_session_maker() as session:
        user = select(User.User).filter(User.User.email == user_data.email) 
        result = (await session.execute(user)).scalars().first()
    if not result or verify_password(plain_password=user_data.password, hashed_password=result.hashed_password) is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(result.user_id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}


@app.get("/me/")
async def get_me(user_data: User.User = Depends(get_current_user)):
    return {"user_id": user_data.user_id, "name": user_data.first_name}


@app.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@app.get("/balance/")
async def get_balance(user: dict = Depends(get_me)):
    async with async_session_maker() as session:
        query = select(func.coalesce(func.sum(Transaction.Transaction.amount), 0)).where(
            Transaction.Transaction.user_id == user["user_id"],
            Transaction.Transaction.status.in_(["completed", "pending"])
        )
        result = await session.execute(query)
        balance = result.scalar()  # Если транзакций нет, вернёт None, поэтому используем coalesce для замены на 0.
    return float(balance)


@app.get("/predict/{day}/{month}/{year}/{doctor_name}/{n_model}")
async def get_predict(day: int, 
                      month: int, 
                      year: int, 
                      doctor_name: str,
                      n_model: int | None = 1,
                      user: dict = Depends(get_me),
                      balance: float = Depends(get_balance)):
    
    prices = {1: 5, 2: 10}
    models_dict = {1: "model_log_reg.pkl", 2: "model_xgb_gs.pkl"}

    # Проверка корректности даты
    try:
        target_date = datetime.date(year, month, day)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=f"Передана некорректная дата: {error}")

    data = []
    # Получение записей
    async with async_session_maker() as session:

        query = select(Appointment.Appointment).filter(
            Appointment.Appointment.appointment_date == target_date, 
            Appointment.Appointment.doctor_name == doctor_name
        )

        result = await session.execute(query)
        appointments = result.scalars().all()
  
    if not appointments:
        raise HTTPException(status_code=404, detail="Записи не найдены")

    async with async_session_maker() as session:
        async with session.begin():
            if prices[n_model] > balance:
                raise HTTPException(status_code=400, detail="Недостаточно средств")
            
            # Создаем запись транзакции со статусом PENDING
            transaction = Transaction.Transaction(
                user_id=user["user_id"],
                amount=-prices[n_model],
                status="pending"
            )
            session.add(transaction)
            await session.flush()

            # Получение данных по пациентам
            for appt in appointments:
                patient_query = select(Patient.Patient).filter(Patient.Patient.patient_id == appt.patient_id)
                patient_result = await session.execute(patient_query)
                patient_record = patient_result.scalars().first()

                row = Appointment.AppointmentInDB.model_validate(appt).model_dump()
                row_add = Patient.PatientInDB.model_validate(patient_record).model_dump()
                row.update(row_add)
                data.append(row)

            # Выполняем предсказание
            try:
                predictions = await asyncio.to_thread(predict_model, data, models_dict[n_model])
                transaction.status = "completed"
            except Exception as e:
                transaction.status = "failed"
                raise HTTPException(status_code=500, detail=f"Ошибка предсказания: {e}")
   
    return predictions     