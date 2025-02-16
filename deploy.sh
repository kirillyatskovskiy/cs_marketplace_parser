#!/bin/bash

# Остановка контейнеров Docker
echo "Stopping Docker containers..."
docker compose down

# Диалог выбора, очищать ли volume для Postgres
read -p "Do you want to remove the Postgres volume? (y/n): " remove_volume

# Обновление репозитория
echo "Pulling latest changes from Git..."
git pull

# Строим и запускаем контейнеры Docker с обновлением
echo "Building and starting Docker containers..."
docker compose up --build

# Завершаем выполнение
echo "Deployment complete!"

