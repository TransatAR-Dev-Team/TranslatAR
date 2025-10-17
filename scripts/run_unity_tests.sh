#!/usr/bin/env bash
set -euo pipefail

# This script runs Unity tests in batch mode for both EditMode and PlayMode.
# It requires the Unity Editor to be installed in its default location.

# --- Configuration ---
UNITY_VERSION="2022.3.62f1"
# Assumes the script is run from the project root. We need the full path.
PROJECT_PATH="$(pwd)/unity" 

# --- OS-Specific Setup ---
UNITY_EXECUTABLE=""
# Get the lowercase name of the OS for easier checking
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS_NAME" == "darwin" ]]; then
    # macOS default path
    UNITY_EXECUTABLE="/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity"
elif [[ "$OS_NAME" == "linux" ]] && grep -q -i "microsoft" /proc/version; then
    # WSL (Windows Subsystem for Linux)
    # The C: drive is mounted at /mnt/c
    UNITY_EXECUTABLE="/mnt/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
elif [[ "$OS_NAME" == mingw* || "$OS_NAME" == cygwin* || "$OS_NAME" == msys* ]]; then
    # Windows (Git Bash) default path
    UNITY_EXECUTABLE="/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
elif [[ "$OS_NAME" == "linux" ]]; then
    # Native Linux
    echo "Unity testing on native Linux is not supported for this project." >&2
    exit 1
else
    echo "Unsupported operating system: $(uname -s)" >&2
    exit 1
fi

if [ ! -f "$UNITY_EXECUTABLE" ]; then
    echo "Unity Editor executable not found at the expected path: $UNITY_EXECUTABLE" >&2
    echo "Please ensure Unity version $UNITY_VERSION is installed in the default location or update the path in this script." >&2
    exit 1
fi

# --- Paths for Test Artifacts ---
ARTIFACTS_PATH="$PROJECT_PATH/Logs/TestResults"
mkdir -p "$ARTIFACTS_PATH"
RESULTS_PATH_EDITMODE="$ARTIFACTS_PATH/editmode-results.xml"
LOG_PATH_EDITMODE="$ARTIFACTS_PATH/editmode.log"
RESULTS_PATH_PLAYMODE="$ARTIFACTS_PATH/playmode-results.xml"
LOG_PATH_PLAYMODE="$ARTIFACTS_PATH/playmode.log"

FINAL_RC=0

echo "This may take a while, especially if this is your first time running Unity tests."

# --- Run Edit Mode Tests ---
echo "-------------------------------------"
echo "  RUNNING UNITY EDIT MODE TESTS"
echo "-------------------------------------"
# Note the quotes around the executable path to handle spaces
"$UNITY_EXECUTABLE" \
  -batchmode \
  -nographics \
  -projectPath "$PROJECT_PATH" \
  -runTests \
  -testPlatform editmode \
  -testResults "$RESULTS_PATH_EDITMODE" \
  -logFile "$LOG_PATH_EDITMODE"

RC_EDITMODE=$?
if [[ $RC_EDITMODE -ne 0 ]]; then
    echo "❌ Edit Mode tests failed. Check logs at: $LOG_PATH_EDITMODE" >&2
    FINAL_RC=$RC_EDITMODE
else
    echo "✅ Edit Mode tests passed."
fi

# --- Run Play Mode Tests ---
if [[ $FINAL_RC -eq 0 ]]; then
    echo "-------------------------------------"
    echo "  RUNNING UNITY PLAY MODE TESTS"
    echo "-------------------------------------"
    "$UNITY_EXECUTABLE" \
      -batchmode \
      -nographics \
      -projectPath "$PROJECT_PATH" \
      -runTests \
      -testPlatform playmode \
      -testResults "$RESULTS_PATH_PLAYMODE" \
      -logFile "$LOG_PATH_PLAYMODE"

    RC_PLAYMODE=$?
    if [[ $RC_PLAYMODE -ne 0 ]]; then
        echo "❌ Play Mode tests failed. Check logs at: $LOG_PATH_PLAYMODE" >&2
        FINAL_RC=$RC_PLAYMODE
    else
        echo "✅ Play Mode tests passed."
    fi
fi

# --- Final Summary ---
if [[ $FINAL_RC -eq 0 ]]; then
    echo "-------------------------------------"
    echo "✅ All Unity tests passed!"
    echo "-------------------------------------"
else
    echo "-------------------------------------" >&2
    echo "❌ Unity test suite failed." >&2
    echo "-------------------------------------" >&2
fi

exit $FINAL_RC
