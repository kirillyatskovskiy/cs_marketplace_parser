from utils import logger
from database import create_table, insert_item
from fetcher import get_total_items, fetch_items
from concurrent.futures import ThreadPoolExecutor, as_completed
from cfg import MODE

logger.info(f"Running in {MODE.upper()} mode...")

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
            try:
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
            except Exception as e:
                logger.error(f"Error processing future result: {e}")
    
    logger.info(f"Completed loading all items.")


if __name__ == "__main__":
    parse_market()
