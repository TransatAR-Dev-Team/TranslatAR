#!/usr/bin/env bash
set -euo pipefail

# Unity Code Coverage Script
# This script runs Unity tests while collecting code coverage data.

# --- Process Cleanup ---
cleanup() {
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
        fi
        unset UNITY_PID
    fi
    if [ ! -z "${PROJECT_PATH_NATIVE+x}" ]; then
        echo "Cleaning up project Temp directory..."
        rm -rf "$PROJECT_PATH_NATIVE/Temp"
        echo "Cleanup complete."
    fi
}
trap cleanup EXIT INT TERM


# --- Configuration ---
UNITY_VERSION="2022.3.62f1"
PROJECT_PATH_NATIVE="$(pwd)/unity"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- OS-Specific Setup ---
UNITY_EXECUTABLE="${UNITY_EXECUTABLE:-}"
PROJECT_PATH_FOR_UNITY="$PROJECT_PATH_NATIVE"
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')

if [[ "$OS_NAME" == "darwin" ]]; then
    if [[ -z "$UNITY_EXECUTABLE" ]]; then
        CANDIDATE="/Applications/Unity/Hub/Editor/$UNITY_VERSION/Unity.app/Contents/MacOS/Unity"
        if [[ -f "$CANDIDATE" ]]; then
            UNITY_EXECUTABLE="$CANDIDATE"
        else
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
    echo "Unity Editor executable not found. Set UNITY_EXECUTABLE env var or adjust UNITY_VERSION." >&2
    exit 1
fi

# --- Paths ---
COVERAGE_PATH="$PROJECT_PATH_NATIVE/CodeCoverage"
ARTIFACTS_PATH="$PROJECT_PATH_NATIVE/Logs/TestResults"
mkdir -p "$ARTIFACTS_PATH"
mkdir -p "$COVERAGE_PATH"

# Clean up previous coverage results
rm -rf "$COVERAGE_PATH"/*

UNITY_PID=""
FINAL_RC=0

echo "====================================="
echo "Starting Unity Code Coverage"
echo "====================================="
echo "Unity: $UNITY_EXECUTABLE"
echo "Project: $PROJECT_PATH_FOR_UNITY"
echo ""

# --- EditMode Tests + Coverage ---
echo "-------------------------------------"
echo "Running EditMode tests (with coverage)..."
echo "-------------------------------------"

"$UNITY_EXECUTABLE" \
  -batchmode -nographics \
  -projectPath "$PROJECT_PATH_FOR_UNITY" \
  -runTests -testPlatform editmode \
  -testResults "$ARTIFACTS_PATH/editmode-results.xml" \
  -logFile "$ARTIFACTS_PATH/editmode-coverage.log" \
  -enableCodeCoverage \
  -coverageResultsPath "$COVERAGE_PATH" \
  -coverageOptions "generateAdditionalMetrics;generateHtmlReport;generateBadgeReport;assemblyFilters:+GameRuntime,+LanguageUI" \
  > /dev/null 2>&1 &
UNITY_PID=$!
wait $UNITY_PID || true
RC_EDITMODE=$?
unset UNITY_PID

if [[ $RC_EDITMODE -ne 0 ]]; then
    echo "⚠️  EditMode tests encountered issues (exit code: $RC_EDITMODE)"
    FINAL_RC=$RC_EDITMODE
fi

# --- PlayMode Tests + Coverage ---
echo "-------------------------------------"
echo "Running PlayMode tests (with coverage)..."
echo "-------------------------------------"

"$UNITY_EXECUTABLE" \
  -batchmode -nographics \
  -projectPath "$PROJECT_PATH_FOR_UNITY" \
  -runTests -testPlatform playmode \
  -testResults "$ARTIFACTS_PATH/playmode-results.xml" \
  -logFile "$ARTIFACTS_PATH/playmode-coverage.log" \
  -enableCodeCoverage \
  -coverageResultsPath "$COVERAGE_PATH" \
  -coverageOptions "generateAdditionalMetrics;generateHtmlReport;generateBadgeReport;assemblyFilters:+GameRuntime,+LanguageUI" \
  > /dev/null 2>&1 &
UNITY_PID=$!
wait $UNITY_PID || true
RC_PLAYMODE=$?
unset UNITY_PID

if [[ $RC_PLAYMODE -ne 0 ]]; then
    echo "⚠️  PlayMode tests encountered issues (exit code: $RC_PLAYMODE)"
    if [[ $FINAL_RC -eq 0 ]]; then
        FINAL_RC=$RC_PLAYMODE
    fi
fi

# --- Coverage Report Check ---
echo ""
echo "====================================="
echo "Coverage Results"
echo "====================================="

# Find OpenCover XML file
COVERAGE_XML=$(find "$COVERAGE_PATH" -name "*.xml" -type f 2>/dev/null | head -n1)

if [[ -n "$COVERAGE_XML" && -f "$COVERAGE_XML" ]]; then
    echo "✅ Coverage XML generated: $COVERAGE_XML"
    
    # Extract simple coverage summary (OpenCover format)
    if command -v python3 &> /dev/null; then
        python3 - "$COVERAGE_XML" << 'PYTHON_SCRIPT'
import sys
import xml.etree.ElementTree as ET

try:
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()
    
    # Extract coverage info from OpenCover format
    summary = root.find('.//Summary')
    if summary is not None:
        seq_coverage = summary.get('sequenceCoverage', 'N/A')
        branch_coverage = summary.get('branchCoverage', 'N/A')
        visited_seq = summary.get('visitedSequencePoints', '0')
        total_seq = summary.get('numSequencePoints', '0')
        
        print(f"  Sequence Coverage: {seq_coverage}%")
        print(f"  Branch Coverage: {branch_coverage}%")
        print(f"  Lines Covered: {visited_seq} / {total_seq}")
    else:
        # Try CoverageSession format
        modules = root.findall('.//Module')
        total_covered = 0
        total_lines = 0
        for module in modules:
            for method in module.findall('.//Method'):
                for seq_point in method.findall('.//SequencePoint'):
                    total_lines += 1
                    if int(seq_point.get('vc', '0')) > 0:
                        total_covered += 1
        
        if total_lines > 0:
            coverage_pct = (total_covered / total_lines) * 100
            print(f"  Line Coverage: {coverage_pct:.2f}%")
            print(f"  Lines Covered: {total_covered} / {total_lines}")
        else:
            print("  Unable to parse coverage data.")
except Exception as e:
    print(f"  Coverage parsing error: {e}")
PYTHON_SCRIPT
    fi
else
    echo "⚠️  Coverage XML file not found."
    echo "   Check log files at: $ARTIFACTS_PATH/"
fi

# Check for HTML report
HTML_REPORT=$(find "$COVERAGE_PATH" -name "index.htm" -o -name "index.html" 2>/dev/null | head -n1)
if [[ -n "$HTML_REPORT" && -f "$HTML_REPORT" ]]; then
    echo ""
    echo "📊 HTML Report: $HTML_REPORT"
    echo "   Open in browser: open \"$HTML_REPORT\""
fi

echo ""
echo "====================================="
if [[ $FINAL_RC -eq 0 ]]; then
    echo "✅ Unity code coverage collection complete!"
else
    echo "⚠️  Some tests failed, but coverage was collected"
fi
echo "====================================="

exit $FINAL_RC
