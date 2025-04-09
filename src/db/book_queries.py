from psycopg2.extras import RealDictCursor
from src.db.connections import get_db_connection, logger

def get_book_by_title(title: str):
    """Fetch a book by its title."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using RealDictCursor to return the result as a dictionary
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Executing SQL query to fetch the book by title
                cursor.execute("SELECT id, title, published_year, genre, author_id FROM books WHERE title = %s", (title,))
                book = cursor.fetchone()  # Fetch the first result (book)
                return book
    except Exception as e:
        # Logging error if fetching the book fails
        logger.error(f"Error fetching book by title {title}: {e}")
        raise

def create_book(title, published_year, genre, author_id):
    """Create a new book in the database."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using default cursor to execute queries
            with conn.cursor() as cursor:
                # Executing the insert query to create a new book
                cursor.execute("""
                    INSERT INTO books (title, published_year, genre, author_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (title, published_year, genre, author_id))
                # Fetching the ID of the newly created book
                book_id = cursor.fetchone()[0]
                conn.commit()  # Committing the transaction to the database
                # Logging the creation of the new book
                logger.info(f"Book created with ID: {book_id}")
                return book_id
    except Exception as e:
        # Logging error if book creation fails
        logger.error(f"Error creating book: {e}")
        raise ValueError(f"Error creating book: {e}")

def get_book(book_id):
    """Fetch a specific book by its ID."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using RealDictCursor to return the result as a dictionary
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Executing query to fetch book details by book_id, joining with authors
                cursor.execute("""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name AS author
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    WHERE b.id = %s
                """, (book_id,))
                book = cursor.fetchone()  # Fetch the first result (book)
                
                # Checking if the book exists for the given ID
                if not book:
                    raise ValueError(f"Book with ID {book_id} not found")
                    
                return book
    except Exception as e:
        # Logging error if fetching the book fails
        logger.error(f"Error fetching book with ID {book_id}: {e}")
        raise

def get_books(skip=0, limit=10, sort_by="title"):
    """Fetch books with pagination and sorting."""
    # Validating the sort_by parameter
    if sort_by not in ["title", "published_year", "author_id"]:
        sort_by = "title"  # Default sort by title
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using RealDictCursor to return the result as a dictionary
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Executing the query to fetch books with pagination and sorting
                cursor.execute(f"""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name AS author
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    ORDER BY {sort_by}
                    OFFSET %s LIMIT %s
                """, (skip, limit))
                books = cursor.fetchall()  # Fetching all results
                return books
    except Exception as e:
        # Logging error if fetching books fails
        logger.error(f"Error fetching books with pagination: {e}")
        raise

def update_book(book_id, title, published_year, genre, author_id):
    """Update the details of a book."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using default cursor to execute queries
            with conn.cursor() as cursor:
                # Executing update query to change book details
                cursor.execute("""
                    UPDATE books SET title=%s, published_year=%s, genre=%s, author_id=%s
                    WHERE id=%s
                """, (title, published_year, genre, author_id, book_id))
                
                # If no rows are updated, raise an error
                if cursor.rowcount == 0:
                    raise ValueError("Book not found or no change")
                conn.commit()  # Committing the changes to the database
                # Logging successful update
                logger.info(f"Book with ID {book_id} updated successfully.")
    except Exception as e:
        # Logging error if updating the book fails
        logger.error(f"Error updating book with ID {book_id}: {e}")
        conn.rollback()  # Rolling back in case of error
        raise ValueError(f"Error updating book: {e}")

def delete_book(book_id):
    """Delete a book from the database."""
    try:
        # Establishing the database connection
        with get_db_connection() as conn:
            # Using default cursor to execute queries
            with conn.cursor() as cursor:
                # Deleting the book's history from the user_history table
                cursor.execute("DELETE FROM user_history WHERE book_id=%s", (book_id,))
                conn.commit()  # Committing the deletion of history

                # Deleting the book from the books table
                cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
                
                # If no rows were deleted, raise an error
                if cursor.rowcount == 0:
                    raise ValueError("Book not found")

                conn.commit()  # Committing the deletion of the book
                # Logging successful deletion
                logger.info(f"Book with ID {book_id} deleted successfully.")
    except Exception as e:
        # Rolling back in case of an error and logging it
        if conn:
            conn.rollback()
        logger.error(f"Error deleting book with ID {book_id}: {e}")
        raise ValueError(f"Error deleting book: {e}")
