from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, EmailStr


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения, считываемых из переменных окружения
    и .env файла. Использует Pydantic для валидации.
    """

    # Настройки PostgreSQL
    # Pydantic попытается найти переменную окружения с таким же именем
    # (регистронезависимо) или в .env файле.
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432  # Значение по умолчанию
    POSTGRES_DB: str

    # Конфигурация для Pydantic BaseSettings
    model_config = SettingsConfigDict(
        env_file=".env",  # Указываем имя .env файла
        env_file_encoding="utf-8",  # Указываем кодировку
        extra="ignore",  # Игнорировать лишние переменные в окружении
    )

    # Настройки JWT
    JWT_SECRET_KEY: str = (
        "your-default-secret-key-change-me-in-env"  # Значение по умолчанию
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 48 * 60  # 48 часов = 2880 минут

    # НАСТРОЙКИ ДЛЯ АДМИНИСТРАТОРА ПО УМОЛЧАНИЮ
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: EmailStr = "admin@example.com"
    ADMIN_PASSWORD: str = "Changeme123!"  # Обязательно изменить это в .env!

    @property
    def DATABASE_URL_ASYNC(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings()

# Небольшая проверка при запуске модуля
# if __name__ == "__main__":
#     print("Loaded settings:")
#     print(f"  User: {settings.POSTGRES_USER}")
#     print(f"  Server: {settings.POSTGRES_SERVER}")
#     print(f"  Port: {settings.POSTGRES_PORT}")
#     print(f"  DB: {settings.POSTGRES_DB}")
#     # Пароль не выводим в лог по соображениям безопасности
#     # print(f"  Password: {settings.POSTGRES_PASSWORD}")
#     print(f"  Async DSN: {settings.DATABASE_URL_ASYNC}")
