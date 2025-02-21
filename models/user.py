from sqlmodel import SQLModel, Field
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    member = "member"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.member)
