# Base stage installs ONLY production dependencies
FROM python:3.11-slim AS base
WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root --only main

# Test stage builds on 'base' and adds development dependencies
FROM base AS test
COPY . .
# Install dev dependencies
RUN poetry install --no-interaction --no-ansi --no-root
CMD ["pytest", "-v"]

# Production stage copies code into the 'base' image
FROM base AS production
COPY . .

EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
