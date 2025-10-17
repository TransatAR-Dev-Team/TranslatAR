#!/usr/bin/env bash
set -euo pipefail

# This script runs Unity tests in batch mode for both EditMode and PlayMode.
# It requires the Unity Editor to be installed in its default location.

# --- Configuration ---
UNITY_VERSION="2022.3.62f1"
PROJECT_PATH="$(pwd)/unity" # Assumes the script is run from the project root

# --- OS-Specific Setup ---
UNITY_EXECUTABLE=""
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS default path
    UNITY_EXECUTABLE="/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity"
elif [[ "$(uname -s)" == "Linux" ]]; then
    echo "Unity testing on Linux is not supported for this project." >&2
    exit 1
elif [[ "$(uname -s)" == MINGW* || "$(uname -s)" == CYGWIN* || "$(uname -s)" == MSYS* ]]; then
    # Windows (Git Bash) default path
    # We must use quotes to handle the space in "Program Files".
    UNITY_EXECUTABLE="/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
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
# Create a directory to store test results and logs, ignored by git.
ARTIFACTS_PATH="$PROJECT_PATH/Logs/TestResults"
mkdir -p "$ARTIFACTS_PATH"
RESULTS_PATH_EDITMODE="$ARTIFACTS_PATH/editmode-results.xml"
LOG_PATH_EDITMODE="$ARTIFACTS_PATH/editmode.log"
RESULTS_PATH_PLAYMODE="$ARTIFACTS_PATH/playmode-results.xml"
LOG_PATH_PLAYMODE="$ARTIFACTS_PATH/playmode.log"

# This variable will track the final exit code.
FINAL_RC=0

# --- Run Edit Mode Tests ---
echo "-------------------------------------"
echo "  RUNNING UNITY EDIT MODE TESTS"
echo "-------------------------------------"
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
# Only run playmode tests if editmode tests passed
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
