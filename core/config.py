from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Akaza restaurante Backend"

    # Conexión Base de Datos
    DATABASE_URL: str

    # API Keys
    GEMINI_API_KEY: str
    TELEGRAM_API_KEY: str
    SECRET_KEY: str
    ID_ADMIN: str

    class Config:
        env_file = ".env"


settings = Settings()