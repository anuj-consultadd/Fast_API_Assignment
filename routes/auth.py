# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User, RoleEnum
from schemas.user import UserCreate, UserResponse
from database import get_session
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IntegrityError


router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_200_OK)
def register_user(user_data: UserCreate, db: Session = Depends(get_session)):
    if not user_data.username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    if not user_data.email.strip():
        raise HTTPException(status_code=400, detail="Email cannot be empty")
    if not user_data.password.strip():
        raise HTTPException(status_code=400, detail="Password cannot be empty")

    user = db.exec(select(User).where(User.email == user_data.email)).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Login
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)
):
    user = db.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Get current user
@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.exec(select(User).where(User.id == int(payload.get("sub")))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Refresh Token
@router.post("/refresh")
def refresh_token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    new_access_token = create_access_token(
        {"sub": payload["sub"], "role": payload["role"]},
        expires_delta=timedelta(minutes=30),
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
