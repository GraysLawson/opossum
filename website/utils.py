import redis
import os
from config import discord

def get_redis_connection():
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        raise ValueError("REDIS_URL environment variable is not set")
    return redis.from_url(redis_url)

# Other utility functions...