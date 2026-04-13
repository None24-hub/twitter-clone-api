# 🚀 Twitter Clone API (FastAPI Backend)

Backend API для сервиса микроблогинга (аналог Twitter).
Реализует работу с пользователями, твитами, лайками и подписками.

Проект демонстрирует навыки разработки REST API, работы с базой данных и асинхронного backend на Python.

---

## ⚙️ Стек технологий

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy (async)
* Docker / docker-compose
* Nginx
* Pytest

---

## 🔥 Основной функционал

* Регистрация и получение профиля пользователя
* Публикация и удаление твитов
* Лайки и подписки
* Формирование ленты
* Загрузка медиа
* REST API с документацией (Swagger)

---

## 🧠 Что реализовано

* Асинхронный backend (FastAPI + async SQLAlchemy)
* Работа с PostgreSQL
* Контейнеризация через Docker
* Разделение логики (routers / models / schemas)
* REST API архитектура
* Автоматические тесты (pytest)

---

## 🚀 Запуск проекта

```bash
git clone <repo_url>
cd python_advanced_diploma
docker compose --profile dev up -d
```

После запуска:

* Swagger: http://localhost:8000/docs
* Frontend: http://localhost

---

## 🔐 Тестовый доступ

```
api-key: test
```

---

## 📂 Структура проекта

```
app/
 ├── routers/
 ├── models/
 ├── schemas/
 ├── database/
 └── utils/
```

---

## 🧪 Тесты

```bash
sh run_scripts/start_tests.sh
```

---

## 📌 О проекте

Проект разработан в рамках обучения, но отражает реальные подходы к построению backend-сервисов.
