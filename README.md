# 🐍 FastAPI Articles Service

A REST API service for managing users and articles with authentication,
role-based access control, PostgreSQL database and full Docker setup.

The project demonstrates a production-like backend architecture
including authentication, permissions, database migrations, testing and
containerized deployment.

------------------------------------------------------------------------

## Features

-   JWT Authentication
-   Role-based permissions (admin / editor / user)
-   Articles CRUD API
-   Admin user management
-   PostgreSQL database
-   Dockerized environment
-   Database seed scripts
-   Unit tests with coverage
-   Liveness (health) endpoint

------------------------------------------------------------------------

## Tech Stack

-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Pydantic v2
-   Alembic
-   Pytest + pytest-cov
-   Docker & Docker Compose

------------------------------------------------------------------------

## Environment Setup

Create `.env` file:

DATABASE_URL=postgresql://articles_user:articles_pass@db:5432/articles_db\
SECRET_KEY=your_secret_key\
ACCESS_TOKEN_EXPIRE_MINUTES=60

------------------------------------------------------------------------

```
## Quick start to Build Application

1. Start containers
2. Apply migrations
3. Seed database
4. Open docs
5. Run tests
6. Run specific test
7. Test Coverage

```
docker compose up --build -d
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
docker compose run --rm tests
docker compose run --rm tests pytest tests/test_admin_users.py
docker compose run --rm tests pytest --cov=app --cov-report=term-missing

------------------------------------------------------------------------

## API available at:

http://localhost:8000/docs

------------------------------------------------------------------------

## Liveness Endpoint

GET /health

Example response:

{ "status": "ok", "db": "ok" }

------------------------------------------------------------------------

## Initialize Database (Load Initial Data)

Created roles:

-   admin
-   editor
-   user

------------------------------------------------------------------------

## Project Structure

### app/

#### api/

-   admin_users.py --- Admin user management endpoints
-   articles.py --- Articles CRUD operations
-   auth.py --- Login and token issuing
-   users.py --- Current user endpoints

#### core/

-   auth.py --- Authentication helpers
-   jwt.py --- JWT logic
-   permissions.py --- Role permissions
-   roles.py --- Role definitions
-   security.py --- Password hashing

#### db/

-   base.py --- SQLAlchemy Base
-   deps.py --- DB dependency injection
-   engine.py --- DB engine
-   session.py --- SessionLocal config
-   users.py --- User queries
-   init_db.py --- DB initialization

#### models/

ORM models: - user.py - article.py

#### schemas/

Pydantic schemas.

------------------------------------------------------------------------

### scripts/

-   create_db.py --- DB creation helper
-   seed.py --- Initial data loader

------------------------------------------------------------------------

### tests/

-   test_auth.py --- Authentication tests
-   test_articles.py --- Articles tests
-   test_admin_users.py --- Admin edge cases
-   test_health.py --- Liveness endpoint test

------------------------------------------------------------------------

### Root Files

-   Dockerfile --- API container
-   docker-compose.yml --- Environment orchestration
-   alembic.ini --- Migration config
-   requirements.txt --- Dependencies
-   .env.example --- Environment template

------------------------------------------------------------------------

## Docker Setup

The project runs fully inside Docker:

docker compose up

Only Docker Engine and internet connection are required.

------------------------------------------------------------------------

## Implemented Requirements

-   REST API
-   Authentication & authorization
-   PostgreSQL integration
-   Dockerized infrastructure
-   Seed script
-   Unit tests
-   Coverage ≥ 20%
-   Liveness endpoint
-   README documentation

------------------------------------------------------------------------

## Result

A fully containerized FastAPI backend service demonstrating real-world
backend architecture suitable for production-style development and
testing.
