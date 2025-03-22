from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI

from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Annotated

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

