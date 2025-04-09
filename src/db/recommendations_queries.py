from typing import List, Dict
from src.db.connections import get_db_connection, logger

def add_book_view(user_id: int, book_id: int):
    """Record a book view by a user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Check if a record already exists for this user and book
                cursor.execute("""
                    SELECT 1 FROM user_history WHERE user_id = %s AND book_id = %s
                """, (user_id, book_id))
                existing_view = cursor.fetchone()

                if existing_view:
                    logger.info(f"User {user_id} has already viewed book {book_id}. No new record added.")
                    return  # Exit if the record already exists

                # Add a new record for the book view
                cursor.execute("""
                    INSERT INTO user_history (user_id, book_id, action)
                    VALUES (%s, %s, 'viewed')
                """, (user_id, book_id))
                conn.commit()
                logger.info(f"Recorded book view for user {user_id}, book {book_id}")
    except Exception as e:
        logger.error(f"Error adding book view for user {user_id}, book {book_id}: {e}")
        raise

def recommend_books_by_genre(user_id: int, genre_input: str) -> List[Dict]:
    """Recommend books by genre that the user has not yet viewed."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if the genre exists in the database
                cur.execute("""
                    SELECT COUNT(*) FROM books
                    WHERE genre = %s
                    LIMIT 1;
                """, (genre_input,))
                genre_count = cur.fetchone()[0]

                if genre_count == 0:
                    return []  # Return empty if no books of that genre exist

                # Recommend books of the specified genre that the user has not viewed
                cur.execute("""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name AS author_name
                    FROM books b
                    JOIN authors a ON a.id = b.author_id
                    WHERE b.genre = %s
                      AND b.id NOT IN (
                          SELECT book_id FROM user_history WHERE user_id = %s
                      )
                    LIMIT 10;
                """, (genre_input, user_id))

                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]  # Extract column names
                result = []
                for row in rows:
                    book = dict(zip(columns, row))  # Create a dictionary for each book
                    book["author"] = {
                        "id": book.pop("author_id"),
                        "name": book.pop("author_name")
                    }
                    result.append(book)  # Add the book to the result list
                return result
    except Exception as e:
        logger.error(f"Error recommending books by genre for user {user_id}, genre {genre_input}: {e}")
        raise

def recommend_books_by_author(user_id: int, author_name: str) -> List[Dict]:
    """Recommend books by a specific author that the user has not yet viewed."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Find the author by name
                cur.execute("""
                    SELECT id FROM authors
                    WHERE LOWER(name) = LOWER(%s)
                    LIMIT 1;
                """, (author_name,))
                author_row = cur.fetchone()
                if not author_row:
                    return []  # Return empty if the author is not found
                author_id = author_row[0]

                # Recommend books by the author that the user has not viewed
                cur.execute("""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name AS author_name
                    FROM books b
                    JOIN authors a ON a.id = b.author_id
                    WHERE b.author_id = %s
                      AND b.id NOT IN (
                          SELECT book_id FROM user_history WHERE user_id = %s
                      )
                    LIMIT 10;
                """, (author_id, user_id))

                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                result = []
                for row in rows:
                    book = dict(zip(columns, row))
                    book["author"] = {
                        "id": book.pop("author_id"),
                        "name": book.pop("author_name")
                    }
                    result.append(book)
                return result
    except Exception as e:
        logger.error(f"Error recommending books by author for user {user_id}, author {author_name}: {e}")
        raise

def recommend_books_based_on_history(user_id: int) -> List[Dict]:
    """Recommend books based on user's past history of book views."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.id, b.title, b.published_year, b.genre, b.author_id, a.name as author_name
                    FROM books b
                    JOIN authors a ON a.id = b.author_id
                    WHERE (
                        b.genre IN (
                            SELECT b2.genre
                            FROM user_history h
                            JOIN books b2 ON b2.id = h.book_id
                            WHERE h.user_id = %s
                            GROUP BY b2.genre
                            ORDER BY COUNT(*) DESC
                            LIMIT 3
                        )
                        OR b.author_id IN (
                            SELECT b3.author_id
                            FROM user_history h
                            JOIN books b3 ON b3.id = h.book_id
                            WHERE h.user_id = %s
                            GROUP BY b3.author_id
                            ORDER BY COUNT(*) DESC
                            LIMIT 3
                        )
                    )
                    AND b.id NOT IN (
                        SELECT book_id FROM user_history WHERE user_id = %s
                    )
                    LIMIT 15;
                """, (user_id, user_id, user_id))

                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                result = []
                for row in rows:
                    book = dict(zip(columns, row))
                    book["author"] = {
                        "id": book.pop("author_id"),
                        "name": book.pop("author_name")
                    }
                    result.append(book)
                return result
    except Exception as e:
        logger.error(f"Error recommending books based on history for user {user_id}: {e}")
        raise
