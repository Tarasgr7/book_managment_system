from psycopg2.extras import RealDictCursor
from src.db.connections import get_db_connection, logger

def get_author_by_name(name: str):
    """Fetch author details by name."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using RealDictCursor to return the result as a dictionary
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Querying the database to fetch the author by name
                cursor.execute("SELECT id, name FROM authors WHERE name = %s", (name,))
                author = cursor.fetchone()  # Fetch the first result (author)
                return author
    except Exception as e:
        # Logging the error if fetching fails
        logger.error(f"Error fetching author by name {name}: {e}")
        raise

def create_author(name: str):
    """Create a new author in the database."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using default cursor to execute queries
            with conn.cursor() as cursor:
                # Check if an author with the same name already exists
                cursor.execute("SELECT id FROM authors WHERE name = %s", (name,))
                existing_author = cursor.fetchone()  # Fetch the result
                if existing_author:
                    # Raise an error if the author already exists
                    raise ValueError(f"Author with name '{name}' already exists.")

                # Insert the new author into the database and get the generated ID
                cursor.execute("INSERT INTO authors (name) VALUES (%s) RETURNING id", (name,))
                author_id = cursor.fetchone()[0]  # Fetch the inserted author's ID
                conn.commit()  # Commit the transaction to the database
                # Log the creation of the new author
                logger.info(f"Author created with ID: {author_id}")
                return author_id
    except Exception as e:
        # Log the error if creating the author fails
        logger.error(f"Error creating author with name {name}: {e}")
        if conn:
            conn.rollback()  # Rollback the transaction in case of error
        raise
