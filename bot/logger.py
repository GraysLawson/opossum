import logging
import os
import psycopg2
import sys

class DatabaseHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        try:
            self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
            self.cursor = self.conn.cursor()
            print("Successfully connected to the database", file=sys.stderr)
            self.create_table()
        except Exception as e:
            print(f"Error connecting to database: {str(e)}", file=sys.stderr)
            raise

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level VARCHAR(10),
                    message TEXT
                )
            """)
            self.conn.commit()
            print("Successfully created or verified bot_logs table", file=sys.stderr)
        except Exception as e:
            print(f"Error creating table: {str(e)}", file=sys.stderr)
            raise

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.cursor.execute(
                "INSERT INTO bot_logs (level, message) VALUES (%s, %s)",
                (record.levelname, log_entry)
            )
            self.conn.commit()
            print(f"Successfully inserted log: {log_entry}", file=sys.stderr)
        except Exception as e:
            print(f"Error inserting log: {str(e)}", file=sys.stderr)
            self.handleError(record)

def setup_logger():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # Database handler
    try:
        db_handler = DatabaseHandler()
        db_handler.setLevel(logging.DEBUG)
        db_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        db_handler.setFormatter(db_format)
        logger.addHandler(db_handler)
        print("Successfully added DatabaseHandler to logger", file=sys.stderr)
    except Exception as e:
        print(f"Error setting up DatabaseHandler: {str(e)}", file=sys.stderr)

    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
print("Logger setup complete", file=sys.stderr)
