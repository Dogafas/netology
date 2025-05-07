# app/views/advertisement.py
import orjson  # Используем orjson для сериализации JSON
from aiohttp import web

# Импортируем Pydantic схемы
from app.schemas import AdvertisementCreate, AdvertisementUpdate, AdvertisementResponse

# Импортируем модели SQLAlchemy
from app.models import User

# Импортируем CRUD функции
from app.crud import advertisement as crud_ad

# Импортируем менеджер сессий БД
from app.db import get_db_session

# Импортируем валидатор данных запроса
from .utils import validate_request_data

# --- Защищенные эндпоинты (требуют токен, проверяется в auth_middleware) ---


async def create_advertisement(request: web.Request) -> web.Response:
    """
    Создание нового объявления.
    Аутентификация проверяется в auth_middleware.
    Метод: POST /ads/
    Тело запроса: JSON с AdvertisementCreate (title, description).
    Ответ: JSON с AdvertisementResponse (созданное объявление).
    """
    # Получаем пользователя из request, добавленного middleware
    # Типизация User | None важна для mypy/статического анализа
    current_user: User | None = request.get("user")

    # Middleware уже должно было вернуть 401, если юзера нет,
    # но добавим проверку для надежности.
    if not current_user:
        # Эта ситуация не должна возникать при правильной работе middleware
        print("Error: User not found in request after auth middleware.")
        raise web.HTTPInternalServerError(reason="Authentication failed unexpectedly.")

    # Валидируем входные данные JSON из тела запроса
    try:
        ad_in: AdvertisementCreate = await validate_request_data(
            request, AdvertisementCreate
        )
    except web.HTTPException as e:
        # Возвращаем ошибку валидации (например, 400 Bad Request)
        return e

    # Создаем объявление в БД
    async with get_db_session() as db_session:
        try:
            created_ad = await crud_ad.create_advertisement(
                db=db_session, ad_in=ad_in, owner_id=current_user.id
            )
            # Преобразуем ORM модель в Pydantic схему для ответа
            response_data = AdvertisementResponse.model_validate(created_ad)

            # Возвращаем успешный ответ с данными созданного объявления
            return web.Response(
                body=orjson.dumps(response_data.model_dump()),
                status=201,
                content_type="application/json",
            )
        except Exception as e:
            # Обработка других возможных ошибок БД
            print(f"Database error during ad creation: {e}")
            raise web.HTTPInternalServerError(
                reason="Could not create advertisement due to a database error."
            )


async def update_advertisement(request: web.Request) -> web.Response:
    """
    Обновление объявления (только владелец).
    Аутентификация и наличие пользователя проверяются в auth_middleware.
    Метод: PUT /ads/{ad_id}
    Тело запроса: JSON с AdvertisementUpdate (опциональные title, description).
    Ответ: JSON с AdvertisementResponse (обновленное объявление).
    """
    current_user: User | None = request.get("user")
    if not current_user:
        print("Error: User not found in request after auth middleware.")
        raise web.HTTPInternalServerError(reason="Authentication failed unexpectedly.")

    # Получаем ID объявления из URL
    try:
        ad_id = int(request.match_info["ad_id"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest(reason="Invalid advertisement ID format in URL")

    # Валидируем входные данные JSON из тела запроса
    try:
        ad_in: AdvertisementUpdate = await validate_request_data(
            request, AdvertisementUpdate
        )
    except web.HTTPException as e:
        return e

    # Проверяем, переданы ли вообще поля для обновления
    if not ad_in.model_dump(exclude_unset=True):
        raise web.HTTPBadRequest(reason="No fields provided for update in request body")

    async with get_db_session() as db_session:
        # Находим объявление в БД
        db_ad = await crud_ad.get_advertisement_by_id(db=db_session, ad_id=ad_id)
        if not db_ad:
            raise web.HTTPNotFound(reason=f"Advertisement with ID {ad_id} not found")

        # Проверяем права доступа (пользователь должен быть владельцем)
        if db_ad.owner_id != current_user.id:
            raise web.HTTPForbidden(
                reason="You do not have permission to modify this advertisement"
            )

        # Обновляем объявление в БД
        try:
            updated_ad = await crud_ad.update_advertisement(
                db=db_session, db_ad=db_ad, ad_in=ad_in
            )
            # Формируем ответ
            response_data = AdvertisementResponse.model_validate(updated_ad)

            return web.Response(
                body=orjson.dumps(response_data.model_dump()),
                content_type="application/json",
            )
        except Exception as e:
            print(f"Database error during ad update: {e}")
            raise web.HTTPInternalServerError(
                reason="Could not update advertisement due to a database error."
            )


async def delete_advertisement(request: web.Request) -> web.Response:
    """
    Удаление объявления (только владелец).
    Аутентификация и наличие пользователя проверяются в auth_middleware.
    Метод: DELETE /ads/{ad_id}
    Ответ: Статус 204 No Content в случае успеха.
    """
    current_user: User | None = request.get("user")
    if not current_user:
        print("Error: User not found in request after auth middleware.")
        raise web.HTTPInternalServerError(reason="Authentication failed unexpectedly.")

    # Получаем ID объявления из URL
    try:
        ad_id = int(request.match_info["ad_id"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest(reason="Invalid advertisement ID format in URL")

    async with get_db_session() as db_session:
        # Находим объявление
        db_ad = await crud_ad.get_advertisement_by_id(db=db_session, ad_id=ad_id)
        if not db_ad:
            raise web.HTTPNotFound(reason=f"Advertisement with ID {ad_id} not found")

        # Проверяем права доступа
        if db_ad.owner_id != current_user.id:
            raise web.HTTPForbidden(
                reason="You do not have permission to delete this advertisement"
            )

        # Удаляем объявление
        try:
            await crud_ad.delete_advertisement(db=db_session, db_ad=db_ad)
            # Успешное удаление, возвращаем 204 No Content без тела ответа
            return web.Response(status=204)
        except Exception as e:
            print(f"Database error during ad deletion: {e}")
            raise web.HTTPInternalServerError(
                reason="Could not delete advertisement due to a database error."
            )


# --- Публичные эндпоинты (не требуют токена) ---


async def list_advertisements(request: web.Request) -> web.Response:
    """
    Получение списка объявлений (публичный доступ).
    Метод: GET /ads/
    Параметры запроса: ?skip=0&limit=10
    Ответ: JSON со списком объектов AdvertisementResponse.
    """
    # Получаем параметры пагинации из query string с валидацией
    try:
        skip = int(request.query.get("skip", "0"))
        limit = int(request.query.get("limit", "10"))  # По умолчанию 10
        if skip < 0:
            raise ValueError("Parameter 'skip' must be non-negative.")
        # Ограничим максимальный limit для предотвращения перегрузки
        if not (0 < limit <= 100):
            raise ValueError("Parameter 'limit' must be between 1 and 100.")
    except ValueError as e:
        raise web.HTTPBadRequest(reason=f"Invalid pagination parameters: {e}")

    async with get_db_session() as db_session:
        ads_list = await crud_ad.get_advertisements(
            db=db_session, skip=skip, limit=limit
        )

        # Преобразуем список ORM моделей в список Pydantic схем
        response_data = [AdvertisementResponse.model_validate(ad) for ad in ads_list]

        # Преобразуем каждую схему в словарь для JSON ответа
        response_json = [ad.model_dump() for ad in response_data]

        return web.Response(
            body=orjson.dumps(response_json),
            content_type="application/json",
        )


async def get_advertisement(request: web.Request) -> web.Response:
    """
    Получение одного объявления по ID (публичный доступ).
    Метод: GET /ads/{ad_id}
    Ответ: JSON с объектом AdvertisementResponse.
    """
    # Получаем ID объявления из URL
    try:
        ad_id = int(request.match_info["ad_id"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest(reason="Invalid advertisement ID format in URL")

    async with get_db_session() as db_session:
        # Получаем объявление из БД (включая данные владельца, если настроено в CRUD)
        db_ad = await crud_ad.get_advertisement_by_id(db=db_session, ad_id=ad_id)
        if not db_ad:
            raise web.HTTPNotFound(reason=f"Advertisement with ID {ad_id} not found")

        # Преобразуем ORM модель в Pydantic схему
        response_data = AdvertisementResponse.model_validate(db_ad)

        # Возвращаем ответ
        return web.Response(
            body=orjson.dumps(response_data.model_dump()),
            content_type="application/json",
        )
