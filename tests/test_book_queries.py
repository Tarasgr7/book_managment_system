import pytest
import uuid
from src.db.book_queries import create_book, get_book_by_title, get_book, update_book, delete_book
from src.db.connections import get_db_connection


# Фікстура для створення автора в таблиці authors
@pytest.fixture(scope="module")
def create_author():
    author_name = "J.K. Rowling"
    
    # Перевіряємо, чи вже є автор з таким іменем
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM authors WHERE name = %s", (author_name,))
            existing_author = cursor.fetchone()
            if existing_author:
                author_id = existing_author[0]
            else:
                # Якщо автора нема, створюємо нового
                cursor.execute("INSERT INTO authors (name) VALUES (%s) RETURNING id", (author_name,))
                author_id = cursor.fetchone()[0]
                conn.commit()
            yield author_id
            # Очистка після тестів
            if not existing_author:
                cursor.execute("DELETE FROM authors WHERE id = %s", (author_id,))
                conn.commit()


# Тест на створення книги
def test_create_book(create_author):
    title = f"Harry Potter and the Philosopher's Stone {uuid.uuid4()}"
    published_year = 1997
    genre = "Fantasy"
    author_id = create_author

    # Створюємо книгу
    book_id = create_book(title, published_year, genre, author_id)

    # Перевіряємо, чи книга була успішно створена
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, published_year, genre, author_id FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            assert book is not None
            assert book[1] == title  # title
            assert book[2] == published_year  # published_year
            assert book[3] == genre  # genre
            assert book[4] == author_id  # author_id


# Тест на отримання книги за назвою
def test_get_book_by_title(create_author):
    title = f"Harry Potter and the Philosopher's Stone {uuid.uuid4()}"
    published_year = 1997
    genre = "Fantasy"
    author_id = create_author

    book_id = create_book(title, published_year, genre, author_id)

    # Перевіряємо отримання книги за назвою
    book = get_book_by_title(title)
    assert book is not None
    assert book['id'] == book_id
    assert book['title'] == title


# Тест на отримання книги за ID
def test_get_book(create_author):
    title = f"Harry Potter and the Philosopher's Stone {uuid.uuid4()}"
    published_year = 1997
    genre = "Fantasy"
    author_id = create_author

    book_id = create_book(title, published_year, genre, author_id)

    # Перевіряємо отримання книги за ID
    book = get_book(book_id)
    assert book is not None
    assert book['id'] == book_id
    assert book['title'] == title
    assert book['author'] == "J.K. Rowling"


# Тест на оновлення книги
def test_update_book(create_author):
    title = f"Harry Potter and the Philosopher's Stone {uuid.uuid4()}"
    published_year = 1997
    genre = "Fantasy"
    author_id = create_author

    book_id = create_book(title, published_year, genre, author_id)

    new_title = f"Harry Potter and the Chamber of Secrets {uuid.uuid4()}"
    new_published_year = 1998
    new_genre = "Fantasy"

    # Оновлюємо книгу
    update_book(book_id, new_title, new_published_year, new_genre, author_id)

    # Перевіряємо, чи книга була оновлена
    updated_book = get_book(book_id)
    assert updated_book['title'] == new_title
    assert updated_book['published_year'] == new_published_year
    assert updated_book['genre'] == new_genre


# Тест на видалення книги
def test_delete_book(create_author):
    title = f"Harry Potter and the Philosopher's Stone {uuid.uuid4()}"
    published_year = 1997
    genre = "Fantasy"
    author_id = create_author

    book_id = create_book(title, published_year, genre, author_id)

    # Видаляємо книгу
    delete_book(book_id)

    # Перевіряємо, чи книга була видалена
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            assert book is None
