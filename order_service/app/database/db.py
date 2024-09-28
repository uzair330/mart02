from typing import Annotated
from fastapi import Depends
from sqlmodel import create_engine,Session, SQLModel
from app.settings import DATABASE_URL



# Connection to database

connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string, connect_args={}, pool_recycle=300
)

def get_session():
    with Session(engine) as session:
        yield session


DATABASE_SESSION = Annotated[Session, Depends(get_session)]

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)