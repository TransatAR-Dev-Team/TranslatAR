# base stage
FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# testing stage
FROM base AS test
COPY . .

# prod stage
FROM base AS production
COPY . . 
EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
