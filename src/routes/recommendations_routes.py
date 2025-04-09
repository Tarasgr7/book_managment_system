from typing import List
from fastapi import APIRouter, Request, status, HTTPException, Query
from src.dependencies import logger
from src.utils.auth_utils import user_dependency
from src.utils.rate_limit import limiter
from src.schemas.book_schemas import BookRead
from src.db.recommendations_queries import (
    recommend_books_by_genre,
    recommend_books_by_author,
    recommend_books_based_on_history,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

def format_author_field(book: dict) -> dict:
    if isinstance(book.get("author"), dict):
        book["author"] = book["author"].get("name", "Unknown Author")
    return book

@router.get("/recommendations/genre", response_model=List[BookRead])
@limiter.limit("5/minute")
async def recommend_books_by_genre_endpoint(
    user: user_dependency, genre: str, request: Request
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    logger.info(f"User {user.get('id')} requested genre-based book recommendations for genre: {genre}")
    try:
        recommended_books = recommend_books_by_genre(user.get("id"), genre)
        formatted_books = [format_author_field(book) for book in recommended_books]
        logger.info(f"Successfully retrieved {len(formatted_books)} books based on genre '{genre}'")
        return formatted_books
    except ValueError as e:
        logger.error(f"Error in recommending books by genre: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error occurred while recommending books by genre.")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/recommendations/author", response_model=List[BookRead])
@limiter.limit("5/minute")
async def recommend_books_by_author_endpoint(
    user: user_dependency = None,
    request: Request = None,
    author_name: str = Query(..., description="Author name to base recommendations on"),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    logger.info(f"User {user.get('id')} requested author-based book recommendations for author: {author_name}")
    try:
        recommended_books = recommend_books_by_author(user.get("id"), author_name)
        formatted_books = [format_author_field(book) for book in recommended_books]
        logger.info(f"Successfully retrieved {len(formatted_books)} books based on author '{author_name}'")
        return formatted_books
    except Exception as e:
        logger.exception(f"Unexpected error occurred while recommending books by author {author_name}.")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/recommendations/history", response_model=List[BookRead])
@limiter.limit("5/minute")
async def recommend_books_history_endpoint(
    user: user_dependency, request: Request
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    logger.info(f"User {user.get('id')} requested book recommendations based on their history")
    try:
        recommended_books = recommend_books_based_on_history(user.get("id"))
        formatted_books = [format_author_field(book) for book in recommended_books]
        logger.info(f"Successfully retrieved {len(formatted_books)} books based on user's history")
        return formatted_books
    except Exception as e:
        logger.exception("Unexpected error occurred while recommending books based on history.")
        raise HTTPException(status_code=500, detail="Internal server error")
