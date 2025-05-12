import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str               
    ALGORITHM: str = "HS256"                     # Алгоритм подписи JWT-токена.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24*30  # Время действия токена.

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "jwt.env")
    )     

# Создаем и загружаем настройки
settings = Settings()

def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}

