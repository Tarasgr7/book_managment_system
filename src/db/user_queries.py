from psycopg2.extras import RealDictCursor
from src.db.connections import get_db_connection,logger

def get_user_by_username(username: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT  id, username, password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                return user
    except Exception as e:
        logger.error(f"Error fetching user by username {username}: {e}")
        raise

def create_user(username: str, hashed_password: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id", (username, hashed_password))
                user_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"User created with ID: {user_id}")
                return user_id
    except Exception as e:
        logger.error(f"Error creating user with username {username}: {e}")
        raise
