
# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from aiokafka import AIOKafkaConsumer
# import smtplib
# from email.message import EmailMessage
# import asyncio
# import json
# import logging
# from typing import AsyncGenerator
# from sqlmodel import Field, Session, SQLModel, create_engine, select
# from typing import Optional
# from starlette.config import Config
# from starlette.datastructures import Secret
# from app import settings

# # Logging configuration
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Database setup
# connection_string = str(settings.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
# engine = create_engine(connection_string, connect_args={}, pool_recycle=300)

# class Product(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     description: str = Field(default="")
#     price: float
    

# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

# # Function to send email using smtplib
# def send_email(subject: str, body: str, to_email: str):
#     from_email = settings.MAIL_USERNAME
#     password = settings.MAIL_PASSWORD
    
#     # Create the email
#     msg = EmailMessage()
#     msg.set_content(body)
#     msg['Subject'] = subject
#     msg['From'] = from_email
#     msg['To'] = to_email

#     # Send the email using SMTP_SSL
#     try:
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Use SMTP_SSL for secure connection
#             server.login(from_email, password)
#             server.send_message(msg)
#         logger.info(f"Email sent successfully to {to_email}")
#     except Exception as e:
#         logger.error(f"Failed to send email to {to_email}: {e}")

# # Kafka Consumer for auth-user topic (notification service)
# async def consume_auth_user_messages():
#     while True:
#         try:
#             consumer = AIOKafkaConsumer(
#                 settings.KAFKA_TOPIC,  # Topic to consume
#                 bootstrap_servers=settings.BOOTSTRAP_SERVER,
#                 group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION,  # Consumer group ID
#                 auto_offset_reset='earliest'
#             )
#             await consumer.start()
#             try:
#                 async for message in consumer:
#                     data = json.loads(message.value.decode("utf-8"))
#                     logger.info(f"Received data: {data}")

#                     event_type = data.get("type")
#                     email = data.get("email")
#                     token = data.get("token")

#                     if event_type == "signup":
#                         if not email or not token:
#                             logger.error("Missing email or token in signup data")
#                             continue
                        
#                         # Send the signup confirmation email
#                         subject = "Welcome! Your Signup is Successful"
#                         body = f"Hello, your account has been successfully created."
#                         send_email(subject, body, email)

#                     elif event_type == "password_reset":
#                         if not email or not token:
#                             logger.error("Missing email or token in password reset data")
#                             continue
                        
#                         # Send the password reset email
#                         subject = "Password Reset Request"
#                         body = (
#                             f"Hi, to reset your password.\n"
#                             f"Here is your access token (valid for 5 minutes):\n"
#                             f"-------------------Access Token-----------------------\n"
#                             f"{token}\n"
#                             f"--------------------------------------------------------\n"
#                             f"Note: Kindly paste this token and your new password in the reset password endpoint."
#                         )
#                         send_email(subject, body, email)

#             finally:
#                 await consumer.stop()
#         except Exception as e:
#             logger.error(f"Error in Kafka consumer loop: {e}")
#             await asyncio.sleep(5)

# # Kafka Consumer for product management
# async def consume_product_messages():
#     while True:
#         try:
#             consumer = AIOKafkaConsumer(
#                 settings.KAFKA_PRODUCT_TOPIC,  # Topic to consume
#                 bootstrap_servers=settings.BOOTSTRAP_SERVER,
#                 group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
#                 auto_offset_reset='earliest'
#             )
#             await consumer.start()
#             logger.info("Product Consumer started successfully")
#             # 
#             try:
#                 async for message in consumer:
#                     data = json.loads(message.value.decode("utf-8"))
#                     action = data.get("action")
#                     product = data.get("product")
#                     product_id = data.get("product_id")
#                     email=data.get("email")

#                     if action == "create":
#                         subject = "Product Created"
#                         body = f"A new product has been created: {product['name']}."
#                         send_email(subject, body, email)

#                     elif action == "update":
#                         subject = "Product Updated"
#                         body = f"Product ID {product_id} has been updated."
#                         send_email(subject, body, email)

#                     elif action == "delete":
#                         subject = "Product Deleted"
#                         body = f"Product ID {product_id} has been deleted."
#                         send_email(subject, body, email)

                    
                    
#             # 
#             finally:
#                 await consumer.stop()
#         except Exception as e:
#             logger.error(f"Error in Kafka product consumer loop: {e}")
#         finally:
#             await asyncio.sleep(5)

# # Lifespan function to manage both consumers
# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator:
#     task1 = asyncio.create_task(consume_auth_user_messages())
#     task2 = asyncio.create_task(consume_product_messages())
#     try:
#         yield
#     finally:
#         task1.cancel()
#         task2.cancel()
#         await task1
#         await task2


# # Define base URL and ports for each service
# BASE_URL = "http://139.59.90.137"

# PORTS = {
#     "inventory_service": 8007,
#     "user_service": 8004,
#     "product_service": 8005,
#     "notification_service": 8006,
#     "order_service": 8008
# }

# # Create FastAPI applications for each service
# app = FastAPI(
#     lifespan=lifespan,
#     title="Nodification Service",
#     version="0.0.1",
#     servers=[
#         {
#             "url": f"{BASE_URL}:{PORTS['notification_service']}",
#             "description": "Nodification Service on DigitalOcean"
#         }
#     ]
# )

# @app.get("/")
# def read_root():
#     return {"message": "Nodification Service"}

from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
import smtplib
from email.message import EmailMessage
import asyncio
import json
import logging
from typing import AsyncGenerator
from app import settings

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to send email using smtplib
def send_email(subject: str, body: str, to_email: str):
    from_email = settings.MAIL_USERNAME
    password = settings.MAIL_PASSWORD
    
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")


# Kafka Consumer for user-related events (User Signup, Password Reset)
async def consume_user_messages():
    while True:  # Continuous loop to restart consumer in case of failure
        try:
            consumer = AIOKafkaConsumer(
                settings.KAFKA_TOPIC,  # User topic
                bootstrap_servers="broker:19092",
                group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION,
                auto_offset_reset='earliest'
            )
            await consumer.start()
            logger.info("User Kafka consumer started successfully")

            async for message in consumer:
                try:
                    data = json.loads(message.value.decode("utf-8"))
                    logger.info(f"Received data: {data}")
                    event_type = data.get("type")
                    email = data.get("email")
                    token = data.get("token")

                    if event_type == "signup":
                        if not email or not token:
                            logger.error("Missing email or token in signup data")
                            continue
                        subject = "Welcome! Your Signup is Successful"
                        body = "Hello, your account has been successfully created."
                        send_email(subject, body, email)

                    elif event_type == "password_reset":
                        if not email or not token:
                            logger.error("Missing email or token in password reset data")
                            continue
                        subject = "Password Reset Request"
                        body = (
                            f"Hi, to reset your password.\n"
                            f"Here is your access token (valid for 5 minutes):\n"
                            f"{token}\n"
                            f"Note: Paste this token and your new password in the reset password endpoint."
                        )
                        send_email(subject, body, email)

                except Exception as e:
                    logger.error(f"Error processing user message: {e}")

        except Exception as e:
            logger.error(f"Error connecting to Kafka broker: {e}")

        finally:
            logger.info("Stopping user Kafka consumer")
            await consumer.stop()
            await asyncio.sleep(10)  # Sleep before retrying


# Kafka Consumer for product-related events
# async def consume_product_messages():
#     while True:  # Continuous loop to restart consumer in case of failure
#         try:
#             consumer = AIOKafkaConsumer(
#                 settings.KAFKA_PRODUCT_TOPIC,  # Product topic
#                 bootstrap_servers=settings.BOOTSTRAP_SERVER,
#                 group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
#                 auto_offset_reset='earliest'
#             )
#             await consumer.start()
#             logger.info("Product Kafka consumer started successfully")

#             async for message in consumer:
#                 try:
#                     data = json.loads(message.value.decode("utf-8"))
#                     action = data.get("action")
#                     product = data.get("product")
#                     product_id = data.get("product_id")
#                     email = data.get("email")

#                     if action == "create":
#                         subject = "Product Created"
#                         body = f"A new product has been created: {product['name']}."
#                         send_email(subject, body, email)

#                     elif action == "update":
#                         subject = "Product Updated"
#                         body = f"Product ID {product_id} has been updated."
#                         send_email(subject, body, email)

#                     elif action == "delete":
#                         subject = "Product Deleted"
#                         body = f"Product ID {product_id} has been deleted."
#                         send_email(subject, body, email)

#                     elif action == "password_reset":
#                         reset_link = data.get("reset_link")
#                         send_email("Password Reset", "Password reset successfully.", email)

#                     elif action == "password_update":
#                         send_email("Password Updated", "Your password has been updated successfully.", email)

#                 except Exception as e:
#                     logger.error(f"Error processing product message: {e}")

#         except Exception as e:
#             logger.error(f"Error connecting to Kafka broker: {e}")

#         finally:
#             logger.info("Stopping product Kafka consumer")
#             await consumer.stop()
#             await asyncio.sleep(10)  # Sleep before retrying

async def consume_product_messages():
    while True:  # Continuous loop to restart consumer in case of failure
        try:
            # Create Kafka consumer for product-related events
            consumer = AIOKafkaConsumer(
                settings.KAFKA_PRODUCT_TOPIC,  # Product topic
                bootstrap_servers=settings.BOOTSTRAP_SERVER,
                group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
                auto_offset_reset='earliest'
            )
            await consumer.start()
            logger.info("Product Kafka consumer started successfully")

            # Consume messages from Kafka topic
            async for message in consumer:
                try:
                    # Decode and parse the Kafka message
                    data = json.loads(message.value.decode("utf-8"))
                    logger.info(f"Received Kafka message: {data}")

                    # Validate the message structure
                    action = data.get("action")
                    product = data.get("product", {})  # Use empty dict if product is missing
                    product_id = data.get("product_id")
                    email = data.get("email")

                    # Ensure action, product_id, and email are present
                    if not action or not product_id or not email:
                        logger.error(f"Missing required fields in message: {data}")
                        continue

                    # Handle different actions
                    if action == "create":
                        subject = "Product Created"
                        body = f"A new product has been created: {product.get('name', 'Unknown')}."
                        send_email(subject, body, email)

                    elif action == "update":
                        subject = "Product Updated"
                        body = f"Product ID {product_id} has been updated."
                        send_email(subject, body, email)

                    elif action == "delete":
                        subject = "Product Deleted"
                        body = f"Product ID {product_id} has been deleted."
                        send_email(subject, body, email)

                    elif action == "password_reset":
                        reset_link = data.get("reset_link")
                        if reset_link:
                            send_email("Password Reset", f"Password reset successfully.\nLink: {reset_link}", email)
                        else:
                            logger.error(f"Missing reset link in password_reset message: {data}")

                    elif action == "password_update":
                        send_email("Password Updated", "Your password has been updated successfully.", email)

                    else:
                        logger.error(f"Unknown action '{action}' in message: {data}")

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode Kafka message: {message.value}")
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")

        except Exception as e:
            logger.error(f"Error connecting to Kafka broker: {e}")

        finally:
            logger.info("Stopping Product Kafka consumer")
            await consumer.stop()  # Stop the consumer gracefully
            await asyncio.sleep(10)  # Sleep before retrying the connection




# Kafka Consumer for order-related events
async def consume_order_messages():
    while True:  # Continuous loop to restart consumer in case of failure
        try:
            consumer = AIOKafkaConsumer(
                settings.KAFKA_ORDER_TOPIC,  # Order topic
                bootstrap_servers=settings.BOOTSTRAP_SERVER,
                group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION,
                auto_offset_reset='earliest'
            )
            await consumer.start()
            logger.info("Order Kafka consumer started successfully")

            async for message in consumer:
                try:
                    data = json.loads(message.value.decode("utf-8"))
                    action = data.get("action")
                    order_id = data.get("order_id")
                    email = data.get("email")

                    if action == "order_created":
                        subject = f"Order {order_id} Created Successfully"
                        body = f"Your order {order_id} has been successfully created and is being processed."
                        send_email(subject, body, email)

                except Exception as e:
                    logger.error(f"Error processing order message: {e}")

        except Exception as e:
            logger.error(f"Error connecting to Kafka broker: {e}")

        finally:
            logger.info("Stopping order Kafka consumer")
            await consumer.stop()
            await asyncio.sleep(10)  # Sleep before retrying


# Kafka Consumer for inventory-related events (e.g., Low Stock Alerts)
async def consume_inventory_messages():
    while True:  # Continuous loop to restart consumer in case of failure
        try:
            consumer = AIOKafkaConsumer(
                settings.KAFKA_INVENTORY_TOPIC,  # Inventory topic
                bootstrap_servers=settings.BOOTSTRAP_SERVER,
                group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY,
                auto_offset_reset='earliest'
            )
            await consumer.start()
            logger.info("Inventory Kafka consumer started successfully")

            async for message in consumer:
                try:
                    data = json.loads(message.value.decode("utf-8"))
                    action = data.get("action")
                    product_id = data.get("product_id")
                    email = data.get("email")

                    if action == "low_stock":
                        subject = f"Low Stock Alert for Product {product_id}"
                        body = f"Warning: Product {product_id} is running low on stock."
                        send_email(subject, body, email)

                except Exception as e:
                    logger.error(f"Error processing inventory message: {e}")

        except Exception as e:
            logger.error(f"Error connecting to Kafka broker: {e}")

        finally:
            logger.info("Stopping inventory Kafka consumer")
            await consumer.stop()
            await asyncio.sleep(10)  # Sleep before retrying




# Lifespan function to manage all consumers
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    task_user = asyncio.create_task(consume_user_messages())
    task_product = asyncio.create_task(consume_product_messages())
    task_order = asyncio.create_task(consume_order_messages())
    task_inventory = asyncio.create_task(consume_inventory_messages())
    
    try:
        yield
    finally:
        task_user.cancel()
        task_product.cancel()
        task_order.cancel()
        task_inventory.cancel()
        await task_user
        await task_product
        await task_order
        await task_inventory

# Define base URL and ports for each service
BASE_URL = "http://139.59.90.137"

PORTS = {
    "inventory_service": 8007,
    "user_service": 8004,
    "product_service": 8005,
    "notification_service": 8006,
    "order_service": 8008
}

# FastAPI app setup
app = FastAPI(
    lifespan=lifespan,
    title="Notification Service",
    version="0.0.1",
    servers=[
        {
            "url": f"{BASE_URL}:{PORTS['notification_service']}",
            "description": "Notification Service on DigitalOcean"
        }
    ]
)

@app.get("/")
def read_root():
    return {"message": "Notification Service"}
