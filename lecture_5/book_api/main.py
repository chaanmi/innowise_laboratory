# main.py
# Main FastAPI application file

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- DATABASE SETUP ---
# Create connection to SQLite database (file will be created automatically)
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"

# Create SQLAlchemy engine for database operations
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
)

# Create session factory for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


# --- DATABASE MODEL (SQLAlchemy) ---
class BookDB(Base):
    """
    Book model for database.
    Each instance of this class represents a row in the 'books' table.
    """

    __tablename__ = "books"  # Table name in database

    # Table columns
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # Required field
    author = Column(String, nullable=False)  # Required field
    year = Column(Integer, nullable=True)  # Optional field


# Create all tables in the database
# This will execute on first application run
Base.metadata.create_all(bind=engine)


# --- PYDANTIC MODELS (for API data validation) ---
class BookCreate(BaseModel):
    """
    Model for creating a new book.
    Used for validating input data in POST and PUT requests.
    """

    title: str = Field(..., min_length=1, description="Book title")
    author: str = Field(..., min_length=1, description="Book author")
    year: Optional[int] = Field(None, ge=0, le=2100, description="Publication year")


class BookResponse(BaseModel):
    """
    Model for API response when retrieving a book.
    Includes all fields including id.
    """

    id: int
    title: str
    author: str
    year: Optional[int]

    # Configuration for working with SQLAlchemy objects
    class Config:
        orm_mode = True


# --- FASTAPI DEPENDENCIES ---
def get_db():
    """
    Dependency for getting database session.
    This function will be called for each API request.
    Ensures session is closed after request processing.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- CREATE FASTAPI APPLICATION ---
app = FastAPI(
    title="Simple Book Collection API",
    description="API for managing book collection",
    version="1.0.0",
)


# --- ROOT ENDPOINT ---
@app.get("/")
def read_root():
    """
    Root endpoint for API health check.
    """
    return {"message": "Welcome to Book Collection API"}


# --- API ENDPOINTS ---


# ENDPOINT 1: Create new book
@app.post("/books/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Creates a new book in the collection.

    Args:
        book: Book data (title, author, year)
        db: Database session (auto-injected)

    Returns:
        Created book with assigned id
    """
    # Create book object for database
    db_book = BookDB(**book.dict())

    # Add book to database
    db.add(db_book)
    db.commit()  # Save changes
    db.refresh(db_book)  # Refresh object to get id

    return db_book


# ENDPOINT 2: Get all books
@app.get("/books/", response_model=List[BookResponse])
def read_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieves list of all books with pagination support.

    Args:
        skip: How many records to skip (for pagination)
        limit: Maximum records per page
        db: Database session

    Returns:
        List of books with pagination
    """
    # Get books from database with pagination
    books = db.query(BookDB).offset(skip).limit(limit).all()
    return books


# ENDPOINT 3: Get book by ID
@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a book by its ID.

    Args:
        book_id: Book ID
        db: Database session

    Raises:
        HTTPException: If book is not found

    Returns:
        Book with specified ID
    """
    # Find book in database
    book = db.query(BookDB).filter(BookDB.id == book_id).first()

    # If book not found, return 404 error
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# ENDPOINT 4: Update book
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookCreate, db: Session = Depends(get_db)):
    """
    Updates book information.

    Args:
        book_id: ID of book to update
        book_update: New book data
        db: Database session

    Raises:
        HTTPException: If book is not found

    Returns:
        Updated book
    """
    # Find book in database
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update book fields
    for key, value in book_update.dict().items():
        setattr(db_book, key, value)

    # Save changes
    db.commit()
    db.refresh(db_book)

    return db_book


# ENDPOINT 5: Delete book
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Deletes a book from collection.

    Args:
        book_id: ID of book to delete
        db: Database session

    Raises:
        HTTPException: If book is not found
    """
    # Find book in database
    book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Delete book
    db.delete(book)
    db.commit()

    # Return empty response with status 204 (No Content)


# ENDPOINT 6: Search books
@app.get("/books/search/", response_model=List[BookResponse])
def search_books(
    title: Optional[str] = Query(None, description="Search by title (partial match)"),
    author: Optional[str] = Query(None, description="Search by author (partial match)"),
    year: Optional[int] = Query(
        None, ge=0, le=2100, description="Search by publication year"
    ),
    db: Session = Depends(get_db),
):
    """
    Search books by various criteria.
    Can search by title, author, or publication year.
    Parameters can be combined.

    Args:
        title: Part of book title (case-insensitive search)
        author: Part of author name (case-insensitive search)
        year: Publication year
        db: Database session

    Returns:
        List of books matching search criteria
    """
    # Start database query
    query = db.query(BookDB)

    # Add search conditions if parameters provided
    if title:
        query = query.filter(BookDB.title.ilike(f"%{title}%"))

    if author:
        query = query.filter(BookDB.author.ilike(f"%{author}%"))

    if year is not None:
        query = query.filter(BookDB.year == year)

    # Execute query and return results
    books = query.all()
    return books


# --- APPLICATION RUN ---
# To run application use command:
# uvicorn main:app --reload
# Then go to: http://127.0.0.1:8000/docs
