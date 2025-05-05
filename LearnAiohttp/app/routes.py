# app\routes.py
from aiohttp import web
from app.views import user as user_views
from app.views import advertisement as ad_views


def setup_routes(app: web.Application):
    """
    Настраивает маршруты для приложения aiohttp.
    """
    print("Setting up routes...")

    # Маршруты для пользователей
    app.router.add_post("/users/register", user_views.register_user, name="register")
    app.router.add_post("/users/login", user_views.login_for_access_token, name="login")

    # Маршруты для объявлений (CRUD)
    # Создание (POST /ads/) - требует токена
    app.router.add_post("/ads/", ad_views.create_advertisement, name="create_ad")
    # Получение списка (GET /ads/) - публичный
    app.router.add_get("/ads/", ad_views.list_advertisements, name="list_ads")
    # Получение одного (GET /ads/{ad_id}) - публичный
    app.router.add_get(
        "/ads/{ad_id:\d+}", ad_views.get_advertisement, name="get_ad"
    )  # \d+ только цифры
    # Обновление (PUT /ads/{ad_id}) - требует токена, владелец
    app.router.add_put(
        "/ads/{ad_id:\d+}", ad_views.update_advertisement, name="update_ad"
    )
    # Удаление (DELETE /ads/{ad_id}) - требует токена, владелец
    app.router.add_delete(
        "/ads/{ad_id:\d+}", ad_views.delete_advertisement, name="delete_ad"
    )

    print("Routes configured.")
