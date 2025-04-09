from psycopg2.extras import RealDictCursor
from src.db.connections import get_db_connection, logger

def get_book_by_title(title: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, title, published_year, genre, author_id FROM books WHERE title = %s", (title,))
                book = cursor.fetchone()
                return book
    except Exception as e:
        logger.error(f"Error fetching book by title {title}: {e}")
        raise

def create_book(title, published_year, genre, author_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO books (title, published_year, genre, author_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (title, published_year, genre, author_id))
                book_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"Book created with ID: {book_id}")
                return book_id
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        raise ValueError(f"Error creating book: {e}")

def get_book(book_id):
    """Fetch a specific book by its ID."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name AS author
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    WHERE b.id = %s
                """, (book_id,))
                book = cursor.fetchone()
                if not book:
                    raise ValueError(f"Book with ID {book_id} not found")
                    
                return book
    except Exception as e:
        logger.error(f"Error fetching book with ID {book_id}: {e}")
        raise

def get_books(skip=0, limit=10, sort_by="title"):
    if sort_by not in ["title", "published_year", "author_id"]:
        sort_by = "title"
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name AS author
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    ORDER BY {sort_by}
                    OFFSET %s LIMIT %s
                """, (skip, limit))
                books = cursor.fetchall()
                return books
    except Exception as e:
        logger.error(f"Error fetching books with pagination: {e}")
        raise

def update_book(book_id, title, published_year, genre, author_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE books SET title=%s, published_year=%s, genre=%s, author_id=%s
                    WHERE id=%s
                """, (title, published_year, genre, author_id, book_id))
                
                if cursor.rowcount == 0:
                    raise ValueError("Book not found or no change")
                conn.commit()
                logger.info(f"Book with ID {book_id} updated successfully.")
    except Exception as e:
        logger.error(f"Error updating book with ID {book_id}: {e}")
        conn.rollback()
        raise ValueError(f"Error updating book: {e}")

def delete_book(book_id):
    """Delete a book from the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM user_history WHERE book_id=%s", (book_id,))
                conn.commit()

                cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
                
                if cursor.rowcount == 0:
                    raise ValueError("Book not found")

                conn.commit()
                logger.info(f"Book with ID {book_id} deleted successfully.")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error deleting book with ID {book_id}: {e}")
        raise ValueError(f"Error deleting book: {e}")
