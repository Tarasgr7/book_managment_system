from dotenv import load_dotenv
from src.dependencies import logger
from src.db.connections import get_db_connection
load_dotenv()

# SQL query to create necessary tables if they do not exist
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
        cur.execute(query)  # Execute query to get all table names
        tables = {table[0] for table in cur.fetchall()}  # Fetch table names and store in a set
    return tables.issuperset(table_names)  # Check if the set of required tables is a subset of existing tables

def init_db():
    """Initialize the database by creating necessary tables if they do not exist."""
    try:
        with get_db_connection() as conn:  # Use context manager for database connection
            conn.autocommit = True  # Enable autocommit for DDL operations
            logger.info("Connected to the database successfully.")
            
            required_tables = {'users', 'authors', 'books', 'user_history'}
            
            # Check if the required tables exist
            if not check_tables_exist(conn, required_tables):
                logger.warning("Some tables are missing. Creating tables...")
                with conn.cursor() as cur:  # Use cursor to execute SQL
                    try:
                        logger.info("Executing init SQL to create tables...")
                        cur.execute(init_sql)  # Execute SQL to create the tables
                        logger.info("Tables created successfully.")
                    except Exception as e:
                        logger.error(f"Failed to create tables: {e}")
                        raise  # Raise error if table creation fails
            else:
                logger.info("Tables already exist. No need to create.")
                
    except Exception as e:
        # Log and raise an error if database initialization fails
        logger.error(f"Failed to initialize database: {e}")
