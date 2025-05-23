# app\security.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from .config import (
    settings,
)
from . import schemas, crud, models
from .database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession


# --- Настройки для JWT ---


JWT_SECRET_KEY = getattr(
    settings, "JWT_SECRET_KEY", "your-super-secret-key-please-change-it"
)
ALGORITHM = getattr(settings, "ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(
    settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 48 * 60
)  # 48 часов

# --- Контекст для хеширования паролей ---
# Используем bcrypt как схему по умолчанию
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Схема ---
# "tokenUrl" указывает на эндпоинт, где можно получить токен (наш /login)
# Это используется Swagger UI для удобной авторизации через интерфейс.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# --- Функции для работы с паролями ---


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли обычный пароль хешированному."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Возвращает хеш пароля."""
    return pwd_context.hash(password)


# --- Функции для работы с JWT токенами ---


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT токен доступа."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # По умолчанию токен действителен ACCESS_TOKEN_EXPIRE_MINUTES минут
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Зависимость для получения текущего пользователя ---


async def get_current_user(
    token: Annotated[
        str, Depends(oauth2_scheme)
    ],  # Получаем токен из заголовка Authorization: Bearer <token>
    db: Annotated[AsyncSession, Depends(get_async_session)],  # Получаем сессию БД
) -> models.User:
    """
    Декодирует токен, проверяет его валидность и возвращает объект пользователя из БД.
    Если токен невалиден или пользователь не найден, выбрасывает HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем JWT токен
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        # Извлекаем имя пользователя из полезной нагрузки (payload)
        username: Optional[str] = payload.get(
            "sub"
        )  # "sub" (subject) - стандартное поле для идентификатора пользователя
        if username is None:
            raise credentials_exception  # Если имени пользователя нет в токене

        # Создаем объект TokenData для валидации
        token_data = schemas.TokenData(username=username)

    except (
        JWTError
    ):  # Если произошла ошибка при декодировании (например, неверная подпись, истек срок)
        raise credentials_exception
    except ValidationError:  # Если данные в токене не соответствуют схеме TokenData
        raise credentials_exception

    # Получаем пользователя из базы данных по имени пользователя из токена
    user = await crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        # Если пользователь, указанный в токене, не найден в БД
        raise credentials_exception

    # Возвращаем объект пользователя SQLAlchemy
    return user


# --- Зависимость для получения текущего активного пользователя ---
async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    """
    Проверяет, активен ли пользователь (если бы у нас было поле is_active).
    В данном случае просто возвращает текущего пользователя.
    """
    # if not current_user.is_active:  # Пример, если бы было поле is_active
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# --- Зависимости для проверки прав ---


async def get_current_admin_user(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
) -> models.User:
    """
    Проверяет, является ли текущий пользователь администратором.
    Если нет, выбрасывает HTTPException 403 Forbidden.
    """
    if current_user.group != models.UserGroup.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (admin required).",
        )
    return current_user
