# Добро пожаловать в Finance Manager API

Finance Manager API — это RESTful сервис для управления личными финансами, учета доходов и расходов, а также планирования бюджетов.

## 🛠 Технологический стек

- **Фреймворк**: FastAPI
- **База данных**: PostgreSQL
- **ORM**: SQLModel (на базе SQLAlchemy & Pydantic)
- **Аутентификация**: JWT (JSON Web Tokens) с хэшированием `pbkdf2_sha256`
- **Миграции**: Alembic

## 🚀 Быстрый старт

Для запуска сервера локально используйте команду:

```bash
uvicorn main:app --reload