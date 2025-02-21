import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select
from database import get_session
from main import app
import os
from dotenv import load_dotenv
from models.user import User
from utils.security import (
    create_access_token,
)


load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = Session(engine)


@pytest.fixture
def test_db():
    """Creates a fresh test database before tests and drops it after."""
    SQLModel.metadata.create_all(engine)
    try:
        db = TestingSessionLocal
        yield db
    finally:
        db.rollback()
        db.close()
        SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_client(test_db):
    """Overrides FastAPI's get_session dependency with the test database."""

    def override_get_session():
        try:
            yield test_db
        finally:
            test_db.rollback()
            test_db.close()

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


@pytest.fixture
def test_admin(test_client, test_db):
    """Fixture to create an admin user and return both user data and JWT token."""
    test_client.post(
        "/auth/signup",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "adminpass",
            "role": "admin",
        },
    )

    # created user from the database
    admin_user = test_db.exec(
        select(User).where(User.email == "admin@example.com")
    ).first()

    # Generate JWT token
    login_response = test_client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "adminpass"},
    )
    token = login_response.json()["access_token"]

    return {"user": admin_user, "token": token}


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture
def test_member(test_db):
    """Creates a test member user with a hashed password."""
    hashed_pw = pwd_context.hash("memberpassword")

    member_user = User(
        username="member",
        email="member@example.com",
        hashed_password=hashed_pw,
        role="member",
    )
    test_db.add(member_user)
    test_db.commit()
    test_db.refresh(member_user)
    return member_user


@pytest.fixture
def admin_token(test_admin):
    """Returns the admin's JWT token from test_admin."""
    return test_admin["token"]


def test_admin_access(test_client, test_admin):
    admin_user = test_admin["user"]
    assert admin_user.email == "admin@example.com"
