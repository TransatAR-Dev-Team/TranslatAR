#!/usr/bin/env bash
set -e

# Setup directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Resolve ".." to a clean absolute path
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARTIFACTS_DIR="$PROJECT_ROOT/coverage-report"

# Cleanup previous run
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

echo "=========================================="
echo "  TranslatAR Test Coverage Generation"
echo "=========================================="

echo ""

# --- 1. Python Services ---
# Note: advice_service uses an underscore, others use hyphens
PYTHON_SERVICES=("backend" "stt-service" "translation-service" "summarization-service" "advice_service")

for service in "${PYTHON_SERVICES[@]}"; do
    echo ""
    echo "📊 Running coverage for: $service"

    if [ -d "$PROJECT_ROOT/$service" ]; then
        cd "$PROJECT_ROOT/$service"

        # Ensure dependencies exist (in case make clean was run)
        poetry install --quiet > /dev/null 2>&1 || true

        # Run pytest with coverage flags
        poetry run pytest --cov=. --cov-report=html:htmlcov --cov-report=json:coverage.json || true

        # Move artifacts to global folder
        if [ -d "htmlcov" ]; then
            mkdir -p "$ARTIFACTS_DIR/$service"
            cp -r htmlcov/* "$ARTIFACTS_DIR/$service/"
            cp coverage.json "$ARTIFACTS_DIR/$service/" 2>/dev/null || true
        else
            echo "⚠️  No coverage report generated for $service"
        fi
    else
        echo "⚠️  Directory $service not found, skipping..."
    fi
done

# --- 2. Web Portal ---
echo ""
echo "📊 Running coverage for: Web Portal"
if [ -d "$PROJECT_ROOT/web-portal" ]; then
    cd "$PROJECT_ROOT/web-portal"

    # --- FIX: Check for 'vite' specifically, not just the folder ---
    # This ensures we run install if node_modules exists but is empty/corrupt
    if [ ! -d "node_modules" ] || [ ! -d "node_modules/vite" ]; then
        echo "📦 Installing Node dependencies (this may take a moment)..."
        npm install --silent --no-progress
    fi

    # Run vitest with coverage using the LOCAL installation
    # We use 'npm exec' to ensure we use the project version, preventing npx prompts
    npm exec vitest -- run --coverage.enabled --coverage.reporter=html --coverage.reporter=json-summary || true

    # Move artifacts
    if [ -d "coverage" ]; then
        mkdir -p "$ARTIFACTS_DIR/web-portal"

        # Copy HTML content (Vitest puts index.html directly in coverage/ or coverage/html/ depending on version)
        if [ -d "coverage/html" ]; then
             cp -r coverage/html/* "$ARTIFACTS_DIR/web-portal/"
        else
             cp -r coverage/* "$ARTIFACTS_DIR/web-portal/" 2>/dev/null || true
        fi

        # Copy JSON summary
        if [ -f "coverage/coverage-summary.json" ]; then
            cp coverage/coverage-summary.json "$ARTIFACTS_DIR/web-portal/"
        fi
    else
        echo "⚠️  No coverage report generated for web-portal"
    fi
fi

# --- 3. Unity ---
echo ""
echo "📊 Running coverage for: Unity"

# Check if Unity is available (macOS/Windows only)
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')
UNITY_AVAILABLE=false

if [[ "$OS_NAME" == "darwin" ]]; then
    if ls -1d /Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity 2>/dev/null | head -n1 > /dev/null; then
        UNITY_AVAILABLE=true
    fi
elif [[ "$OS_NAME" == mingw* || "$OS_NAME" == cygwin* || "$OS_NAME" == msys* ]]; then
    UNITY_AVAILABLE=true
elif [[ "$OS_NAME" == "linux" ]] && [ -f "/proc/version" ] && grep -q -i "microsoft" /proc/version; then
    UNITY_AVAILABLE=true
fi

if [ "$UNITY_AVAILABLE" = true ]; then
    cd "$PROJECT_ROOT"
    
    # Run Unity coverage script
    if [ -f "$SCRIPT_DIR/run_unity_coverage.sh" ]; then
        "$SCRIPT_DIR/run_unity_coverage.sh" || true
        
        # Copy Unity coverage artifacts
        if [ -f "$PROJECT_ROOT/unity/CodeCoverage/Report/Summary.json" ]; then
            mkdir -p "$ARTIFACTS_DIR/unity"
            cp -r "$PROJECT_ROOT/unity/CodeCoverage/Report/"* "$ARTIFACTS_DIR/unity/" 2>/dev/null || true
            
            # Create a coverage.json in the format expected by dashboard
            # Extract data from Summary.json and convert to dashboard format
            python3 - "$PROJECT_ROOT/unity/CodeCoverage/Report/Summary.json" "$ARTIFACTS_DIR/unity/coverage.json" << 'PYTHON_CONVERT'
import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

summary = data.get("summary", {})
output = {
    "unity_format": True,
    "totals": {
        "covered_lines": summary.get("coveredlines", 0),
        "num_statements": summary.get("coverablelines", 0),
        "percent_covered": summary.get("linecoverage", 0)
    }
}

with open(sys.argv[2], "w") as f:
    json.dump(output, f, indent=2)
PYTHON_CONVERT
            echo "✅ Unity coverage collected"
        else
            echo "⚠️  Unity coverage report not generated"
        fi
    else
        echo "⚠️  run_unity_coverage.sh not found, skipping Unity"
    fi
else
    echo "⚠️  Unity not available on this platform, skipping..."
fi

# --- 4. Generate Dashboard ---
echo ""
echo "📈 Generating Dashboard..."
# Check if python script exists before running
if [ -f "$SCRIPT_DIR/generate_dashboard.py" ]; then
    python3 "$SCRIPT_DIR/generate_dashboard.py" "$ARTIFACTS_DIR"
else
    echo "❌ Error: scripts/generate_dashboard.py not found."
    exit 1
fi

# --- 4. Open Report ---
INDEX_PATH="$ARTIFACTS_DIR/index.html"
echo ""

if [ -f "$INDEX_PATH" ]; then
    echo "✅ Report ready at: $INDEX_PATH"

    # OS detection to open the file
    case "$(uname -s)" in
       Darwin*) open "$INDEX_PATH" ;;
       Linux*)  xdg-open "$INDEX_PATH" 2>/dev/null || echo "Open '$INDEX_PATH' in your browser." ;;
       CYGWIN*|MINGW*|MSYS*) start "$INDEX_PATH" ;;
       *) echo "Open '$INDEX_PATH' in your browser to view." ;;
    esac
else
    echo "❌ Report generation failed (index.html missing)."
    exit 1
fi
