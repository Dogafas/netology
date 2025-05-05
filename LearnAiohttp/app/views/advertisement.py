# app\views\advertisement.py
from aiohttp import web
from typing import List
from app.schemas import AdvertisementCreate, AdvertisementUpdate, AdvertisementResponse
from app.models import User, Advertisement
from app.crud import advertisement as crud_ad
from app.db import get_db_session
from .utils import get_request_user, validate_request_data  # Импортируем хелперы
import orjson

# --- Защищенные эндпоинты (требуют токен) ---


async def create_advertisement(request: web.Request) -> web.Response:
    """
    Создание нового объявления (требует аутентификации).
    Метод: POST /ads/
    """
    # Получаем текущего пользователя по токену
    current_user: User | None = await get_request_user(request)
    if not current_user:
        raise web.HTTPUnauthorized(reason="Authentication required")

    # Валидируем входные данные
    try:
        ad_in: AdvertisementCreate = await validate_request_data(
            request, AdvertisementCreate
        )
    except web.HTTPException as e:
        return e

    # Создаем объявление в БД
    async with get_db_session() as db_session:
        try:
            created_ad = await crud_ad.create_advertisement(
                db=db_session, ad_in=ad_in, owner_id=current_user.id
            )
        except Exception as e:
            print(f"Database error during ad creation: {e}")
            raise web.HTTPInternalServerError(reason="Could not create advertisement.")

        # Возвращаем созданное объявление
        response_data = AdvertisementResponse.model_validate(created_ad)  # Pydantic V2
        # Для Pydantic V1: response_data = AdvertisementResponse.from_orm(created_ad)
        return web.Response(
            body=orjson.dumps(response_data.model_dump()),
            status=201,
            content_type="application/json",
        )
        # Для Pydantic V1: return web.json_response(response_data.dict(), status=201)


async def update_advertisement(request: web.Request) -> web.Response:
    """
    Обновление объявления (только владелец).
    Метод: PUT /ads/{ad_id}
    """
    current_user: User | None = await get_request_user(request)
    if not current_user:
        raise web.HTTPUnauthorized(reason="Authentication required")

    # Получаем ID объявления из URL
    try:
        ad_id = int(request.match_info["ad_id"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest(reason="Invalid advertisement ID format")

    # Валидируем входные данные
    try:
        ad_in: AdvertisementUpdate = await validate_request_data(
            request, AdvertisementUpdate
        )
    except web.HTTPException as e:
        return e

    # Проверяем, есть ли что обновлять
    if not ad_in.model_dump(exclude_unset=True):  # Pydantic V2
        # Для Pydantic V1: if not ad_in.dict(exclude_unset=True):
        raise web.HTTPBadRequest(reason="No fields provided for update")

    async with get_db_session() as db_session:
        # Находим объявление в БД
        db_ad = await crud_ad.get_advertisement_by_id(db=db_session, ad_id=ad_id)
        if not db_ad:
            raise web.HTTPNotFound(reason="Advertisement not found")

        # Проверяем права доступа (владелец ли?)
        if db_ad.owner_id != current_user.id:
            raise web.HTTPForbidden(
                reason="You do not have permission to modify this advertisement"
            )

        # Обновляем объявление
        try:
            updated_ad = await crud_ad.update_advertisement(
                db=db_session, db_ad=db_ad, ad_in=ad_in
            )
        except Exception as e:
            print(f"Database error during ad update: {e}")
            raise web.HTTPInternalServerError(reason="Could not update advertisement.")

        response_data = AdvertisementResponse.model_validate(updated_ad)  # Pydantic V2
        # Для Pydantic V1: response_data = AdvertisementResponse.from_orm(updated_ad)
        return web.Response(
            body=orjson.dumps(response_data.model_dump()),
            content_type="application/json",
        )
        # Для Pydantic V1: return web.json_response(response_data.dict())


async def delete_advertisement(request: web.Request) -> web.Response:
    """
    Удаление объявления (только владелец).
    Метод: DELETE /ads/{ad_id}
    """
    current_user: User | None = await get_request_user(request)
    if not current_user:
        raise web.HTTPUnauthorized(reason="Authentication required")

    try:
        ad_id = int(request.match_info["ad_id"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest(reason="Invalid advertisement ID format")

    async with get_db_session() as db_session:
        db_ad = await crud_ad.get_advertisement_by_id(db=db_session, ad_id=ad_id)
        if not db_ad:
            raise web.HTTPNotFound(reason="Advertisement not found")

        if db_ad.owner_id != current_user.id:
            raise web.HTTPForbidden(
                reason="You do not have permission to delete this advertisement"
            )

        try:
            await crud_ad.delete_advertisement(db=db_session, db_ad=db_ad)
        except Exception as e:
            print(f"Database error during ad deletion: {e}")
            raise web.HTTPInternalServerError(reason="Could not delete advertisement.")

        # Успешное удаление, возвращаем 204 No Content
        return web.Response(status=204)


# --- Публичные эндпоинты ---


async def list_advertisements(request: web.Request) -> web.Response:
    """
    Получение списка объявлений (публичный доступ).
    Метод: GET /ads/
    Параметры запроса (query params): ?skip=0&limit=10
    """
    # Получаем параметры пагинации из query string (с значениями по умолчанию)
    try:
        skip = int(request.query.get("skip", "0"))
        limit = int(request.query.get("limit", "10"))
        if skip < 0 or limit <= 0 or limit > 100:  # Ограничиваем limit
            raise ValueError("Invalid pagination parameters")
    except ValueError as e:
        raise web.HTTPBadRequest(reason=str(e))

    async with get_db_session() as db_session:
        ads_list = await crud_ad.get_advertisements(
            db=db_session, skip=skip, limit=limit
        )

        # Преобразуем список ORM моделей в список Pydantic схем
        response_data = [
            AdvertisementResponse.model_validate(ad) for ad in ads_list
        ]  # Pydantic V2
        # Для Pydantic V1: response_data = [AdvertisementResponse.from_orm(ad) for ad in ads_list]

        # Преобразуем каждую схему в словарь для JSON ответа
        response_json = [ad.model_dump() for ad in response_data]  # Pydantic V2
        # Для Pydantic V1: response_json = [ad.dict() for ad in response_data]
        return web.Response(
            body=orjson.dumps(response_json),
            content_type="application/json",
        )


async def get_advertisement(request: web.Request) -> web.Response:
    """
    Получение одного объявления по ID (публичный доступ).
    Метод: GET /ads/{ad_id}
    """
    try:
        ad_id = int(request.match_info["ad_id"])
    except (KeyError, ValueError):
        raise web.HTTPBadRequest(reason="Invalid advertisement ID format")

    async with get_db_session() as db_session:
        db_ad = await crud_ad.get_advertisement_by_id(db=db_session, ad_id=ad_id)
        if not db_ad:
            raise web.HTTPNotFound(reason="Advertisement not found")

        response_data = AdvertisementResponse.model_validate(db_ad)  # Pydantic V2
        # Для Pydantic V1: response_data = AdvertisementResponse.from_orm(db_ad)
        return web.Response(
            body=orjson.dumps(response_data.model_dump()),
            content_type="application/json",
        )
