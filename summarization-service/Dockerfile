# Base stage for shared dependencies
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Test stage adds dev dependencies
FROM base AS test
COPY . .

# Production stage
FROM base AS production
COPY . .
EXPOSE 9002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9002"]
