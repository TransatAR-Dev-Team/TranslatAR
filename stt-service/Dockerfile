# This 'base' stage sets up CUDA, Python, and installs ONLY production dependencies
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 AS base

# Set non-interactive mode for package installations.
ENV DEBIAN_FRONTEND=noninteractive

# Install system prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates

# Install NVIDIA keyring and cuDNN
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    apt-get update && \
    apt-get -y install libcudnn9-cuda-12 libcudnn9-dev-cuda-12

# Install Python 3.10, Pip, and clean up
RUN apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install and configure Poetry, then install production dependencies
RUN python3.10 -m pip install poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root --only main


# The 'test' stage builds on 'base' and adds development dependencies to run tests
FROM base AS test
COPY . .
# Install dev dependencies
RUN poetry install --no-interaction --no-ansi --no-root
CMD ["pytest", "-v"]


# The 'production' stage uses the lean 'base' image and adds the application code
FROM base AS production
COPY . .
EXPOSE 9000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
