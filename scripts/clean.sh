#!/usr/bin/env bash
# This script performs a deep clean of the entire TranslatAR project,
# removing temporary files, build artifacts, caches, and legacy SDKs.
set -euo pipefail

# Move to the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

echo "--- Starting Deep Clean ---"

# --- 1. Unity Project Cleanup (Most Important) ---
echo "Cleaning Unity project..."
if [ -d "unity" ]; then
    # Use sudo for these removals as they might be root-owned from inside Unity
    echo "  - Removing legacy Assets/Oculus and Assets/MetaXR directories..."
    sudo rm -rf "unity/Assets/Oculus"
    sudo rm -rf "unity/Assets/MetaXR"

    echo "  - Removing legacy OVR/Meta config files from Assets/Resources..."
    sudo rm -f unity/Assets/Resources/OculusRuntimeSettings.asset*
    sudo rm -f unity/Assets/Resources/OVROverlayCanvasSettings.asset*
    sudo rm -f unity/Assets/Resources/OVRPlatformToolSettings.asset*

    echo "  - Deleting generated Unity cache folders..."
    sudo rm -rf "unity/Library" "unity/Logs" "unity/obj" "unity/Temp" "unity/UserSettings"

    echo "  - Deleting IDE project files (.csproj, .sln)..."
    sudo rm -f unity/*.sln unity/*.csproj
else
    echo "Skipping Unity clean (directory not found)."
fi

# --- 2. Python Services Cleanup ---
echo "Cleaning Python services (using sudo for Docker-generated files)..."
# These files are often created by a root user inside a Docker container
sudo find . -type d -name "__pycache__" -exec rm -rf {} +
sudo find . -type d -name ".pytest_cache" -exec rm -rf {} +
sudo find . -type d -name ".ruff_cache" -exec rm -rf {} +

# --- 3. Web Portal Cleanup ---
echo "Cleaning Web Portal..."
if [ -d "web-portal/node_modules" ]; then
    echo "  - Deleting web-portal/node_modules..."
    sudo rm -rf "web-portal/node_modules"
fi
if [ -d "web-portal/dist" ]; then
    echo "  - Deleting web-portal/dist..."
    sudo rm -rf "web-portal/dist"
fi

echo ""
echo "✅ Deep Clean Complete."
echo "You can now safely open the Unity project. It will take a long time to re-import everything on the first launch."
