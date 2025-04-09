# src/routes/book_routes.py
import json
import csv
from io import StringIO
from typing import List
from datetime import datetime

from fastapi import APIRouter, status, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse

from src.utils.auth_utils import user_dependency
from src.utils.rate_limit import limiter
from src.schemas.book_schemas import BookCreate, BookRead, BookUpdate, GENRES
from src.db.book_queries import get_book_by_title, create_book, get_book, get_books, update_book, delete_book
from src.db.author_queries import get_author_by_name, create_author
from src.db.recommendations_queries import add_book_view
from src.dependencies import logger


router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/get_all_books", response_model=List[BookRead])
@limiter.limit("5/minute")
async def get_books_endpoint(request: Request, skip: int = 0, limit: int = 10, sort_by: str = "title"):
    try:
        books = get_books(skip, limit, sort_by)
        logger.info(f"Retrieved {len(books)} books with skip={skip}, limit={limit}, sort_by={sort_by}")
        return books
    except ValueError as e:
        logger.error(f"Error retrieving books: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/get_book/{book_id}", response_model=BookRead)
@limiter.limit("5/minute")
async def get_book_endpoint(book_id: int, user: user_dependency, request: Request):
    try:
        book = get_book(book_id)
        add_book_view(user.get("id"), book_id)
        logger.info(f"User {user.get('id')} viewed book {book_id}")
        return book
    except ValueError as e:
        logger.error(f"Error retrieving book with ID {book_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/create_book", status_code=status.HTTP_201_CREATED, response_model=BookRead)
@limiter.limit("5/minute")
async def create_book_endpoint(book: BookCreate, user: user_dependency, request: Request):
    if not user:
        logger.warning("Attempt to create book without authentication.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        existing = get_book_by_title(book.title)
        if existing:
            logger.warning(f"Book with title {book.title} already exists.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book with this title already exists")

        author = get_author_by_name(book.author)
        author_id = author["id"] if author else create_author(book.author)

        book_id = create_book(book.title, book.published_year, book.genre, author_id)

        logger.info(f"Created new book: {book.title} (ID: {book_id})")
        return {**book.dict(), "id": book_id}
    except ValueError as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/update_book/{book_id}", response_model=BookRead)
@limiter.limit("5/minute")
async def update_book_endpoint(book_id: int, book: BookUpdate, user: user_dependency, request: Request):
    if not user:
        logger.warning("Attempt to update book without authentication.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        existing_book = get_book(book_id)
        if not existing_book:
            logger.warning(f"Book with ID {book_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        updated_title = book.title or existing_book["title"]
        updated_year = book.published_year or existing_book["published_year"]
        updated_genre = book.genre or existing_book["genre"]
        updated_author_name = book.author or existing_book["author"]

        if updated_title != existing_book["title"]:
            same_title = get_book_by_title(updated_title)
            if same_title:
                logger.warning(f"Book with title {updated_title} already exists.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book with this title already exists")

        current_year = datetime.now().year
        if not updated_title.strip():
            raise ValueError("Title must not be empty")
        if not updated_author_name.strip():
            raise ValueError("Author must not be empty")
        if updated_year < 1800 or updated_year > current_year:
            raise ValueError(f"Year must be between 1800 and {current_year}")
        if updated_genre not in GENRES:
            raise ValueError(f"Genre must be one of {GENRES}")

        author = get_author_by_name(updated_author_name)
        author_id = author["id"] if author else create_author(updated_author_name)

        update_book(book_id, updated_title, updated_year, updated_genre, author_id)

        logger.info(f"Book {book_id} updated successfully.")
        return {
            "id": book_id,
            "title": updated_title,
            "published_year": updated_year,
            "genre": updated_genre,
            "author": updated_author_name
        }

    except ValueError as e:
        logger.error(f"Error updating book {book_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/delete_book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_book_endpoint(book_id: int, user: user_dependency, request: Request):
    if not user:
        logger.warning("Attempt to delete book without authentication.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        delete_book(book_id)
        logger.info(f"Book {book_id} deleted successfully.")
        return {"message": "Book deleted"}
    except ValueError as e:
        logger.error(f"Error deleting book {book_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/import", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def import_books(user: user_dependency, request: Request, file: UploadFile = File(...)):
    if not user:
        logger.warning("Attempt to import books without authentication.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    content = await file.read()
    try:
        if file.filename.endswith(".json"):
            books_data = json.loads(content.decode("utf-8"))
        elif file.filename.endswith(".csv"):
            csv_content = content.decode("utf-8")
            reader = csv.DictReader(StringIO(csv_content))
            books_data = list(reader)
        else:
            logger.error("Unsupported file type uploaded.")
            raise HTTPException(status_code=400, detail="Only JSON and CSV files are supported")

        imported = []
        skipped = []

        for book in books_data:
            title = book["title"].strip()
            year = int(book["published_year"])
            genre = book["genre"].strip()
            author_name = book["author"].strip()

            if get_book_by_title(title):
                skipped.append(title)
                continue

            author = get_author_by_name(author_name)
            author_id = author["id"] if author else create_author(author_name)

            try:
                book_id = create_book(title, year, genre, author_id)
                imported.append(title)
            except ValueError:
                skipped.append(title)

        logger.info(f"Import summary: Imported {len(imported)} books, skipped {len(skipped)}.")
        return {
            "imported": imported,
            "skipped": skipped,
            "message": f"Imported {len(imported)} books, skipped {len(skipped)} (already exist or invalid)"
        }

    except Exception as e:
        logger.error(f"Error importing books: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import books: {str(e)}")



@router.get("/export", status_code=status.HTTP_200_OK)
async def export_books(format: str = "json", skip: int = 0, limit: int = 10, sort_by: str = "title"):
    books = get_books(skip=skip, limit=limit, sort_by=sort_by)

    if format == "json":
        json_output = json.dumps({"books": books}, ensure_ascii=False)
        response = StreamingResponse(StringIO(json_output), media_type="application/json")
        response.headers["Content-Disposition"] = "attachment; filename=books.json"
        return response

    elif format == "csv":
        csv_output = StringIO()
        fieldnames = ["id", "title", "published_year", "genre", "author", "author_id"]
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()

        for book in books:
            book_data = {key: book[key] for key in fieldnames if key in book}
            writer.writerow(book_data)

        csv_output.seek(0)
        response = StreamingResponse(csv_output, media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=books.csv"
        return response

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format. Use 'json' or 'csv'.")

