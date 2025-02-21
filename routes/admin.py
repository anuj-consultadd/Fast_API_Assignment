from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from models.book import Book
from schemas.book import BookCreate, BookResponse
from database import get_session
from utils.dependencies import is_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_200_OK)
def add_book(
    book_data: BookCreate, db: Session = Depends(get_session), admin=Depends(is_admin)
):
    if not book_data.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not book_data.author.strip():
        raise HTTPException(status_code=400, detail="Author cannot be empty")
    if not str(book_data.isbn).isnumeric():
        raise HTTPException(status_code=400, detail="ISBN must be numeric")

    try:
        book = Book(
            title=book_data.title, author=book_data.author, isbn=str(book_data.isbn)
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="ISBN already exists")


# Update book details
@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookCreate,
    db: Session = Depends(get_session),
    admin=Depends(is_admin),
):
    book = db.exec(select(Book).where(Book.id == book_id)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book_data.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not book_data.author.strip():
        raise HTTPException(status_code=400, detail="Author cannot be empty")
    if not str(book_data.isbn).isnumeric():
        raise HTTPException(status_code=400, detail="ISBN must be numeric")

    try:
        book.title = book_data.title
        book.author = book_data.author
        book.isbn = book_data.isbn
        db.commit()
        db.refresh(book)
        return book
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="ISBN already exists")


# Delete a book
@router.delete("/books/{book_id}")
def delete_book(
    book_id: int, db: Session = Depends(get_session), admin=Depends(is_admin)
):
    book = db.exec(select(Book).where(Book.id == book_id)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}


# View all books
@router.get("/books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_session), admin=Depends(is_admin)):
    books = db.exec(select(Book)).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return books


# Get book details
@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_session), admin=Depends(is_admin)):
    book = db.exec(select(Book).where(Book.id == book_id)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book
