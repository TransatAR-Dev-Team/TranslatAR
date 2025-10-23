#!/usr/bin/env bash
set -uo pipefail

# Get the directory of this script to find the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

OVERALL_RC=0

echo "--- Formatting Python Services ---"
PYTHON_SERVICES=("backend" "stt-service" "translation-service" "summarization-service")

for service in "${PYTHON_SERVICES[@]}"; do
    echo ""
    echo "==> Formatting service: $service"
    # Run commands in a subshell. If it fails, the `if` condition triggers.
    if ! (
        set -e # Exit subshell immediately on error
        cd "$service"
        PYTHON_VERSION=$(grep "requires-python" pyproject.toml | cut -d'"' -f2 | sed 's/[~=]//g')
        PYTHON_EXEC="python${PYTHON_VERSION}"

        if ! command -v "$PYTHON_EXEC" &> /dev/null; then
            echo "❌ ERROR: Python version ${PYTHON_VERSION} not found. Please install '${PYTHON_EXEC}'." >&2
            exit 1
        fi
        
        echo "--> Ensuring dependencies are installed with ${PYTHON_EXEC}..."
        poetry env use "$PYTHON_EXEC" >/dev/null
        poetry sync --no-root >/dev/null

        echo "--> Running formatters..."
        poetry run black .
        poetry run ruff format .
    ); then
        echo "❌ ERROR: Formatting failed for service: $service" >&2
        OVERALL_RC=1
    fi
done

echo ""
echo "--- Formatting Web Portal ---"
if ! (
    set -e
    cd web-portal
    echo "--> Ensuring dependencies are installed..."
    npm install > /dev/null
    echo "--> Running formatter..."
    npm run format
); then
    echo "❌ ERROR: Formatting failed for Web Portal" >&2
    OVERALL_RC=1
fi

echo ""
if [[ $OVERALL_RC -eq 0 ]]; then
    echo "✅ Formatting complete."
else
    echo "❌ One or more formatting tasks failed." >&2
fi

exit $OVERALL_RC
