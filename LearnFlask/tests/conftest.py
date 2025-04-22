# tests/conftest.py
import sys
import os

# Добавляем корневую директорию проекта в sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import pytest
from app import create_app, db
from app.config import TestConfig
from app.models.user import User
from app.models.advert import Advert


@pytest.fixture(scope="session")
def app():
    """Создает экземпляр приложения Flask для тестовой сессии."""
    _app = create_app(TestConfig)

    with _app.app_context():
        print("\n--- [Session Setup] Dropping all tables (if they exist) ---")
        db.drop_all()
        print("\n--- [Session Setup] Creating all tables for test database ---")
        db.create_all()

        yield _app  # Предоставляем приложение тестам

        print("\n--- [Session Teardown] Dropping all tables in test database ---")
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Фикстура тестового клиента Flask."""
    return app.test_client()


@pytest.fixture()
def db_session(app):
    """Предоставляет стандартную сессию Flask-SQLAlchemy db.session."""
    with app.app_context():
        yield db.session


@pytest.fixture(autouse=True)
def clean_tables(app, db_session):  # Зависит от db_session для контекста
    """Очищает данные из таблиц после каждого теста."""
    yield  # Даем тесту выполниться

    # Очистка данных после теста
    print("\n--- [Test Teardown] Cleaning data from tables ---")
    try:
        # СНАЧАЛА удаляем записи, которые ССЫЛАЮТСЯ на другие (Adverts -> Users)
        db_session.query(Advert).delete()
        # ПОТОМ удаляем записи, на которые ссылались
        db_session.query(User).delete()
        db_session.commit()  # Подтверждаем удаление
        print("--- [Test Teardown] Data cleaned successfully ---")
    except Exception as e:
        print(f"Error during table cleanup: {e}")
        db_session.rollback()  # Откатываем, если удаление не удалось
    finally:
        db_session.remove()  # Убираем сессию в любом случае


@pytest.fixture()
def auth_headers(client, db_session):
    """
    Создает пользователя, логинит его и возвращает
    заголовки авторизации и объект пользователя.
    """
    email = "owner@example.com"
    password = "password"
    # 1. Создаем пользователя
    user = User(email=email)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()  # Важно сохранить пользователя

    # 2. Логинимся, чтобы получить токен
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200  # Убедимся, что логин успешен
    access_token = response.json["access_token"]

    # 3. Формируем заголовки
    headers = {"Authorization": f"Bearer {access_token}"}
    # Возвращаем заголовки и пользователя
    return headers, user
