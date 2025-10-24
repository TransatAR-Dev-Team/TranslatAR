#!/usr/bin/env bash
set -euo pipefail

# This script runs Unity tests in batch mode and uses a Python script to parse the results.
# It includes robust cleanup for both project state and stale test artifacts.

# --- Robust Process Cleanup ---
cleanup() {
    # Check if a UNITY_PID was set. The '+x' is a robust way to check for existence.
    if [ ! -z "${UNITY_PID+x}" ] && [ ! -z "$UNITY_PID" ]; then
        echo "" && echo "--- Running cleanup ---"
        echo "Attempting to terminate Unity process (PID: $UNITY_PID)..."
        if ps -p $UNITY_PID > /dev/null; then
            if [[ "$OS_NAME" == mingw* || "$OS_NAME" == cygwin* || "$OS_NAME" == msys* ]] || \
               ([[ "$OS_NAME" == "linux" ]] && [ -f "/proc/version" ] && grep -q -i "microsoft" /proc/version); then
                taskkill //PID $UNITY_PID //F //T > /dev/null 2>&1 || true
            else
                kill $UNITY_PID > /dev/null 2>&1 || true
            fi
            echo "Termination signal sent."
        else
            echo "Unity process with PID $UNITY_PID already exited."
        fi
        unset UNITY_PID
    fi
    # The PROJECT_PATH_NATIVE variable might not be set if the script fails very early.
    # We check for its existence before trying to use it.
    if [ ! -z "${PROJECT_PATH_NATIVE+x}" ]; then
        echo "Cleaning up project Temp directory..."
        rm -rf "$PROJECT_PATH_NATIVE/Temp"
        echo "Cleanup complete."
    fi
}
# Set the trap: the `cleanup` function will run on any script exit.
trap cleanup EXIT INT TERM


# --- Configuration ---
UNITY_VERSION="2022.3.62f1"
PROJECT_PATH_NATIVE="$(pwd)/unity" 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSER_SCRIPT="$SCRIPT_DIR/parse_unity_results.py"

# --- OS-Specific Setup ---
UNITY_EXECUTABLE="${UNITY_EXECUTABLE:-}"
PROJECT_PATH_FOR_UNITY="$PROJECT_PATH_NATIVE"
ARTIFACTS_PATH_FOR_UNITY="$PROJECT_PATH_NATIVE/Logs/TestResults"
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS_NAME" == "darwin" ]]; then
    # If UNITY_EXECUTABLE not provided, try the requested version, otherwise auto-detect latest installed
    if [[ -z "$UNITY_EXECUTABLE" ]]; then
        CANDIDATE="/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity"
        if [[ -f "$CANDIDATE" ]]; then
            UNITY_EXECUTABLE="$CANDIDATE"
        else
            # Auto-detect latest installed editor
            DETECTED=$(ls -1d /Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity 2>/dev/null | sort -Vr | head -n1 || true)
            if [[ -n "$DETECTED" && -f "$DETECTED" ]]; then
                echo "Unity version $UNITY_VERSION not found. Auto-detected: $DETECTED"
                UNITY_EXECUTABLE="$DETECTED"
            fi
        fi
    fi
elif [[ "$OS_NAME" == "linux" ]] && [ -f "/proc/version" ] && grep -q -i "microsoft" /proc/version; then
    UNITY_EXECUTABLE="/mnt/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
    PROJECT_PATH_FOR_UNITY=$(wslpath -w "$PROJECT_PATH_NATIVE")
    ARTIFACTS_PATH_FOR_UNITY=$(wslpath -w "$PROJECT_PATH_NATIVE/Logs/TestResults")
elif [[ "$OS_NAME" == mingw* || "$OS_NAME" == cygwin* || "$OS_NAME" == msys* ]]; then
    UNITY_EXECUTABLE="/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
elif [[ "$OS_NAME" == "linux" ]]; then
    echo "Unity testing on native Linux is not supported for this project." >&2
    exit 1
else
    echo "Unsupported operating system: $(uname -s)" >&2
    exit 1
fi

if [ -z "$UNITY_EXECUTABLE" ] || [ ! -f "$UNITY_EXECUTABLE" ]; then
    echo "Unity Editor executable not found. Set UNITY_EXECUTABLE env var to your editor path or adjust UNITY_VERSION." >&2
    echo "Tried path: /Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity" >&2
    exit 1
fi

# --- Paths ---
ARTIFACTS_PATH_NATIVE="$PROJECT_PATH_NATIVE/Logs/TestResults"
mkdir -p "$ARTIFACTS_PATH_NATIVE"
RESULTS_PATH_EDITMODE_NATIVE="$ARTIFACTS_PATH_NATIVE/editmode-results.xml"
LOG_PATH_EDITMODE_NATIVE="$ARTIFACTS_PATH_NATIVE/editmode.log"
RESULTS_PATH_PLAYMODE_NATIVE="$ARTIFACTS_PATH_NATIVE/playmode-results.xml"
LOG_PATH_PLAYMODE_NATIVE="$ARTIFACTS_PATH_NATIVE/playmode.log"
RESULTS_PATH_EDITMODE_FOR_UNITY="$ARTIFACTS_PATH_FOR_UNITY/editmode-results.xml"
RESULTS_PATH_PLAYMODE_FOR_UNITY="$ARTIFACTS_PATH_FOR_UNITY/playmode-results.xml"


FINAL_RC=0
UNITY_PID=""

echo "-------------------------------------"
echo "Note: This may take a while..."

# --- Run Edit Mode Tests ---
echo "-------------------------------------"
echo "RUNNING UNITY EDIT MODE TESTS..."

echo "Cleaning up previous Edit Mode test results..."
rm -f "$RESULTS_PATH_EDITMODE_NATIVE"

# Run Unity silently in the background
echo "Using Unity: $UNITY_EXECUTABLE"
echo "Project: $PROJECT_PATH_FOR_UNITY"

"$UNITY_EXECUTABLE" \
  -batchmode -nographics \
  -projectPath "$PROJECT_PATH_FOR_UNITY" \
  -runTests -testPlatform editmode \
  -testResults "$RESULTS_PATH_EDITMODE_FOR_UNITY" \
  -logFile "$LOG_PATH_EDITMODE_NATIVE" > /dev/null 2>&1 &
UNITY_PID=$!
wait $UNITY_PID || true
unset UNITY_PID

if [[ ! -f "$RESULTS_PATH_EDITMODE_NATIVE" ]]; then
    echo "❌ ERROR: Results file not found at '$RESULTS_PATH_EDITMODE_NATIVE'" >&2
    echo "Unity log (last 200 lines):" >&2
    tail -n 200 "$LOG_PATH_EDITMODE_NATIVE" 2>/dev/null || true
fi

python3 "$PARSER_SCRIPT" "$RESULTS_PATH_EDITMODE_NATIVE"
RC_EDITMODE=$?

if [[ $RC_EDITMODE -ne 0 ]]; then
    echo "Full log available at: $LOG_PATH_EDITMODE_NATIVE" >&2
    FINAL_RC=$RC_EDITMODE
fi

# --- Run Play Mode Tests ---
if [[ $FINAL_RC -eq 0 ]]; then
    echo "-------------------------------------"
    echo "RUNNING UNITY PLAY MODE TESTS..."

    echo "Cleaning up previous Play Mode test results..."
    rm -f "$RESULTS_PATH_PLAYMODE_NATIVE"

    "$UNITY_EXECUTABLE" \
      -batchmode -nographics \
      -projectPath "$PROJECT_PATH_FOR_UNITY" \
      -runTests -testPlatform playmode \
      -testResults "$RESULTS_PATH_PLAYMODE_FOR_UNITY" \
      -logFile "$LOG_PATH_PLAYMODE_NATIVE" > /dev/null 2>&1 &
    UNITY_PID=$!
    wait $UNITY_PID || true
    unset UNITY_PID

    python3 "$PARSER_SCRIPT" "$RESULTS_PATH_PLAYMODE_NATIVE"
    RC_PLAYMODE=$?
    
    if [[ $RC_PLAYMODE -ne 0 ]]; then
        echo "Full log available at: $LOG_PATH_PLAYMODE_NATIVE" >&2
        FINAL_RC=$RC_PLAYMODE
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
