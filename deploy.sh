#!/bin/bash

# Остановка контейнеров Docker
echo "Stopping Docker containers..."
docker compose down

# Диалог выбора, очищать ли volume для Postgres
read -p "Do you want to remove the Postgres volume? (y/n): " remove_volume

if [ "$remove_volume" == "y" ]; then
  echo "Removing Docker volume..."
  docker volume rm $(docker volume ls -qf name=postgres_data_cs2p)
else
  echo "Skipping Docker volume removal."
fi

# Обновление репозитория
echo "Pulling latest changes from Git..."
git pull

# Строим и запускаем контейнеры Docker с обновлением
echo "Building and starting Docker containers..."
docker compose up --build

# Завершаем выполнение
echo "Deployment complete!"

