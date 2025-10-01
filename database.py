import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def execute_query(self, query, params=None):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().lower().startswith('select'):
                    return cursor.fetchall()
                else:
                    self.conn.commit()
                    return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query execution error: {e}")
            raise

    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            # Создание таблицы категорий
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE
                )
            ''')

            # Создание таблицы контактов
            self.execute_query('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    category_id INTEGER REFERENCES categories(id),
                    number VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
            ''')

            # Добавление тестовых данных
            self.execute_query('''
                INSERT INTO categories (name) 
                VALUES 
                    ('Строительство'),
                    ('Ремонт техники'),
                    ('Водоснабжение'),
                    ('Откачка/Септики'),
                    ('Электрика'),
                    ('Уничтожение насекомых'),
                    ('Строительные материалы'),
                    ('Работы по участку'),
                    ('Услуги'),
                    ('Еда'),
                    ('Ручная работа')
                ON CONFLICT (name) DO NOTHING
            ''')



            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise


class CategoryRepository:
    def __init__(self, db):
        self.db = db

    def get_all_categories(self):
        query = "SELECT id, name FROM categories ORDER BY name"
        return self.db.execute_query(query)

    def get_category_by_id(self, category_id):
        query = "SELECT id, name FROM categories WHERE id = %s"
        return self.db.execute_query(query, (category_id,))


class ContactRepository:
    def __init__(self, db):
        self.db = db

    def get_contacts_by_category(self, category_id):
        query = '''
            SELECT id, category_id, number, name, is_deleted 
            FROM contacts 
            WHERE category_id = %s AND is_deleted = false 
            ORDER BY name
        '''
        return self.db.execute_query(query, (category_id,))

    def get_contact_by_id(self, contact_id):
        query = "SELECT * FROM contacts WHERE id = %s AND is_deleted = false"
        return self.db.execute_query(query, (contact_id,))