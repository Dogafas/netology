# tests/test_api.py
import sys
import os
import pytest
from app import create_app, db
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Load .env file
load_dotenv()


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('TEST_DB_NAME')}",
        }
    )

    with app.app_context():
        from flask_migrate import upgrade
        upgrade()
        # Debug: List tables
        tables = db.engine.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'").fetchall()
        print("Tables in test_learnflask:", tables)
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 201
