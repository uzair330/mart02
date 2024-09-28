from datetime import timedelta
from starlette.config import Config
from starlette.datastructures import Secret

try:
    env = Config(".env")
except FileNotFoundError:
    env = Config()

DATABASE_URL = env("DATABASE_URL", cast=Secret)
ALGORITHM = env("ALGORITHM", cast=str)
SECRET_KEY = env("SECRET_KEY", cast=Secret)
TOKEN_EXPIRE_MINUTES = timedelta(
    minutes=int(env.get("TOKEN_EXPIRE_MINUTES"))
)