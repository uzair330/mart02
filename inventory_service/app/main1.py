# from app.routes import product_routes
from fastapi import FastAPI,Depends
from app.database.db import create_db_and_tables
from contextlib import asynccontextmanager
from app.settings import BOOTSTRAP_SERVER
from app.database.db import DATABASE_SESSION
from app.kafka.kafka import consume_messages


topic="product_topic"

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    await consume_messages(
        
        topic=topic,
        bootstrap_servers=BOOTSTRAP_SERVER,
        process_message=product_kafka_message,  # Custom processing function
        consumer_group_id="Product_consumer_group_id",
            )
    yield


app = FastAPI(
    title="Product Service",
    description="API for Products",
    version="1.0.0",
    lifespan=lifespan,
)




# Define a processing function to route messages based on action type
async def product_kafka_message(data):
    with Session as session:
        action = data.get("action")
        if action == "create":
            await handle_create_product(data,session)
        elif action == "update":
            await handle_update_product(data,session)
        else:
            logger.warning(f"Unknown action type: {action}")


# async def handle_create_product(data):
#     product_id = data["id"]  # Extract product ID
#     user_id = data["user_id"]  # Extract user ID
#     product_name = data["product_name"]  # Extract product name
#     product_description = data["product_description"]  # Extract description
#     stock = data["stock"]  # Extract initial stock

#     # Create the inventory record
#     inventory = InventoryModel(
#         product_id=UUID(product_id),  # Ensure product_id is a UUID
#         user_id=UUID(user_id),  # Ensure user_id is a UUID
#         product_name=product_name,
#         product_description=product_description,
#         stock=stock
#     )

#     with Session(engine) as session:
#         session.add(inventory)
#         session.commit()

#     logger.info(f"Inventory created for product {product_id} by user {user_id}: stock is {stock}")


# async def handle_update_product(data):
#     product_id = data["product_id"]  # Extract product ID
#     user_id = data["user_id"]  # Extract user ID
#     updated_fields = data["updated_fields"]  # Extract updated fields

#     with Session(engine) as session:
#         inventory = session.exec(select(InventoryModel).where(InventoryModel.product_id == UUID(product_id))).first()
#         if not inventory:
#             logger.error(f"Inventory for product {product_id} not found")
#             return

#         # Optionally check if user_id matches the owner
#         if inventory.user_id != UUID(user_id):
#             logger.error(f"User {user_id} is not authorized to update inventory for product {product_id}")
#             return

#         # Update the fields based on the updated_fields dictionary
#         for key, value in updated_fields.items():
#             if key == "stock":  # Handle stock updates specifically if needed
#                 inventory.stock = value  # Update stock

#         session.commit()
#         logger.info(f"Inventory updated for product {product_id} by user {user_id}: updated fields are {updated_fields}")




# async def handle_create_product(data: dict):
#     product_id = data["id"]  # Extract product ID
#     user_id = data["user_id"]  # Extract user ID
#     product_name = data["product_name"]  # Extract product name
#     product_description = data["product_description"]  # Extract description
#     stock = data["stock"]  # Extract initial stock

#     # Create the inventory record
#     inventory = InventoryModel(
#         product_id=UUID(product_id),  # Ensure product_id is a UUID
#         user_id=UUID(user_id),  # Ensure user_id is a UUID
#         product_name=product_name,
#         product_description=product_description,
#         stock=stock
#     )
#     con=session:DATABASE_SESSION
#     con.add(inventory)
#     con.commit()
#     logger.info(f"Inventory created for product {product_id} by user {user_id}: stock is {stock}")

# async def handle_update_product(data: dict):
#     product_id = data["product_id"]  # Extract product ID
#     user_id = data["user_id"]  # Extract user ID
#     updated_fields = data["updated_fields"]  # Extract updated fields

#     inventory = session.exec(select(InventoryModel).where(InventoryModel.product_id == UUID(product_id))).first()
#     if not inventory:
#         logger.error(f"Inventory for product {product_id} not found")
#         return

#     # Optionally check if user_id matches the owner
#     if inventory.user_id != UUID(user_id):
#         logger.error(f"User {user_id} is not authorized to update inventory for product {product_id}")
#         return

#     # Update the fields based on the updated_fields dictionary
#     for key, value in updated_fields.items():
#         if key == "stock":  # Handle stock updates specifically if needed
#             inventory.stock = value  # Update stock

#     con=session:DATABASE_SESSION
#     con.commit()
#     logger.info(f"Inventory updated for product {product_id} by user {user_id}: updated fields are {updated_fields}")

# @app.get("/")
# def home():
#     return "Inventory Service API Is Running"


# Correct the session usage inside the function by passing it through the parameter
async def handle_create_product(data: dict, session:DATABASE_SESSION):
    product_id = data["id"]  # Extract product ID
    user_id = data["user_id"]  # Extract user ID
    product_name = data["product_name"]  # Extract product name
    product_description = data["product_description"]  # Extract description
    stock = data["stock"]  # Extract initial stock

    # Create the inventory record
    inventory = InventoryModel(
        product_id=UUID(product_id),  # Ensure product_id is a UUID
        user_id=UUID(user_id),  # Ensure user_id is a UUID
        product_name=product_name,
        product_description=product_description,
        stock=stock
    )

    # Add and commit using the session
    session.add(inventory)
    session.commit()
    logger.info(f"Inventory created for product {product_id} by user {user_id}: stock is {stock}")


async def handle_update_product(data: dict, session: DATABASE_SESSION):
    product_id = data["product_id"]  # Extract product ID
    user_id = data["user_id"]  # Extract user ID
    updated_fields = data["updated_fields"]  # Extract updated fields

    # Select inventory record
    inventory = session.exec(select(InventoryModel).where(InventoryModel.product_id == UUID(product_id))).first()
    if not inventory:
        logger.error(f"Inventory for product {product_id} not found")
        return

    # Check if user_id matches the owner
    if inventory.user_id != UUID(user_id):
        logger.error(f"User {user_id} is not authorized to update inventory for product {product_id}")
        return

    # Update the fields based on the updated_fields dictionary
    for key, value in updated_fields.items():
        if key == "stock":
            inventory.stock = value

    session.commit()
    logger.info(f"Inventory updated for product {product_id} by user {user_id}: updated fields are {updated_fields}")

# Home route
@app.get("/")
def home():
    return "Inventory Service API Is Running"