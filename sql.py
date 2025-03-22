from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from sqlalchemy import Column, JSON
from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Annotated

# Song Tables
class Song(BaseModel):
    name: str
    url: str

# User Tables
class User(SQLModel):
    name: str
    age: int | None
    email: str

class MainUser(User, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    password: str
    salt: int
    songs: list[Song] | None = Field(default=None, sa_column=Column(JSON))

class UserPublic(User):
    id: int
    songs: list[Song] | None = None

class UserCreate(User):
    password: str
    salt: int | None = Field(default=0)

class VerifyUser(BaseModel):
    email: str
    password: str | None = Field(default=None)

class UpdateUser(User):
    name: str | None = None
    age: int | None = None
    email: str | None = None
    password: str | None = None
    songs: list[Song] | None = None

# SQLite file naming

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create the engine

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

# Create the tables in the db
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Get the session dep
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Run the create_db_and_tables on startup
@asynccontextmanager
async def lifespan(api: FastAPI):
    create_db_and_tables()
    yield

