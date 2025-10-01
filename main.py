import logging
from config import Config
from database import Database
from bot_handler import TelegramBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    # Загрузка конфигурации
    config = Config()

    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return

    # Подключение к базе данных
    try:
        db = Database(config.DB_CONNECTION_STRING)
        db.connect()

        # Инициализация базы данных
        db.init_db()

        # Создание и запуск бота
        bot = TelegramBot(config.BOT_TOKEN, db)
        bot.run()

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()