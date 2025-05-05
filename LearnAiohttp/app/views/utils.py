# app\views\utils.py
from typing import Type, Optional
from pydantic import BaseModel, ValidationError
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.security import get_user_from_token
from app.db import get_db_session  # Импортируем менеджер сессий


async def get_request_user(request: web.Request) -> Optional[User]:
    """
    Извлекает пользователя из запроса на основе JWT токена в заголовке Authorization.

    Args:
        request: Объект запроса aiohttp.

    Returns:
        Объект User или None, если токен отсутствует, невалиден,
        или пользователь не найден.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None  # Нет заголовка или неверный формат

    token = auth_header.split(" ")[1]

    # Получаем сессию БД для запроса пользователя
    async with get_db_session() as db_session:
        user = await get_user_from_token(token=token, db=db_session)
        return user


async def validate_request_data(
    request: web.Request, schema: Type[BaseModel]
) -> BaseModel:
    """
    Извлекает JSON из тела запроса и валидирует его с помощью Pydantic схемы.

    Args:
        request: Объект запроса aiohttp.
        schema: Класс Pydantic схемы для валидации.

    Returns:
        Экземпляр Pydantic схемы с валидными данными.

    Raises:
        web.HTTPBadRequest: Если тело запроса не JSON или данные невалидны.
    """
    try:
        json_data = await request.json()
    except Exception:  # Ловим ошибку парсинга JSON
        raise web.HTTPBadRequest(reason="Invalid JSON body")

    try:
        validated_data = schema.model_validate(json_data)  # Pydantic V2
        # Для Pydantic V1 используйте: validated_data = schema(**json_data)
        return validated_data
    except ValidationError as e:
        # Формируем сообщение об ошибке валидации
        error_details = e.errors()  # [{loc: ('field',), msg: '...', type: '...'}]
        raise web.HTTPBadRequest(
            reason=f"Validation failed: {error_details}",
            content_type="application/json",  # Можно вернуть ошибки в json
            # body=json.dumps({"detail": error_details}) # Если хотим вернуть детали
        )
    except Exception as e:  # На случай других ошибок Pydantic
        raise web.HTTPBadRequest(reason=f"Data parsing error: {e}")
