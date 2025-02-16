FROM python:3.11-slim

ENV TERM=xterm-256color

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN chmod +x wait-for-it.sh

RUN pip install --no-cache-dir -r requirements.txt