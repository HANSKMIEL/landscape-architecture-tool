#!/bin/bash
# Package Synchronization Script
# Ensures V1.00D package stays in sync with main source directories

set -e

echo "🔄 Synchronizing V1.00D package with main source..."

# Configuration
MAIN_SRC="src"
MAIN_FRONTEND="frontend"
MAIN_DOCS="docs"
V1_00D_PATH="packages/v1.00D"

# Function to sync directory
sync_directory() {
    local source="$1"
    local target="$2"
    local name="$3"
    
    if [ ! -d "$source" ]; then
        echo "⚠️ Warning: Source directory $source not found"
        return 0
    fi
    
    echo "  📁 Syncing $name..."
    mkdir -p "$target"
    
    # Remove old content and copy new
    rm -rf "$target"/*
    cp -r "$source"/* "$target/"
    
    echo "  ✅ $name synchronized"
}

# Step 1: Backup current V1.00D package
BACKUP_DIR="backups/v1.00D_sync_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup at $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"
if [ -d "$V1_00D_PATH" ]; then
    cp -r "$V1_00D_PATH" "$BACKUP_DIR/"
    echo "✅ Backup created"
fi

# Step 2: Ensure V1.00D structure exists
echo "🏗️ Ensuring V1.00D package structure..."
mkdir -p "$V1_00D_PATH"/{backend,frontend,docs,deploy}

# Step 3: Sync main source to V1.00D package
echo "🔄 Synchronizing directories..."
sync_directory "$MAIN_SRC" "$V1_00D_PATH/backend" "Backend"
sync_directory "$MAIN_FRONTEND" "$V1_00D_PATH/frontend" "Frontend"  
sync_directory "$MAIN_DOCS" "$V1_00D_PATH/docs" "Documentation"

# Step 4: Copy essential files
echo "📋 Copying essential files..."
for file in requirements.txt requirements-dev.txt pyproject.toml .env.example; do
    if [ -f "$file" ]; then
        cp "$file" "$V1_00D_PATH/"
        echo "  ✅ Copied $file"
    fi
done

# Step 5: Create deployment scripts for V1.00D
echo "🛠️ Creating V1.00D deployment scripts..."
cat > "$V1_00D_PATH/deploy/start_dev.sh" << 'EOF'
#!/bin/bash
# V1.00D Development Server Startup

echo "🚀 Starting V1.00D development servers..."

# Start backend
cd backend
PYTHONPATH=. python main.py &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ V1.00D servers started"
echo "🔗 Backend: http://localhost:5000"
echo "🔗 Frontend: http://localhost:5174"
echo "🛑 Stop with: kill $BACKEND_PID $FRONTEND_PID"
EOF

chmod +x "$V1_00D_PATH/deploy/start_dev.sh"

# Step 6: Update package metadata
echo "📋 Updating package metadata..."
cat > "$V1_00D_PATH/PACKAGE_INFO" << EOF
V1.00D Development Package
Last Sync: $(date)
Source: Main development directories
Sync Method: Automated synchronization script
Backup: $BACKUP_DIR

Contents:
- Backend: Synced from src/
- Frontend: Synced from frontend/
- Docs: Synced from docs/
- Deploy: Development deployment scripts

Usage:
- Development work should be done in main source directories
- This package is for reference and testing
- Use promotion script to update V1.00: ../scripts/update_v1_from_dev.sh
EOF

# Step 7: Validate synchronization
echo "🔍 Validating synchronization..."

# Count files in each directory
MAIN_BACKEND_FILES=$(find "$MAIN_SRC" -type f | wc -l)
MAIN_FRONTEND_FILES=$(find "$MAIN_FRONTEND" -type f | wc -l)
PACKAGE_BACKEND_FILES=$(find "$V1_00D_PATH/backend" -type f | wc -l)
PACKAGE_FRONTEND_FILES=$(find "$V1_00D_PATH/frontend" -type f | wc -l)

echo "📊 Synchronization Summary:"
echo "  Backend: $MAIN_BACKEND_FILES → $PACKAGE_BACKEND_FILES files"
echo "  Frontend: $MAIN_FRONTEND_FILES → $PACKAGE_FRONTEND_FILES files"

# Check for major discrepancies
if [ $((MAIN_BACKEND_FILES - PACKAGE_BACKEND_FILES)) -gt 5 ] || [ $((PACKAGE_BACKEND_FILES - MAIN_BACKEND_FILES)) -gt 5 ]; then
    echo "⚠️ Warning: Backend file count discrepancy detected"
fi

if [ $((MAIN_FRONTEND_FILES - PACKAGE_FRONTEND_FILES)) -gt 5 ] || [ $((PACKAGE_FRONTEND_FILES - MAIN_FRONTEND_FILES)) -gt 5 ]; then
    echo "⚠️ Warning: Frontend file count discrepancy detected"
fi

# Step 8: Git operations
echo "📝 Updating git tracking..."
git add "$V1_00D_PATH"
if git diff --cached --quiet; then
    echo "📝 No changes to commit"
else
    git commit -m "Sync V1.00D package with main source - $(date)"
    echo "✅ Changes committed"
fi

echo ""
echo "✅ V1.00D package synchronization complete!"
echo "📦 Backup available at: $BACKUP_DIR"
echo "📁 Package location: $V1_00D_PATH"
echo ""
echo "🚀 To start V1.00D development servers:"
echo "   cd $V1_00D_PATH/deploy && ./start_dev.sh"
echo ""
echo "🔄 To promote to V1.00:"
echo "   ./scripts/update_v1_from_dev.sh"