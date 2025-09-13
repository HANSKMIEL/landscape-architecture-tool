# 🌿 Landscape Architecture Tool

A comprehensive web application for managing landscape architecture projects, suppliers, plants, products, and clients. 

**Current Status**: ✅ V1.00D Post-Reorganization Complete  
**Production**: 🚀 Deployed at https://optura.nl  
**Development**: 🔧 Active on V1.00D branch with workflow fixes applied

## 🏗️ V1.00 Repository Organization

This repository follows a dual-version strategy for optimal development and production stability:

### 📦 Version Packages
- **V1.00 (Protected)** - Stable production release deployed to VPS
- **V1.00D (Development)** - Active development branch for new features

```
landscape-architecture-tool/
├── src/                 # 🎯 Main backend source (V1.00D)
├── frontend/            # 🎯 Main frontend source (V1.00D)  
├── packages/
│   ├── v1.00/          # 🛡️ Protected production package
│   └── v1.00D/         # 🚧 Development package
├── archive/            # 📁 Legacy files (pre-V1.00)
└── DEV_OPS_STEPS/      # 🔧 Complete development guides
```

## 🚀 Quick Start

### For Developers
```bash
# Clone and setup development environment
git clone <repository-url>
cd landscape-architecture-tool
git checkout v1.00D

# Install dependencies and start developing
make install
make backend-test
```

### For Production Deployment
```bash
# Deploy the stable V1.00 package
cd packages/v1.00/deploy
./deploy.sh
```

### For Updates (Development → Production)
```bash
# Promote tested V1.00D changes to V1.00
./scripts/update_v1_from_dev.sh
```

## 🏢 Enterprise Features

### 🔄 V1.00 DevOps Strategy
- **Protected Production** - V1.00 package isolated from development changes
- **Automated Promotion** - Tested V1.00D changes promoted via automated script
- **Rollback Protection** - Automatic backups before V1.00 updates
- **CI/CD Pipeline** - Comprehensive testing before production promotion
- **GitHub Pages** - Automated deployment for V1.00 frontend

### 🛡️ Production Stability
- **Branch Protection** - V1.00 protected from direct modifications
- **Version Tagging** - Automatic versioning with promotion timestamps
- **Backup Management** - Automated backup retention for recovery
- **Deployment Validation** - Pre-deployment testing and validation

### 🚧 Development Workflow
- **V1.00D Development** - Work in main source directories (src/, frontend/, docs/)
- **Continuous Testing** - Full CI/CD validation on development branch
- **Package Synchronization** - V1.00D package auto-synced with main source
- **Manual Promotion** - Controlled updates to V1.00 via promotion script

### 🌐 Cloud-First Development
- **GitHub Codespaces** - Instant cloud development environment
- **VS Code Remote** - Consistent development with devcontainers
- **Container Orchestration** - Production-ready Docker Compose setup
- **OneDrive Integration** - Cloud storage and collaboration features

### 🔐 Security & Compliance
- **Automated Security Scanning** - Trivy and Bandit integration
- **Dependency Vulnerability Checking** - Safety and automated updates
- **Environment Configuration** - Secure secrets management
- **Multi-stage Docker Builds** - Minimal attack surface

### 📊 Monitoring & Analytics
- **Health Checks** - Comprehensive application monitoring
- **Performance Metrics** - Built-in performance tracking
- **Error Handling** - Centralized error management
- **Package Integrity** - Automated package validation

## 🌱 Core Features
- **Dashboard** - Overview with statistics and recent activity
- **Suppliers Management** - Complete CRUD operations for suppliers
- **Plants Catalog** - Manage plant inventory with detailed information
- **Products Management** - Track products and inventory
- **Clients Database** - Manage client information and projects
- **Projects Management** - Create and manage landscape projects

### Advanced Features
- **Plant Recommendations** - Smart suggestions based on project criteria
- **Budget Tracking** - Project cost management and reporting
- **Search & Filtering** - Advanced search across all entities
- **Dutch Localization** - Sample data and formatting for Dutch market
- **Responsive Design** - Works on desktop and mobile devices

## 📚 Documentation

Comprehensive documentation is organized in the `documentation/` directory by category:

- **📖 [Documentation Index](documentation/README.md)** - Complete documentation overview and navigation
- **🛠️ [Development](documentation/development/)** - Developer guidelines, setup, and contributing
- **🚀 [Deployment](documentation/deployment/)** - Production deployment and hosting guides  
- **🔧 [Pipeline](documentation/pipeline/)** - CI/CD troubleshooting and pipeline optimization
- **📊 [Analysis](documentation/analysis/)** - Reports, testing, and development tracking
- **📖 [Guides](documentation/guides/)** - Integration guides and advanced features
- **📋 [Project Management](documentation/project-management/)** - Roadmaps and project planning

### Quick Links
- **Getting Started**: [Setup Instructions](documentation/development/SETUP_INSTRUCTIONS.md)
- **For Developers**: [Developer Guidelines](documentation/development/DEVELOPER_GUIDELINES.md)
- **For DevOps**: [Deployment Guide](documentation/deployment/DEPLOYMENT_GUIDE.md)
- **Troubleshooting**: [Pipeline Troubleshooting](documentation/pipeline/PIPELINE_TROUBLESHOOTING.md)

### New in v2.0 (Backend Refactoring)
- **Modular Architecture** - Separated models, services, routes, and utilities
- **Persistent Database** - SQLite database with SQLAlchemy ORM
- **Data Validation** - Pydantic schemas for request validation
- **Database Migrations** - Flask-Migrate for schema management
- **Structured Error Handling** - Comprehensive error handling framework
- **Service Layer** - Business logic separation from API routes

## 🚀 Quick Start

### ⚡ Instant Cloud Development (Recommended)

Get started immediately with zero local setup:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/HANSKMIEL/landscape-architecture-tool)

**GitHub Codespaces** provides a complete development environment in the cloud:
- Pre-configured with all dependencies
- VS Code with extensions installed
- PostgreSQL and Redis services ready
- Port forwarding for instant access
- No Docker or local setup required

### 🐳 Docker Setup (Local Development)

Start the full application stack with one command:

```bash
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool

# Start all services (PostgreSQL, Redis, Backend, Frontend, Nginx)
docker-compose up --build

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# Nginx Proxy: http://localhost:80
```

### 🖥️ VS Code Remote Development

Use VS Code with devcontainers for consistent development:

1. Install [VS Code](https://code.visualstudio.com/) and [Remote-Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Clone the repository and open in VS Code
3. Click "Reopen in Container" when prompted
4. Complete environment with debugging, linting, and testing ready

### Manual Setup (Traditional Development)

For detailed manual setup instructions, see [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)

**Quick Manual Setup:**
```bash
# Backend (production dependencies only)
pip install -r requirements.txt

# For development with testing and additional tools
pip install -r requirements-dev.txt

# Start backend
export PYTHONPATH=. && python src/main.py

# Frontend (in new terminal)
cd frontend && npm install --legacy-peer-deps && npm run dev
```

**Access Points:**
- Frontend: http://localhost:5174
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/

## 📁 Project Structure

```
landscape-architecture-tool/
├── .devcontainer/             # VS Code devcontainer & Codespaces config
│   └── devcontainer.json      # Development environment specification
├── .github/                   # GitHub automation & workflows
│   ├── workflows/
│   │   └── ci.yml            # CI/CD pipeline with PostgreSQL testing
│   └── dependabot.yml       # Automated dependency updates
├── src/                       # Backend (Python/Flask)
│   ├── main.py               # Main Flask application (refactored)
│   ├── models/
│   │   ├── user.py          # Database configuration
│   │   └── landscape.py     # Database models (updated)
│   ├── routes/              # API routes (blueprints for future use)
│   │   ├── dashboard.py
│   │   ├── suppliers.py
│   │   ├── plants.py
│   │   ├── products.py
│   │   ├── clients.py
│   │   └── projects.py
│   ├── services/            # Business logic layer (NEW)
│   │   └── __init__.py     # Service classes for all entities
│   ├── schemas/             # Pydantic validation schemas (NEW)
│   │   └── __init__.py     # Request/response schemas
│   └── utils/               # Utilities
│       ├── sample_data.py   # Sample data initialization (legacy)
│       ├── db_init.py      # Database initialization (NEW)
│       └── error_handlers.py # Error handling framework (NEW)
├── frontend/                # Frontend (React/Vite)
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/
│   │   │   └── api.js      # API service layer
│   │   └── lib/
│   │       └── utils.js    # Utility functions
│   ├── Dockerfile          # Multi-stage frontend container
│   ├── package.json
│   └── vite.config.js
├── migrations/              # Database migrations (NEW)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                   # Backend tests
├── Dockerfile              # Multi-stage backend container
├── docker-compose.yml      # Multi-service orchestration
├── pyproject.toml             # Python project configuration (Black, isort, flake8, pytest)
├── .env.example            # Environment configuration template
├── SETUP_INSTRUCTIONS.md   # Comprehensive setup guide
├── ONEDRIVE_GUIDE.md       # Cloud integration guide
├── requirements.txt        # Python dependencies (updated)
└── README.md
```

## 🏗️ Architecture Overview

### Backend Architecture (v2.0)

The backend has been completely refactored from a monolithic structure to a modular, production-ready architecture:

#### **Models Layer** (`src/models/`)
- **SQLAlchemy Models**: Persistent database entities with relationships
- **Database Configuration**: Centralized database setup and configuration

#### **Services Layer** (`src/services/`)
- **Business Logic**: Core business operations separated from API routes
- **CRUD Operations**: Standardized create, read, update, delete operations
- **Data Processing**: Complex data operations and calculations

#### **Schemas Layer** (`src/schemas/`)
- **Pydantic Validation**: Input validation and data sanitization
- **Type Safety**: Strong typing for API requests and responses
- **Documentation**: Auto-generated API documentation from schemas

#### **Utilities Layer** (`src/utils/`)
- **Error Handling**: Structured error responses and logging
- **Database Initialization**: Automated database setup and sample data
- **Helper Functions**: Reusable utility functions

#### **Database Layer**
- **SQLite Database**: Persistent storage with relational integrity
- **Migrations**: Version-controlled database schema changes
- **Relationships**: Foreign key constraints and data consistency

### Key Improvements

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Scalability**: Modular structure allows for easy expansion
3. **Maintainability**: Clear code organization and documentation
4. **Data Persistence**: No more data loss on server restart
5. **Validation**: Input validation prevents data corruption
6. **Error Handling**: Consistent error responses across all endpoints
7. **Migration Support**: Database schema changes are managed and versioned

## 🔧 API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity feed

### Suppliers
- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Create new supplier (with validation)
- `PUT /api/suppliers/{id}` - Update supplier (with validation)
- `DELETE /api/suppliers/{id}` - Delete supplier

### Plants
- `GET /api/plants` - List all plants
- `POST /api/plants` - Create new plant (with validation)
- `PUT /api/plants/{id}` - Update plant (with validation)
- `DELETE /api/plants/{id}` - Delete plant

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product (with validation)
- `PUT /api/products/{id}` - Update product (with validation)
- `DELETE /api/products/{id}` - Delete product

### Clients
- `GET /api/clients` - List all clients
- `POST /api/clients` - Create new client (with validation)
- `PUT /api/clients/{id}` - Update client (with validation)
- `DELETE /api/clients/{id}` - Delete client

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project (with validation)
- `PUT /api/projects/{id}` - Update project (with validation)
- `DELETE /api/projects/{id}` - Delete project

### Project Plants (New)
- `GET /api/projects/{id}/plants` - Get all plants for a project
- `POST /api/projects/{id}/plants` - Add plant to project (with validation)
- `PUT /api/projects/{id}/plants/{plant_id}` - Update plant in project
- `DELETE /api/projects/{id}/plants/{plant_id}` - Remove plant from project
- `POST /api/projects/{id}/plants/batch` - Add multiple plants to project
- `GET /api/projects/{id}/cost-analysis` - Get project cost breakdown
- `GET /api/projects/{id}/plant-order-list` - Generate plant order list

### Plant Recommendations (New)
- `POST /api/plant-recommendations` - Get plant recommendations based on criteria
- `GET /api/plant-recommendations/criteria-options` - Get available criteria options
- `POST /api/plant-recommendations/feedback` - Submit recommendation feedback
- `GET /api/plant-recommendations/history` - Get recommendation history
- `POST /api/plant-recommendations/export` - Export recommendations to CSV
- `POST /api/plant-recommendations/import` - Import plant data from CSV

### Reports (New)
- `GET /api/reports/business-summary` - Generate business summary report (JSON/PDF)
- `GET /api/reports/project/{id}` - Generate detailed project report (JSON/PDF)
- `GET /api/reports/plant-usage` - Generate plant usage statistics
- `GET /api/reports/supplier-performance` - Generate supplier performance report

## 🔄 CI/CD Pipeline

The project uses a modernized CI/CD pipeline that ensures code quality, security, and reliability through automated testing and validation.

### Pipeline Architecture

The CI/CD pipeline consists of the following jobs that run in parallel and sequence:

#### **Core Testing Jobs** (Run in Parallel)
- **`test-backend`** - Backend testing with SQLite and PostgreSQL
- **`test-frontend`** - Frontend build, lint, and dependency security audit
- **`code-quality`** - Python linting, formatting checks, and security scanning
- **`security-scan`** - Trivy vulnerability scanning and Python safety checks

#### **Integration & Deployment Jobs** (Sequential)
- **`integration-tests`** - End-to-end API testing with real services
- **`docker-build`** - Container builds and vulnerability scanning
- **`monitoring`** - Pipeline status monitoring and reporting
- **`deepsource`** - Code quality analysis and coverage reporting
- **`deploy`** - Deployment readiness validation

### Enhanced Error Handling

The pipeline features improved error handling with detailed artifact collection:

- **Migration Failures** - Database migration issues captured with environment details
- **Test Failures** - Detailed test reports with failure context
- **Linting Issues** - Complete lint reports with line-by-line feedback
- **Security Vulnerabilities** - JSON reports with vulnerability details
- **Build Failures** - Comprehensive build logs and dependency information
- **Service Reliability** - Enhanced PostgreSQL and Redis health checks with 10-15 retry attempts

### Security Features

- **Dependency Scanning** - npm audit for frontend, Safety for Python backend
- **Container Security** - Trivy scanning for Docker images
- **Code Security** - Bandit security linting for Python code
- **SARIF Upload** - Security results uploaded to GitHub Security tab

### Monitoring & Observability

- **Pipeline Monitoring** - Real-time job status and performance metrics
- **Artifact Management** - Organized collection of build artifacts and reports
- **Health Checks** - Enhanced service health validation with timeouts
- **Coverage Reporting** - Automated test coverage analysis

### Setting Up CI/CD

#### Required Secrets
Add these to your GitHub repository secrets for full functionality:

```bash
DEEPSOURCE_DSN=https://your-deepsource-dsn@deepsource.io  # Optional: For DeepSource integration
```

#### Environment Configuration
The pipeline uses the existing `.env.example` for configuration templates.

#### Customizing the Pipeline
Edit `.github/workflows/ci.yml` to modify:
- Test timeout values
- Security scan severity levels
- Artifact retention periods
- Deployment conditions

### Pipeline Triggers

- **Push to main/develop** - Full pipeline execution
- **Pull Requests to main** - All jobs except deployment
- **Manual Triggers** - Can be run manually from GitHub Actions tab

### Artifact Collection

The pipeline automatically collects and stores:
- Test reports and coverage data
- Security scan results (SARIF format)
- Code quality reports
- Build artifacts and logs
- Failure diagnostics

## 📚 Documentation & Setup

### 📖 Comprehensive Guides
- **[SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)** - Complete setup guide for all environments
- **[ONEDRIVE_GUIDE.md](./ONEDRIVE_GUIDE.md)** - Cloud storage and collaboration setup
- **API Documentation** - Interactive docs at `/api/` when backend is running

### 🚀 Quick Start Options
1. **[GitHub Codespaces](https://codespaces.new/HANSKMIEL/landscape-architecture-tool)** - Instant cloud development
2. **Docker** - `docker-compose up --build` for full stack
3. **VS Code Remote** - Devcontainer support for consistent environment
4. **Manual Setup** - Traditional local development setup

### 🔧 Development Tools
- **Automated Testing** - CI/CD with PostgreSQL and Redis services
- **Code Quality** - Linting, formatting, and security scanning with `pyproject.toml` configuration
- **Dependency Management** - Automated updates via Dependabot
- **Health Monitoring** - Comprehensive health checks and logging
- **Environment Stabilization** - Enhanced database service reliability and connection validation

### 🛠️ Environment Setup

#### Environment Configuration
Copy the template and customize for your environment:

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
nano .env
```

Key configuration sections:
- **Application Environment**: Set `FLASK_ENV` (development/production)
- **Database**: Configure PostgreSQL or SQLite connection
- **Security**: Generate secure `SECRET_KEY` with `openssl rand -hex 32`
- **Redis**: Configure caching and rate limiting
- **CORS**: Set allowed origins for frontend
- **Logging**: Configure log levels and output

#### Local Development Setup

**Production Dependencies:**
```bash
# Install core application dependencies
pip install -r requirements.txt
```

**Development Dependencies:**
```bash
# Install development and testing dependencies (includes production deps)
pip install -r requirements-dev.txt
```

**Complete Setup:**
```bash
# Install frontend dependencies
cd frontend
npm install --legacy-peer-deps

# Initialize database
flask --app src.main db upgrade

# Seed with sample data (optional)
python scripts/dev_log.py add sample-data "Added Dutch sample data for testing"

# Run backend development server
python src/main.py

# Run frontend development server (in another terminal)
cd frontend
npm run dev
```

#### Production Setup Checklist

- [ ] Configure PostgreSQL database
- [ ] Set up Redis for caching
- [ ] Generate secure SECRET_KEY
- [ ] Configure CORS origins
- [ ] Set up SSL certificates (optional)
- [ ] Configure Gunicorn workers
- [ ] Set LOG_LEVEL to WARNING
- [ ] Review and secure environment variables

#### Maintenance Tasks

```bash
# Update dependencies
pip install --upgrade -r requirements.txt
cd frontend && npm update

# For development environments, update dev dependencies
pip install --upgrade -r requirements-dev.txt

# Run security audits
pip install safety && safety check
cd frontend && npm audit

# Check code quality (configured via pyproject.toml)
flake8 src/ tests/
black src/ tests/
isort src/ tests/
bandit -r src/

# Run comprehensive tests
python -m pytest tests/ -v
cd frontend && npm run test
```

### Project Configuration

The project uses **`pyproject.toml`** for centralized Python tool configuration:

- **Black**: Line length 120, excludes migrations and .copilot directories
- **isort**: Black-compatible profile with trailing commas, line length 120
- **ruff**: Line length 120, comprehensive linting and security checks
- **flake8**: Line length 120, complexity limit 25, specific ignore rules
- **pytest**: Verbose output, strict markers, maxfail 5, coverage integration
- **coverage**: Source tracking with appropriate exclusions

This ensures consistent formatting and testing behavior across all environments.

### Development vs Production Dependencies

This project separates production and development dependencies for optimal deployment:

- **`requirements.txt`** - Contains only production dependencies needed to run the application
- **`requirements-dev.txt`** - Contains all development dependencies including testing tools, linters, and debugging utilities (includes production dependencies via `-r requirements.txt`)
- **`requirements-test.txt`** - **REMOVED** - Use `requirements-dev.txt` instead for all development needs (see [REQUIREMENTS_GUIDE.md](documentation/development/REQUIREMENTS_GUIDE.md))

**For Production Deployment:**
```bash
pip install -r requirements.txt
```

**For Development Environment:**
```bash
pip install -r requirements-dev.txt  # Includes production dependencies via -r requirements.txt
```

**Requirements File Structure:**
- **Core Production**: Flask, SQLAlchemy, Pydantic, Redis, Gunicorn
- **Development Tools**: pytest, black, isort, flake8, bandit, safety
- **Testing Support**: factory_boy, faker, pytest-flask, pytest-cov
- **Database Testing**: psycopg2-binary for PostgreSQL integration testing
- **Development Utilities**: python-dotenv, debugpy, ipython
- **Documentation**: sphinx, sphinx-rtd-theme

### Database Operations

#### Initialize Database
```bash
# Initialize migration repository (one time)
PYTHONPATH=. flask --app src.main db init

# Create migration for schema changes
PYTHONPATH=. flask --app src.main db migrate -m "Description of changes"

# Apply migrations to database
PYTHONPATH=. flask --app src.main db upgrade
```

#### Sample Data
```bash
# Sample data is automatically loaded on first run
# Database will be created at: landscape_architecture.db
```

### Running Tests

#### Backend Tests
```bash
# Run all backend tests (28 tests available)
PYTHONPATH=. python -m pytest tests/ -v

# Results: ✅ 28 PASSED (as of July 25, 2025)
# Coverage: Health checks, API endpoints, CRUD operations, security
```

#### Frontend Tests  
```bash
cd frontend
npm run test
# Note: Frontend test suite not yet implemented
# Build verification: npm run build (✅ WORKING)
```

#### Test Status (Latest: July 25, 2025)
- **Backend Tests**: ✅ 28/28 PASSING
- **API Endpoints**: ✅ All CRUD operations working
- **Sample Data**: ✅ Loading correctly  
- **Docker Compose**: ✅ Configuration validated
- **Frontend Build**: ✅ Production build successful
- **Code Quality**: ⚠️ Style improvements needed (see [TEST_REPORT.md](./TEST_REPORT.md))

For comprehensive test results and code quality analysis, see [TEST_REPORT.md](./TEST_REPORT.md).

### Building for Production
```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
```

### Code Quality
```bash
# All formatting tools are configured in pyproject.toml

# Python linting
flake8 src/

# Python formatting  
black src/

# Import sorting
isort src/
```

## 🚀 Deployment

### Using Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
1. Build the frontend: `cd frontend && npm run build`
2. Copy built files to Flask static directory
3. Configure production WSGI server (gunicorn, uWSGI)
4. Set up reverse proxy (nginx, Apache)
5. Configure SSL certificates

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV` - Set to 'production' for production deployment
- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `SECRET_KEY` - Flask secret key for sessions

### Database
The application uses SQLite by default for development. For production, configure PostgreSQL or MySQL via the `DATABASE_URL` environment variable.

## 📝 Sample Data

The application includes comprehensive Dutch sample data:
- **3 Suppliers** - Dutch garden suppliers with realistic contact information
- **3 Plants** - Common Dutch landscape plants (Acer platanoides, Lavandula, Buxus)
- **4 Products** - Garden supplies and materials
- **3 Clients** - Dutch municipalities and private clients
- **3 Projects** - Realistic landscape projects

Data is automatically loaded on first application startup and persisted in the database.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/api/`
- Review the sample data initialization in `src/utils/db_init.py`

## 🔄 Updates

### Phase 1: Environment Stabilization (Latest - August 2025)
- **Comprehensive pyproject.toml Configuration** - Centralized configuration for Black, isort, flake8, and pytest
- **Enhanced CI/CD Pipeline** - Improved database service reliability with extended health checks and retry logic
- **Black Formatting Standardization** - Applied consistent code formatting across 74 files
- **Environment Variable Validation** - Added validation step to catch configuration issues early
- **Database Connection Hardening** - 15-attempt retry logic with 5-second intervals for PostgreSQL and Redis
- **Gitignore Cleanup** - Enhanced .gitignore to exclude Copilot temporary files and formatting artifacts

### Version 2.0 - Backend Refactoring
- Complete backend architecture refactoring
- Modular structure with services, schemas, and utilities
- Persistent SQLite database with SQLAlchemy ORM
- Pydantic validation for all API requests
- Structured error handling framework
- Database migrations with Flask-Migrate
- Comprehensive logging and monitoring

### Version 1.0 - Initial Release
- Fixed GitHub Actions CI/CD pipeline to use npm instead of pnpm
- Updated package.json with compatible dependencies
- Enhanced utils.js with comprehensive utility functions
- Improved error handling and logging
- Added Dutch localization and sample data

