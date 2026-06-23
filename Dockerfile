FROM python:3.11

# Install Node.js directly from Debian repositories
RUN apt-get update && apt-get install -y nodejs && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Add timeout and verbose to pip install to prevent hanging and see errors
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY api_server.py .

CMD ["sh", "-c", "uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8080}"]
