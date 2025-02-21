from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.book import Book
from models.borrow import Borrow
from schemas.book import BookResponse
from schemas.borrow import BorrowResponse
from database import get_session
from utils.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/books", tags=["User"])


# Browse books
@router.get("/", response_model=list[BookResponse])
def browse_books(db: Session = Depends(get_session)):
    books = db.exec(select(Book)).all()
    return books


# Borrow a book
@router.post("/{book_id}/borrow", response_model=BorrowResponse)
def borrow_book(
    book_id: int, db: Session = Depends(get_session), user=Depends(get_current_user)
):
    book = db.exec(select(Book).where(Book.id == book_id)).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    if not book.available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not available"
        )

    try:
        book.available = False
        borrow_entry = Borrow(
            user_id=user.id, book_id=book_id, borrowed_at=datetime.utcnow()
        )
        db.add(borrow_entry)
        db.commit()
        db.refresh(borrow_entry)
        return borrow_entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{book_id}/return")
def return_book(
    book_id: int, db: Session = Depends(get_session), user=Depends(get_current_user)
):
    borrow_entry = db.exec(
        select(Borrow).where(
            Borrow.book_id == book_id,
            Borrow.user_id == user.id,
            Borrow.returned_at == None,
        )
    ).first()

    if not borrow_entry:
        # Instead of checking for the book first, check if it even exists in the system
        book = db.exec(select(Book).where(Book.id == book_id)).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active borrow record found for this book",
        )

    try:
        borrow_entry.returned_at = datetime.utcnow()
        book = db.exec(select(Book).where(Book.id == book_id)).first()
        book.available = True
        db.commit()
        return {"message": "Book returned successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# View borrowing history
@router.get("/history", response_model=list[BorrowResponse])
def borrowing_history(
    db: Session = Depends(get_session), user=Depends(get_current_user)
):
    history = db.exec(select(Borrow).where(Borrow.user_id == user.id)).all()
    return history
