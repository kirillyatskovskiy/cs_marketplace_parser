from cfg import MODE
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

# Создание базового класса для SQLAlchemy
Base = declarative_base() # если тут ошибка кругового импорта, то заменить импорт в databse.py с Base на Cs2Market и использовать вместо Base

# Определение модели для таблицы cs2_market

if MODE == 'full':
    hash_name_column = Column(Text, nullable=False)

elif MODE == 'update':
    hash_name_column = Column(Text, nullable=False, unique=True)

class Cs2Market(Base):
    __tablename__ = 'cs_steam_marketplace'  # SELECT COUNT(*) FROM cs_steam_marketplace;

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    hash_name = hash_name_column
    sell_listings = Column(Integer)
    sell_price = Column(Integer)  # Цена в целых числах
    sell_price_text = Column(Text)
    app_icon = Column(Text)
    app_name = Column(Text)
    appid = Column(Integer)
    classid = Column(Text)
    instanceid = Column(Text)
    icon_url = Column(Text)
    tradable = Column(Integer)  # 0 или 1
    item_name = Column(Text)
    name_color = Column(Text)
    item_type = Column(Text)
    market_name = Column(Text)
    market_hash_name = Column(Text)
    commodity = Column(Integer)  # 0 или 1
    sale_price_text = Column(Text)

def create_item(data):
    return Cs2Market(
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