# main.py
from fastapi import FastAPI
from app.database.db import create_db_and_tables  # Import your database setup function
from app.kafka.kafka import consume_messages  # Import Kafka consumer function
from contextlib import asynccontextmanager
from app.settings import BOOTSTRAP_SERVER
from app.routes import inventory_routes


# Topic Configuration
topic = "product_topic"

# Lifespan event to set up the database and Kafka consumer
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    create_db_and_tables()
    
    # Start consuming Kafka messages
    await consume_messages(
        topic="product_topic",
        bootstrap_servers=BOOTSTRAP_SERVER,
        consumer_group_id="Product_consumer_group_id",
    )
    yield

app = FastAPI(
    title="Product Service",
    description="API for Products",
    version="1.0.0",
    lifespan=lifespan,
)

# Home route
@app.get("/")
def home():
    return "Inventory Service API Is Running"

app.include_router(
    router=inventory_routes.router, prefix="/api/inventory-service"
)
