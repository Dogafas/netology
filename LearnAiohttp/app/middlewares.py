# app\middlewares.py

from typing import Awaitable, Callable, Set
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import StreamResponse
from app.db import get_db_session
from app.security import get_user_from_token
from app.models import User

# Определим множество имен роутов, которые требуют аутентификации
# Имена берутся из файла app/routes.py (параметр name=...)
PROTECTED_ROUTE_NAMES: Set[str] = {
    "create_ad",
    "update_ad",
    "delete_ad",
    # Добавлять сюда другие имена роутов, если они появятся и будут требовать защиты
}


@web.middleware
async def auth_middleware(
    request: Request,
    handler: Callable[[Request], Awaitable[StreamResponse]],
) -> StreamResponse:
    """
    Middleware для проверки JWT токена в заголовке Authorization.

    - Проверяет токен только для роутов, указанных в PROTECTED_ROUTE_NAMES.
    - Если токен валиден, добавляет объект User в request['user'].
    - Если роут защищен, но токен невалиден или отсутствует, возвращает 401 Unauthorized.
    - Для публичных роутов просто вызывает следующий обработчик.
    """
    # Добавляем ключ 'user' в запрос со значением None по умолчанию
    # Это гарантирует, что ключ всегда будет присутствовать
    request["user"] = None

    # Получаем информацию о текущем совпавшем роуте
    current_route_name = request.match_info.route.name

    # Проверяем, нужно ли защищать этот роут
    if current_route_name in PROTECTED_ROUTE_NAMES:
        print(
            f"Route '{current_route_name}' requires authentication. Checking token..."
        )  # Для отладки

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print("Authentication failed: Missing or invalid Authorization header.")
            raise web.HTTPUnauthorized(
                reason="Authentication required. Missing or invalid Authorization header.",
                headers={"WWW-Authenticate": "Bearer"},  # Стандартный заголовок для 401
            )

        token = auth_header.split(" ")[1]

        try:
            # Получаем сессию БД для запроса пользователя
            # Важно: делаем это только если роут защищен
            async with get_db_session() as db_session:
                user: User | None = await get_user_from_token(
                    token=token, db=db_session
                )

                if user is None:
                    print(
                        "Authentication failed: Invalid or expired token, or user not found."
                    )
                    raise web.HTTPUnauthorized(
                        reason="Invalid or expired token.",
                        headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
                    )

                # Если пользователь найден, добавляем его в объект запроса
                print(
                    f"Authentication successful for user ID: {user.id}"
                )  # Для отладки
                request["user"] = user

        except web.HTTPUnauthorized as e:
            # Просто пробрасываем исключение, если оно уже было сгенерировано
            raise e
        except Exception as e:
            # Ловим другие возможные ошибки при получении сессии или пользователя
            print(f"Error during authentication: {e}")
            # Лучше вернуть 500, т.к. это внутренняя проблема сервера
            raise web.HTTPInternalServerError(
                reason="Server error during authentication."
            )

    else:
        print(
            f"Route '{current_route_name}' is public. Skipping authentication."
        )  # Для отладки

    # Если аутентификация прошла (для защищенных роутов) или не требовалась,
    # вызываем следующий обработчик в цепочке (или сам view)
    response = await handler(request)
    return response
