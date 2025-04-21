# tests/test_api.py

from app.models.user import User
from app.models.advert import Advert

# --- Тесты для регистрации (/api/auth/register) ---


def test_register_user_success(client, db_session):
    """
    Тест успешной регистрации нового пользователя.
    """
    response = client.post(
        "/api/auth/register",
        json={"email": "testuser@example.com", "password": "password123"},
    )

    # 1. Проверяем HTTP статус код
    assert response.status_code == 201

    # 2. Проверяем тело JSON ответа
    assert response.json == {"message": "User registered successfully"}

    # 3. Проверяем, что пользователь действительно создан в базе данных
    user = db_session.query(User).filter_by(email="testuser@example.com").first()
    assert user is not None
    assert user.email == "testuser@example.com"
    # Проверяем, что пароль сохранен не в открытом виде, а как хеш
    assert user.password_hash is not None
    assert user.password_hash != "password123"
    # Дополнительно можно проверить, что хеш корректен
    assert user.check_password("password123") is True
    assert user.check_password("wrongpassword") is False


def test_register_user_missing_email(client):
    """
    Тест регистрации пользователя без email.
    """
    response = client.post("/api/auth/register", json={"password": "password123"})
    assert response.status_code == 400
    assert response.json == {"message": "Email and password are required"}


def test_register_user_missing_password(client):
    """
    Тест регистрации пользователя без пароля.
    """
    response = client.post(
        "/api/auth/register", json={"email": "testuser2@example.com"}
    )
    assert response.status_code == 400
    assert response.json == {"message": "Email and password are required"}


def test_register_user_empty_data(client):
    """
    Тест регистрации пользователя с пустым JSON телом.
    """
    response = client.post("/api/auth/register", json={})
    assert response.status_code == 400
    assert response.json == {"message": "Email and password are required"}


def test_register_user_existing_email(client, db_session):
    """
    Тест регистрации пользователя с уже существующим email.
    """
    # Сначала создаем пользователя напрямую в БД через модель
    existing_user = User(email="existing@example.com")
    existing_user.set_password("password123")
    db_session.add(existing_user)
    db_session.commit()  # Сохраняем пользователя перед API запросом

    # Пытаемся зарегистрировать пользователя с тем же email через API
    response = client.post(
        "/api/auth/register",
        json={"email": "existing@example.com", "password": "newpassword"},
    )

    # Проверяем ожидаемый ответ об ошибке
    assert response.status_code == 400
    assert response.json == {"message": "Email already exists"}

    # Убедимся, что в БД остался только один пользователь с этим email
    user_count = db_session.query(User).filter_by(email="existing@example.com").count()
    assert user_count == 1


def test_register_user_wrong_method(client):
    """
    Тест попытки доступа к эндпоинту регистрации с неправильным методом (GET).
    """
    response = client.get("/api/auth/register")
    assert response.status_code == 405  # Method Not Allowed


# --- тесты для /api/auth/login  ---


def test_login_success(client, db_session):
    """
    Тест успешного входа пользователя с правильными учетными данными.
    """
    # Arrange: Создаем пользователя в БД
    email = "logintest@example.com"
    password = "goodpassword"
    user = User(email=email)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()

    # Act: Отправляем запрос на вход
    response = client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )

    # Assert: Проверяем успешный ответ и наличие токена
    assert response.status_code == 200
    assert "access_token" in response.json
    assert isinstance(response.json["access_token"], str)
    assert len(response.json["access_token"]) > 0  # Токен не пустой


def test_login_invalid_password(client, db_session):
    """
    Тест входа пользователя с неверным паролем.
    """
    # Arrange: Создаем пользователя
    email = "wrongpass@example.com"
    correct_password = "correctpassword"
    wrong_password = "wrongpassword"
    user = User(email=email)
    user.set_password(correct_password)
    db_session.add(user)
    db_session.commit()

    # Act: Пытаемся войти с неверным паролем
    response = client.post(
        "/api/auth/login", json={"email": email, "password": wrong_password}
    )

    # Assert: Проверяем ошибку 401 Unauthorized
    assert response.status_code == 401
    assert response.json == {"message": "Invalid credentials"}


def test_login_non_existent_user(client):
    """
    Тест входа с email пользователя, которого нет в базе данных.
    """
    # Arrange: БД чиста (благодаря clean_tables)

    # Act: Пытаемся войти с несуществующим email
    response = client.post(
        "/api/auth/login",
        json={"email": "nosuchuser@example.com", "password": "anypassword"},
    )

    # Assert: Проверяем ошибку 401 Unauthorized
    assert response.status_code == 401
    assert response.json == {"message": "Invalid credentials"}


def test_login_missing_email(client):
    """
    Тест входа без указания email в запросе.
    """
    # Act: Отправляем запрос без email
    response = client.post("/api/auth/login", json={"password": "somepassword"})

    # Assert: Ожидаем 401, т.к. User.query...first() вернет None
    assert response.status_code == 401
    assert response.json == {"message": "Invalid credentials"}


def test_login_missing_password(client, db_session):
    """
    Тест входа без указания пароля в запросе.
    """
    # Arrange: Создаем пользователя, чтобы был найден по email
    email = "nopassword@example.com"
    user = User(email=email)
    user.set_password("somepassword")
    db_session.add(user)
    db_session.commit()

    # Act: Отправляем запрос без пароля
    response = client.post("/api/auth/login", json={"email": email})

    # Assert: Ожидаем 401, т.к. check_password(None) вернет False
    assert response.status_code == 401
    assert response.json == {"message": "Invalid credentials"}


def test_login_empty_data(client):
    """
    Тест входа с пустым JSON телом.
    """
    # Act: Отправляем пустой запрос
    response = client.post("/api/auth/login", json={})

    # Assert: Ожидаем 401
    assert response.status_code == 401
    assert response.json == {"message": "Invalid credentials"}


def test_login_wrong_method(client):
    """
    Тест попытки доступа к эндпоинту входа с неправильным методом (GET).
    """
    response = client.get("/api/auth/login")
    assert response.status_code == 405  # Method Not Allowed


# Тесты для POST /api/adverts/ (Создание)
# ========================================


def test_create_advert_success(client, auth_headers, db_session):
    """Тест успешного создания объявления аутентифицированным пользователем."""
    headers, user = auth_headers  # Получаем заголовки и пользователя
    advert_data = {
        "title": "New Test Advert",
        "description": "This is a description for the test advert.",
    }

    response = client.post("/api/adverts/", json=advert_data, headers=headers)

    # Проверяем ответ
    assert response.status_code == 201
    json_data = response.json
    assert json_data["title"] == advert_data["title"]
    assert json_data["description"] == advert_data["description"]
    assert json_data["owner_id"] == user.id  # Проверяем владельца
    assert "id" in json_data
    assert "created_at" in json_data

    # Проверяем БД
    advert_in_db = db_session.query(Advert).filter_by(id=json_data["id"]).first()
    assert advert_in_db is not None
    assert advert_in_db.title == advert_data["title"]
    assert advert_in_db.owner_id == user.id


def test_create_advert_unauthorized(client):
    """Тест создания объявления без аутентификации."""
    advert_data = {"title": "Unauthorized Advert", "description": "Should fail"}
    response = client.post("/api/adverts/", json=advert_data)
    assert response.status_code == 401  # Ожидаем Unauthorized


def test_create_advert_missing_title(client, auth_headers):
    """Тест создания объявления без заголовка."""
    headers, _ = auth_headers
    advert_data = {"description": "Missing title here"}
    response = client.post("/api/adverts/", json=advert_data, headers=headers)
    assert response.status_code == 400
    assert response.json == {"message": "Title and description are required"}


def test_create_advert_missing_description(client, auth_headers):
    """Тест создания объявления без описания."""
    headers, _ = auth_headers
    advert_data = {"title": "Missing description"}
    response = client.post("/api/adverts/", json=advert_data, headers=headers)
    assert response.status_code == 400
    assert response.json == {"message": "Title and description are required"}


# Тесты для GET /api/adverts/ (Получение списка)
# ============================================


def test_get_adverts_empty(client):
    """Тест получения списка объявлений, когда их нет."""
    response = client.get("/api/adverts/")
    assert response.status_code == 200
    assert response.json == []


def test_get_adverts_with_data(client, db_session):
    """Тест получения списка с несколькими объявлениями."""
    # Arrange: Создаем пользователя и пару объявлений
    user = User(email="advert_lister@example.com")
    user.set_password("pw")
    db_session.add(user)
    db_session.commit()  # Сохраняем пользователя, чтобы получить user.id

    advert1 = Advert(title="Advert 1", description="First one", owner_id=user.id)
    advert2 = Advert(title="Advert 2", description="Second one", owner_id=user.id)
    db_session.add_all([advert1, advert2])
    db_session.commit()

    # Act
    response = client.get("/api/adverts/")

    # Assert
    assert response.status_code == 200
    json_data = response.json
    assert isinstance(json_data, list)
    assert len(json_data) == 2

    # Проверяем, что данные объявлений присутствуют (проверка id и title)
    response_titles = {ad["title"] for ad in json_data}
    expected_titles = {"Advert 1", "Advert 2"}
    assert response_titles == expected_titles
    assert all("id" in ad for ad in json_data)
    assert all("owner_id" in ad for ad in json_data)


# Тесты для PUT /api/adverts/<id> (Обновление)
# ===========================================


def test_update_advert_success(client, auth_headers, db_session):
    """Тест успешного обновления своего объявления."""
    headers, user = auth_headers
    # Arrange: Создаем объявление для этого пользователя
    advert = Advert(
        title="Original Title", description="Original Desc", owner_id=user.id
    )
    db_session.add(advert)
    db_session.commit()
    advert_id = advert.id  # Получаем ID

    update_data = {"title": "Updated Title", "description": "Updated Desc"}

    # Act
    response = client.put(
        f"/api/adverts/{advert_id}", json=update_data, headers=headers
    )

    # Assert
    assert response.status_code == 200
    json_data = response.json
    assert json_data["title"] == update_data["title"]
    assert json_data["description"] == update_data["description"]
    assert json_data["id"] == advert_id
    assert json_data["owner_id"] == user.id

    # Проверяем БД
    updated_advert = db_session.get(Advert, advert_id)
    assert updated_advert.title == update_data["title"]
    assert updated_advert.description == update_data["description"]


def test_update_advert_partial(client, auth_headers, db_session):
    """Тест частичного обновления (только title)."""
    headers, user = auth_headers
    original_desc = "Original Description for partial update"
    advert = Advert(
        title="Original Title Partial", description=original_desc, owner_id=user.id
    )
    db_session.add(advert)
    db_session.commit()
    advert_id = advert.id

    update_data = {"title": "Updated Title Partial"}  # Только title

    response = client.put(
        f"/api/adverts/{advert_id}", json=update_data, headers=headers
    )

    assert response.status_code == 200
    assert response.json["title"] == update_data["title"]
    assert (
        response.json["description"] == original_desc
    )  # Описание не должно измениться

    updated_advert = db_session.get(Advert, advert_id)
    assert updated_advert.title == update_data["title"]
    assert updated_advert.description == original_desc


def test_update_advert_not_found(client, auth_headers):
    """Тест обновления несуществующего объявления."""
    headers, _ = auth_headers
    response = client.put(
        "/api/adverts/99999", json={"title": "Not Found"}, headers=headers
    )
    assert response.status_code == 404


def test_update_advert_unauthorized(client, db_session):
    """Тест обновления без аутентификации."""
    # Arrange: Создаем пользователя и объявление
    user = User(email="dummy@example.com")
    user.set_password("p")
    db_session.add(user)
    db_session.commit()
    advert = Advert(title="Dummy", description="Dummy", owner_id=user.id)
    db_session.add(advert)
    db_session.commit()
    # Act: Пытаемся обновить без заголовков
    response = client.put(f"/api/adverts/{advert.id}", json={"title": "updated"})
    assert response.status_code == 401


def test_update_advert_forbidden(client, db_session, auth_headers):
    """Тест попытки обновления чужого объявления."""
    # Arrange
    headers_user_a, user_a = auth_headers  # Пользователь A (аутентифицирован)
    # Создаем пользователя B
    user_b = User(email="user_b@example.com")
    user_b.set_password("pass_b")
    db_session.add(user_b)
    db_session.commit()
    # Создаем объявление, принадлежащее пользователю B
    advert_b = Advert(title="B's Advert", description="Owned by B", owner_id=user_b.id)
    db_session.add(advert_b)
    db_session.commit()

    # Act: Пользователь A пытается обновить объявление пользователя B
    response = client.put(
        f"/api/adverts/{advert_b.id}", json={"title": "Hacked"}, headers=headers_user_a
    )

    # Assert
    assert response.status_code == 403  # Ожидаем Forbidden
    # Проверяем, что данные в БД не изменились
    original_advert = db_session.get(Advert, advert_b.id)
    assert original_advert.title == "B's Advert"


# Тесты для DELETE /api/adverts/<id> (Удаление)
# ============================================


def test_delete_advert_success(client, auth_headers, db_session):
    """Тест успешного удаления своего объявления."""
    headers, user = auth_headers
    # Arrange: Создаем объявление
    advert = Advert(title="To Be Deleted", description="Delete me", owner_id=user.id)
    db_session.add(advert)
    db_session.commit()
    advert_id = advert.id

    # Act
    response = client.delete(f"/api/adverts/{advert_id}", headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.json == {"message": "Advert deleted"}

    # Проверяем БД
    deleted_advert = db_session.get(Advert, advert_id)
    assert deleted_advert is None


def test_delete_advert_not_found(client, auth_headers):
    """Тест удаления несуществующего объявления."""
    headers, _ = auth_headers
    response = client.delete("/api/adverts/99999", headers=headers)
    assert response.status_code == 404


def test_delete_advert_unauthorized(client, db_session):
    """Тест удаления без аутентификации."""
    # Arrange: Создаем пользователя и объявление
    user = User(email="dummy2@example.com")
    user.set_password("p")
    db_session.add(user)
    db_session.commit()
    advert = Advert(title="Dummy2", description="Dummy2", owner_id=user.id)
    db_session.add(advert)
    db_session.commit()
    advert_id = advert.id
    # Act: Пытаемся удалить без заголовков
    response = client.delete(f"/api/adverts/{advert_id}")
    assert response.status_code == 401

    # Проверяем БД - объявление должно остаться
    # assert db_session.query(Advert).get(advert_id) is not None
    assert db_session.get(Advert, advert_id) is not None


def test_delete_advert_forbidden(client, db_session, auth_headers):
    """Тест попытки удаления чужого объявления."""
    # Arrange
    headers_user_a, user_a = auth_headers  # Пользователь A (аутентифицирован)
    user_b = User(email="user_b_del@example.com")
    user_b.set_password("pass_b")
    db_session.add(user_b)
    db_session.commit()
    advert_b = Advert(
        title="B's Advert Delete", description="Owned by B", owner_id=user_b.id
    )
    db_session.add(advert_b)
    db_session.commit()
    advert_b_id = advert_b.id

    # Act: Пользователь A пытается удалить объявление пользователя B
    response = client.delete(f"/api/adverts/{advert_b_id}", headers=headers_user_a)

    # Assert
    assert response.status_code == 403  # Ожидаем Forbidden
    # Проверяем БД - объявление должно остаться
    # assert db_session.query(Advert).get(advert_b_id) is not None
    assert db_session.get(Advert, advert_b_id) is not None
