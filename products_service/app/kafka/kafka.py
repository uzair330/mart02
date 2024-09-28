from aiokafka import AIOKafkaProducer
import json
import logging
from contextlib import asynccontextmanager
from app.settings import BOOTSTRAP_SERVER  # Assuming you have a settings module for configuration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define an async context manager for the Kafka producer
@asynccontextmanager
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
        
#--------------------------------------------------------------------------
# Kafka message producer function
#--------------------------------------------------------------------------

async def kafka_producer(kafka_topic: str, message: dict):
    # Get producer instance using context manager
    async with get_kafka_producer() as producer:
        try:
            # Convert message to JSON and encode it
            await producer.send_and_wait(kafka_topic, json.dumps(message).encode("utf-8"))
            logger.info(f"Produced message to topic {kafka_topic}: {message}")
            return f"Kafka produced message with topic {kafka_topic} and message {message}"
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {str(e)}")
            raise

#--------------------------------------------------------------------------
#kafka consumer message function
#--------------------------------------------------------------------------

async def consume_messages(
    topic: str, 
    bootstrap_servers: str, 
    process_message: callable,  # A callback function to process each message
    consumer_group_id: str
):
    while True:
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
                    # Decode and process the message using the callback
                    data = json.loads(message.value.decode())
                    await process_message(data)  # Process each message with the custom handler
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"Error connecting to Kafka broker: {e}")
        finally:
            logger.info("Stopping consumer")
            await consumer.stop()
            await asyncio.sleep(10)  # Wait before reconnecting