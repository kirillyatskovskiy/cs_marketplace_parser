from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app_cfg import MODE, DB_CONFIG
from utils import logger
from models import create_item, Cs2Market, Base
import traceback

# Настройки базы данных PostgreSQL из переменных окружения
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

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
                        existing_item.sell_price_text = data["sell_price_text"]
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