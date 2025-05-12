from pydantic import BaseModel
from datetime import date

class AppointmentInDB(BaseModel):
    doctor_name : str
    slot_id: int
    patient_id: int
    appointment_id: int
    appointment_date: date    # Дата приема
    scheduled_date: date      # Дата записи

    model_config = {
        "from_attributes": True
    }

from sqlalchemy import Column, Integer, Date, String
from config.database import Base

class Appointment(Base):
    appointment_id = Column(Integer, primary_key=True)
    doctor_name = Column(String)
    slot_id = Column(Integer)
    patient_id = Column(Integer)
    scheduled_date = Column(Date)
    appointment_date = Column(Date)

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.appointment_id})")
    
    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.appointment_id}")