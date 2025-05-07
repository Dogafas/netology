# app\security\auth.py
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# --- Хеширование паролей ---

# Настраиваем контекст passlib для хеширования паролей
# Используем bcrypt как схему по умолчанию
# deprecated="auto" автоматически обновит хеши при использовании старых алгоритмов (если добавить)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли предоставленный пароль хешу.

    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хеш пароля из базы данных.

    Returns:
        True, если пароли совпадают, иначе False.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Логирование ошибки может быть полезно
        print(f"Error verifying password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Генерирует хеш для заданного пароля.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Строка с хешем пароля.
    """
    return pwd_context.hash(password)


# --- Работа с JWT ---
def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT access token.

    Args:
        data: Данные (payload) для включения в токен (например, {'user_id': 1}).
        expires_delta: Необязательное время жизни токена. Если не указано,
                       используется значение ACCESS_TOKEN_EXPIRE_MINUTES из конфига.

    Returns:
        Строка с закодированным JWT.

    Raises:
        ValueError: Если JWT_SECRET_KEY не установлен.
    """
    if not JWT_SECRET_KEY:
        # Критично для безопасности, без ключа не можем генерировать токены
        raise ValueError("JWT_SECRET_KEY is not set in the configuration.")

    to_encode = data.copy()

    # Устанавливаем время истечения токена
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})

    # Добавляем время создания токена (опционально, но полезно)
    to_encode.update({"iat": datetime.now(timezone.utc)})

    # Кодируем токен
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt  # Возвращаем строку токена


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Декодирует JWT access token и возвращает его полезную нагрузку (payload).

    Args:
        token: Строка с JWT.

    Returns:
        Словарь с данными токена (payload) или None, если токен невалиден или истек.
    """
    if not JWT_SECRET_KEY:
        print("Warning: JWT_SECRET_KEY is not set. Cannot decode token.")
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        # Можно добавить дополнительную валидацию payload, если нужно
        # Например, проверить наличие обязательных полей
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.PyJWTError as e:
        # Ловим общую ошибку PyJWT (неверная подпись, неверный формат и т.д.)
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        # На случай других непредвиденных ошибок
        print(f"An unexpected error occurred during token decoding: {e}")
        return None
