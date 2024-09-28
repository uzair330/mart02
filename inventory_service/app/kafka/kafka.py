# kafka.py
from aiokafka import AIOKafkaConsumer
from sqlmodel import Session, select
from app.database.db import get_session  # Import the session generator function directly
from app.models.inventory_model import InventoryModel
from uuid import UUID
import json
import logging
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to consume Kafka messages
async def consume_messages(topic: str, bootstrap_servers: str, consumer_group_id: str):
    consumer = None

    try:
        # Initialize Kafka consumer
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group_id,
            auto_offset_reset='earliest'
        )

        await consumer.start()
        logger.info(f"Consumer started successfully on topic {topic}")

        # Consume messages from the topic
        async for message in consumer:
            try:
                # Decode the message
                data = json.loads(message.value.decode())

                # Process the message based on action type
                await product_kafka_message(data)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    except Exception as e:
        logger.error(f"Error connecting to Kafka broker: {e}")
    finally:
        if consumer:
            logger.info("Stopping consumer")
            await consumer.stop()
        await asyncio.sleep(10)  # Wait before reconnecting

# Function to process Kafka messages based on the action type
async def product_kafka_message(data: dict):
    # Manually resolve the session using the context manager from get_session
    session_generator = get_session()  # This gets the generator
    session = next(session_generator)  # Get the actual session object

    try:
        action = data.get("action")
        if action == "create":
            await handle_create_product(data, session)
        elif action == "update":
            await handle_update_product(data, session)
        else:
            logger.warning(f"Unknown action type: {action}")
    finally:
        session.close()  # Ensure the session is closed after processing

# Function to handle product creation
async def handle_create_product(data: dict, session: Session):
    try:
        # Extract data fields
        product_id = data["id"]
        user_id = data["user_id"]
        product_name = data["product_name"]
        product_description = data["product_description"]
        stock = data["stock"]

        # Create the inventory record
        inventory = InventoryModel(
            product_id=UUID(product_id),
            user_id=UUID(user_id),
            product_name=product_name,
            product_description=product_description,
            stock=stock,
        )

        # Add and commit the session
        session.add(inventory)
        session.commit()
        logger.info(f"Inventory created for product {product_id} by user {user_id}: stock is {stock}")
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        session.rollback()  # Rollback the session on error

# Function to handle product updates
async def handle_update_product(data: dict, session: Session):
    try:
        # Extract data fields
        product_id = data["product_id"]
        user_id = data["user_id"]
        updated_fields = data["updated_fields"]

        # Fetch the inventory record
        inventory = session.exec(
            select(InventoryModel).where(InventoryModel.product_id == UUID(product_id))
        ).first()

        if not inventory:
            logger.error(f"Inventory for product {product_id} not found")
            return

        # Authorization check
        if inventory.user_id != UUID(user_id):
            logger.error(f"User {user_id} is not authorized to update inventory for product {product_id}")
            return

        # Update inventory fields
        for key, value in updated_fields.items():
            if key == "stock":
                inventory.stock = value

        # Commit the session
        session.commit()
        logger.info(f"Inventory updated for product {product_id} by user {user_id}: updated fields are {updated_fields}")
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        session.rollback()  # Rollback the session on error

