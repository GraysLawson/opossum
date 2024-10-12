import logging
import os
import redis
import sys
import json
import time

class RedisHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        try:
            self.redis_client = redis.Redis.from_url(os.environ['REDIS_URL'])
            print("Successfully connected to Redis", file=sys.stderr)
        except Exception as e:
            print(f"Error connecting to Redis: {str(e)}", file=sys.stderr)
            raise

    def emit(self, record):
        log_entry = self.format(record)
        try:
            log_data = {
                'timestamp': int(time.time() * 1000),  # Use milliseconds for easier ordering
                'level': record.levelname,
                'message': log_entry
            }
            self.redis_client.lpush('bot_logs', json.dumps(log_data))
            self.redis_client.ltrim('bot_logs', 0, 999)  # Keep only the last 1000 logs
        except Exception as e:
            print(f"Error inserting log: {str(e)}", file=sys.stderr)
            self.handleError(record)

def setup_logger():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)

    # Check if we're in production (REDIS_URL is set)
    if os.environ.get('REDIS_URL'):
        # Production: Use only Redis handler
        try:
            redis_handler = RedisHandler()
            redis_handler.setLevel(logging.DEBUG)
            redis_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            redis_handler.setFormatter(redis_format)
            logger.addHandler(redis_handler)
            print("Successfully added RedisHandler to logger", file=sys.stderr)
        except Exception as e:
            print(f"Error setting up RedisHandler: {str(e)}", file=sys.stderr)
    else:
        # Development: Use only console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
print("Logger setup complete", file=sys.stderr)
