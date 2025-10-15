FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set non-interactive mode for package installations.
ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisites needed for adding new software repositories.
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates

# Manually install the NVIDIA keyring to access their repositories.
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
RUN dpkg -i cuda-keyring_1.0-1_all.deb
RUN apt-get update

# Install the SPECIFIC cuDNN 9 packages for a CUDA 12 environment
RUN apt-get -y install libcudnn9-cuda-12 libcudnn9-dev-cuda-12

# Install Python 3.10 and Pip
RUN apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install poetry using the installed python
RUN python3.10 -m pip install poetry

# Configure poetry to install dependencies in the system's python environment
RUN poetry config virtualenvs.create false

# Copy dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install python dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 9000

# Run the Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
