# tests/conftest.py

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Завантаження .env
load_dotenv()

# SQL для створення таблиць
init_sql = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    published_year INT NOT NULL,
    genre VARCHAR(50) NOT NULL CHECK (genre IN (
        'Fiction', 'Non-Fiction', 'Science', 'History', 'Fantasy', 
        'Biography', 'Romance', 'Thriller', 'Mystery', 'Philosophy'
    )),
    author_id INTEGER NOT NULL REFERENCES authors(id)
);

CREATE TABLE IF NOT EXISTS user_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    book_id INTEGER NOT NULL REFERENCES books(id),
    action VARCHAR(50) CHECK (action IN ('viewed')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

@pytest.fixture(scope="session")
def init_test_db():
    """Ініціалізує таблиці в тестовій базі даних."""
    conn = psycopg2.connect(
        dbname=os.getenv("TEST_DB_NAME"),
        user=os.getenv("TEST_DB_USER"),
        password=os.getenv("TEST_DB_PASSWORD"),
        host=os.getenv("TEST_DB_HOST").strip(),
        port=os.getenv("TEST_DB_PORT")
    )
    print(f"🔗 Connected to test DB: {os.getenv('TEST_DB_NAME')} at {os.getenv('TEST_DB_HOST')}")
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(init_sql)
    conn.close()

@pytest.fixture(scope="function")
def test_db_conn(init_test_db):
    """Повертає підключення до тестової БД, з rollback після тесту."""
    conn = psycopg2.connect(
        dbname=os.getenv("TEST_DB_NAME"),
        user=os.getenv("TEST_DB_USER"),
        password=os.getenv("TEST_DB_PASSWORD"),
        host=os.getenv("TEST_DB_HOST").strip(),
        port=os.getenv("TEST_DB_PORT"),
        cursor_factory=RealDictCursor
    )
    yield conn
    conn.rollback()
    conn.close()

@pytest.fixture(autouse=True)
def clean_users(test_db_conn):
    """Очищає таблицю users перед кожним тестом."""
    with test_db_conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
        test_db_conn.commit()
