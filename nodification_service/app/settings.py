

from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

# Settings for Kafka, email, and database
DATABASE_URL = config("DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_NODIFICATION_TOPIC = config("KAFKA_NODIFICATION_TOPIC", cast=str)
KAFKA_SIGNUP_TOPIC = config("KAFKA_SIGNUP_TOPIC", cast=str)
KAFKA_TOPIC = config("KAFKA_TOPIC", default="auth-user")
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_INVENTORY_TOPIC=config("KAFKA_INVENTORY_TOPIC", cast=str)



# FastAPI Mail configuration
MAIL_USERNAME = config("MAIL_USERNAME", cast=str)
MAIL_PASSWORD = config("MAIL_PASSWORD", cast=str)

# Consumer Group IDs
KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION = config("KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION", cast=str, default="Group_Id_Notification")
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY="inventory"