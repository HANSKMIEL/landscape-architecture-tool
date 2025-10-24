# Contributing to Landscape Architecture Tool

This guide consolidates all development, testing, and CI/CD information for the Landscape Architecture Management Tool into a single authoritative resource.

## 🏗️ Development Setup

### Quick Start Options

#### 1. GitHub Codespaces (Recommended)
Get started immediately with zero local setup:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/HANSKMIEL/landscape-architecture-tool)

- Pre-configured with all dependencies
- VS Code with extensions installed
- PostgreSQL and Redis services ready
- Port forwarding for instant access

#### 2. Docker Setup (Local Development)
Start the full application stack:

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

#### 3. Manual Setup (Traditional Development)

**Prerequisites:**
- Node.js 20+
- Python 3.11+
- Redis (optional, for optimal caching)
- PostgreSQL (optional, for production database)

**Backend Setup:**
```bash
# Install dependencies
pip install -r requirements.txt      # Production dependencies
pip install -r requirements-dev.txt  # Development + testing dependencies

# Initialize database
export PYTHONPATH=.
flask --app src.main db upgrade

# Start backend
python src/main.py
```

**Frontend Setup:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

**Access Points:**
- Frontend: http://localhost:5174
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/

### Environment Configuration

Copy and customize the environment template:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Key configuration sections:
- **Application Environment**: Set `FLASK_ENV` (development/production)
- **Database**: Configure PostgreSQL or use default SQLite
- **Security**: Generate secure `SECRET_KEY` with `openssl rand -hex 32`
- **Redis**: Configure caching and rate limiting (optional)
- **CORS**: Set allowed origins for frontend
- **Logging**: Configure log levels and output

## 🧪 Testing

### Running Tests

**Backend Tests:**
```bash
# Run all backend tests (287 tests)
PYTHONPATH=. python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/services/ -v          # Service layer tests
python -m pytest tests/routes/ -v            # API endpoint tests
python -m pytest tests/test_basic.py -v      # Basic functionality tests

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Frontend Tests:**
```bash
cd frontend
npm test                    # Run Jest/Vitest tests
npm run test:coverage       # Run with coverage
npm run lint               # ESLint validation
npm run build              # Production build test
```

### Test Structure

**Backend Test Organization:**
```
tests/
├── conftest.py              # Test configuration and fixtures
├── fixtures/                # Test data factories
├── routes/                  # API endpoint tests
├── services/                # Business logic tests
└── test_*.py               # Basic functionality tests
```

**Test Data:**
- Uses Factory Boy and Faker for realistic test data
- Isolated test databases (SQLite in-memory)
- Comprehensive fixtures for all entities

### Current Test Status

**Backend: 273+ passing tests**
- Health endpoint validation ✅
- API documentation endpoint ✅  
- Supplier CRUD operations ✅
- Plant CRUD operations ✅
- Production configuration ✅
- Security headers ✅
- Rate limiting configuration ✅

**Frontend: 7 passing tests**
- UI component tests ✅
- Utility function tests ✅
- API service tests ✅

## 🏗️ Architecture

### Backend Architecture (Flask + SQLAlchemy)

**Modular Structure:**
```
src/
├── main.py                  # Application factory and routes
├── models/
│   ├── user.py             # Database configuration
│   └── landscape.py        # Database models
├── services/               # Business logic layer
│   ├── __init__.py        # Service classes
│   └── dashboard_service.py
├── schemas/                # Pydantic validation schemas
│   └── __init__.py        # Request/response schemas
├── routes/                 # API route blueprints
└── utils/                  # Utilities and helpers
```

**Key Features:**
- **Service Layer**: Business logic separated from API routes
- **Pydantic Validation**: Strong typing for API requests/responses
- **SQLAlchemy ORM**: Persistent database with relationships
- **Error Handling**: Structured error responses and logging
- **Database Migrations**: Version-controlled schema changes

### Frontend Architecture (React + Vite)

**Component Structure:**
```
frontend/src/
├── components/             # React components
├── services/
│   └── api.js             # API service layer
├── lib/
│   └── utils.js           # Utility functions
└── test/                   # Test files and mocks
```

## 🔄 CI/CD Pipeline

### Pipeline Overview

The CI/CD pipeline ensures code quality, security, and reliability through automated testing and validation.

**Core Testing Jobs (Parallel):**
- **Backend Testing** - SQLite and PostgreSQL testing with comprehensive coverage
- **Frontend Testing** - Build, lint, and dependency security audit
- **Code Quality** - Python linting (flake8, black, isort), security scanning (bandit)
- **Security Scanning** - Trivy vulnerability scanning and Python safety checks

**Integration & Deployment (Sequential):**
- **Integration Tests** - End-to-end API testing with real services
- **Docker Build** - Container builds with vulnerability scanning
- **Monitoring** - Pipeline status monitoring and reporting
- **DeepSource** - Code quality analysis and coverage reporting

### Pipeline Configuration

**Required Environment Variables:**
```bash
# Optional: For enhanced code quality analysis
DEEPSOURCE_DSN=https://your-deepsource-dsn@deepsource.io
```

**Pipeline Triggers:**
- Push to main/develop → Full pipeline execution
- Pull Requests to main → All jobs except deployment
- Manual triggers available from GitHub Actions tab

### Pipeline Features

**Enhanced Error Handling:**
- Migration failure reports with environment details
- Test failure reports with detailed context
- Linting reports with line-by-line feedback
- Security vulnerability reports in JSON/SARIF format
- Build failure logs with dependency information

**Security Features:**
- Dependency scanning (npm audit, Safety)
- Container security (Trivy scanning)
- Code security (Bandit security linting)
- SARIF upload to GitHub Security tab

**Monitoring & Observability:**
- Real-time job status and performance metrics
- Organized artifact collection and storage
- Enhanced service health validation
- Automated test coverage analysis

## 🔧 Code Quality Standards

### Python Code Standards

**Formatting and Style:**
```bash
# Black formatting (line length 88)
black src/ tests/ --line-length 88

# Import sorting
isort src/ tests/

# Linting
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

# Security scanning
bandit -r src/
```

**Code Quality Requirements:**
- All code must pass Black formatting
- Import organization with isort
- Flake8 linting compliance
- Security scanning with Bandit
- Type hints where appropriate
- Comprehensive docstrings

### Frontend Code Standards

**ESLint and Prettier:**
```bash
cd frontend
npm run lint              # ESLint validation
npm run lint:fix          # Auto-fix ESLint issues
npm run format            # Prettier formatting
```

**Requirements:**
- ESLint compliance with React rules
- Prettier formatting consistency
- Unused variable/import removal
- Proper React hook dependencies
- Component test coverage

### Git Workflow

**Branch Strategy:**
1. Create feature branch from main: `git checkout -b feature/description`
2. Make focused commits with descriptive messages
3. Ensure all tests pass locally
4. Push branch and create Pull Request
5. CI/CD pipeline validates changes
6. Code review and approval required
7. Merge to main triggers deployment

**Commit Message Standards:**
- Use descriptive commit messages
- Start with verb in present tense
- Include context and reasoning
- Reference issue numbers when applicable

## 🛠️ Development Workflow

### Daily Development

**Starting Development:**
```bash
# Update dependencies
git pull origin main
pip install --upgrade -r requirements-dev.txt
cd frontend && npm install --legacy-peer-deps

# Start development servers
python src/main.py        # Backend (Terminal 1)
cd frontend && npm run dev # Frontend (Terminal 2)
```

**Before Committing:**
```bash
# Run all checks locally
python -m pytest tests/ -v                    # Backend tests
cd frontend && npm test && npm run build      # Frontend tests & build
black src/ tests/                             # Format Python code
cd frontend && npm run lint                    # Frontend linting
```

### Database Operations

**Migrations:**
```bash
# Create migration for schema changes
PYTHONPATH=. flask --app src.main db migrate -m "Description of changes"

# Apply migrations to database  
PYTHONPATH=. flask --app src.main db upgrade

# Initialize migration repository (one time setup)
PYTHONPATH=. flask --app src.main db init
```

**Sample Data:**
- Sample data automatically loaded on first application startup
- Database persisted as `landscape_architecture.db`
- Dutch sample data: 3 suppliers, 3 plants, 4 products, 3 clients, 3 projects

### Adding New Features

**Backend Feature Development:**
1. **Create Models** - Add/update database models in `src/models/landscape.py`
2. **Create Schemas** - Add Pydantic validation schemas in `src/schemas/__init__.py`
3. **Create Services** - Add business logic in `src/services/`
4. **Create Routes** - Add API endpoints in `src/main.py` or blueprint files
5. **Write Tests** - Add comprehensive tests in `tests/`
6. **Update Documentation** - Update API documentation and this guide

**Frontend Feature Development:**
1. **Create Components** - Add React components in `frontend/src/components/`
2. **Add API Calls** - Update API service in `frontend/src/services/api.js`
3. **Add Styling** - Use Tailwind CSS classes for consistent styling
4. **Write Tests** - Add component and integration tests
5. **Update Navigation** - Add routes and navigation as needed

## 🔍 Debugging and Troubleshooting

### Common Issues

**Backend Issues:**
```bash
# Database connection issues
flask --app src.main db upgrade               # Apply migrations
rm landscape_architecture.db && python src/main.py  # Reset database

# Import/module issues
export PYTHONPATH=.                           # Set Python path
pip install -r requirements-dev.txt          # Ensure all deps installed

# Redis connection warnings (non-critical)
# Install Redis locally or ignore in-memory storage warning
```

**Frontend Issues:**
```bash
# Dependency conflicts
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps               # Clean install

# Build issues
npm run build                                 # Test production build
npm run preview                               # Preview production build

# Port conflicts
npm run dev -- --port 3001                   # Use different port
```

**Test Issues:**
```bash
# Backend test failures
python -m pytest tests/ -v --tb=long         # Detailed failure info
python -m pytest tests/ -k "test_name" -v    # Run specific test

# Frontend test issues
cd frontend
npm test -- --verbose                        # Detailed test output
npm test -- --watch                          # Watch mode for development
```

### Performance Monitoring

**Backend Performance:**
- Health check endpoint: `GET /health`
- API documentation: `GET /api/`
- Performance metrics: `GET /api/performance/stats` (if available)

**Database Performance:**
- SQLite for development (single file database)
- PostgreSQL recommended for production
- Connection pooling configured automatically

## 📦 Deployment

### Production Deployment Checklist

**Environment Setup:**
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for caching and rate limiting
- [ ] Generate secure SECRET_KEY (`openssl rand -hex 32`)
- [ ] Configure CORS origins for frontend domain
- [ ] Set up SSL certificates
- [ ] Configure Gunicorn workers for backend
- [ ] Set LOG_LEVEL to WARNING or ERROR
- [ ] Review and secure all environment variables

**Build Process:**
```bash
# Frontend production build
cd frontend
npm run build

# Backend production setup
pip install -r requirements.txt  # Production dependencies only
export FLASK_ENV=production
export DATABASE_URL=postgresql://...
export SECRET_KEY=your-secure-secret-key

# Start with Gunicorn
gunicorn -c gunicorn.conf.py wsgi:application
```

**Docker Deployment:**
```bash
# Build and deploy with Docker Compose
docker-compose -f docker-compose.yml up --build -d

# Health checks
docker-compose ps
curl http://localhost/health
```

### Maintenance Tasks

**Regular Updates:**
```bash
# Update dependencies (monthly)
pip install --upgrade -r requirements.txt
cd frontend && npm update

# Security audits (weekly)
pip install safety && safety check
cd frontend && npm audit

# Database maintenance
flask --app src.main db upgrade              # Apply new migrations
```

## 🚨 Emergency Procedures

### Rollback Procedures
```bash
# Rollback database migration
flask --app src.main db downgrade            # Rollback one migration

# Rollback Docker deployment
docker-compose down
git checkout previous-stable-commit
docker-compose up --build -d
```

### Critical Issue Response
1. **Stop affected services** immediately
2. **Check logs** for error details
3. **Rollback to last known good state**
4. **Create hotfix branch** for urgent fixes
5. **Deploy fix with expedited review**
6. **Post-mortem analysis** and documentation

## 📈 Performance Optimization

### Backend Optimization
- Database indexing on frequently queried fields
- API response caching with Redis
- Database connection pooling
- Query optimization and monitoring

### Frontend Optimization  
- Code splitting and lazy loading
- Image optimization and asset management
- Bundle size monitoring
- Performance budgets

## 🤝 Contributing Guidelines

### Code Review Process
- All changes require pull request review
- Automated CI/CD validation must pass
- Manual testing for UI changes
- Documentation updates for API changes
- Security review for sensitive changes

### Issue Reporting
- Use GitHub issue templates
- Include reproduction steps
- Provide environment details
- Label issues appropriately (bug, feature, enhancement)

### Feature Requests
- Discussion before implementation
- Design document for large features
- Consider backwards compatibility
- Include tests and documentation

---

## 📞 Support and Resources

**Getting Help:**
- Create GitHub issues for bugs and feature requests
- Check API documentation at `/api/` when backend is running
- Review test files for usage examples
- Consult this guide for development questions

**Key Resources:**
- **Backend API**: http://localhost:5000/api/
- **Frontend**: http://localhost:5174
- **Database**: SQLite file `landscape_architecture.db`
- **Test Coverage**: Generated in `htmlcov/` directory

**External Dependencies:**
- Flask 3.1.1 (Backend framework)
- React 19.1.0 (Frontend framework)
- SQLAlchemy 2.0.41 (Database ORM)
- Pydantic 2.11.7 (Data validation)
- Tailwind CSS 3.4.0 (Frontend styling)

This guide consolidates all development information. For specific technical details, refer to the source code and test files as the authoritative implementation reference.