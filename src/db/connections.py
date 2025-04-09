import psycopg2
from src.dependencies import DATABASE_URL, logger
from contextlib import contextmanager

@contextmanager
def get_db_connection(testing_status=False):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")
