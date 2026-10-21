# Book Management API

A REST API for managing a book catalogue, built with FastAPI and PostgreSQL. Users register and log in with JWT authentication, manage books and authors, bulk-import and export the catalogue as JSON or CSV, and get book recommendations based on genre, author, or their own viewing history. Database access uses raw SQL through psycopg2, and every endpoint except export is rate-limited with SlowAPI.

## Features

- **Authentication** - registration and OAuth2 password-flow login that issues JWT bearer tokens; passwords hashed with bcrypt (passlib).
- **Book CRUD** - create, read, update and delete books; authors are created automatically on first use.
- **Validation** - Pydantic schemas enforce a fixed genre list, a published year between 1800 and the current year, and non-empty title/author.
- **Pagination and sorting** - `skip` / `limit` plus sorting by `title`, `published_year` or `author_id`.
- **Bulk import** - upload a `.json` or `.csv` file; books with duplicate titles are skipped and reported.
- **Export** - download the catalogue as JSON or CSV.
- **Recommendations** - unviewed books by genre, by author, or based on the top genres/authors in the user's view history (views are recorded when an authenticated user opens a book).
- **Rate limiting** - 5 requests per minute per client IP on auth, CRUD, import and recommendation endpoints.
- **Docker** - Dockerfile and Compose setup with the API, a main PostgreSQL database and a separate test database.

## Tech stack

Python 3.12, FastAPI, Uvicorn, PostgreSQL 13, psycopg2, Pydantic v2, python-jose (JWT), passlib/bcrypt, SlowAPI, pytest, Docker Compose.

## API overview

All routes are prefixed with `/api/v1`. Interactive docs are served by FastAPI at `http://localhost:8000/docs` (Swagger UI) and `/redoc`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | - | Register a user (JSON body: `username`, `password`) |
| POST | `/auth/login` | - | OAuth2 form login, returns a bearer token |
| GET | `/books/get_all_books` | - | List books (`skip`, `limit`, `sort_by`) |
| GET | `/books/get_book/{book_id}` | JWT | Get a book and record the view |
| POST | `/books/create_book` | JWT | Create a book |
| PUT | `/books/update_book/{book_id}` | JWT | Partially update a book |
| DELETE | `/books/delete_book/{book_id}` | JWT | Delete a book |
| POST | `/books/import` | JWT | Import books from a JSON or CSV file |
| GET | `/books/export` | - | Export books (`format=json` or `format=csv`) |
| GET | `/recommendations/recommendations/genre` | JWT | Recommendations by `genre` |
| GET | `/recommendations/recommendations/author` | JWT | Recommendations by `author_name` |
| GET | `/recommendations/recommendations/history` | JWT | Recommendations from view history |

Supported genres: Fiction, Non-Fiction, Science, History, Fantasy, Biography, Romance, Thriller, Mystery, Philosophy.

## Project structure

```
.
├── src/
│   ├── main.py              # App factory: routers, rate limiter, DB init
│   ├── dependencies.py      # Env config (JWT, database URL), logging
│   ├── db/                  # psycopg2 connection, schema init, SQL queries
│   ├── routes/              # auth, books, recommendations routers
│   ├── schemas/             # Pydantic models
│   └── utils/               # JWT/password helpers, rate limiter
├── tests/                   # pytest suite (requires PostgreSQL)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

Tables (`users`, `authors`, `books`, `user_history`) are created automatically on startup if they don't exist.

## Getting started

### Configuration

```bash
cp .env.example .env
```

Set at least `SECRET_KEY`, `DB_PASSWORD` and `TEST_DB_PASSWORD`. All variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT signing (e.g. `HS256`) |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | Application database |
| `TEST_DB_USER`, `TEST_DB_PASSWORD`, `TEST_DB_HOST`, `TEST_DB_PORT`, `TEST_DB_NAME` | Test database used by pytest fixtures |

### Run with Docker Compose

```bash
docker compose up --build
```

This starts the API on `http://localhost:8000`, the main database on port `5432` and the test database on port `5433`. Compose reads the database credentials from `.env`; inside the Compose network the API connects to the `postgres_db` service.

### Run locally

Requires Python 3.12+ and a reachable PostgreSQL instance configured via `DB_*` in `.env` (for example, the `postgres_db` service from Compose: `docker compose up -d postgres_db test_db`).

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Running tests

The tests run against real PostgreSQL databases: fixtures in `tests/conftest.py` connect to the `TEST_DB_*` database, while the application code under test uses `DB_*`. Start both databases first, then run pytest from the project root:

```bash
docker compose up -d postgres_db test_db
pytest
```
