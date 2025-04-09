import time
from dotenv import load_dotenv
from src.dependencies import logger
from src.db.connections import get_db_connection
load_dotenv()

init_sql = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    published_year INT NOT NULL,
    genre VARCHAR(50) NOT NULL CHECK (genre IN (
        'Fiction', 'Non-Fiction', 'Science', 'History', 'Fantasy', 
        'Biography', 'Romance', 'Thriller', 'Mystery', 'Philosophy'
    )),
    author_id INTEGER NOT NULL REFERENCES authors(id)
);

CREATE TABLE IF NOT EXISTS user_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    book_id INTEGER NOT NULL REFERENCES books(id),
    action VARCHAR(50) CHECK (action IN ('viewed')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def check_tables_exist(conn, table_names):
    """Check if specific tables exist in the database."""
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """
    with conn.cursor() as cur:
        cur.execute(query)  
        tables = {table[0] for table in cur.fetchall()}  
    return tables.issuperset(table_names)

def init_db(retries=5, delay=3):
    for attempt in range(1, retries + 1):
        try:
            with get_db_connection() as conn:
                conn.autocommit = True
                logger.info("Connected to the database successfully.")
                
                required_tables = {'users', 'authors', 'books', 'user_history'}
                
                if not check_tables_exist(conn, required_tables):
                    logger.warning("Some tables are missing. Creating tables...")
                    with conn.cursor() as cur:
                        try:
                            logger.info("Executing init SQL to create tables...")
                            cur.execute(init_sql)
                            logger.info("Tables created successfully.")
                        except Exception as e:
                            logger.error(f"Failed to create tables: {e}")
                            raise
                else:
                    logger.info("Tables already exist. No need to create.")
                break 
        except Exception as e:
            logger.error(f"Attempt {attempt} - Failed to initialize database: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.critical("Exceeded maximum number of retries. Exiting.")
