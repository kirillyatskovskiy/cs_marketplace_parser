FROM python:3.11-slim

ENV TERM=xterm-256color

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

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["python", "parser.py", "--mode", "full"]
