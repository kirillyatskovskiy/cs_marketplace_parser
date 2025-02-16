import time
from utils import logger
import random
from network import get_response, proxy_cycle
import requests

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
        # Генерация случайной задержки и логирование
        delay = random.uniform(1, 10)
        logger.info(f"Fetching items from {start} to {start + step}... Sleeping for {delay:.2f} seconds...")

        # Ожидание
        time.sleep(delay)

        response = get_response(url, proxy_cycle, params=params) # default timeout

        if response is None:
            logger.error("Failed to get a valid response.")
            return []

        # Если ошибка 429 (слишком много запросов), применяем фиксированную задержку
        if response.status_code == 429:
            # Фиксированная задержка в 30 секунд
            logger.warning(f"Rate limit exceeded. Retrying after 30 seconds...")
            time.sleep(30)  # Ожидаем 30 секунд перед повтором запроса

            # Повторяем запрос
            return fetch_items(start, step, retries + 1)

        response.raise_for_status()  # Выбрасываем исключение для других ошибок статуса
        data = response.json()
        return data.get("results", [])

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return []

# Получение количества предметов на рынке
def get_total_items():
    try:
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
        
        response = get_response(url, proxy_cycle, params=params) # default timeout

        # Проверка на успешный ответ
        if response.status_code != 200:
            logger.error(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return 0

        data = response.json()

        # Проверка на None
        if data is None:
            logger.error(f"Response data is None. The endpoint might be on cooldown: {url}")
            return 0

        return data.get("total_count", 0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 0