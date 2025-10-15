FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to not create a virtualenv
RUN poetry config virtualenvs.create false

# Copy dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
# --no-interaction: Do not ask any interactive questions
# --no-ansi: Disable ANSI output
# --no-root: Do not install the project itself
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the backend code
COPY . .

EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
