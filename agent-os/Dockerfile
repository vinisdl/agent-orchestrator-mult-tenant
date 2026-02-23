FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint outside /app so it is not overwritten by volume mount (docker-compose.dev volume: ./agent-os:/app)
COPY scripts/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Fix CRLF in scripts under /app (used when no volume mount)
RUN sed -i 's/\r$//' /app/scripts/entrypoint.sh /app/scripts/wait_for_db.py 2>/dev/null || true

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD []
