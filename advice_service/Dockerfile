# Base stage : production dependencies only
FROM python:3.11-slim AS base
WORKDIR /app

# Install poetry
RUN pip install poetry

# Poetry config so deps install into global env
RUN poetry config virtualenvs.create false

# Copy dependency definitions
COPY pyproject.toml poetry.lock* ./
RUN echo "===== PYPROJECT INSIDE CONTAINER =====" && \
    sed -n 'l' pyproject.toml && \
    echo "======================================"
# Install production dependencies
RUN poetry install --no-interaction --no-ansi --only main --no-root

# --- Production Image ---
FROM base AS production

COPY . .

EXPOSE 9003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9003"]
