FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend (shared deps)
COPY backend/requirements.txt /tmp/backend-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt || true

# Install orchestrator-specific deps
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic

# Copy project code
COPY orchestrator/ /app/orchestrator/
COPY bots/ /app/bots/
COPY swarm/ /app/swarm/
COPY integrations/ /app/integrations/
COPY tools/ /app/tools/
COPY infrastructure/ /app/infrastructure/
COPY core/ /app/core/

ENV PYTHONPATH=/app
ENV ORCHESTRATOR_PORT=8081

EXPOSE 8081

CMD ["python", "-u", "orchestrator/main.py"]
