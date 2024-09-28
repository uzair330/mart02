from app.routes import user_routes
from fastapi import FastAPI
from app.database.db import create_db_and_tables
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan
)    

@app.get("/")
def auth_service():
    return "User Service is running...."

app.include_router(router=user_routes.router,prefix="/api/user-auth")    