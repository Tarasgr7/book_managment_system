from fastapi import APIRouter, status, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from src.dependencies import logger
from src.schemas.user_schemas import UserCreate
from src.schemas.token_schemas import Token
from src.utils.auth_utils import authenticate_user, create_access_token, hash_password
from src.db.user_queries import create_user, get_user_by_username
from src.utils.rate_limit import limiter


router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(user: UserCreate, request: Request):
    existing_user = get_user_by_username(user.username)
    if existing_user:
        logger.warning(f"Attempt to register an already existing username: {user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    user_id = create_user(user.username, hash_password(user.password))
    logger.info(f"User {user.username} successfully registered with user_id {user_id}")
    
    return {"message": f"User {user.username} successfully registered", "user_id": user_id}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(user['username'], user['id'], timedelta(minutes=20))
    logger.info(f"User {form_data.username} successfully logged in and token generated.")
    
    return {"access_token": token, "token_type": "bearer"}
