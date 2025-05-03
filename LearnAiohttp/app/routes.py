# app\routes.py
from aiohttp import web


def setup_routes(app: web.Application):
    """
    Настраивает маршруты для приложения aiohttp.
    Пока что эта функция пуста, мы добавим реальные роуты позже.
    """
    # Пример добавления роута (закомментирован)
    # app.router.add_get('/', lambda request: web.Response(text="Hello, world!"))
    print("Setting up routes...")  # Для отладки
    pass  # Добавим сюда роуты на следующих шагах
