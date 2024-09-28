from app.routes import product_routes
from fastapi import FastAPI
from app.database.db import create_db_and_tables
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Product Service",
    description="API for Products",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return "Product Service API Is Healthy"


app.include_router(
    router=product_routes.router, prefix="/api/product-service"
)
