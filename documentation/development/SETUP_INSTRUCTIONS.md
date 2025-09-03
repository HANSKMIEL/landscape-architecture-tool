# Landscape Architecture Tool - Setup Instructions

Welcome to the Landscape Architecture Management Tool! This guide provides comprehensive setup instructions for different development environments and deployment scenarios.

## 🚀 Quick Start Options

Choose your preferred development environment:

### 1. **GitHub Codespaces (Recommended for Cloud Development)**
The fastest way to get started with zero local setup required.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/HANSKMIEL/landscape-architecture-tool)

1. Click the "Open in GitHub Codespaces" button above
2. Wait for the container to build (2-3 minutes)
3. Once ready, the backend and frontend will be automatically available:
   - **Backend API**: `http://localhost:5000`
   - **Frontend**: `http://localhost:5174`
4. Start developing immediately with full VS Code integration!

### 2. **Docker Setup (Recommended for Local Development)**
Run the entire application stack with a single command.

```bash
# Clone the repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool

# Start the full application stack
docker-compose up --build

# Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:5000
# API Docs: http://localhost:5000/api/
```

### 3. **VS Code Remote Development**
Use VS Code with the devcontainer for a consistent development environment.

1. Install [VS Code](https://code.visualstudio.com/) and the [Remote-Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Clone the repository
3. Open the folder in VS Code
4. When prompted, click "Reopen in Container"
5. VS Code will build the development container and set up the environment

### 4. **Manual Setup (Traditional Development)**
Set up the backend and frontend manually on your local machine.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### For Docker Setup:
- [Docker](https://www.docker.com/get-started) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+

### For Manual Setup:
- [Python](https://www.python.org/downloads/) 3.11+
- [Node.js](https://nodejs.org/) 20+
- [PostgreSQL](https://www.postgresql.org/download/) 15+ (optional, SQLite used by default)
- [Redis](https://redis.io/download) 7+ (optional, for production features)

## 🔧 Manual Setup Instructions

### Backend Setup

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
   cd landscape-architecture-tool
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file with your configuration
   # For development, the defaults work fine
   ```

5. **Initialize Database**
   ```bash
   # Set Python path
   export PYTHONPATH=.  # On Windows: set PYTHONPATH=.
   
   # Initialize database migrations
   flask --app src.main db init
   
   # Create migration
   flask --app src.main db migrate -m "Initial migration"
   
   # Apply migrations
   flask --app src.main db upgrade
   ```

6. **Start Backend Server**
   ```bash
   # Development server
   export PYTHONPATH=. && python src/main.py
   
   # Or using Flask directly
   export PYTHONPATH=. && flask --app src.main run --port 5000 --debug
   
   # Production server (using Gunicorn)
   gunicorn -c gunicorn.conf.py wsgi:application
   ```

   Backend will be available at: `http://127.0.0.1:5000`

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   # Clean install with legacy peer deps for compatibility
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   
   Frontend will be available at: `http://localhost:5174`

4. **Build for Production**
   ```bash
   npm run build
   # Built files will be in the 'dist' directory
   ```

## 🐳 Docker Configuration

### Development with Docker Compose

The application includes a comprehensive Docker setup for easy development and production deployment.

```bash
# Start all services (backend, frontend, database, redis, nginx)
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Clean up (remove volumes)
docker-compose down -v
```

### Production Deployment

1. **Configure Environment**
   ```bash
   # Create production environment file
   cp .env.example .env.production
   
   # Update with production values:
   # - Strong SECRET_KEY
   # - Production DATABASE_URL
   # - CORS_ORIGINS for your domain
   # - SSL certificate paths
   ```

2. **Deploy with Docker**
   ```bash
   # Build and deploy
   docker-compose -f docker-compose.yml up -d --build
   
   # Or use the production script
   ./deploy-production.sh
   ```

### Individual Service Management

```bash
# Start only the database
docker-compose up db redis

# Start backend only
docker-compose up backend

# Rebuild specific service
docker-compose build backend
docker-compose up backend
```

## 🗃️ Database Setup

### SQLite (Default - Development)
No additional setup required. Database file will be created automatically at `landscape_architecture.db`.

### PostgreSQL (Production)

1. **Using Docker (Recommended)**
   ```bash
   # Included in docker-compose.yml
   docker-compose up db
   ```

2. **Manual PostgreSQL Setup**
   ```bash
   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE landscape_architecture_prod;
   CREATE USER landscape_user WITH PASSWORD 'landscape_password';
   GRANT ALL PRIVILEGES ON DATABASE landscape_architecture_prod TO landscape_user;
   \q
   
   # Update .env file
   DATABASE_URL=postgresql://landscape_user:landscape_password@localhost/landscape_architecture_prod
   ```

3. **Apply Migrations**
   ```bash
   export PYTHONPATH=. && flask --app src.main db upgrade
   ```

## 🔒 Security Configuration

### Environment Variables

Essential environment variables for production:

```bash
# Security
SECRET_KEY=your-cryptographically-strong-secret-key
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# CORS (important for production)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=WARNING
```

### SSL/TLS Setup

For production deployment with HTTPS:

1. **Obtain SSL Certificates**
   ```bash
   # Using Let's Encrypt with Certbot
   sudo certbot certonly --nginx -d yourdomain.com
   ```

2. **Update nginx.conf**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
       # ... rest of configuration
   }
   ```

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_basic.py -v
```

### Frontend Tests
```bash
cd frontend

# Run tests (when available)
npm run test

# Run linting
npm run lint

# Type checking (if TypeScript)
npm run type-check
```

### Integration Testing
```bash
# Test Docker build
docker build -t landscape-architecture-tool .

# Test full stack
docker-compose up --build
# Manual testing at http://localhost:80
```

## 🚀 Development Workflow

### Code Quality Tools

```bash
# Python formatting and linting
pip install black flake8 isort

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Frontend linting
cd frontend
npm run lint
npm run lint:fix
```

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes and Test**
   ```bash
   # Backend tests
   python -m pytest tests/
   
   # Frontend build test
   cd frontend && npm run build
   
   # Docker build test
   docker build -t test-build .
   ```

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - GitHub Actions will automatically run CI/CD pipeline
   - Dependabot will keep dependencies updated

### GitHub Repository Setup

If you're setting up a new repository or encountering Dependabot label issues:

1. **Setup GitHub Labels for Dependabot**
   ```bash
   # Automated setup (requires GitHub CLI)
   python scripts/setup_github_labels.py --create
   
   # Or check what labels are needed
   python scripts/setup_github_labels.py --dry-run
   ```

2. **Manual Label Creation**
   See [GITHUB_LABELS_SETUP.md](./GITHUB_LABELS_SETUP.md) for detailed instructions

3. **Common Dependabot Issues**
   - Missing labels: Use the setup script above
   - Network timeouts: Check [DEPENDENCY_UPDATE_PROCEDURES.md](../deployment/DEPENDENCY_UPDATE_PROCEDURES.md)

## 📚 Additional Resources

### API Documentation
- **Interactive API Docs**: `http://localhost:5000/api/` (when backend is running)
- **Health Check**: `http://localhost:5000/health`

### OneDrive Integration
For OneDrive setup and cloud storage integration, see: [ONEDRIVE_GUIDE.md](./ONEDRIVE_GUIDE.md)

### Project Structure
```
landscape-architecture-tool/
├── src/                    # Backend Python/Flask application
│   ├── main.py            # Main Flask application
│   ├── models/            # Database models
│   ├── routes/            # API routes
│   ├── services/          # Business logic
│   ├── schemas/           # Pydantic validation schemas
│   └── utils/             # Utility functions
├── frontend/              # Frontend React/Vite application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── lib/          # Utilities
│   └── package.json
├── migrations/            # Database migrations
├── tests/                # Backend tests
├── .devcontainer/        # VS Code devcontainer config
├── .github/              # GitHub Actions & Dependabot
├── docker-compose.yml    # Multi-container setup
├── Dockerfile           # Backend container
└── requirements.txt     # Python dependencies
```

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

2. **Database Connection Issues**
   ```bash
   # Reset database
   rm landscape_architecture.db
   export PYTHONPATH=. && flask --app src.main db upgrade
   ```

3. **Frontend Build Issues**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

4. **Docker Issues**
   ```bash
   # Clean up Docker
   docker-compose down -v
   docker system prune -a
   ```

### Getting Help

- **Issues**: Create an issue on [GitHub](https://github.com/HANSKMIEL/landscape-architecture-tool/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/HANSKMIEL/landscape-architecture-tool/discussions)
- **Documentation**: Check the [README.md](./README.md)

## 🎯 Next Steps

After setup, you can:

1. **Explore the Application**
   - Visit the frontend to see the dashboard
   - Check the API documentation
   - Review sample data

2. **Start Development**
   - Add new features to the codebase
   - Customize the UI components
   - Extend the API endpoints

3. **Deploy to Production**
   - Use the Docker setup for deployment
   - Configure SSL certificates
   - Set up monitoring and backups

Happy coding! 🚀