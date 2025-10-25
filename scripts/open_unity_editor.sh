#!/usr/bin/env bash
set -euo pipefail

# This script finds the correct Unity Editor executable for the current OS
# and opens the project located in the `unity/` directory.

# --- Configuration ---
UNITY_VERSION="2022.3.62f1"
PROJECT_PATH_NATIVE="$(pwd)/unity" 

# --- OS-Specific Setup ---
UNITY_EXECUTABLE=""
PROJECT_PATH_FOR_UNITY="$PROJECT_PATH_NATIVE"
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS_NAME" == "darwin" ]]; then
    # macOS
    UNITY_EXECUTABLE="/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity"
elif [[ "$OS_NAME" == "linux" ]] && [ -f "/proc/version" ] && grep -q -i "microsoft" /proc/version; then
    # Windows Subsystem for Linux (WSL)
    UNITY_EXECUTABLE="/mnt/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
    # The Windows cmd.exe needs Windows-style paths, so we convert them.
    PROJECT_PATH_FOR_UNITY=$(wslpath -w "$PROJECT_PATH_NATIVE")
elif [[ "$OS_NAME" == mingw* || "$OS_NAME" == cygwin* || "$OS_NAME" == msys* ]]; then
    # Windows (Git Bash, etc.)
    UNITY_EXECUTABLE="/c/Program Files/Unity/Hub/Editor/$UNITY_VERSION/Editor/Unity.exe"
else
    echo "ERROR: Unsupported platform '$(uname -s)'." >&2
    echo "   This command can only be run on macOS or Windows (via Git Bash or WSL)." >&2
    exit 1
fi

# --- Verification ---
if [ ! -f "$UNITY_EXECUTABLE" ]; then
    echo "ERROR: Unity Editor not found at the expected path:" >&2
    echo "   $UNITY_EXECUTABLE" >&2
    echo "   Please ensure Unity version $UNITY_VERSION is installed in the default location via Unity Hub." >&2
    exit 1
fi

# --- Launch Editor ---
echo "Found Unity Editor: $UNITY_EXECUTABLE"
echo "Opening project: $PROJECT_PATH_NATIVE"
echo "   Please wait, the editor may take a moment to launch..."

# Launch the editor as a separate, non-blocking process.
if [[ "$OS_NAME" == "darwin" ]]; then
    # On macOS, 'open' is the best way to launch a GUI app from the terminal.
    open -a "/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app" --args -projectPath "$PROJECT_PATH_FOR_UNITY"
elif [[ "$OS_NAME" == "linux" ]] && [ -f "/proc/version" ] && grep -q -i "microsoft" /proc/version; then
    # --- FIX: For WSL, we must explicitly call the Windows command prompt ---
    # We also convert the Unity executable path to a Windows-style path.
    UNITY_EXECUTABLE_WIN_PATH=$(wslpath -w "$UNITY_EXECUTABLE")
    cmd.exe /c start "" "$UNITY_EXECUTABLE_WIN_PATH" -projectPath "$PROJECT_PATH_FOR_UNITY"
else
    # On Git Bash, 'start' is an alias that works correctly.
    # The empty "" is a quirk to handle paths with spaces correctly.
    start "" "$UNITY_EXECUTABLE" -projectPath "$PROJECT_PATH_FOR_UNITY"
fi

echo "✨ Unity Editor is launching."
