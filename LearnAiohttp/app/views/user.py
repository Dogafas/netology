# app\views\user.py
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError  # Для отлова ошибки уникальности

from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.models import User
from app.crud import user as crud_user
from app.security import get_password_hash, verify_password, create_access_token
from app.db import get_db_session  # Импортируем менеджер сессий
from .utils import validate_request_data  # Импортируем валидатор
import orjson


async def register_user(request: web.Request) -> web.Response:
    """
    Обработчик для регистрации нового пользователя.
    Метод: POST
    Путь: /users/register (или похожий)
    Тело запроса: JSON с данными UserCreate (email, password).
    Ответ: JSON с данными UserResponse (id, email, created_at).
    """
    try:
        user_in: UserCreate = await validate_request_data(request, UserCreate)
    except web.HTTPException as e:
        # Перехватываем ошибку валидации и возвращаем ее
        return e

    async with get_db_session() as db_session:
        # Проверяем, не существует ли уже пользователь с таким email
        existing_user = await crud_user.get_user_by_email(
            db_session, email=user_in.email
        )
        if existing_user:
            raise web.HTTPConflict(
                reason=f"User with email '{user_in.email}' already exists."
            )

        # Хешируем пароль
        hashed_password = get_password_hash(user_in.password)

        try:
            # Создаем пользователя в БД
            created_user = await crud_user.create_user(
                db=db_session, user_in=user_in, password_hash=hashed_password
            )
        except (
            IntegrityError
        ):  # На случай, если гонка запросов все же привела к дубликату
            raise web.HTTPConflict(
                reason="User with this email already exists (concurrent request)."
            )
        except Exception as e:
            # Обработка других возможных ошибок БД
            print(f"Database error during user creation: {e}")
            raise web.HTTPInternalServerError(
                reason="Could not create user due to a database error."
            )

        # Преобразуем ORM модель в Pydantic схему для ответа
        response_data = UserResponse.model_validate(created_user)  # Pydantic V2
        # Для Pydantic V1: response_data = UserResponse.from_orm(created_user)

        return web.Response(
            body=orjson.dumps(response_data.model_dump()),
            status=201,
            content_type="application/json",
        )
        # Для Pydantic V1: return web.json_response(response_data.dict(), status=201)


async def login_for_access_token(request: web.Request) -> web.Response:
    """
    Обработчик для входа пользователя и получения JWT токена.
    Метод: POST
    Путь: /users/login (или /token)
    Тело запроса: JSON с данными UserLogin (email, password).
    Ответ: JSON с данными Token (access_token, token_type).
    """
    try:
        login_data: UserLogin = await validate_request_data(request, UserLogin)
    except web.HTTPException as e:
        return e

    async with get_db_session() as db_session:
        # Ищем пользователя по email
        user = await crud_user.get_user_by_email(db_session, email=login_data.email)

        # Проверяем, найден ли пользователь и верен ли пароль
        if not user or not verify_password(login_data.password, user.password_hash):
            raise web.HTTPUnauthorized(reason="Incorrect email or password")

        # Создаем JWT токен
        access_token_data = {"user_id": user.id}  # Данные для включения в токен
        try:
            access_token = create_access_token(data=access_token_data)
        except ValueError as e:  # Если JWT_SECRET_KEY не задан
            print(f"JWT configuration error: {e}")
            raise web.HTTPInternalServerError(reason="Server configuration error.")

        # Формируем ответ с токеном
        token_response = Token(access_token=access_token)
        return web.Responce(
            body=orjson.dumps(token_response.model_dump()),
            content_type="application/json",
        )
        # Для Pydantic V1: return web.json_response(token_response.dict())
