import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("service")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Function to fetch environment variables with validation
def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """
    Retrieves environment variable value with optional default.
    Raises an error if the variable is not set and no default is provided.
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value

# Database Configuration
class DatabaseConfig:
    def __init__(self):
        self.user = get_env_variable("DB_USER")
        self.password = get_env_variable("DB_PASSWORD")
        self.host = get_env_variable("DB_HOST")
        self.db = get_env_variable("DB_NAME")
        self.port = get_env_variable("DB_PORT")

    def get_db_url(self) -> str:
        """
        Constructs the database URL from environment variables.
        Logs the URL at info level, but excludes sensitive data.
        """
        url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        logger.info(f"DB URL generated, user: {self.user}, host: {self.host},port:{self.port} ,db: {self.db}")
        return url

# Create an instance of the DatabaseConfig to manage database connection URL
db_config = DatabaseConfig()
DATABASE_URL = db_config.get_db_url()
