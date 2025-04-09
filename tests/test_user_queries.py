# tests/test_user_queries.py

import pytest
from src.db import user_queries

def test_create_user(monkeypatch, test_db_conn):
    # Підміна функції get_db_connection
    monkeypatch.setattr(user_queries, "get_db_connection", lambda: test_db_conn)

    username = "testuser"
    password = "hashedpassword123"

    user_id = user_queries.create_user(username, password)

    assert isinstance(user_id, int)

    # Перевірка, що користувач дійсно створився
    with test_db_conn.cursor() as cursor:
        cursor.execute("SELECT username, password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

    assert user["username"] == username
    assert user["password"] == password


def test_get_user_by_username(monkeypatch, test_db_conn):
    monkeypatch.setattr(user_queries, "get_db_connection", lambda: test_db_conn)

    username = "anotheruser"
    password = "somehash"

    # Створюємо користувача напряму
    with test_db_conn.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        test_db_conn.commit()

    user = user_queries.get_user_by_username(username)

    assert user is not None
    assert user["username"] == username
    assert user["password"] == password


def test_get_user_by_username_not_found(monkeypatch, test_db_conn):
    monkeypatch.setattr(user_queries, "get_db_connection", lambda: test_db_conn)

    user = user_queries.get_user_by_username("nonexistent_user")
    assert user is None


def test_create_user_duplicate(monkeypatch, test_db_conn):
    monkeypatch.setattr(user_queries, "get_db_connection", lambda: test_db_conn)

    username = "duplicate_user"
    password = "dup123"

    user_queries.create_user(username, password)

    with pytest.raises(Exception):
        user_queries.create_user(username, password)
