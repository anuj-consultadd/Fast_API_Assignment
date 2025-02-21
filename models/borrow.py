from sqlmodel import SQLModel, Field
from datetime import datetime


class Borrow(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    book_id: int = Field(foreign_key="book.id")
    borrowed_at: datetime = Field(default_factory=datetime.utcnow)
    returned_at: datetime = Field(default=None, nullable=True)
