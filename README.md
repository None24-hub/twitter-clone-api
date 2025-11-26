# Twitter Clone — Итоговый проект Python Advanced

Учебный проект — упрощённый клон Twitter: публикация твитов, лайки, подписки, просмотр ленты, загрузка медиа и работа с профилями пользователей.  
Backend реализован как полноценный REST API и может использоваться не только с текущим интерфейсом, но и с любым другим frontend-приложением.

Проект соответствует требованиям итогового задания Python Advanced.

---

## 🚀 Стек технологий

- **Python** — основной язык
- **FastAPI** — backend
- **SQLAlchemy 2.0 (async)** — ORM
- **PostgreSQL 16** — база данных
- **pytest** — тесты
- **Docker + docker-compose** — запуск и оркестрация
- **Nginx** — раздача фронтенда

---

## ⚙️ Как запустить проект

### 1. Клонировать репозиторий


git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ>
cd python_advanced_diploma


### 2. Запуск сервиса (development-профиль)
docker compose --profile dev up -d


## Будут запущены контейнеры:

**Сервис**	**Описание**
api    	      backend (FastAPI)
db	          PostgreSQL
server	      UI + статика (клон Twitter)
### 3. Доступы

## Swagger (REST API):
👉 http://localhost:8000/docs

## Фронтенд (интерфейс Twitter):
👉 http://localhost

## 🔐 Авторизация по API-Key

**Проект использует простую авторизацию по API ключу:**

## api-key: <ваш ключ>


## В тестовой сборке доступен пользователь:

username: test user
api-key: test


В Swagger нажмите Authorize, затем введите test в поле api-key.

## 📌 Основной функционал
## ✔ Публикация твитов

POST /api/tweets
Поддерживается прикрепление изображений через tweet_media_ids[].

## ✔ Удаление твитов

DELETE /api/tweets/{tweet_id}

## ✔ Лайки

Поставить лайк: POST /api/tweets/{id}/likes

Убрать лайк: DELETE /api/tweets/{id}/likes

## ✔ Подписки

Подписаться: POST /api/users/{id}/follow

Отписаться: DELETE /api/users/{id}/follow

## ✔ Лента твитов

GET /api/tweets

Лента формируется из пользователей, на которых подписан текущий.
Сортировка — по популярности (числу лайков).

## ✔ Загрузка изображений

POST /api/medias
Формат — multipart/form-data.

## ✔ Профили

Текущий пользователь: GET /api/users/me

Другой пользователь: GET /api/users/{id}

## 📂 Структура проекта
app/
 ├── main.py                # Точка входа FastAPI
 ├── routers/               # Роуты (users, tweets, media)
 ├── models/                # SQLAlchemy модели
 ├── schemas/               # Pydantic-схемы
 ├── database/              # Подключение к БД, engine, session
 ├── utils/                 # Вспомогательные функции
 └── static/                # Медиафайлы (изображения)

server/                     # Интерфейс и конфигурация Nginx
init_postgres/              # Скрипты для инициализации БД
docker-compose.yaml

## 🧪 Запуск тестов
sh run_scripts/start_tests.sh

## Покрытие включает:

**публикация твитов**

**лайки**

**подписки**

**лента**

**работа с профилями**

## 📝 Особенности реализации

**Полностью асинхронный backend на FastAPI**

**Авторизация по API-Key**

**Swagger-документация доступна сразу после запуска**

**Использование .env файлов для конфигурации**

**Отдельные профили docker-compose: dev и test**

**Хранение медиа в Docker volume**

## 📄 Лицензия

**Проект выполнен в рамках итогового задания курса Python Advanced
и предназначен для учебных целей.**