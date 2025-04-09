# src/utils/auth_utils.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from src.dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status,Depends
from src.db.user_queries import get_user_by_username
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated 


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer=OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user['password']):
        return False
    return user



def create_access_token(username: str, user_id: int, expires_delta: timedelta = None):
    to_encode = {"sub": username, "id": user_id}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    return {'username': payload.get('sub'), 'id': payload.get('id')}

user_dependency=Annotated[dict,Depends(get_current_user)]
