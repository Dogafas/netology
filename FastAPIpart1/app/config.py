from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn  # Специальный тип для DSN PostgreSQL


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

    # Сгенерируем DSN (Data Source Name) для SQLAlchemy асинхронного подключения
    # Формат: postgresql+asyncpg://user:password@host:port/database
    # Используем @property, чтобы DSN пересчитывался при изменении компонентов
    @property
    def DATABASE_URL_ASYNC(self) -> PostgresDsn:
        """
        Генерирует асинхронный DSN для подключения к PostgreSQL.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Конфигурация для Pydantic BaseSettings
    model_config = SettingsConfigDict(
        env_file=".env",  # Указываем имя .env файла
        env_file_encoding="utf-8",  # Указываем кодировку
        extra="ignore",  # Игнорировать лишние переменные в окружении
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
