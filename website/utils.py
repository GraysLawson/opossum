import redis
import os

REDIS_URL = os.getenv('REDIS_URL')

if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is not set")

def get_redis_connection():
    return redis.Redis.from_url(REDIS_URL)

# Import discord from app to avoid circular imports
from app import discord

