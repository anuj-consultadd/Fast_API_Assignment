# database.py
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


# Function to initialize the database
def init_db():
    SQLModel.metadata.create_all(engine)


# Dependency for database session
def get_session():
    with Session(engine) as session:
        yield session
