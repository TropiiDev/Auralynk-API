from pydantic import BaseModel
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

# Email Tables
class WelcomeEmail(BaseModel):
    email: str
    name: str

# Song Tables
class Song(BaseModel):
    name: str
    url: str

class QuerySong(BaseModel):
    query: str

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