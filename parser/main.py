import os
import requests
import psycopg2
import time

# Настройки базы данных PostgreSQL из переменных окружения
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "cs2_steam_marketplace"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432)
}

# Функция для создания таблицы в PostgreSQL
def create_table():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cs2_market (
            id SERIAL PRIMARY KEY,
            name TEXT,
            hash_name TEXT,
            sell_listings INTEGER,
            sell_price INTEGER,
            sell_price_text TEXT,
            app_icon TEXT,
            app_name TEXT,
            appid INTEGER,
            classid TEXT,
            instanceid TEXT,
            icon_url TEXT,
            tradable INTEGER,
            item_name TEXT,
            name_color TEXT,
            item_type TEXT,
            market_name TEXT,
            market_hash_name TEXT,
            commodity INTEGER,
            sale_price_text TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Функция для вставки данных в базу
def insert_item(data):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cs2_market (name, hash_name, sell_listings, sell_price, sell_price_text, app_icon, app_name,
                                appid, classid, instanceid, icon_url, tradable, item_name, name_color, item_type, 
                                market_name, market_hash_name, commodity, sale_price_text)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["name"], data["hash_name"], data["sell_listings"], data["sell_price"], data["sell_price_text"],
        data["app_icon"], data["app_name"], data["appid"], data["classid"], data["instanceid"], 
        data["icon_url"], data["tradable"], data["item_name"], data["name_color"], data["item_type"], 
        data["market_name"], data["market_hash_name"], data["commodity"], data["sale_price_text"]
    ))
    conn.commit()
    cursor.close()
    conn.close()

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

# Функция для парсинга всех предметов
def parse_market():
    create_table()
    total_items = get_total_items()
    print(f"Всего предметов: {total_items}")
    
    url = "https://steamcommunity.com/market/search/render/"
    step = 100  # Запрашиваем по 100 предметов
    
    for start in range(0, total_items, step):
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
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Ошибка запроса: {response.status_code}")
            time.sleep(5)  # Ожидание перед повтором
            continue
        
        data = response.json()
        results = data.get("results", [])
        
        for item in results:
            # Извлечение данных из ответа
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
            
            # Вставка данных в базу
            insert_item(item_data)
        
        print(f"Loaded {start + len(results)} of {total_items} items")
        time.sleep(2)  # Пауза, чтобы избежать блокировки Steam API

if __name__ == "__main__":
    parse_market()
