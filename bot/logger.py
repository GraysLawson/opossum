import logging
import os
import redis
import sys
import json

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
                'timestamp': record.created,
                'level': record.levelname,
                'message': log_entry
            }
            self.redis_client.lpush('bot_logs', json.dumps(log_data))
            print(f"Successfully inserted log: {log_entry}", file=sys.stderr)
        except Exception as e:
            print(f"Error inserting log: {str(e)}", file=sys.stderr)
            self.handleError(record)

def setup_logger():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)

    # Always add console handler for local development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Only add Redis handler if REDIS_URL is set (production environment)
    if os.environ.get('REDIS_URL'):
        try:
            redis_handler = RedisHandler()
            redis_handler.setLevel(logging.DEBUG)
            redis_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            redis_handler.setFormatter(redis_format)
            logger.addHandler(redis_handler)
            print("Successfully added RedisHandler to logger", file=sys.stderr)
        except Exception as e:
            print(f"Error setting up RedisHandler: {str(e)}", file=sys.stderr)

    return logger

logger = setup_logger()
print("Logger setup complete", file=sys.stderr)
