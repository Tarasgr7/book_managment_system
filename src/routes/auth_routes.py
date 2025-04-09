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

# OAuth2 scheme for password-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(user: UserCreate, request: Request):
    """
    Register a new user in the system.
    
    This endpoint allows a user to register by providing a username and password. 
    The server will check if the username is already taken and if not, the user will be created.
    
    - **username**: Unique username for the new user.
    - **password**: Password for the new user (plain text, will be hashed).
    
    Returns a success message along with the user ID.
    """
    # Check if the username already exists
    existing_user = get_user_by_username(user.username)
    if existing_user:
        logger.warning(f"Attempt to register an already existing username: {user.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Create the new user in the database
    user_id = create_user(user.username, hash_password(user.password))
    logger.info(f"User {user.username} successfully registered with user_id {user_id}")
    
    return {"message": f"User {user.username} successfully registered", "user_id": user_id}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate a user and return an access token.
    
    This endpoint is used to log in a user by providing their username and password. 
    If authentication is successful, a JWT access token is returned that can be used for further protected endpoints.
    
    - **username**: The username of the user.
    - **password**: The password for the user.
    
    Returns a JWT token that can be used to authenticate future requests.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Generate the access token for the user
    token = create_access_token(user['username'], user['id'], timedelta(minutes=20))
    logger.info(f"User {form_data.username} successfully logged in and token generated.")
    
    return {"access_token": token, "token_type": "bearer"}
