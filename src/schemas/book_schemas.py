from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

GENRES = {
    'Fiction', 'Non-Fiction', 'Science', 'History',
    'Fantasy', 'Biography', 'Romance', 'Thriller',
    'Mystery', 'Philosophy'
}

current_year = datetime.now().year

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=250, description="The title of the book.")
    published_year: int = Field(..., description="The year the book was published.")
    genre: str = Field(..., description="The genre of the book. Must be one of the predefined genres.")
    author: str = Field(..., min_length=1, max_length=250, description="The name of the author.")

    @validator("published_year")
    def validate_year(cls, v):
        if not 1800 <= v <= current_year:
            raise ValueError(f"Published year must be between 1800 and the current year ({current_year}).")
        return v

    @validator("genre")
    def validate_genre(cls, v):
        if v not in GENRES:
            raise ValueError(f"Genre must be one of: {', '.join(GENRES)}.")
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The title of the book. If not provided, the title will not be updated.")
    published_year: Optional[int] = Field(None, description="The year the book was published. If not provided, the year will not be updated.")
    genre: Optional[str] = Field(None, description="The genre of the book. If not provided, the genre will not be updated.")
    author: Optional[str] = Field(None, description="The name of the author. If not provided, the author will not be updated.")

    @validator("published_year")
    def validate_year(cls, v):
        if v is not None and not 1800 <= v <= current_year:
            raise ValueError(f"Year must be between 1800 and {current_year}.")
        return v

    @validator("genre")
    def validate_genre(cls, v):
        if v is not None and v not in GENRES:
            raise ValueError(f"Genre must be one of {', '.join(GENRES)}.")
        return v

    @validator("title", "author")
    def validate_non_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Field must not be empty.")
        return v

class BookRead(BookBase):
    id: int = Field(..., description="The unique identifier for the book.")
    author: str = Field(..., description="The name of the author.")

class BookWithAuthor(BaseModel):
    id: int = Field(..., description="The unique identifier for the book.")
    title: str = Field(..., description="The title of the book.")
    published_year: int = Field(..., description="The year the book was published.")
    genre: str = Field(..., description="The genre of the book.")
    author: str = Field(..., description="The name of the author.")
