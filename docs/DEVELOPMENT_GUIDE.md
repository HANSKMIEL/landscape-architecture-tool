# Development Guide: Engineering Velocity Framework

This guide implements the comprehensive framework for engineering velocity based on modern software development best practices. It covers five core pillars that transform development from a series of frustrating hurdles into a smooth, professional, and sustainable engineering practice.

## Table of Contents

1. [Bulletproof Development Environment](#1-bulletproof-development-environment)
2. [Disciplined Version Control](#2-disciplined-version-control)
3. [Architecture for Maintainability](#3-architecture-for-maintainability)
4. [Proactive Code Quality & Automation](#4-proactive-code-quality--automation)
5. [Systematic Debugging Framework](#5-systematic-debugging-framework)

---

## 1. Bulletproof Development Environment

### Goal: Environment Parity

**Principle**: "It works on my machine" is a red flag, not a solution.

The development environment must be a high-fidelity simulation of production to prevent environment-specific bugs and configuration battles.

### Current Implementation

#### Docker & Docker Compose
We use containerization to ensure consistent environments across all development machines:

```bash
# Start the full stack with Docker Compose
docker-compose up --build

# Services included:
# - PostgreSQL database
# - Redis cache
# - Backend API (Flask)
# - Frontend (React/Vite)
# - Nginx reverse proxy
```

#### Environment Configuration
- `.env.example` - Template for required environment variables
- `.env.production.template` - Production configuration template
- All sensitive data in `.env` (gitignored)

#### Makefile Commands
Standardized commands for all developers:

```bash
make install        # Install all dependencies
make build          # Build frontend and backend
make test           # Run comprehensive test suite
make lint           # Run code quality checks
make backend-test   # Run backend tests only
make frontend-test  # Run frontend tests only
```

### Best Practices

1. **Never commit environment-specific configuration** to version control
2. **Always use the Makefile** for standard operations
3. **Document any manual setup steps** immediately if they can't be automated
4. **Test in Docker** before claiming a feature is complete
5. **Keep dependencies up to date** using Dependabot

### Quick Start

```bash
# Clone repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Install and build
make install
make build

# Verify setup
make test
```

---

## 2. Disciplined Version Control

### Goal: Predictable, Safe Development Workflow

**Principle**: "The lifetime of a branch is inversely proportional to the health of a project."

### Branching Strategy

We follow a **GitHub Flow** variant with production protection:

#### Branch Types

1. **main** - Production branch
   - Protected from direct pushes
   - Always deployable
   - Deployed to https://optura.nl

2. **V1.00D** - Development branch
   - Active development work
   - Auto-deploys to http://72.60.176.200:8080
   - Promotion path to main via scripts

3. **Feature Branches** - Short-lived work branches
   - Pattern: `feat/feature-name`, `fix/bug-name`, `chore/task-name`
   - Created from V1.00D
   - Merged back via Pull Request
   - **Deleted immediately after merge**

### Workflow Process

#### For New Features

```bash
# 1. Start from latest V1.00D
git checkout V1.00D
git pull origin V1.00D

# 2. Create feature branch
git checkout -b feat/add-supplier-search

# 3. Make changes, commit frequently
git add .
git commit -m "feat(suppliers): add search functionality"

# 4. Push and create PR
git push origin feat/add-supplier-search
# Open Pull Request on GitHub

# 5. After PR approval and merge
git checkout V1.00D
git pull origin V1.00D
git branch -d feat/add-supplier-search
```

#### For Bug Fixes

```bash
# 1. Create fix branch
git checkout -b fix/supplier-validation

# 2. Write failing test first
# Add test that reproduces the bug

# 3. Fix the bug
# Make minimal changes to pass the test

# 4. Verify fix
make test

# 5. Create PR
git push origin fix/supplier-validation
```

### Pull Request Guidelines

Every PR must:
- [ ] Have a clear, descriptive title
- [ ] Reference related issues (e.g., "Fixes #123")
- [ ] Include tests for new functionality
- [ ] Pass all CI checks
- [ ] Be reviewed (even if self-reviewing)
- [ ] Have a clear description of changes and rationale

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`, `ci`

**Examples**:
- `feat(api): add supplier search endpoint`
- `fix(plants): resolve duplicate plant entries`
- `docs(readme): update installation instructions`
- `chore(deps): upgrade Flask to 3.0`

### Branch Protection Rules

Configured in GitHub settings for `main`:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- No direct pushes
- No force pushes
- Require linear history (optional)

---

## 3. Architecture for Maintainability

### Goal: Easy to Change, Easy to Test

**Principle**: "A good architecture makes it easy to change decisions tomorrow."

### SOLID Principles Implementation

Our architecture follows SOLID principles for maintainability:

#### Single Responsibility Principle (SRP)
Each module has one reason to change:

```
src/
├── routes/          # HTTP request/response handling only
├── services/        # Business logic only
├── models/          # Database schema only
├── schemas/         # Data validation only
├── utils/           # Shared utilities only
```

**Example**:
- `routes/suppliers.py` - Route definitions, request validation
- `services/supplier_service.py` - Business logic (search, create, update)
- `models/supplier.py` - SQLAlchemy model definition
- `schemas/supplier.py` - Marshmallow validation schemas

#### Open/Closed Principle (OCP)
Open for extension, closed for modification:

```python
# Base service provides common CRUD operations
class BaseService:
    def get_all(self):
        # Generic implementation
        
# Specific services extend without modifying base
class SupplierService(BaseService):
    def search_by_specialty(self, specialty):
        # Extended functionality
```

#### Liskov Substitution Principle (LSP)
Derived classes are substitutable for base classes:

```python
# Any service can be used where BaseService is expected
def process_items(service: BaseService):
    return service.get_all()
    
# Works with any service
process_items(SupplierService())
process_items(PlantService())
```

#### Interface Segregation Principle (ISP)
Many small interfaces over one large interface:

```python
# Instead of one large interface
class IDataService:
    def get_users(self): pass
    def get_products(self): pass
    def get_orders(self): pass

# Use specific interfaces
class IUserService:
    def get_users(self): pass
    
class IProductService:
    def get_products(self): pass
```

#### Dependency Inversion Principle (DIP)
Depend on abstractions, not concretions:

```python
# Controllers depend on service interfaces, not implementations
class SupplierController:
    def __init__(self, supplier_service: ISupplierService):
        self.service = supplier_service  # Can inject any implementation
```

### RESTful API Design

#### Resource-Oriented URIs

```
Good:
GET    /suppliers          - List all suppliers
POST   /suppliers          - Create supplier
GET    /suppliers/123      - Get specific supplier
PUT    /suppliers/123      - Update supplier
DELETE /suppliers/123      - Delete supplier

Bad:
GET    /getSuppliers
POST   /createSupplier
GET    /supplier?id=123
```

#### HTTP Methods Correctly

- **GET** - Retrieve (safe, idempotent)
- **POST** - Create (not idempotent)
- **PUT** - Full update (idempotent)
- **PATCH** - Partial update (idempotent)
- **DELETE** - Remove (idempotent)

#### Status Codes

- **200 OK** - Successful GET, PUT, PATCH
- **201 Created** - Successful POST
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Invalid input
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource doesn't exist
- **500 Internal Server Error** - Server error

#### Response Format

```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Example Supplier"
  },
  "meta": {
    "timestamp": "2025-10-24T13:00:00Z"
  }
}
```

### Frontend Architecture

#### Component Hierarchy

```
src/
├── components/
│   ├── common/        # Reusable UI components
│   ├── features/      # Feature-specific components
│   └── layouts/       # Page layouts
├── services/
│   └── api.js         # API client
├── hooks/             # Custom React hooks
├── context/           # React Context providers
└── utils/             # Utility functions
```

#### Separation of Concerns

```javascript
// ❌ Bad: Mixed concerns
function SupplierList() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/suppliers')  // Fetching in component
      .then(r => r.json())
      .then(setData);
  }, []);
  
  return <div>{/* rendering */}</div>;
}

// ✅ Good: Separated concerns
// services/api.js
export const supplierApi = {
  getAll: () => fetch('/api/suppliers').then(r => r.json())
};

// hooks/useSuppliers.js
export function useSuppliers() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    supplierApi.getAll()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);
  
  return { data, loading };
}

// components/SupplierList.js
function SupplierList() {
  const { data, loading } = useSuppliers();
  
  if (loading) return <Loading />;
  return <div>{/* rendering */}</div>;
}
```

---

## 4. Proactive Code Quality & Automation

### Goal: Catch Errors Early, Enforce Standards

**Principle**: "Automation is the definitive, testable specification of how things work."

### Pre-Commit Hooks

Automatically enforced before every commit:

```yaml
# .pre-commit-config.yaml
- Black formatting (Python)
- Ruff linting (Python)
- isort import sorting (Python)
- Trailing whitespace removal
- YAML/JSON validation
- Bandit security scanning
- Large file prevention
```

**Setup**:
```bash
pip install pre-commit
pre-commit install
```

### CI/CD Pipeline

Every PR triggers automated checks:

#### Code Quality Job
- Python linting (Ruff, Black, isort)
- Security scanning (Bandit)
- Dependency vulnerability check (Safety)

#### Backend Tests Job
- Unit tests
- Integration tests
- Database migrations
- Code coverage reporting

#### Frontend Tests Job
- Vitest unit tests
- Component tests
- Build verification

#### Deployment Job (V1.00D only)
- Automatic deployment to dev server
- Health check verification

### Test-Driven Development (TDD)

For bug fixes, always follow this process:

1. **Write a failing test** that reproduces the bug
2. **Run the test** to confirm it fails
3. **Fix the code** to make the test pass
4. **Run all tests** to ensure no regressions
5. **Commit** the test and fix together

**Example**:
```python
# Step 1: Write failing test
def test_supplier_email_validation():
    invalid_email = "not-an-email"
    with pytest.raises(ValidationError):
        SupplierService.create(email=invalid_email)

# Step 2: Run test - it fails ✗

# Step 3: Fix the code
class SupplierSchema(Schema):
    email = fields.Email(required=True)  # Add validation

# Step 4: Run test - it passes ✓
```

### Code Coverage

Target: **80%+ coverage** for new code

```bash
# Run tests with coverage
make test

# View coverage report
open htmlcov/index.html
```

### Linting Standards

**Python**:
- Line length: 120 characters
- Formatter: Black
- Linter: Ruff
- Import sorter: isort

**JavaScript**:
- ESLint configuration
- Prettier formatting
- TypeScript strict mode

---

## 5. Systematic Debugging Framework

### Goal: Transform Troubleshooting into a Repeatable Science

**Principle**: Debugging is a systematic process, not an art.

### The 5-Step Debugging Process

#### 1. Identify the Problem

**Define the symptom clearly:**
- What is the expected behavior?
- What is the actual behavior?
- Under what conditions does it occur?

**Example**:
```
❌ Bad: "The supplier page doesn't work"
✅ Good: "When clicking 'Save' on the supplier form with a valid email,
         the API returns 500 error instead of 201 Created"
```

#### 2. Reproduce Consistently

**Create a minimal reproduction:**
- Simplify to the smallest test case
- Document exact steps
- Note environment details

**Steps**:
```
1. Navigate to /suppliers/new
2. Fill in form: name="Test", email="test@example.com"
3. Click "Save" button
4. Observe: Network tab shows 500 error
5. Expected: Should show 201 and redirect to supplier detail
```

#### 3. Isolate the Root Cause

**Use systematic tools:**

**Backend Debugging**:
```python
# Add strategic logging
import logging
logger = logging.getLogger(__name__)

@app.route('/suppliers', methods=['POST'])
def create_supplier():
    logger.info(f"Received supplier data: {request.json}")
    
    try:
        result = SupplierService.create(request.json)
        logger.info(f"Created supplier: {result.id}")
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Failed to create supplier: {e}", exc_info=True)
        raise
```

**Frontend Debugging**:
```javascript
// Use browser DevTools
console.log('Form data:', formData);  // Check data before send

// Network tab: Inspect request/response
// Breakpoints: Pause execution to inspect state

// React DevTools: Inspect component state
```

**Database Debugging**:
```bash
# Check SQL queries
export FLASK_ENV=development  # Enables SQL logging

# View migrations
flask db history

# Test migration
flask db upgrade
flask db downgrade
```

#### 4. Fix the Issue

**Make minimal, targeted changes:**
- Change only what's necessary
- Don't refactor while debugging
- Keep the fix focused on the root cause

#### 5. Verify the Fix

**Comprehensive verification:**

```bash
# 1. Does the specific issue work?
# Test the exact reproduction steps

# 2. Did we break anything else?
make test

# 3. Does it work in production-like environment?
docker-compose up
# Test in container

# 4. Add a test to prevent regression
# Write test that would have caught this bug
```

### Common Issues & Solutions

#### Issue: "Tests pass locally but fail in CI"

**Diagnosis**:
- Environment differences
- Race conditions
- Timezone differences
- Database state issues

**Solution**:
```bash
# Run tests in Docker to match CI environment
docker-compose run backend pytest

# Check for test isolation issues
pytest --lf  # Run last failed test alone
pytest -v --tb=short  # Verbose output with short traceback
```

#### Issue: "Frontend can't connect to backend"

**Diagnosis**:
- CORS configuration
- API URL misconfiguration
- Network/firewall issues

**Solution**:
```javascript
// Check API configuration
console.log('API URL:', import.meta.env.VITE_API_URL);

// Test direct API call
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

#### Issue: "Database migration fails"

**Diagnosis**:
```bash
# Check migration history
flask db history

# Try manual migration
flask db upgrade
# Read error message carefully

# Check for conflicting migrations
ls migrations/versions/
```

**Solution**:
```bash
# Rollback and retry
flask db downgrade -1
flask db upgrade

# Or create merge migration
flask db merge heads
```

### Debugging Tools Reference

#### Backend
- **Flask Debug Toolbar** - Request inspection
- **Python debugger (pdb)** - Interactive debugging
- **Logging** - Strategic log statements
- **pytest** - Test-driven debugging

#### Frontend
- **React DevTools** - Component inspection
- **Browser DevTools** - Network, console, debugger
- **Vite HMR** - Hot module reload for fast iteration
- **Vitest** - Unit test debugging

#### Database
- **pgAdmin** - PostgreSQL GUI
- **Flask-Migrate** - Migration management
- **SQLAlchemy logging** - Query inspection

### Debugging Checklist

When stuck, systematically check:

- [ ] Are environment variables set correctly?
- [ ] Is the service running? (check `ps aux | grep python`)
- [ ] Are dependencies installed? (`make install`)
- [ ] Are there any errors in logs? (check `logs/` directory)
- [ ] Is the database accessible? (try `flask db current`)
- [ ] Are ports available? (`netstat -tuln | grep LISTEN`)
- [ ] Is code formatted correctly? (`make lint`)
- [ ] Do tests pass? (`make test`)
- [ ] Is Docker up to date? (`docker-compose pull`)
- [ ] Did I restart the service after changes?

---

## Quick Reference

### Daily Development Workflow

```bash
# Morning: Update and check
git checkout V1.00D
git pull origin V1.00D
make install
make test

# During work: Frequent commits
git add .
git commit -m "feat(area): what I did"

# Before PR: Final checks
make lint
make test
git push origin feat/my-feature

# Evening: Clean up
git branch -d feat/completed-feature
```

### Emergency Procedures

#### Rollback Deployment
```bash
# If V1.00D deployment breaks
ssh root@72.60.176.200
cd /opt/landscape-architecture-tool
./scripts/deployment/rollback.sh
```

#### Fix Broken Main
```bash
# Only if main is broken (rare due to protection)
git checkout main
git revert <bad-commit-sha>
git push origin main
```

#### Database Recovery
```bash
# Restore from backup
flask db downgrade <revision>
# Or restore from backup files in /backups/
```

---

## Additional Resources

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [ARCHITECTURE.md](./architecture/README.md) - Architecture details
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API reference
- [DEBUGGING_GUIDE.md](./DEBUGGING_GUIDE.md) - Detailed debugging guide
- [VPS_DEPLOYMENT_SOLUTION.md](./VPS_DEPLOYMENT_SOLUTION.md) - Deployment guide

---

## Conclusion

Following this framework systematically eliminates development friction and maximizes engineering velocity. The five pillars work together:

1. **Environment parity** ensures "it works everywhere"
2. **Disciplined version control** provides safety and predictability
3. **Clean architecture** makes changes easy
4. **Automation** catches errors early
5. **Systematic debugging** solves problems efficiently

**Remember**: Engineering velocity is not about coding faster, but about removing obstacles that slow us down.
