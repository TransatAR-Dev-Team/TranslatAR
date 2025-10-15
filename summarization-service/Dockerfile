FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to not create a virtualenv
RUN poetry config virtualenvs.create false

# Copy dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . .

EXPOSE 9002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9002"]
