#!/bin/bash

# Остановка контейнеров Docker
echo "Stopping Docker containers..."
docker compose down

# Очистка volumes
echo "Removing Docker volume..." 
docker volume rm $(docker volume ls -qf name=postgres_data_cs2p)

# Обновление репозитория
echo "Pulling latest changes from Git..."
git pull

# Строим и запускаем контейнеры Docker с обновлением
echo "Building and starting Docker containers..."
docker compose up --build

# Завершаем выполнение
echo "Deployment complete!"
