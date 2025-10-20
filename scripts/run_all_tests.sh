#!/usr/bin/env bash
# This script runs all test suites in order.
# Because of 'set -e', it will exit immediately if any test suite fails.
set -euo pipefail

# Get the directory of this script to find the others
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_TEST_SCRIPT="$SCRIPT_DIR/run_unit_tests.sh"
INTEGRATION_TEST_SCRIPT="$SCRIPT_DIR/run_integration_tests.sh"
UNITY_TEST_SCRIPT="$SCRIPT_DIR/run_unity_tests.sh"

# --- Run Unit Tests ---
echo "================================="
echo "  RUNNING UNIT TESTS"
echo "================================="
"$UNIT_TEST_SCRIPT"

# --- Run Integration Tests ---
# This part will only be reached if the unit tests passed.
echo ""
echo "================================="
echo "  RUNNING INTEGRATION TESTS"
echo "================================="
"$INTEGRATION_TEST_SCRIPT"

# --- Run Unity Tests (Platform Dependent) ---
# This part will only be reached if the previous tests passed.
echo ""
echo "================================="
echo "  CHECKING FOR UNITY TEST SUPPORT"
echo "================================="

# Check if the current OS is macOS (Darwin) or Windows (Git Bash or WSL)
IS_SUPPORTED_OS=false
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS_NAME" == "darwin" ]] || \
   [[ "$OS_NAME" == mingw* || "$OS_NAME" == cygwin* || "$OS_NAME" == msys* ]] || \
   ([[ "$OS_NAME" == "linux" ]] && [ -f "/proc/version" ] && grep -q -i "microsoft" /proc/version); then
    IS_SUPPORTED_OS=true
fi

if [[ "$IS_SUPPORTED_OS" == true ]]; then
    echo "Supported platform detected. Running Unity tests..."
    "$UNITY_TEST_SCRIPT"
else
    # For unsupported platforms like native Linux, print a warning but do not fail.
    echo "⚠️  WARNING: Skipping Unity tests. Unsupported platform '$(uname -s)'."
    echo "   Unity tests can only be run on macOS or Windows (via Git Bash or WSL)."
fi

# --- Final Success Message ---
# This line will only be reached if all mandatory scripts passed.
echo ""
echo "================================="
if [[ "$IS_SUPPORTED_OS" == false ]]; then
    echo "✅ ALL BACKEND TEST SUITES PASSED (UNITY SKIPPED)!"
else
    echo "✅ ALL TEST SUITES PASSED!"
fi
echo "================================="
