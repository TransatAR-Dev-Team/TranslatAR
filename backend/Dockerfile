# Base stage installs ONLY production dependencies
FROM python:3.11-slim AS base
WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

# Ensure lockfile reflects pyproject changes (e.g., added websockets)
RUN poetry lock --no-interaction --no-ansi || true \
    && poetry install --no-interaction --no-ansi --only main

# Test stage builds on 'base' and adds development dependencies
FROM base AS test
COPY . .
# Install dev dependencies (refresh lock in case sources changed)
RUN poetry lock --no-interaction --no-ansi || true \
    && poetry install --no-interaction --no-ansi
CMD ["pytest", "-v"]

# Production stage copies code into the 'base' image
FROM base AS production
COPY . .

EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
