FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire bot directory including subdirectories (commands/, formatters/, etc.)
COPY . .

ENV PYTHONUNBUFFERED=1
ENV BOT_TOKEN=""
ENV BACKEND_URL="http://backend:8000"
ENV ORCHESTRATOR_URL="http://orchestrator:8082"
ENV CHANNEL_NEWS=""
ENV CHANNEL_ALERTS=""
ENV CHANNEL_PREMIUM=""
ENV CHANNEL_ALPHA=""
ENV ADMIN_IDS=""
ENV WEBHOOK_URL=""
ENV WEBHOOK_PORT=8080
ENV WEBHOOK_PATH=/webhook
ENV WEBHOOK_LISTEN=0.0.0.0

EXPOSE 8080

CMD ["python", "bot.py"]
