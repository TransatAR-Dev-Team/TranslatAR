#!/usr/bin/env bash
# This script intelligently starts or stops the Docker Compose environment.
# It detects if an NVIDIA GPU is available and automatically layers
# the GPU-specific compose file if it is.
#
# Any arguments passed to this script will be forwarded directly to the
# `docker compose` command.
#
# Examples:
#   ./scripts/start.sh up --build -d
#   ./scripts/start.sh down --remove-orphans
#   ./scripts/start.sh logs -f backend

set -euo pipefail

# Move to the project root directory to ensure all paths are correct
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# --- Build the base command array ---
# We always start with the base docker-compose.yml file.
COMPOSE_FILES=("-f" "docker-compose.yml")

# --- Detect NVIDIA GPU and layer GPU config if available ---
# The `command -v` is a robust, cross-platform way to check if a command exists.
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected. Applying GPU-specific configuration."
    # Add the GPU compose file to our array of files.
    COMPOSE_FILES+=("-f" "docker-compose.gpu.yml")
else
    echo "ℹ️  No NVIDIA GPU detected. Running in CPU-only mode."
fi

# --- Execute the final command ---
# "$@" is a special variable that expands to all arguments passed to this script.
echo "-------------------------------------"
echo "Running command: docker compose ${COMPOSE_FILES[*]} "$@""
echo "-------------------------------------"

# `exec` replaces the script process with the docker compose process.
# This ensures that signals like Ctrl+C are handled correctly by docker compose.
exec docker compose "${COMPOSE_FILES[@]}" "$@"
