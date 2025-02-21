from pydantic import BaseModel, EmailStr
import uuid
from models.user import RoleEnum


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.member


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum

    class Config:
        from_attributes = True
