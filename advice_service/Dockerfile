# ==========================
# Base stage
# ==========================
FROM python:3.11-slim AS base
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Configure Poetry to install globally
RUN poetry config virtualenvs.create false

# Copy dependency definitions
COPY pyproject.toml poetry.lock* ./

# Install ONLY main dependencies for production build
RUN poetry install --no-interaction --no-ansi --only main --no-root


# ==========================
# Production stage
# ==========================
FROM base AS production
COPY . .
EXPOSE 9003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9003"]


# ==========================
# Test stage
# ==========================
FROM python:3.11-slim AS test
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Configure Poetry to install globally
RUN poetry config virtualenvs.create false

# Copy dependency definitions
COPY pyproject.toml poetry.lock* ./

# Install ALL dependencies (main + dev)
RUN poetry install --no-interaction --no-ansi --with dev --no-root

# Copy app code
COPY . .

# Default command for unit testing
CMD ["pytest", "-v"]
