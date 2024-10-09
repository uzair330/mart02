from fastapi import FastAPI
from app.routes import routes
from app.database.db import create_db_and_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Order Service",
    description="API for Orders and Carts",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def home():
    return "Order Service API is Healthy"

app.include_router(
    router=routes.router, prefix="/api/order-service"
)
