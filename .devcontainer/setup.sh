#!/bin/bash

# GitHub Codespaces setup script for Landscape Architecture Tool
echo "🚀 Setting up Landscape Architecture Tool for GitHub Codespaces..."

# Determine workspace directory
if [ -d "/workspaces/landscape-architecture-tool" ]; then
    WORKSPACE_DIR="/workspaces/landscape-architecture-tool"
elif [ -d "/workspace" ]; then
    WORKSPACE_DIR="/workspace"
else
    WORKSPACE_DIR="$(pwd)"
fi

echo "📁 Using workspace directory: $WORKSPACE_DIR"

# Navigate to workspace
cd "$WORKSPACE_DIR"

# Copy environment configuration
echo "📋 Setting up environment configuration..."
if [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Copied .env.example to .env"
else
    echo "ℹ️  .env file already exists or .env.example not found"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps
cd ..

# Initialize database (SQLite for Codespaces simplicity)
echo "🗄️  Initializing database..."
export PYTHONPATH="$WORKSPACE_DIR"
python3 -c "
import sys
sys.path.insert(0, '$WORKSPACE_DIR')
from src.main import create_app
from src.utils.db_init import initialize_database, populate_sample_data

app = create_app()
with app.app_context():
    initialize_database()
    populate_sample_data()
    print('✅ Database initialized with sample data')
"

# Determine home directory
if [ -n "$CODESPACES" ]; then
    HOME_DIR="/home/codespace"
elif [ -d "/home/vscode" ]; then
    HOME_DIR="/home/vscode"
else
    HOME_DIR="$HOME"
fi

# Create helpful aliases and environment setup
echo "⚙️  Setting up development environment..."
cat >> "$HOME_DIR/.bashrc" << EOF

# Development aliases for Landscape Architecture Tool
alias start-backend="cd $WORKSPACE_DIR && PYTHONPATH=$WORKSPACE_DIR python3 src/main.py"
alias start-frontend="cd $WORKSPACE_DIR/frontend && npm run dev"
alias start-docker="cd $WORKSPACE_DIR && docker-compose up -d"

# Show available commands
alias help-dev="echo '
📋 Available development commands:
🔥 start-backend  - Start Flask backend server (port 5001)
🎨 start-frontend - Start Vite frontend server (port 5174) 
🐳 start-docker   - Start full stack with Docker Compose
📖 help-dev      - Show this help message

🌍 Your app will be available at:
- Frontend: https://{\$CODESPACE_NAME}-5174.app.github.dev
- Backend API: https://{\$CODESPACE_NAME}-5001.app.github.dev
- Health Check: https://{\$CODESPACE_NAME}-5001.app.github.dev/health

📋 Quick start:
1. Run start-backend to start the Flask API server
2. In a new terminal, run start-frontend to start React dev server
3. Open the forwarded ports to access your application
'"

# Auto-run help on login for Codespaces
if [ -n "\$CODESPACES" ]; then
    help-dev
fi
EOF

echo "🎉 Setup complete! Your Codespace is ready for development."
echo ""
echo "📋 Quick start:"
echo "1. Run 'start-backend' to start the Flask API server"
echo "2. In a new terminal, run 'start-frontend' to start the React development server"
echo "3. Open the forwarded ports to access your application"
echo ""
echo "💡 Type 'help-dev' to see all available commands"