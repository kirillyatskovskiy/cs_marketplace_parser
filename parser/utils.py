import logging

# Настроим базовое логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("parser.log", mode='a')
    ]
)

logger = logging.getLogger(__name__)