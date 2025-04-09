from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.routes.auth_routes import router as auth_router
from src.routes.book_routes import router as book_router
from src.routes.recommendations_routes import router as recommendation_routes
from src.db.init_db import init_db
from src.utils.rate_limit import limiter

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    """
    app = FastAPI(title="Book Management API", version="1.0")

    # Limiter setup
    app.state.limiter = limiter

    # Exception handler for rate limits
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Initialize the database if not already initialized
    init_db()

    # Include routers for various functionalities
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(book_router, prefix="/api/v1")
    app.include_router(recommendation_routes, prefix="/api/v1")

    return app

app = create_app()
