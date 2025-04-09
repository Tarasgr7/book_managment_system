import pytest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from src.utils.auth_utils import (
    verify_password,
    hash_password,
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_current_user,
)
from fastapi import HTTPException



# Тест для verify_password
def test_verify_password():
    plain_password = "test_password"
    hashed_password = hash_password(plain_password)
    
    # Перевірка, що функція вірно порівнює пароль
    assert verify_password(plain_password, hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False


# Тест для hash_password
def test_hash_password():
    password = "test_password"
    hashed_password = hash_password(password)
    
    # Перевірка, що хешування повертає строку
    assert isinstance(hashed_password, str)
    assert hashed_password != password  # Перевірка, що вони не однакові



# Тест для create_access_token та decode_access_token
def test_create_and_decode_access_token():
    username = "test_user"
    user_id = 1
    expires_delta = timedelta(minutes=30)
    
    token = create_access_token(username, user_id, expires_delta)
    
    # Перевірка, що токен не порожній
    assert token is not None
    
    decoded_token = decode_access_token(token)
    
    # Перевірка, що декодований токен містить правильні дані
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id


# Тест для get_current_user
@patch("src.utils.auth_utils.decode_access_token")
def test_get_current_user(mock_decode_access_token):
    token = "valid_token"
    username = "test_user"
    user_id = 1
    
    # Мок для функції decode_access_token
    mock_decode_access_token.return_value = {"sub": username, "id": user_id}
    
    user = get_current_user(token)
    
    assert user["username"] == username
    assert user["id"] == user_id
    
    # Тест для помилки, коли токен некоректний
    mock_decode_access_token.return_value = None
    with pytest.raises(HTTPException):
        get_current_user(token)
