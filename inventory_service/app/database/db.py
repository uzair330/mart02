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

# from typing import Annotated
# from fastapi import Depends
# from sqlmodel import create_engine, SQLModel
# from sqlmodel.ext.asyncio.session import AsyncSession
# from app.settings import DATABASE_URL

# # Connection to database
# connection_string = str(DATABASE_URL).replace(
#     "postgresql", "postgresql+asyncpg"  # Use asyncpg for async support
# )

# # Create an asynchronous engine
# engine = create_engine(
#     connection_string, echo=True, future=True  # Enable async operation
# )


# # Async session generator function
# async def get_session() -> AsyncSession:
#     async with AsyncSession(engine) as session:
#         yield session


# # Dependency Injection for AsyncSession
# DATABASE_SESSION = Annotated[AsyncSession, Depends(get_session)]


# # Function to create database and tables
# def create_db_and_tables() -> None:
#     SQLModel.metadata.create_all(engine)
