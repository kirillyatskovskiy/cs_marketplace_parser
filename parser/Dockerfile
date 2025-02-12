FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
COPY parser.py ./

RUN pip install --no-cache-dir -r requirements.txt

ENV DB_NAME=cs2_steam_marketplace
ENV DB_USER=root
ENV DB_PASSWORD=root
ENV DB_HOST=postgres_cs2p
ENV DB_PORT=5432

CMD ["python", "steam_parser.py"]
