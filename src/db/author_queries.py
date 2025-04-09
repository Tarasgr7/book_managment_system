from psycopg2.extras import RealDictCursor
from src.db.connections import get_db_connection, logger

def get_author_by_name(name: str):
    """Fetch author details by name."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, name FROM authors WHERE name = %s", (name,))
                author = cursor.fetchone()
                return author
    except Exception as e:
        logger.error(f"Error fetching author by name {name}: {e}")
        raise

def create_author(name: str):
    """Create a new author in the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM authors WHERE name = %s", (name,))
                existing_author = cursor.fetchone()
                if existing_author:
                    raise ValueError(f"Author with name '{name}' already exists.")
                cursor.execute("INSERT INTO authors (name) VALUES (%s) RETURNING id", (name,))
                author_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Author created with ID: {author_id}")
                return author_id
    except Exception as e:
        logger.error(f"Error creating author with name {name}: {e}")
        if conn:
            conn.rollback()
        raise
