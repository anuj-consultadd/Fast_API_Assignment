from sqlmodel import SQLModel, Field


class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author: str
    isbn: str = Field(unique=True, index=True)
    available: bool = Field(default=True)
