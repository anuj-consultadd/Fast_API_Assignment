from pydantic import BaseModel, Field
import uuid


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")
    author: str = Field(..., min_length=1, description="Author cannot be empty")
    isbn: str = Field(..., min_length=1, description="ISBN must be a non-empty string")


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    available: bool

    class Config:
        from_attributes = True
