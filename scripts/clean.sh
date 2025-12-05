#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------
# Clean temporary and build files for TranslatAR
# Usage:
#   ./scripts/clean_temp_files.sh [--python] [--node] [--docker] [--unity] [--deep]
# ----------------------------------------------------------------------

show_help() {
  cat <<EOF
TranslatAR Cleanup Utility

Usage:
  ./scripts/clean_temp_files.sh [options]

Options:
  --python     Clean Python caches (.venv, __pycache__, .ruff_cache, etc.)
  --node       Clean Node.js caches (node_modules, .next, dist, etc.)
  --docker     Clean Docker system data (images, containers, caches)
  --unity      Clean Unity temporary and build files (asks for confirmation)
  --deep       Perform a full cleanup (Python, Node, Docker, Unity)
  --help       Show this help message

Examples:
  ./scripts/clean_temp_files.sh --python
  ./scripts/clean_temp_files.sh --node
  ./scripts/clean_temp_files.sh --docker --node --python
  ./scripts/clean_temp_files.sh --deep
EOF

  exit 0
}

PYTHON=false
NODE=false
DOCKER=false
UNITY=false

# ----------------------------------------------------------------------
# Parse flags
# ----------------------------------------------------------------------
if [[ $# -eq 0 ]]; then
  show_help
fi

for arg in "$@"; do
  case "$arg" in
    --python) PYTHON=true ;;
    --node) NODE=true ;;
    --docker) DOCKER=true ;;
    --unity) UNITY=true ;;
    --deep)
      PYTHON=true
      NODE=true
      DOCKER=true
      UNITY=true
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    *)
      echo "❌ Unknown option: $arg"
      echo
      show_help
      exit 1
      ;;
  esac
done

echo "🧹 Cleaning temporary and build files..."

# ----------------------------------------------------------------------
# Python cleanup
# ----------------------------------------------------------------------

#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------
# Clean temporary and build files for TranslatAR
# Usage:
#   ./scripts/clean_temp_files.sh [--python] [--node] [--docker] [--unity] [--deep]
# ----------------------------------------------------------------------

show_help() {
  cat <<EOF
TranslatAR Cleanup Utility

Usage:
  ./scripts/clean_temp_files.sh [options]

Options:
  --python     Clean Python caches (.venv, __pycache__, .ruff_cache, etc.)
  --node       Clean Node.js caches (node_modules, .next, dist, etc.)
  --docker     Clean Docker system data (images, containers, caches)
  --unity      Clean Unity temporary and build files (asks for confirmation)
  --deep       Perform a full cleanup (Python, Node, Docker, Unity)
  --help       Show this help message

Examples:
  ./scripts/clean_temp_files.sh --python
  ./scripts/clean_temp_files.sh --node
  ./scripts/clean_temp_files.sh --docker --node --python
  ./scripts/clean_temp_files.sh --deep
EOF

  exit 0
}

PYTHON=false
NODE=false
DOCKER=false
UNITY=false

# ----------------------------------------------------------------------
# Parse flags
# ----------------------------------------------------------------------
if [[ $# -eq 0 ]]; then
  show_help
fi

for arg in "$@"; do
  case "$arg" in
    --python) PYTHON=true ;;
    --node) NODE=true ;;
    --docker) DOCKER=true ;;
    --unity) UNITY=true ;;
    --deep)
      PYTHON=true
      NODE=true
      DOCKER=true
      UNITY=true
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    *)
      echo "❌ Unknown option: $arg"
      echo
      show_help
      exit 1
      ;;
  esac
done

echo "🧹 Cleaning temporary and build files..."

# ----------------------------------------------------------------------
# Python cleanup
# ----------------------------------------------------------------------
if [[ "$PYTHON" == true ]]; then
  echo
  echo "🐍 Cleaning Python caches..."
  PYTHON_DIRS=(
    ".ruff_cache"
    ".mypy_cache"
    "__pycache__"
    ".pytest_cache"
    ".venv"
    "htmlcov"
  )
  PYTHON_FILES=(
    ".coverage"
  )

  ROOT_DIRS=(
    "backend"
    "stt-service"
    "translation-service"
    "summarization-service"
    "advice_service" # Added new service
    "scripts"
    "."
  )

  for root in "${ROOT_DIRS[@]}"; do
    if [[ -d "$root" ]]; then
      echo "→ Searching in $root"
      for dir in "${PYTHON_DIRS[@]}"; do
        find "$root" -type d -name "$dir" -exec rm -rf {} + 2>/dev/null || true
      done
      for file in "${PYTHON_FILES[@]}"; do
        find "$root" -type f -name "$file" -exec rm -f {} + 2>/dev/null || true
      done
    fi
  done
  echo "✅ Python cleanup complete."
fi

# ----------------------------------------------------------------------
# Node cleanup
# ----------------------------------------------------------------------
if [[ "$NODE" == true ]]; then
  echo
  echo "📦 Cleaning Node.js caches..."
  NODE_DIRS=(
    "node_modules"
    ".next"
    "dist"
  )

  NODE_ROOTS=(
    "web-portal"
    "."
  )

  for root in "${NODE_ROOTS[@]}"; do
    if [[ -d "$root" ]]; then
      echo "→ Searching in $root"
      for dir in "${NODE_DIRS[@]}"; do
        find "$root" -type d -name "$dir" -exec rm -rf {} + 2>/dev/null || true
      done
    fi
  done
  echo "✅ Node cleanup complete."
fi

# ----------------------------------------------------------------------
# Unity cleanup
# ----------------------------------------------------------------------
if [[ "$UNITY" == true ]]; then
  UNITY_DIR="unity"
  if [[ -d "$UNITY_DIR" ]]; then
    echo
    echo "⚠️  WARNING: You are about to delete Unity temporary and build folders."
    echo "   It will take a long time to reimport and recompile when you reopen the project."
    read -rp "   Continue cleaning Unity artifacts? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
      echo "→ Cleaning Unity-generated directories under '$UNITY_DIR/'..."
      UNITY_CLEAN_DIRS=(
        "Library"
        "Temp"
        "Obj"
        "Build"
        "Builds"
        "Logs"
        "UserSettings"
        "MemoryCaptures"
        "Recordings"
        ".vs"
        ".gradle"
        "ExportedObj"
        "ServerData"
        "Assets/StreamingAssets/aa*"
        "Assets/AddressableAssetsData"
        "Assets/Unity.VisualScripting.Generated"
      )
      for dir in "${UNITY_CLEAN_DIRS[@]}"; do
        echo "Deleting $dir directory..."
        find "$UNITY_DIR" -type d -path "$UNITY_DIR/$dir" -exec rm -rf {} + 2>/dev/null || true
      done
      echo "Deleting logs..."
      find "$UNITY_DIR" -type f -name "*.log" -delete 2>/dev/null || true

      echo "Deleting .csproj files..."
      find "$UNITY_DIR" -type f -name "*.csproj" -delete 2>/dev/null || true

      echo "✅ Unity cleanup complete."
    else
      echo "⏭️  Skipped Unity cleanup."
    fi
  fi
fi

# ----------------------------------------------------------------------
# Docker cleanup
# ----------------------------------------------------------------------
if [[ "$DOCKER" == true ]]; then
  echo
  echo "⚠️  WARNING: You are about to delete all Docker data."
  echo "   This command will stop TranslatAR Docker containers then remove all unused Docker data."
  echo "   This includes all containers, unused networks, dangling images, and build caches, even those not from TranslatAR."
  echo "   It will take a long time to re-download images rebuild containers, and download Ollama models again."
  read -rp "   Continue cleaning Docker system? (y/N): " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "Stopping Docker containers (if they exist)..."
    make down
    echo "🐳 Cleaning Docker system caches and volumes..."
    docker system prune -af --volumes
    echo "✅ Docker cleanup complete."
  else
    echo "⏭️  Skipped Docker cleanup."
  fi
fi

echo
echo "✅ Cleanup complete."
