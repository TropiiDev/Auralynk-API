from pydantic import BaseModel
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

# Token Tables
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None

# Email Tables
class EmailTable(BaseModel):
    email: str
    name: str

class Email(BaseModel):
    email: str

class EmailList(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    name: str | None = Field(default=None)

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
    username: str

class MainUser(User, table=True):
    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(index=True, unique=True)
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