# Dockerfile for 03-analysis-scripts
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Optional: system CA certs (requests), and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates build-essential\
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
