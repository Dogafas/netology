# API Сайта Объявлений [AioHttp Collection](https://bold-astronaut-977939-2110.postman.co/workspace/%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2%D0%B0%D1%8F-%D0%BA%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4%D0%B0-Workspace~1c03f5ee-9ced-48e9-8fd8-011c1a93ffca/collection/42519970-eab996f2-200d-4a54-8f8a-0e1043515d12?action=share&creator=42519970&active-environment=42519970-1997d73a-9750-4a7f-80b1-4b08c7030f69)

Простое REST API для сайта объявлений, написанное на Python с использованием aiohttp, PostgreSQL и JWT для аутентификации.

## Оглавление

1. [Требования](#требования)
2. [Настройка окружения](#настройка-окружения)
3. [Запуск проекта](#запуск-проекта)
   * [Через Docker Compose (рекомендуется)](#через-docker-compose-рекомендуется)
   * [Локальный запуск (для разработки)](#локальный-запуск-для-разработки)
4. [Аутентификация](#аутентификация)
5. [Эндпоинты API](#эндпоинты-api)
   * [Пользователи](#пользователи)
     * [POST /users/register](#post-usersregister)
     * [POST /users/login](#post-userslogin)
   * [Объявления](#объявления)
     * [POST /ads/](#post-ads)
     * [GET /ads/](#get-ads)
     * [GET /ads/{ad_id}](#get-adsad_id)
     * [PUT /ads/{ad_id}](#put-adsad_id)
     * [DELETE /ads/{ad_id}](#delete-adsad_id)
6. [Миграции базы данных (Alembic)](#миграции-базы-данных-alembic)

## Требования

* Python 3.10+
* Docker и Docker Compose
* PostgreSQL (запускается через Docker Compose)
* Poetry или pip для управления зависимостями (если запускать локально)

## Настройка окружения

1. Скопируйте файл `.env.example` (если есть) в `.env` или создайте файл `.env` в корневой директории проекта.
2. Заполните `.env` необходимыми значениями:

   ```dotenv
   # .env

   # --- PostgreSQL Database Configuration ---
   POSTGRES_USER=advertisement_user
   POSTGRES_PASSWORD=supersecretpassword
   POSTGRES_DB=advertisement_db
   POSTGRES_EXPOSED_PORT=5431 # Порт на хосте для подключения к БД

   # --- JWT Configuration ---
   JWT_SECRET_KEY=your_strong_secret_key_here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   # --- Application Configuration ---
   APP_EXPOSED_PORT=8000 # Порт на хосте для подключения к API
   ```

## Запуск проекта

### Через Docker Compose (рекомендуется)

Это наиболее простой способ запустить приложение вместе с базой данных PostgreSQL.

1. Убедитесь, что Docker и Docker Compose установлены и запущены.
2. В корневой директории проекта выполните:

   ```bash
   docker-compose up --build -d
   ```

   * `--build`: Пересобирает образы, если были изменения в коде или `Dockerfile`.
   * `-d`: Запускает контейнеры в фоновом (detached) режиме.

   Приложение будет доступно по адресу `http://localhost:{APP_EXPOSED_PORT}` (например, `http://localhost:8000`).
   База данных будет доступна по адресу `localhost:{POSTGRES_EXPOSED_PORT}` (например, `localhost:5431`).
3. Для остановки сервисов:

   ```bash
   docker-compose down
   ```

   Для остановки и удаления volumes (включая данные БД):

   ```bash
   docker-compose down -v
   ```

### Локальный запуск (для разработки)

1. Установите и настройте PostgreSQL сервер отдельно.
2. Обновите переменные окружения в `.env` для подключения к вашему локальному PostgreSQL (особенно `POSTGRES_HOST`, `POSTGRES_PORT`).
3. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/macOS
   # venv\Scripts\activate    # для Windows
   pip install -r requirements.txt
   ```
4. Примените миграции Alembic:
   ```bash
   alembic upgrade head
   ```
5. Запустите приложение:
   ```bash
   python -m app.main
   ```

## Аутентификация

API использует JWT (JSON Web Tokens) для аутентификации.

1. Для получения токена отправьте POST-запрос на эндпоинт `/users/login` с вашими `email` и `password`.
2. В случае успеха API вернет `access_token`.
3. Для доступа к защищенным эндпоинтам передавайте этот токен в заголовке `Authorization`:
   ```
   Authorization: Bearer <your_access_token>
   ```

## Эндпоинты API

Базовый URL: `http://localhost:{APP_EXPOSED_PORT}` (например, `http://localhost:8000`)

### Пользователи

#### `POST /users/register`

Регистрация нового пользователя.

* **Аутентификация:** Не требуется.
* **Тело запроса (`application/json`):**

  ```json
  {
      "email": "user@example.com",
      "password": "yoursecurepassword"
  }
  ```

  * `email` (string, required, email format): Email пользователя.
  * `password` (string, required, min_length: 6): Пароль пользователя.
* **Успешный ответ (`201 Created`):**

  ```json
  {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2023-10-27T10:00:00Z"
  }
  ```
* **Ошибки:**

  * `400 Bad Request`: Невалидные входные данные.
  * `409 Conflict`: Пользователь с таким email уже существует.

#### `POST /users/login`

Аутентификация пользователя и получение JWT токена.

* **Аутентификация:** Не требуется.
* **Тело запроса (`application/json`):**
  ```json
  {
      "email": "user@example.com",
      "password": "yoursecurepassword"
  }
  ```
* **Успешный ответ (`200 OK`):**
  ```json
  {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
  }
  ```
* **Ошибки:**
  * `400 Bad Request`: Невалидные входные данные.
  * `401 Unauthorized`: Неверный email или пароль.

---

### Объявления

#### `POST /ads/`

Создание нового объявления.

* **Аутентификация:** Требуется (Bearer Token).
* **Тело запроса (`application/json`):**

  ```json
  {
      "title": "Продам велосипед",
      "description": "Отличный велосипед, почти новый."
  }
  ```

  * `title` (string, required, max_length: 100): Заголовок объявления.
  * `description` (string, optional): Описание объявления.
* **Успешный ответ (`201 Created`):**

  ```json
  {
      "id": 1,
      "title": "Продам велосипед",
      "description": "Отличный велосипед, почти новый.",
      "created_at": "2023-10-27T10:05:00Z",
      "owner_id": 1
  }
  ```
* **Ошибки:**

  * `400 Bad Request`: Невалидные входные данные.
  * `401 Unauthorized`: Токен не предоставлен или недействителен.

#### `GET /ads/`

Получение списка всех объявлений. Поддерживается пагинация.

* **Аутентификация:** Не требуется.
* **Параметры запроса (query parameters):**
  * `skip` (integer, optional, default: 0): Количество пропускаемых объявлений.
  * `limit` (integer, optional, default: 10, max: 100): Количество возвращаемых объявлений.
* **Успешный ответ (`200 OK`):**
  ```json
  [
      {
          "id": 1,
          "title": "Продам велосипед",
          "description": "Отличный велосипед, почти новый.",
          "created_at": "2023-10-27T10:05:00Z",
          "owner_id": 1
      },
      // ... другие объявления
  ]
  ```

#### `GET /ads/{ad_id}`

Получение информации о конкретном объявлении по его ID.

* **Аутентификация:** Не требуется.
* **Параметры URL:**
  * `ad_id` (integer, required): ID объявления.
* **Успешный ответ (`200 OK`):**
  ```json
  {
      "id": 1,
      "title": "Продам велосипед",
      "description": "Отличный велосипед, почти новый.",
      "created_at": "2023-10-27T10:05:00Z",
      "owner_id": 1
  }
  ```
* **Ошибки:**
  * `404 Not Found`: Объявление с указанным ID не найдено.

#### `PUT /ads/{ad_id}`

Обновление существующего объявления. Только владелец объявления может его обновить.

* **Аутентификация:** Требуется (Bearer Token).
* **Параметры URL:**

  * `ad_id` (integer, required): ID объявления для обновления.
* **Тело запроса (`application/json`):**

  ```json
  {
      "title": "Продам велосипед СРОЧНО", // Поля опциональны
      "description": "Описание обновлено."
  }
  ```

  * `title` (string, optional, max_length: 100): Новый заголовок.
  * `description` (string, optional): Новое описание.
* **Успешный ответ (`200 OK`):**

  ```json
  {
      "id": 1,
      "title": "Продам велосипед СРОЧНО",
      "description": "Описание обновлено.",
      "created_at": "2023-10-27T10:05:00Z", // Дата создания не меняется
      "owner_id": 1
  }
  ```
* **Ошибки:**

  * `400 Bad Request`: Невалидные входные данные.
  * `401 Unauthorized`: Токен не предоставлен или недействителен.
  * `403 Forbidden`: Пользователь не является владельцем объявления.
  * `404 Not Found`: Объявление с указанным ID не найдено.

#### `DELETE /ads/{ad_id}`

Удаление объявления. Только владелец объявления может его удалить.

* **Аутентификация:** Требуется (Bearer Token).
* **Параметры URL:**
  * `ad_id` (integer, required): ID объявления для удаления.
* **Успешный ответ (`204 No Content`):** Тело ответа отсутствует.
* **Ошибки:**
  * `401 Unauthorized`: Токен не предоставлен или недействителен.
  * `403 Forbidden`: Пользователь не является владельцем объявления.
  * `404 Not Found`: Объявление с указанным ID не найдено.

## Миграции базы данных (Alembic)

Проект использует Alembic для управления миграциями схемы базы данных.

* **Создание новой миграции** (после изменения моделей в `app/models/`):

  ```bash
  alembic revision -m "краткое_описание_изменений" --autogenerate
  ```
  Затем проверьте сгенерированный файл миграции в `migrations/versions/`.
* **Применение миграций к базе данных:**

  ```bash
  alembic upgrade head
  ```
  Эта команда будет автоматически выполняться при старте Docker-контейнера приложения. При локальном запуске ее нужно выполнять вручную.
* **Откат последней миграции:**

  ```bash
  alembic downgrade -1
  ```
* **Просмотр истории миграций:**

  ```bash
  alembic history
  ```
