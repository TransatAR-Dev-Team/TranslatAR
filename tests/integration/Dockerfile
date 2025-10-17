FROM python:3.11-slim
WORKDIR /app

# Install poetry
RUN pip install poetry

# Configure poetry to not create a virtualenv inside the container
RUN poetry config virtualenvs.create false

# Copy dependency definition files
# The wildcard is to handle cases where poetry.lock doesn't exist yet on first build
COPY pyproject.toml poetry.lock* ./

# Install dependencies
# --no-root is used because this isn't a library to be installed, just a test environment
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the test code
COPY . .

# comand given in docker-compose.test.integration.yml
