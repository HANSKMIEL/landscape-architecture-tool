# Landscape Architecture Tool - Developer Instructions

**ALWAYS follow these instructions first.** Only search for additional information or run exploratory bash commands if the information provided here is incomplete or found to be in error.

The Landscape Architecture Tool is a Python Flask backend with React/Vite frontend for managing landscape architecture projects, suppliers, plants, products, and clients.

## CRITICAL: Build and Test Timeouts

**NEVER CANCEL any build or test command.** Always use proper timeouts:

- **Backend tests**: 120 seconds (takes ~50 seconds) 
- **Frontend build**: 180 seconds (takes ~7 seconds) 
- **Frontend tests**: 60 seconds (takes ~8 seconds with some known failures)
- **Docker build**: 300+ seconds (CURRENTLY FAILS - Dockerfile syntax error)
- **Full test suite**: 240 seconds (takes ~58 seconds with mixed results)
- **pip install**: 600 seconds (takes ~1.7 minutes)

## Bootstrap and Build Process

### Initial Setup Commands
Run these commands in order when working with a fresh clone:

```bash
# 1. Install all dependencies (takes ~1.5 minutes)
make install

# 2. Build both backend and frontend (takes ~23 seconds)
make build

# 3. Run backend tests to validate setup (takes ~50 seconds)
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
# Build Docker image (CURRENTLY FAILS - Dockerfile has syntax error on line 37)
# docker build -t landscape-architecture-tool .  # DO NOT USE - BROKEN

# Run with Docker Compose (includes PostgreSQL and Redis)
docker compose up --build  # Note: use 'docker compose' (with space), not 'docker-compose'
```

**KNOWN ISSUE**: The Dockerfile currently has a syntax error in a multi-line Python RUN command. Docker builds will fail until this is fixed.

### Production Deployment

For production deployment, comprehensive guides are available:

- **[Production Deployment Guide](docs/PRODUCTION_DEPLOYMENT.md)** - Complete production setup instructions
- **[Hostinger Deployment Guide](docs/HOSTINGER_DEPLOYMENT_GUIDE.md)** - Hostinger-specific deployment process  
- **[General Deployment Guide](documentation/deployment/DEPLOYMENT_GUIDE.md)** - VPS deployment with N8n integration

**Key Production Features:**
- Zero-downtime deployment system
- SSL certificate automation (Let's Encrypt)
- Production environment configuration (`.env.production.template`)
- Enhanced security settings and monitoring
- Automated backup and recovery procedures

## Architecture and Patterns

### Database Transaction Patterns

**CRITICAL**: Always use proper transaction isolation in tests. The repository uses enhanced SAVEPOINT-based isolation to handle edge cases:

```python
# In tests/conftest.py - Enhanced transaction handling
@pytest.fixture(scope="session")
def connection(engine):
    conn = engine.connect()
    
    # Always create reversible outer transaction for consistent isolation
    if conn.in_transaction():
        # Connection already in transaction - create savepoint for isolation
        outer_tx = conn.begin_nested()
    else:
        # Connection not in transaction - create regular transaction
        outer_tx = conn.begin()
    
    try:
        yield conn
    finally:
        if outer_tx and outer_tx.is_active:
            outer_tx.rollback()
        if not conn.closed:
            conn.close()
```

**Key Patterns**:
- Always use `conn.begin_nested()` for SAVEPOINT-based isolation when `conn.in_transaction()` is true
- Use regular `conn.begin()` for fresh connections
- Always rollback transactions in test cleanup
- Handle both transaction states consistently

### Service Layer Patterns

All business logic should follow the service layer pattern:

```python
# Example: src/services/base_service.py
class BaseService:
    def __init__(self, db_session):
        self.db = db_session
    
    def create(self, data):
        try:
            instance = self.model(**data)
            self.db.add(instance)
            self.db.commit()
            return instance
        except Exception:
            self.db.rollback()
            raise
```

### API Route Patterns

All API routes should follow these patterns:

```python
# Example: src/routes/suppliers.py
@suppliers_bp.route('/', methods=['POST'])
def create_supplier():
    try:
        data = request.get_json()
        # Validate with schema
        supplier = supplier_service.create(data)
        return jsonify({"supplier": supplier.to_dict()}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Supplier creation failed: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

## Testing and Validation

### Backend Testing
```bash
# Run all backend tests (493 tests, takes ~50 seconds)
make backend-test

# Expected results: ~174-179 tests pass, ~5 tests may fail due to test data isolation
# Core functionality works despite some test failures

# Run specific test file
PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/test_basic.py -v

# Run with coverage
PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/ --cov=src --cov-report=html
```

### Frontend Testing
```bash
# Frontend has mixed Jest/Vitest setup - use vitest for better compatibility
cd frontend && npm run test:vitest:run

# Expected results: ~45/47 tests pass, ~2 tests may fail due to timeout/accessibility issues
# Takes ~8 seconds to complete

# For watch mode during development
cd frontend && npm run test:vitest:watch

# Note: Some tests have timeout and accessibility issues documented as known issues
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

## 🎯 MotherSpace Orchestration System

**CRITICAL**: The repository implements a comprehensive multi-space orchestration system for optimal development harmony and task coordination.

### MotherSpace Orchestrator (`.github/workflows/motherspace-orchestrator.yml`)
- **Master orchestrator** that analyzes all spaces for optimal harmony (target: ≥85% harmony score)
- **Task delegation** in chronological development order with quality/security checks
- **Issue/PR optimization** for efficient cross-space collaboration
- **Harmony monitoring** with automated intervention and comprehensive system analysis
- **Cross-space communication** coordination and conflict resolution
- **Triggers**: Issues, PRs, workflow completions, scheduled every 2 hours, manual dispatch

### Daughter Space - UI/UX Manager (`.github/workflows/daughter-space-uiux.yml`)
- **Visual appeal analysis** with accessibility and responsive design assessment
- **User workflow optimization** including data import/export evaluation  
- **Integration requirement reporting** with detailed enhancement recommendations
- **"Daughter-Integration Manager" issues** for major integration needs (manual assignment)
- **Professional UI standards** enforcement and enhancement guidance
- **Triggers**: Issues labeled 'daughter' or 'ui-ux', manual dispatch with target issue

### IntegrationManager Space (`.github/workflows/integrationmanager-space.yml`)
- **Modules repository creation** and management for external integrations
- **Cross-profession adaptation** for Architecture, Engineering, Planning, Design
- **External system integration** (Vectorworks, CRM, AI, APIs)
- **Module development analysis** with priority recommendations
- **Repository synchronization** between main tool and modules repo
- **Triggers**: Issues labeled 'integration-manager' or 'integration', manual dispatch

### Space Communication Patterns

**MotherSpace → All Spaces:**
```yaml
# Harmony monitoring and task delegation
harmony_score: 85%  # Target threshold
delegation_queue: chronological_order
quality_checks: [security, functionality, efficiency]
intervention_mode: automatic_when_below_threshold
```

**Daughter → MotherSpace Reporting:**
```yaml
# UI/UX analysis and integration requirements
analysis_types: [visual_appeal, user_workflow, data_management, accessibility]
report_format: comprehensive_github_comment
integration_issues: "Daughter-Integration Manager [Date Time]"
assignment: manual_to_HANSKMIEL
```

**IntegrationManager → Cross-Repo:**
```yaml
# Module development and external integration
modules_repo: landscape-modules
supported_integrations: [vectorworks, crm, ai, apis]
cross_profession: [architecture, engineering, planning, design]
sync_interval: 6_hours
```

## CI/CD and Automation Patterns

### GitHub Workflows

The repository includes automated workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`):
   - Runs on every push and PR
   - Executes formatting, linting, tests
   - Enhanced security scanning with bandit and safety
   - Generates coverage reports

2. **Enhanced Deployment** (`.github/workflows/enhanced-deployment.yml`):
   - Zero-downtime deployment with parallel testing
   - Supports staging, production, and both environments
   - Health checks and automatic rollback capabilities
   - Manual trigger with environment selection

3. **Production Deployment** (`.github/workflows/production-deployment.yml`):
   - Production-ready deployment pipeline
   - Comprehensive testing before deployment
   - Container registry integration (GHCR)
   - Support for staging, production, and hotfix deployments

4. **Nightly Maintenance** (`.github/workflows/nightly-maintenance.yml`):
   - Runs at 19:30 Europe/Amsterdam time (configurable via REPO_TZ variable)
   - Repository cleanup, security checks, health monitoring
   - Manual trigger available via workflow_dispatch

5. **Post-Merge Automation** (`.github/workflows/post-merge.yml`):
   - Analyzes changes for follow-up requirements
   - Auto-creates issues for API, N8n, and documentation reviews
   - Processes README auto-update markers

6. **Issue Verification** (`.github/workflows/verify-issue-closed.yml`):
   - Validates critical issues after closure
   - Runs appropriate tests based on issue type
   - Adds validation comments

### N8n Workflow Integration

The repository includes N8n workflow templates in `n8n-workflows/`:

```python
# Trigger N8n workflows from application code
import requests

def trigger_client_onboarding(client_id, client_name, client_email):
    requests.post(
        'http://n8n:5678/webhook/client-onboarding',
        json={
            'client_id': client_id,
            'client_name': client_name,
            'client_email': client_email,
            'timestamp': datetime.now().isoformat()
        }
    )
```

**Available Workflows**:
- `client-onboarding.json` - Automated client welcome process
- `project-milestone-tracking.json` - Project progress notifications
- `inventory-management.json` - Stock level monitoring

### Pre-commit Hooks

Always run pre-commit hooks before committing:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Hooks include:
# - Black formatting
# - Ruff linting with security checks
# - Import sorting with isort
# - Automated validation
```

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
# Expected: JSON response with "status": "healthy" and database status

# Test API functionality
curl http://localhost:5000/api/suppliers
# Expected: JSON response with suppliers list (should show 3-4 suppliers)

# Test dashboard statistics
curl http://localhost:5000/api/dashboard/stats
# Expected: JSON with supplier, plant, and project counts
```

### 2. Frontend Integration Testing
```bash
# Start both servers and test integration
# Backend: PYTHONPATH=. python src/main.py (port 5000)
# Frontend: cd frontend && npm run dev (port 5174)

# Test frontend loads
curl http://localhost:5174/
# Expected: HTML response with React application

# Manual browser testing:
# - Navigate to http://localhost:5174/
# - Verify dashboard loads with charts and statistics
# - Test navigation to http://localhost:5174/suppliers
# - Verify suppliers page shows data and CRUD functionality
```

### 3. CRUD Operations Testing
```bash
# Test creating new supplier
curl -X POST http://localhost:5000/api/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Supplier",
    "contact_person": "Test Person",
    "email": "test@example.com",
    "phone": "123-456-7890",
    "address": "Test Address",
    "city": "Test City",
    "postal_code": "12345",
    "country": "Netherlands"
  }'

# Verify supplier count increased
curl http://localhost:5000/api/suppliers | jq '.suppliers | length'
# Expected: Count should increase by 1
```

### 4. End-to-End Application Testing
```bash
# Complete application workflow test:
# 1. Start both servers
# 2. Open browser to http://localhost:5174/
# 3. Verify dashboard displays with Dutch text and working charts
# 4. Navigate to Suppliers page
# 5. Verify supplier data displays correctly
# 6. Test "Add Supplier" button functionality
# 7. Navigate to other pages (Plants, Projects, etc.)
# 8. Verify no JavaScript console errors
```

### 5. Development Workflow Validation
```bash
# Test complete development workflow
make clean && make install && make build && make backend-test && make lint
# Expected: All commands complete successfully with acceptable results

# Test database operations
PYTHONPATH=. flask --app src.main db current
# Expected: No errors, shows current migration status

# Test health monitoring
python scripts/pipeline_health_monitor.py
# Expected: Generates health report with status overview
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
.env.production.template # Production environment configuration
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

### Documentation Structure
```
docs/
├── PRODUCTION_DEPLOYMENT.md          # Production deployment guide
├── HOSTINGER_DEPLOYMENT_GUIDE.md     # Hostinger-specific setup
├── COMPREHENSIVE_DEVELOPMENT_STATUS.md # Complete feature status
├── SPACE_OVERVIEW.md                 # Copilot Space usage guide
└── ARCHITECTURE.md                   # Detailed system architecture

documentation/
├── deployment/                       # Deployment guides and procedures
├── development/                      # Development guidelines and setup
└── pipeline/                         # CI/CD documentation and troubleshooting
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
- **Dockerfile syntax error**: Current Dockerfile fails on line 37 due to malformed multi-line Python RUN command
- **Command change**: Use `docker compose` (with space) instead of `docker-compose`
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

## Current Test Status and Known Issues

### Test Results Summary (Last Validated: August 28, 2025)

**Backend Tests**: ✅ **174/179 PASSING** (~97% pass rate)
- Total test time: ~50 seconds
- 5 tests failing in plant routes due to test data isolation issues
- Core functionality fully operational despite test failures

**Frontend Tests**: ⚠️ **45/47 PASSING** (~96% pass rate)
- Total test time: ~8 seconds 
- 2 tests failing: 1 timeout issue, 1 accessibility violation
- All core components render and function correctly

**Application Status**: ✅ **FULLY FUNCTIONAL**
- Backend API: All endpoints working (health, suppliers, plants, products, clients, projects)
- Frontend UI: Dashboard, navigation, and CRUD operations working
- Database: SQLite initializes correctly with sample data
- CRUD Operations: Create, read, update operations validated

### Known Issues

**1. Docker Build Failure**
- Issue: Dockerfile syntax error on line 37 (malformed multi-line Python RUN command)
- Impact: Cannot build Docker containers
- Workaround: Use development servers directly
- Status: Requires Dockerfile fix

**2. Backend Test Failures**
- Issue: 5 plant route tests fail due to test data contamination between tests
- Files affected: `tests/routes/test_plant_routes.py`
- Impact: Tests fail but functionality works correctly
- Status: Test isolation needs improvement

**3. Frontend Test Issues**
- Issue: 1 timeout test (5000ms), 1 accessibility heading order violation
- Files affected: `src/components/__tests__/Projects.test.jsx`  
- Impact: Tests fail but components work correctly
- Status: Test configuration and accessibility fixes needed

**4. Docker Compose Command**
- Issue: Instructions referenced `docker-compose` (deprecated)
- Correct: Use `docker compose` (with space) 
- Status: ✅ Fixed in instructions

### Validation Screenshots

The application has been visually validated with working screenshots:
- Dashboard with Dutch localization, charts, and statistics
- Suppliers page showing 4 suppliers with CRUD functionality
- Navigation working between all major sections
- No JavaScript console errors in core functionality

## Phase 4 Prevention Measures

The repository includes comprehensive CI/CD problem prevention:

- **Pre-commit hooks**: Automatically run code quality checks
- **VSCode integration**: Configured for optimal Copilot experience  
- **Automated validation**: Scripts for comprehensive code validation
- **Health monitoring**: Pipeline status monitoring and reporting

Use `python scripts/phase4_validation.py` for comprehensive validation of prevention measures.

## Repository Organization and Clutter Management

### File Organization Structure

**ALWAYS organize generated files appropriately to prevent root directory clutter:**

```
reports/
├── validation/          # automated_validation_report_*.json
├── health/             # pipeline_health_report_*.json  
└── security/           # bandit-report.json, safety-report.json

docs/
├── solutions/          # *_SOLUTION*.md, *_SUMMARY*.md
└── planning/           # *_PLAN*.md, *_ROADMAP*.md, dev_log.md

archive/                # Historical files no longer actively used
```

### Clutter Prevention Rules

**Scripts and tools should save outputs to appropriate subfolders:**

```python
# Good: Save reports to appropriate subfolder
report_path = f"reports/validation/automated_validation_report_{timestamp}.json"

# Bad: Save reports to root directory  
report_path = f"automated_validation_report_{timestamp}.json"
```

**The `.gitignore` includes patterns to prevent root clutter:**
- `/*_SOLUTION*.md` → should go in `docs/solutions/`
- `/*_PLAN*.md` → should go in `docs/planning/`
- `*_report_*.json` → should go in `reports/*/`

### Space Management Automation

**Automated workflows monitor and maintain Copilot Space effectiveness:**

1. **Space Update Detection**: Triggers when architecture, workflows, or patterns change
2. **Clutter Monitoring**: Alerts when root directory accumulates >10 loose files
3. **Test Failure Automation**: Creates issues with sub-issues for systematic bug resolution

**Key workflows:**
- `.github/workflows/space-management.yml` - Weekly space validation
- `.github/workflows/test-failure-automation.yml` - Automatic issue creation for test failures
- Clutter prevention via enhanced `.gitignore` and folder structure

### Copilot Space Validation

**Use these prompts to test space effectiveness after updates:**

```
"Explain the database transaction isolation pattern with code examples"
"Show me how to add a new API route following our conventions"  
"What's our current testing strategy and how do I add tests?"
"How should I organize generated reports and prevent clutter?"
"Create a new service following our transaction patterns"
```

**Space files to maintain:**
- `.github/copilot-instructions.md` - This file with all patterns and conventions
- `docs/SPACE_OVERVIEW.md` - Overview and usage guide
- `docs/ARCHITECTURE.md` - Detailed architecture documentation

---

**Remember**: Always follow these instructions first. Search or run exploratory commands only when information here is incomplete or incorrect. Focus on the validated commands and timeout values provided.
