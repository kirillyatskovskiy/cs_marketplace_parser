FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY requirements.txt ./
COPY steam_parser.py ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Определяем переменные окружения для подключения к PostgreSQL
ENV DB_NAME=steam_market
ENV DB_USER=your_user
ENV DB_PASSWORD=your_password
ENV DB_HOST=localhost
ENV DB_PORT=5432

# Запускаем скрипт при старте контейнера
CMD ["python", "steam_parser.py"]
