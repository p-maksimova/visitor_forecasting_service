import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import urllib.parse

FASTAPI_URL = "http://fastapi_server:8000"

# Флаг для показа кнопки входа
if 'show_login' not in st.session_state:
    st.session_state.show_login = False

# Проверяем, авторизован ли пользователь
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None

# Флаг для показа кнопки регистрации
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

def get_cookies():
    jwt_token = st.session_state.get("jwt_token")
    if not jwt_token:
        st.error("JWT токен не найден. Пожалуйста, авторизуйтесь!")
        return None
    cookies = {"users_access_token": jwt_token}
    return cookies

def get_appointments(date, doctor_name):
    day = date.day
    month = date.month
    year = date.year
    url = f"{FASTAPI_URL}/get_appointments/{day}/{month}/{year}"
    
    # Параметры запроса, если нужны
    if doctor_name == "Все сотрудники":
        doctor_name = None
    params = {"doctor_name": doctor_name}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()   # Если статус-код не 200, выбросит исключение
        data = response.json()        # Преобразуем JSON данные в словарь
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP-ошибка: {http_err}")
    except Exception as err:
        print(f"Ошибка запроса: {err}")

def get_balance():
    cookies = get_cookies()
    url = f"{FASTAPI_URL}/balance"
    response = requests.get(url, cookies=cookies)
    response.raise_for_status() 
    balance = response.text.strip()
    return balance

def get_predict(date, doctor_name, model_name):
    models = {'Регрессия (5)': 1, 'Бустинг (10)': 2}
    day = date.day
    month = date.month
    year = date.year
    doctor_name_encoded = urllib.parse.quote(doctor_name)
    url = f"{FASTAPI_URL}/predict/{day}/{month}/{year}/{doctor_name_encoded}/{models[model_name]}"

    cookies = get_cookies()

    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()   # Если статус-код не 200, выбросит исключение
        data = response.json()        # Преобразуем JSON данные в словарь
        return data
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP-ошибка: {http_err}")
        print(f"HTTP-ошибка: {http_err}")
    except Exception as err:
        st.error(f"Ошибка запроса: {err}")
        print(f"Ошибка запроса: {err}")
    return None

def login_user(email: str, password: str) -> bool:
    """
    Отправляет данные для входа на сервер и сохраняет токен в session_state,
    если авторизация прошла успешно.
    """
    login_payload = {"email": email, "password": password}
    response = requests.post(f"{FASTAPI_URL}/login", json=login_payload)
    if response.status_code == 200:
        token = response.json().get("access_token")
        if token:
            st.session_state.jwt_token = token
            st.session_state.email = email
            st.session_state.show_login = False
            st.success("Авторизация успешна!")
        else:
            st.error("Не удалось получить токен.")
    else:
        st.error("Неверное имя пользователя или пароль!")

def process_registration():
    """Обработка регистрации: считывает введённые данные и отправляет их в API для регистрации."""
    reg_email = st.session_state.get("reg_email")
    reg_password = st.session_state.get("reg_password")
    reg_confirm = st.session_state.get("reg_confirm")
    first_name = st.session_state.get("reg_first_name")
    last_name = st.session_state.get("reg_last_name")
    
    if not reg_email or not reg_password or not reg_confirm:
        st.warning("Заполните все поля!")
        return
    if reg_password != reg_confirm:
        st.error("Пароли не совпадают!")
        return

    register_payload = {"email": reg_email, "password": reg_password, "first_name": first_name, "last_name": last_name}
    response = requests.post(f"{FASTAPI_URL}/registration/", json=register_payload)
    if response.status_code in [200, 201]:
        st.success("Регистрация прошла успешно! Теперь вы можете авторизоваться.")
        # После успешной регистрации переключаемся на форму входа
        st.session_state["show_register"] = False
        st.session_state["show_login"] = True
    else:
        st.error("Ошибка регистрации: " + response.text)

def process_login():
    """Обработка авторизации: считывает данные из session_state, отправляет запрос и сохраняет токен."""
    email = st.session_state.get("login_email")
    password = st.session_state.get("login_password")
    if email and password:
        login_payload = {"email": email, "password": password}
        response = requests.post(f"{FASTAPI_URL}/login", json=login_payload)
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                st.session_state["jwt_token"] = token
                st.session_state["email"] = email
                st.session_state["show_login"] = False
                st.success("Авторизация успешна!")
            else:
                st.error("Не удалось получить токен.")
        else:
            st.error("Неверное имя пользователя или пароль!")
    else:
        st.warning("Заполните все поля!")

def main():
    st.title("Прогнозирование посещений")

    # Если пользователь не авторизован, предлагаем кнопки для авторизации и регистрации
    if st.session_state.jwt_token is None:
        st.write("Пожалуйста, войдите или зарегистрируйтесь.")

        # Размещаем две кнопки в две колонки
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Войти"):
                st.session_state["show_login"] = True
                st.session_state["show_register"] = False
        with col2:
            if st.button("Зарегистрироваться"):
                st.session_state["show_register"] = True
                st.session_state["show_login"] = False

        # Если выбран режим авторизации, показываем форму входа
        if st.session_state["show_login"]:
            with st.form("login_form", clear_on_submit=True):
                st.write("Введите данные для авторизации")
                st.text_input("Email", key="login_email")
                st.text_input("Пароль", type="password", key="login_password")
                st.form_submit_button("Подтвердить вход", on_click=process_login)

        # Если выбран режим регистрации, показываем форму регистрации
        if st.session_state["show_register"]:
            with st.form("register_form", clear_on_submit=True):
                st.write("Введите данные для регистрации")
                st.text_input("Имя", key="reg_first_name")
                st.text_input("Фамилия", key="reg_last_name")
                st.text_input("Email", key="reg_email")
                st.text_input("Пароль", type="password", key="reg_password")
                st.text_input("Повтор пароля", type="password", key="reg_confirm")
                st.form_submit_button("Зарегистрироваться", on_click=process_registration)
    else: 
        st.write(f'Добро пожаловать, {st.session_state["email"]}!')
        
        # Баланс
        st.session_state["balance"] = get_balance()
        balance_placeholder = st.empty()
        balance_placeholder.write(f'Ваш баланс: {st.session_state["balance"]}')
        
        # Виджет для выбора даты
        selected_date = st.date_input("Выберите дату", value=datetime.date(2025, 4, 29))

        # Элемент с выбором из выпадающего списка
        employees = ["Все сотрудники", "Иванов А.В.", "Смирнов О.П.", "Петров И.М.", "Соколов Д.Н.", "Васильев Е.С."]
        selected_employee = st.selectbox("Выберите врача", options=employees)

        models = ['Регрессия (5)', 'Бустинг (10)']
        selected_model = st.selectbox("Выберите модель", options=models)

        # Инициализируем переменную для данных
        df = None

        col_left, col_right = st.columns([3, 1])

        with col_left:
            if st.button("Загрузить записи"):    
                appointments = get_appointments(selected_date, selected_employee)
                df = pd.DataFrame(appointments)
                if df.empty:
                    st.warning("Нет доступных записей")
                else:
                    df = df[['slot_id', 'doctor_name', 'appointment_id']]

        with col_right:
            if st.button("Получить прогноз"):    
                predict = get_predict(selected_date, selected_employee, selected_model)
                st.session_state["balance"] = get_balance()
                balance_placeholder.write(f'Ваш баланс: {st.session_state["balance"]}')
                df = pd.DataFrame(predict)
                df = df[['slot_id', 'appointment_id', 'probability_visit', 'predict_visit']]

        # Выводим таблицу
        if df is not None:
            st.table(df)
        else:
            st.write("Данные отсутствуют")

if __name__ == "__main__":
    main()

