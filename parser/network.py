from itertools import cycle
import requests
from utils import logger

# Функция для загрузки прокси из файла
def load_proxies_from_file(file_path):
    with open(file_path, 'r') as file:
        # Чтение прокси из файла, удаление лишних пробелов и пустых строк
        proxies = [line.strip() for line in file.readlines() if line.strip()]
    return proxies

# Загружаем список прокси из файла
proxies_list = load_proxies_from_file('proxies.txt')

# Создаем цикл для перебора прокси
proxy_cycle = cycle(proxies_list)

MAX_ERROR_LENGTH = 100

def get_error_message(e:Exception):
    error_message = str(e)
    if len(error_message) > MAX_ERROR_LENGTH:
        error_message = error_message[:MAX_ERROR_LENGTH] + '...'
    return error_message

def get_response(url, proxy_cycle, params=None, timeout=10): # timeout 10 because handling big data takes big patience ;)
    try:
        # First try the request without proxy
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()  # Check for a successful response
        logger.info("PROXY - Response without proxy.")
        return response  # Return response if request is successful
    except requests.RequestException as e:
        error_message = str(e)
        if len(error_message) > MAX_ERROR_LENGTH:
            error_message = error_message[:MAX_ERROR_LENGTH] + '...'
            
        logger.error(f"PROXY - Error without proxy: {get_error_message(e)}")
    
    # If request without proxy failed, try with proxies
    for proxy in proxy_cycle:  # Iterate through proxies
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        try:
            response = requests.get(url, params=params, proxies=proxies, timeout=timeout)
            response.raise_for_status()  # Check for a successful response
            logger.info(f"PROXY - Response through proxy: {proxy}")
            return response  # Return response if request is successful
        except requests.RequestException as e:
            logger.error(f"PROXY - Error with proxy {proxy}: {get_error_message(e)}")
            return response # добавил то о чем говорил ниже
    
    logger.error("PROXY - All proxies are not working.") # возможно не показывается, т.к. proxy_cycle
    return response # после коммента выше сразу стало все понятно