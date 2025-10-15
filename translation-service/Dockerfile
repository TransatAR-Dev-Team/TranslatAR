# Base stage installs ONLY production dependencies
FROM python:3.11-slim AS base
WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to not create a virtualenv
RUN poetry config virtualenvs.create false

# Copy dependency definition files
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

EXPOSE 9001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9001"]
