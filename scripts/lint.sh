#!/usr/bin/env bash
set -uo pipefail

# Get the directory of this script to find the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

OVERALL_RC=0

echo "--- Linting Python Services ---"
PYTHON_SERVICES=("backend" "stt-service" "translation-service" "summarization-service")

for service in "${PYTHON_SERVICES[@]}"; do
    echo ""
    echo "==> Linting service: $service"
    if ! (
        set -e
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

        echo "--> Running linter..."
        poetry run ruff check . --fix
    ); then
        # The subshell exited with a non-zero code, so we record the failure.
        echo "❌ LINTING ERRORS FOUND in $service" >&2
        OVERALL_RC=1
    else
        echo "✅ No linting errors found in $service"
    fi
done

echo ""
echo "--- Linting Web Portal ---"
if ! (
    set -e
    cd web-portal
    echo "--> Ensuring dependencies are installed..."
    npm install > /dev/null
    echo "--> Running linter..."
    npm run lint
); then
    echo "❌ LINTING ERRORS FOUND in Web Portal" >&2
    OVERALL_RC=1
else
    echo "✅ No linting errors found in Web Portal"
fi


echo ""
if [[ $OVERALL_RC -eq 0 ]]; then
    echo "✅ All services passed linting."
else
    echo "❌ Linting failed for one or more services." >&2
fi

exit $OVERALL_RC
