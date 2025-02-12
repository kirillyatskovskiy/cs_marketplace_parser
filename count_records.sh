#!/bin/bash

# Подключение к контейнеру и выполнение запроса через psql
docker exec -it postgres_cs2p psql -U root -d cs2_steam_marketplace -c "SELECT COUNT(*) FROM cs2_steam_marketplace;"
