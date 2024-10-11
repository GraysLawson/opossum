import logging
import os
import psycopg2

class DatabaseHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR(10),
                message TEXT
            )
        """)
        self.conn.commit()

    def emit(self, record):
        log_entry = self.format(record)
        self.cursor.execute(
            "INSERT INTO bot_logs (level, message) VALUES (%s, %s)",
            (record.levelname, log_entry)
        )
        self.conn.commit()

def setup_logger():
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # Database handler
    db_handler = DatabaseHandler()
    db_handler.setLevel(logging.DEBUG)
    db_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db_handler.setFormatter(db_format)

    logger.addHandler(console_handler)
    logger.addHandler(db_handler)

    return logger

logger = setup_logger()
