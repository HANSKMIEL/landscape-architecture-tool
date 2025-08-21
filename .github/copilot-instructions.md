# Landscape Architecture Tool - Developer Instructions

**ALWAYS follow these instructions first.** Only search for additional information or run exploratory bash commands if the information provided here is incomplete or found to be in error.

The Landscape Architecture Tool is a Python Flask backend with React/Vite frontend for managing landscape architecture projects, suppliers, plants, products, and clients.

## CRITICAL: Build and Test Timeouts

**NEVER CANCEL any build or test command.** Always use proper timeouts:

- **Backend tests**: 120 seconds (takes ~35 seconds)
- **Frontend build**: 180 seconds (takes ~7 seconds) 
- **Docker build**: 300+ seconds (takes ~2 minutes, can be longer)
- **Full test suite**: 240 seconds (takes ~40 seconds with mixed results)
- **pip install**: 600 seconds (takes ~1.5 minutes)

## Bootstrap and Build Process

### Initial Setup Commands
Run these commands in order when working with a fresh clone:

```bash
# 1. Install all dependencies (takes ~1.5 minutes)
make install

# 2. Build both backend and frontend (takes ~23 seconds)
make build

# 3. Run backend tests to validate setup (takes ~35 seconds)
make backend-test

# 4. Run linting to check code quality (takes ~4 seconds)  
make lint
```

**NEVER CANCEL**: All build commands require patience. Docker builds can take 2+ minutes.

### Development Servers

Start development servers for active development:

```bash
# Backend server (runs on http://localhost:5000)
PYTHONPATH=. python src/main.py

# Frontend server (runs on http://localhost:5174) - in separate terminal
cd frontend && npm run dev
```

### Docker Build and Deployment

```bash
# Build Docker image (NEVER CANCEL - takes 2+ minutes, set 300+ second timeout)
docker build -t landscape-architecture-tool .

# Run with Docker Compose (includes PostgreSQL and Redis)
docker-compose up --build
```

## Testing and Validation

### Backend Testing
```bash
# Run all backend tests (456 tests, takes ~35 seconds)
make backend-test

# Run specific test file
PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/test_basic.py -v

# Run with coverage
PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/ --cov=src --cov-report=html
```

### Frontend Testing
```bash
# Frontend has mixed Jest/Vitest setup - use vitest for better compatibility
cd frontend && npm run test:vitest

# Note: Some tests have Jest/Vitest compatibility issues documented as known issues
```

### Full Application Testing
```bash
# Test health endpoint (should return JSON with status)
curl http://localhost:5000/health

# Test API endpoints
curl http://localhost:5000/api/suppliers

# Test frontend accessibility  
curl http://localhost:5174/
```

## Code Quality and Validation

### Pre-commit and Code Quality
```bash
# Format and validate code (takes ~4 seconds)
make lint

# Use Copilot workflow helper for comprehensive validation
python scripts/copilot_workflow.py --all

# Check pipeline health status
python scripts/pipeline_health_monitor.py
```

### Database Operations
```bash
# Run database migrations
PYTHONPATH=. flask --app src.main db upgrade

# Check migration status
PYTHONPATH=. flask --app src.main db current

# Create new migration (if needed)
PYTHONPATH=. flask --app src.main db migrate -m "Description"
```

## Validation Scenarios

**ALWAYS test these scenarios after making changes:**

### 1. Basic Application Functionality
```bash
# Start backend server
PYTHONPATH=. python src/main.py

# In separate terminal, test health endpoint
curl http://localhost:5000/health
# Expected: JSON response with "status": "healthy"

# Test API functionality
curl http://localhost:5000/api/suppliers
# Expected: JSON response with suppliers list
```

### 2. Frontend Integration Testing
```bash
# Start both servers and test integration
# Backend: PYTHONPATH=. python src/main.py (port 5000)
# Frontend: cd frontend && npm run dev (port 5174)

# Test frontend loads
curl http://localhost:5174/
# Expected: HTML response with React application
```

### 3. Build Validation
```bash
# Validate full build process works
make build
# Expected: Both frontend and backend build successfully

# Validate Docker build 
docker build -t test-build .
# Expected: Successful Docker image creation (NEVER CANCEL - 2+ minutes)
```

## Repository Structure and Key Locations

### Backend (Python/Flask)
```
src/
├── main.py              # Main Flask application entry point
├── models/             # SQLAlchemy database models
│   ├── landscape.py    # Core business models (Plant, Project, etc.)
│   └── user.py         # User authentication models
├── routes/             # API route blueprints
│   ├── dashboard.py    # Dashboard statistics endpoints
│   ├── suppliers.py    # Supplier CRUD operations
│   ├── plants.py       # Plant management endpoints
│   ├── products.py     # Product management endpoints
│   ├── clients.py      # Client management endpoints
│   └── projects.py     # Project management endpoints
├── services/           # Business logic layer
├── schemas/            # Pydantic validation schemas
└── utils/              # Utility functions and helpers
    ├── db_init.py      # Database initialization
    └── error_handlers.py # Error handling framework
```

### Frontend (React/Vite)
```
frontend/
├── src/
│   ├── components/     # React UI components
│   ├── services/       
│   │   └── api.js      # API service layer for backend communication
│   └── lib/
│       └── utils.js    # Frontend utility functions
├── package.json        # Frontend dependencies and scripts
└── vite.config.js      # Vite build configuration
```

### Key Configuration Files
```
pyproject.toml          # Python tool configuration (Black, isort, flake8)
.pre-commit-config.yaml # Pre-commit hooks configuration
docker-compose.yml      # Multi-service container orchestration
.env.example           # Environment variables template
requirements.txt       # Python production dependencies
requirements-dev.txt   # Python development dependencies
```

### Scripts and Automation
```
scripts/
├── copilot_workflow.py        # Copilot integration helper
├── pipeline_health_monitor.py # System health monitoring
├── phase4_validation.py       # Comprehensive validation
└── code_quality_check.py      # Code quality validation
```

## Environment Variables

Required environment variables (documented in `.env.example`):
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=development|testing|production

# Optional
DEBUG=true|false
```

## Common Development Tasks

### Add New Feature
1. **Always run tests first**: `make backend-test` to ensure current state
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Develop with validation**: Make changes, run `make lint` frequently
4. **Test thoroughly**: Run validation scenarios from this guide
5. **Pre-commit validation**: `python scripts/copilot_workflow.py --all`

### Fix Bug
1. **Reproduce issue**: Use validation scenarios to confirm bug
2. **Write test**: Add test that reproduces the bug in appropriate test file
3. **Fix issue**: Make minimal changes to resolve the bug
4. **Validate fix**: Run `make backend-test` and `make lint`
5. **Test manually**: Use validation scenarios to confirm fix

### Update Dependencies
1. **Check current state**: `make backend-test` to baseline
2. **Update requirements**: Modify `requirements.in` or `requirements-dev.in`
3. **Compile requirements**: `./scripts/compile_requirements.sh`
4. **Test changes**: `make install && make backend-test`
5. **Validate**: Ensure all tests still pass

## Troubleshooting

### Common Issues and Solutions

**Build Failures:**
- Run `make clean` to clear build artifacts
- Check `pip install -r requirements-dev.txt` for dependency issues
- Verify Node.js version compatibility for frontend

**Test Failures:**
- Database issues: Check if SQLite is accessible for tests
- Import errors: Verify `PYTHONPATH=.` is set for test runs
- Frontend test issues: Known Jest/Vitest compatibility - use vitest when possible

**Frontend Issues:**
- Module resolution: Check `import.meta.env` usage in `src/services/api.js`
- Build issues: Clear `node_modules` and reinstall with `npm ci --legacy-peer-deps`

**Docker Issues:**
- Build timeouts: NEVER CANCEL - Docker builds take 2+ minutes
- Port conflicts: Ensure ports 5000 (backend) and 5174 (frontend) are available

### Emergency Commands
```bash
# Reset development environment
make clean && make install

# Bypass pre-commit checks (emergency only)
git commit --no-verify

# Skip environment validation
export SKIP_ENV_CHECK=1

# Health check
python scripts/pipeline_health_monitor.py
```

## Phase 4 Prevention Measures

The repository includes comprehensive CI/CD problem prevention:

- **Pre-commit hooks**: Automatically run code quality checks
- **VSCode integration**: Configured for optimal Copilot experience  
- **Automated validation**: Scripts for comprehensive code validation
- **Health monitoring**: Pipeline status monitoring and reporting

Use `python scripts/phase4_validation.py` for comprehensive validation of prevention measures.

---

**Remember**: Always follow these instructions first. Search or run exploratory commands only when information here is incomplete or incorrect. Focus on the validated commands and timeout values provided.
