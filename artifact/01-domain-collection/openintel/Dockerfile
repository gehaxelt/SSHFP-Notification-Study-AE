FROM python:3.11-slim

WORKDIR /app

# Install bash (for shell script) and any system deps
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
