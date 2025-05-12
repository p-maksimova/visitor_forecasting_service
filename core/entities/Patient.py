from pydantic import BaseModel

class PatientInDB(BaseModel):
    patient_id: int  
    gender: str                 # Пол пациента ("Male" или "Female")
    age: int                    # Возраст пациента в годах
    neighbourhood: str          # Район проживания пациента
    scholarship: bool           # Наличие медицинской субсидии
    hipertension: bool          # Наличие гипертонии
    diabetes: bool              # Наличие диабета
    alcoholism: bool            # Наличие алкогольной зависимости
    handcap: bool               # Наличие инвалидности
    sms_received: bool          # Получает SMS-уведомления
    no_show_cumsum: int         # Кумулятивное количество пропущенных записей пациентом
    appointment_cumcount: int   # Кумулятивное количество всех записей пациента
    no_show_ratio: float        # Доля пропусков приёмов (0.0–1.0)

    model_config = {
        "from_attributes": True
    }


from sqlalchemy import Column, Integer, String, Float, Boolean
from config.database import Base

class Patient(Base):
    patient_id = Column(Integer, primary_key=True)  
    gender = Column(String)
    age = Column(Integer)
    neighbourhood = Column(String)
    scholarship = Column(Boolean)
    hipertension = Column(Boolean)
    diabetes = Column(Boolean)
    alcoholism = Column(Boolean)
    handcap = Column(Boolean)
    sms_received = Column(Boolean)
    no_show_cumsum = Column(Integer)
    appointment_cumcount = Column(Integer)
    no_show_ratio = Column(Float)
    
    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.patient_id})")
    
    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.patient_id}")