from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from main import MODE
from utils import logger
from models import create_item, Cs2Market
import traceback

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "cs2_steam_marketplace"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432)
}

# Настройки базы данных PostgreSQL из переменных окружения
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# Создание базового класса для SQLAlchemy
Base = declarative_base()

# Создание подключения к базе данных
engine = create_engine(DB_URL, poolclass=NullPool)

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)

# Создание таблицы в базе данных
def create_table():
    Base.metadata.create_all(engine)

# Функция для вставки данных в базу
def insert_item(data):
    with Session() as session:
        try:
            if MODE == 'full':
                session.add(create_item(data))
                logger.info(f"Item '{data['name']}' successfully inserted into database.")
            elif MODE == 'update':
                existing_item = session.query(Cs2Market).filter_by(hash_name=data["hash_name"]).first()
                if existing_item:
                    # Проверка, если цена на товар изменилась, обновляем только если новая цена ниже
                    if data["sell_price"] is not None and data["sell_price"] < existing_item.sell_price:
                        existing_item.sell_price = data["sell_price"]
                        existing_item.sale_price_text = data["sale_price_text"]
                        logger.info(f"Item '{data['name']}' price updated in database.")
                    else:
                        logger.info(f"Item '{data['name']}' price remains unchanged.")
                else: 
                    session.add(create_item(data))
                    logger.info(f"Item '{data['name']}' successfully inserted into database.")
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing item '{data['name']}': {e}\n{traceback.format_exc()}")