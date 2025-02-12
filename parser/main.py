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
            price INTEGER,
            price_text TEXT,
            image_url TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Функция для вставки данных в базу
def insert_item(name, price, price_text, image_url):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cs2_market (name, price, price_text, image_url)
        VALUES (%s, %s, %s, %s)
    """, (name, price, price_text, image_url))
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
            name = item.get("name", "Unknown")
            price = item.get("sell_price", 0)
            price_text = item.get("sell_price_text", "N/A")
            image_url = f"https://community.akamai.steamstatic.com/economy/image/{item.get('asset_description', {}).get('icon_url', '')}"
            insert_item(name, price, price_text, image_url)
        
        print(f"Загружено {start + len(results)} из {total_items} предметов")
        time.sleep(2)  # Пауза, чтобы избежать блокировки Steam API

if __name__ == "__main__":
    parse_market()
