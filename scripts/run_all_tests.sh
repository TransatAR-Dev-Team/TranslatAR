#!/usr/bin/env bash
# This script runs all test suites in order.
# Because of 'set -e', it will exit immediately if any test suite fails.
set -euo pipefail

# Get the directory of this script to find the others
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_TEST_SCRIPT="$SCRIPT_DIR/run_unit_tests.sh"
INTEGRATION_TEST_SCRIPT="$SCRIPT_DIR/run_integration_tests.sh"

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

# --- Final Success Message ---
# This line will only be reached if all scripts above passed.
echo ""
echo "================================="
echo "✅ ALL TEST SUITES PASSED!"
echo "================================="
