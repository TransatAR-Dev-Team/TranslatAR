#!/usr/bin/env bash
set -euo pipefail

# Move to project root (parent of this scripts/ directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# --- Step 1: Clean up any previous runs ---
echo "Tearing down previous test environment if it exists..."
docker compose -f docker-compose.test.integration.yml down --remove-orphans > /dev/null 2>&1 || true

# --- Step 2: Run the tests and capture the exit code ---
# We REMOVED 'exec' so that this script can continue after the command finishes.
docker compose -f docker-compose.test.integration.yml up --build --abort-on-container-exit --exit-code-from test_runner
RC=$?

# --- Step 3: Clean up the environment from the current run ---
echo "Cleaning up test environment..."
docker compose -f docker-compose.test.integration.yml down --remove-orphans > /dev/null 2>&1

# --- Step 4: Check the result and print the final summary message ---
if [[ $RC -eq 0 ]]; then
    echo "-------------------------------------"
    echo "✅ All integration tests passed!"
    echo "-------------------------------------"
else
    echo "-------------------------------------" >&2
    echo "❌ Integration tests failed." >&2
    echo "-------------------------------------" >&2
fi

# --- Step 5: Propagate the original exit code ---
exit $RC
