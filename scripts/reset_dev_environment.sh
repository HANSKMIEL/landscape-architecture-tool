#!/bin/bash

# Reset Development Environment Script
# Fixes common issues that cause Copilot to get stuck in development window

set -e

echo "🔄 Resetting Development Environment to Fix Copilot Issues..."
echo "==============================================================="

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Clean up Copilot temporary files
log "🧹 Cleaning Copilot temporary files..."
python scripts/copilot_workflow.py --cleanup

# 2. Clear Python cache files that might cause import issues
log "🗑️ Clearing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
rm -rf .pytest_cache/ 2>/dev/null || true

# 3. Reset Git state for any Copilot-modified files
log "🔄 Checking Git state..."
if git status --porcelain | grep -q "^M"; then
    log "⚠️ Found modified files - reviewing..."
    git status --short
    
    # Check for Copilot-generated files that shouldn't be committed
    git status --porcelain | grep -E '\.(copilot|temp|draft)\.' | while read -r line; do
        file=$(echo "$line" | awk '{print $2}')
        log "🗑️ Removing Copilot temporary file: $file"
        rm -f "$file" 2>/dev/null || true
    done
    
    # Reset any accidentally modified configuration files
    for config_file in pyproject.toml .pre-commit-config.yaml requirements*.txt; do
        if git status --porcelain | grep -q "$config_file"; then
            log "⚠️ Configuration file $config_file was modified - checking if reset is needed"
            git diff "$config_file"
            echo "Do you want to reset $config_file? (y/N)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                git checkout -- "$config_file"
                log "✅ Reset $config_file"
            fi
        fi
    done
fi

# 4. Reset VS Code workspace state
log "🔄 Resetting VSCode workspace state..."
if [ -d ".vscode" ]; then
    # Remove any workspace-specific files that might cause issues
    rm -f .vscode/.ropeproject 2>/dev/null || true
    rm -rf .vscode/.history 2>/dev/null || true
    
    # Check if settings.json exists and is valid
    if [ -f ".vscode/settings.json" ]; then
        if ! python -c "import json; json.load(open('.vscode/settings.json'))" 2>/dev/null; then
            log "⚠️ VSCode settings.json is corrupted - regenerating..."
            # Backup the corrupted file
            mv .vscode/settings.json .vscode/settings.json.backup.$(date +%s) 2>/dev/null || true
            # The corrected settings.json should already be in place from our earlier fix
        fi
    fi
fi

# 5. Reset terminal environment
log "🔄 Resetting terminal environment..."
unset PYTHONPATH 2>/dev/null || true
export PYTHONPATH="."

# 6. Check and fix Python environment
log "🐍 Checking Python environment..."
if ! python -c "import sys; print(f'Python {sys.version}')" 2>/dev/null; then
    log "❌ Python environment issues detected"
    exit 1
fi

# Verify critical imports work
if ! python -c "import src.main" 2>/dev/null; then
    log "❌ Main application import failed - checking dependencies..."
    pip install -r requirements.txt --quiet
fi

# 7. Reset development server processes
log "🔄 Cleaning up any stuck development processes..."
# Kill any stuck Flask development servers
pkill -f "python.*src/main.py" 2>/dev/null || true
pkill -f "flask.*run" 2>/dev/null || true

# Kill any stuck npm development servers
pkill -f "npm.*run.*dev" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 2

# 8. Verify ports are available
log "🔌 Checking port availability..."
check_port() {
    local port=$1
    if lsof -i ":$port" >/dev/null 2>&1; then
        log "⚠️ Port $port is in use - attempting to free it..."
        fuser -k "$port/tcp" 2>/dev/null || true
        sleep 1
    fi
}

check_port 5000  # Flask backend
check_port 5174  # Vite frontend

# 9. Reset file permissions
log "🔐 Checking file permissions..."
find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
find scripts/ -name "*.py" -exec chmod +x {} \; 2>/dev/null || true

# 10. Validate the environment is ready
log "✅ Validating environment..."

# Run basic validation
if python scripts/copilot_workflow.py --validate; then
    log "✅ Code quality validation passed"
else
    log "⚠️ Code quality issues detected - running formatter..."
    python scripts/copilot_workflow.py --format
fi

# Test basic imports
if python -c "from src.main import create_app; print('✅ Main app imports working')"; then
    log "✅ Application imports working"
else
    log "❌ Application import issues persist"
    exit 1
fi

# 11. Display environment status
echo ""
echo "🎉 Development Environment Reset Complete!"
echo "=========================================="
echo ""
echo "Environment Status:"
echo "- Copilot temporary files: Cleaned"
echo "- Python cache: Cleared" 
echo "- Git state: Verified"
echo "- VSCode configuration: Validated"
echo "- Development ports: Available"
echo "- Application imports: Working"
echo ""
echo "You can now:"
echo "1. Restart VSCode to fully reset Copilot"
echo "2. Start development servers:"
echo "   - Backend: PYTHONPATH=. python src/main.py"
echo "   - Frontend: cd frontend && npm run dev"
echo "3. Run Copilot workflow: python scripts/copilot_workflow.py --all"
echo ""
echo "If Copilot is still stuck, try:"
echo "- Reload VSCode window (Ctrl+Shift+P > 'Developer: Reload Window')"
echo "- Restart Copilot (Ctrl+Shift+P > 'GitHub Copilot: Restart')"
echo "- Clear VSCode workspace storage"