import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME', 'telegram_bot_db')

    @property
    def DB_CONNECTION_STRING(self):
        return f"dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASSWORD} host={self.DB_HOST} port={self.DB_PORT}"