import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.auth_utils import create_access_token
from datetime import timedelta
from psycopg2 import IntegrityError

client = TestClient(app)

# Фікстури

@pytest.fixture(autouse=True)
def clean_db(test_db_conn):
    """Очищаємо таблиці перед кожним тестом."""
    with test_db_conn.cursor() as cursor:
        cursor.execute("DELETE FROM books;")
        cursor.execute("DELETE FROM authors;")
        cursor.execute("DELETE FROM user_history;")  # якщо є така таблиця
        test_db_conn.commit()

@pytest.fixture
def create_books(test_db_conn):
    """Фікстура для створення книг у базі даних перед тестами."""
    with test_db_conn.cursor() as cursor:
        cursor.execute(""" 
            INSERT INTO authors (name) VALUES ('Author A') ON CONFLICT (name) DO NOTHING;
            INSERT INTO books (title, published_year, genre, author_id)
            VALUES ('Book A', 2021, 'Fiction', (SELECT id FROM authors WHERE name = 'Author A')),
                   ('Book B', 2020, 'Non-Fiction', (SELECT id FROM authors WHERE name = 'Author A'));
        """)
        test_db_conn.commit()

@pytest.fixture
def create_book_in_db(test_db_conn):
    """Фікстура для створення однієї книги в базі даних."""
    with test_db_conn.cursor() as cursor:
        cursor.execute(""" 
            INSERT INTO authors (name) VALUES ('Author A') ON CONFLICT (name) DO NOTHING;
            INSERT INTO books (title, published_year, genre, author_id)
            VALUES ('Book A', 2021, 'Fiction', (SELECT id FROM authors WHERE name = 'Author A'));
        """)
        test_db_conn.commit()

@pytest.fixture
def create_author_in_db(test_db_conn):
    """Фікстура для створення автора в базі даних."""
    with test_db_conn.cursor() as cursor:
        cursor.execute("INSERT INTO authors (name) VALUES ('Author A') ON CONFLICT (name) DO NOTHING;")
        test_db_conn.commit()

@pytest.fixture
def create_book_for_update(test_db_conn):
    """Фікстура для створення книги, яку можна буде оновити."""
    with test_db_conn.cursor() as cursor:
        cursor.execute(""" 
            INSERT INTO authors (name) VALUES ('Author A') ON CONFLICT (name) DO NOTHING;
            INSERT INTO books (title, published_year, genre, author_id)
            VALUES ('Book A', 2021, 'Fiction', (SELECT id FROM authors WHERE name = 'Author A'));
        """)
        test_db_conn.commit()

@pytest.fixture
def create_book_for_deletion(test_db_conn):
    """Фікстура для створення книги для видалення."""
    with test_db_conn.cursor() as cursor:
        cursor.execute(""" 
            INSERT INTO authors (name) VALUES ('Author A') ON CONFLICT (name) DO NOTHING;
            INSERT INTO books (title, published_year, genre, author_id)
            VALUES ('Book A', 2021, 'Fiction', (SELECT id FROM authors WHERE name = 'Author A'));
        """)
        test_db_conn.commit()

@pytest.fixture
def token():
    """Фікстура для створення токену доступу."""
    return create_access_token(username="testuser", user_id=1, expires_delta=timedelta(minutes=30))

# Тести

# 1. Тести для ендпоінту GET /books/get_all_books
def test_get_all_books(create_books, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/v1/books/get_all_books?skip=0&limit=2&sort_by=title", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == 'Book A'
    assert data[1]['title'] == 'Book B'

def test_get_books_empty(create_books, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/v1/books/get_all_books?skip=10&limit=5&sort_by=title", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

# 2. Тести для ендпоінту GET /books/get_book/{book_id}
def test_get_book(create_book_in_db, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/v1/books/get_book/1", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Book A'

def test_get_book_not_found(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/v1/books/get_book/999", headers=headers)
    assert response.status_code == 404

# 3. Тести для ендпоінту POST /books/create_book
def test_create_book(create_author_in_db, token):
    book_data = {
        "title": "New Book",
        "published_year": 2022,
        "genre": "Fiction",
        "author": "Author A"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("api/v1/books/create_book", json=book_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == "New Book"
    assert data['author'] == "Author A"

def test_create_book_with_existing_title(create_author_in_db, token):
    book_data = {
        "title": "New Book",
        "published_year": 2022,
        "genre": "Fiction",
        "author": "Author A"
    }
    # Створюємо першу книгу
    headers = {"Authorization": f"Bearer {token}"}
    client.post("api/v1/books/create_book", json=book_data, headers=headers)
    # Тепер спробуємо створити книгу з таким самим заголовком
    response = client.post("api/v1/books/create_book", json=book_data, headers=headers)
    assert response.status_code == 400
    assert response.json()['detail'] == "Book with this title already exists"

# 4. Тести для ендпоінту PUT /books/update_book/{book_id}
def test_update_book(create_book_for_update, token):
    updated_data = {
        "title": "Updated Book",
        "published_year": 2023,
        "genre": "Science",
        "author": "Author A"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put("api/v1/books/update_book/1", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Updated Book"
    assert data['published_year'] == 2023

def test_update_book_not_found(token):
    updated_data = {
        "title": "Updated Book",
        "published_year": 2023,
        "genre": "Science",
        "author": "Author A"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put("api/v1/books/update_book/999", json=updated_data, headers=headers)
    assert response.status_code == 404

# 5. Тести для ендпоінту DELETE /books/delete_book/{book_id}
def test_delete_book(create_book_for_deletion, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("api/v1/books/delete_book/1", headers=headers)
    assert response.status_code == 204

def test_delete_book_not_found(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("api/v1/books/delete_book/999", headers=headers)
    assert response.status_code == 404
