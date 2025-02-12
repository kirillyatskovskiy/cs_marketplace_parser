import os
import requests
import time
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


# Настроим базовое логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "cs2_steam_marketplace"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432)
}

# Настройки базы данных PostgreSQL из переменных окружения
DB_URL = db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# Создание базового класса для SQLAlchemy
Base = declarative_base()

# Определение модели для таблицы cs2_market
class Cs2Market(Base):
    __tablename__ = 'cs2_steam_marketplace' # SELECT COUNT(*) FROM cs2_steam_marketplace;

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    hash_name = Column(Text)
    sell_listings = Column(Integer)
    sell_price = Column(Integer)
    sell_price_text = Column(Text)
    app_icon = Column(Text)
    app_name = Column(Text)
    appid = Column(Integer)
    classid = Column(Text)
    instanceid = Column(Text)
    icon_url = Column(Text)
    tradable = Column(Integer)
    item_name = Column(Text)
    name_color = Column(Text)
    item_type = Column(Text)
    market_name = Column(Text)
    market_hash_name = Column(Text)
    commodity = Column(Integer)
    sale_price_text = Column(Text)

    __table_args__ = (
        UniqueConstraint('appid', 'classid', 'instanceid', 'market_hash_name', name='_unique_item'),
    )

# Создание подключения к базе данных
engine = create_engine(DB_URL, poolclass=NullPool)

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)

# Создание таблицы в базе данных
def create_table():
    Base.metadata.create_all(engine)

# Функция для вставки данных в базу
def insert_item(data):
    session = Session()
    try:
        item = Cs2Market(
            name=data["name"],
            hash_name=data["hash_name"],
            sell_listings=data["sell_listings"],
            sell_price=data["sell_price"],
            sell_price_text=data["sell_price_text"],
            app_icon=data["app_icon"],
            app_name=data["app_name"],
            appid=data["appid"],
            classid=data["classid"],
            instanceid=data["instanceid"],
            icon_url=data["icon_url"],
            tradable=data["tradable"],
            item_name=data["item_name"],
            name_color=data["name_color"],
            item_type=data["item_type"],
            market_name=data["market_name"],
            market_hash_name=data["market_hash_name"],
            commodity=data["commodity"],
            sale_price_text=data["sale_price_text"]
        )
        session.add(item)
        session.commit()
        logger.info(f"Item '{data['name']}' successfully inserted into database.")
    except IntegrityError:
        session.rollback()  # Откатываем транзакцию, если ошибка уникальности
        logger.warning(f"Duplicate item '{data['name']}' found. Skipping insertion.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error inserting item '{data['name']}': {e}")
    finally:
        session.close()

# Получение количества предметов на рынке
def get_total_items():
    url = "https://steamcommunity.com/market/search/render/"
    params = {
        "query": "",
        "start": 0,
        "count": 1,
        "search_descriptions": 0,
        "sort_column": "price",
        "sort_dir": "desc",
        "appid": 730,
        "norender": 1,
        "l": "english"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("total_count", 0)

# Функция для парсинга одного запроса
def fetch_items(start, step, retries=0):
    url = "https://steamcommunity.com/market/search/render/"
    params = {
        "query": "",
        "start": start,
        "count": step,
        "search_descriptions": 1,
        "sort_column": "price",
        "sort_dir": "desc",
        "appid": 730,
        "norender": 1,
        "l": "english"
    }

    try:
        logger.info(f"Fetching items from {start} to {start + step}...")

        response = requests.get(url, params=params, timeout=10)

        # Если ошибка 429 (слишком много запросов), применяем фиксированную задержку
        if response.status_code == 429:
            # Фиксированная задержка в 15 секунд
            logger.warning(f"Rate limit exceeded. Retrying after 15 seconds...")
            time.sleep(15)  # Ожидаем 15 секунд перед повтором запроса

            # Повторяем запрос
            return fetch_items(start, step, retries + 1)

        response.raise_for_status()  # Выбрасываем исключение для других ошибок статуса
        data = response.json()
        return data.get("results", [])

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return []

# Основная функция для парсинга всех предметов
def parse_market():
    create_table()
    total_items = get_total_items()
    logger.info(f"Total items on the market: {total_items}")
    
    step = 100  # Request 100 items per batch
    futures = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:  # Указываем количество потоков
        for start in range(0, total_items, step):
            futures.append(executor.submit(fetch_items, start, step))

        for future in as_completed(futures):
            items = future.result()
            for item in items:
                item_data = {
                    "name": item.get("name", "Unknown"),
                    "hash_name": item.get("hash_name", "Unknown"),
                    "sell_listings": item.get("sell_listings", 0),
                    "sell_price": item.get("sell_price", 0),
                    "sell_price_text": item.get("sell_price_text", "N/A"),
                    "app_icon": item.get("app_icon", ""),
                    "app_name": item.get("app_name", "Unknown"),
                    "appid": item.get("asset_description", {}).get("appid", 0),
                    "classid": item.get("asset_description", {}).get("classid", ""),
                    "instanceid": item.get("asset_description", {}).get("instanceid", ""),
                    "icon_url": item.get("asset_description", {}).get("icon_url", ""),
                    "tradable": item.get("asset_description", {}).get("tradable", 0),
                    "item_name": item.get("asset_description", {}).get("name", "Unknown"),
                    "name_color": item.get("asset_description", {}).get("name_color", ""),
                    "item_type": item.get("asset_description", {}).get("type", ""),
                    "market_name": item.get("asset_description", {}).get("market_name", ""),
                    "market_hash_name": item.get("asset_description", {}).get("market_hash_name", ""),
                    "commodity": item.get("asset_description", {}).get("commodity", 0),
                    "sale_price_text": item.get("sale_price_text", "N/A")
                }
                insert_item(item_data)
    
    logger.info(f"Completed loading all items.")

if __name__ == "__main__":
    parse_market()
