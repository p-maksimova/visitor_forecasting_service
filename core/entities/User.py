from pydantic import BaseModel, EmailStr

# Базовая схема пользователя с общими данными
class UserBase(BaseModel):
    email: EmailStr

# Схема для авторизации пользователя
class UserAuth(UserBase):
    password: str  # открытый пароль, который будет захэширован

# Схема для создания нового пользователя (при регистрации)
class UserCreate(UserAuth):
    first_name: str
    last_name: str
    password: str  # открытый пароль, который будет захэширован

# Схема представления пользователя в базе данных (с хэшированным паролем)
class UserInDB(UserBase):
    user_id: int
    first_name: str
    last_name: str
    hashed_password: str

    model_config = {
        "from_attributes": True
    }


from sqlalchemy import Column, Integer, String
from config.database import Base

class User(Base):
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    email = Column(String)

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.user_id})")
    
    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.user_id}")