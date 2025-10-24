# Tests Directory

This directory contains all automated tests for the Landscape Architecture Tool, following the comprehensive best practices framework.

## 📚 Essential Documentation

Before writing or debugging tests, review these guides:

- **[DEVELOPMENT_GUIDE.md](../docs/DEVELOPMENT_GUIDE.md)** - Test-Driven Development (TDD) workflow (Section 4)
- **[DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md)** - Systematic debugging and test troubleshooting
- **[.github/copilot-instructions/testing.md](../.github/copilot-instructions/testing.md)** - Testing guardrails
- **[scripts/testing/README.md](../scripts/testing/README.md)** - Testing scripts and automation

## Test-Driven Development (TDD)

All tests follow the TDD workflow from [DEVELOPMENT_GUIDE.md - TDD](../docs/DEVELOPMENT_GUIDE.md#test-driven-development-tdd):

### The TDD Cycle

```
1. Write failing test  ❌
2. Run test (confirm it fails)
3. Write minimal code  ✅
4. Run test (confirm it passes)
5. Refactor  ♻️
6. Commit test + code together
```

### Example: Adding a New Feature

```python
# Step 1: Write failing test in tests/routes/test_suppliers.py
def test_create_supplier_with_validation(client, session):
    """Test supplier creation validates required fields."""
    response = client.post('/suppliers', json={
        'name': ''  # Empty name should fail
    })
    assert response.status_code == 422
    assert 'name' in response.json['errors']

# Step 2: Run test - should FAIL
# $ pytest tests/routes/test_suppliers.py::test_create_supplier_with_validation -v

# Step 3: Implement validation in src/schemas/supplier.py
# Step 4: Run test - should PASS
# Step 5: Refactor if needed
# Step 6: Commit together
```

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── fixtures/                # Shared test fixtures
│   ├── auth_fixtures.py     # Authentication fixtures
│   ├── test_data.py         # Test data fixtures
│   ├── test_stability.py    # Stability enhancements
│   └── database.py          # Database fixtures
├── routes/                  # API endpoint tests
├── services/                # Business logic tests
├── models/                  # Database model tests
├── utils/                   # Utility function tests
└── database/                # Database-specific tests
```

### Test File Naming

- **Pattern**: `test_<feature>.py`
- **Classes**: `Test<Feature>` (optional, for grouping)
- **Functions**: `test_<specific_behavior>`

**Examples**:
- `test_suppliers.py` - Tests for supplier endpoints
- `test_supplier_service.py` - Tests for supplier service layer
- `test_basic.py` - Basic smoke tests

## Test Fixtures

### Database Fixtures

From `conftest.py`, following [DEVELOPMENT_GUIDE.md - Testing](../docs/DEVELOPMENT_GUIDE.md#testing):

```python
@pytest.fixture
def session(app):
    """Provides a database session with automatic rollback."""
    # Uses SAVEPOINT transactions for isolation
    # See conftest.py for implementation
    
@pytest.fixture
def client(app):
    """Provides a Flask test client."""
    # For testing API endpoints
```

### Authentication Fixtures

From `fixtures/auth_fixtures.py`:

```python
@pytest.fixture
def auth_headers(client):
    """Provides authentication headers for requests."""
    
@pytest.fixture
def test_user(session):
    """Creates a test user."""
```

### Test Data Fixtures

From `fixtures/test_data.py`:

```python
@pytest.fixture
def sample_supplier(session):
    """Creates a sample supplier for testing."""
    
@pytest.fixture
def sample_plant(session):
    """Creates a sample plant for testing."""
```

## Running Tests

### Quick Commands

```bash
# All backend tests
make backend-test

# Specific test file
pytest tests/routes/test_suppliers.py -v

# Specific test function
pytest tests/routes/test_suppliers.py::test_create_supplier -v

# With coverage
pytest --cov=src tests/

# Failed tests only (last failed)
pytest --lf

# Stop on first failure
pytest -x
```

### Frontend Tests

```bash
cd frontend
npm run test:run          # Run all tests
npm run test:coverage     # With coverage
npm run test -- test_file.spec.js  # Specific file
```

## Debugging Test Failures

When tests fail, use the systematic 5-step process from [DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md#the-5-step-debugging-process):

### Step 1: Identify the Problem

```bash
# Run with verbose output
pytest tests/test_file.py::test_function -v

# Check the error message
# Look at the assertion that failed
```

### Step 2: Reproduce Consistently

```bash
# Run the failing test multiple times
pytest tests/test_file.py::test_function -v --count=5

# Check if it's flaky
pytest tests/test_file.py -v --count=10
```

### Step 3: Isolate the Root Cause

```python
# Add print statements or use pdb
import pdb; pdb.set_trace()

# Check database state
def test_example(session):
    # Print query results
    result = session.query(Model).all()
    print(f"Found {len(result)} records")
    
# Check test isolation
pytest tests/test_file.py::test_function -v --setup-show
```

### Step 4: Fix the Issue

Make minimal changes to fix the root cause:

```python
# Before (failing)
def test_get_supplier(client):
    response = client.get('/suppliers/999')  # Non-existent
    assert response.status_code == 200  # Wrong expectation

# After (passing)
def test_get_supplier_not_found(client):
    response = client.get('/suppliers/999')
    assert response.status_code == 404  # Correct expectation
```

### Step 5: Verify the Fix

```bash
# Run the fixed test
pytest tests/test_file.py::test_function -v

# Run related tests
pytest tests/routes/ -v

# Run full test suite
make backend-test
```

## Common Test Issues

See [DEBUGGING_GUIDE.md - Common Issues](../docs/DEBUGGING_GUIDE.md#common-issues--solutions) for comprehensive troubleshooting.

### Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Solution**: Check for uncommitted transactions
```python
# Always use session fixture
def test_example(session):
    supplier = Supplier(name="Test")
    session.add(supplier)
    # session.commit() is handled by fixture
```

### Test Isolation Issues

**Symptom**: Tests pass individually but fail when run together

**Solution**: Use SAVEPOINT transactions (already configured in conftest.py)
```python
# Fixtures use nested transactions automatically
# No action needed if using session fixture
```

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Set PYTHONPATH
```bash
export PYTHONPATH=.
pytest tests/
```

### Tests Pass Locally, Fail in CI

**Symptom**: Tests pass on your machine but fail in GitHub Actions

**Solution**: Run tests in Docker to match CI
```bash
docker-compose run backend pytest tests/
```

### Flaky Tests

**Symptom**: Tests sometimes pass, sometimes fail

**Solution**: 
1. Check for timing issues (use explicit waits)
2. Check for external dependencies (mock them)
3. Check for random data (use fixed seeds)

```python
# Before (flaky)
def test_with_delay():
    time.sleep(0.1)  # Might not be enough

# After (stable)
def test_with_explicit_wait():
    wait_for_condition(lambda: resource.is_ready(), timeout=5)
```

## Test Coverage

### Current Coverage

Run to see current coverage:
```bash
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

### Coverage Goals

From [DEVELOPMENT_GUIDE.md - Code Coverage](../docs/DEVELOPMENT_GUIDE.md#code-coverage):

- **Target**: 80%+ overall coverage
- **Critical paths**: 95%+ coverage
- **New features**: Must include tests

### Improving Coverage

```bash
# Find uncovered lines
pytest --cov=src --cov-report=term-missing tests/

# Focus on specific module
pytest --cov=src.services.supplier_service --cov-report=term-missing tests/services/test_supplier_service.py
```

## Pre-commit Testing

From [DEVELOPMENT_GUIDE.md - Pre-commit](../docs/DEVELOPMENT_GUIDE.md#pre-commit-hooks):

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

Pre-commit automatically runs:
- **Black** (formatting)
- **Ruff** (linting)
- **isort** (import sorting)
- **Bandit** (security scanning)

## CI/CD Integration

All tests run automatically in CI. See [DEVELOPMENT_GUIDE.md - CI/CD](../docs/DEVELOPMENT_GUIDE.md#cicd-pipeline).

### GitHub Actions Workflow

Every PR triggers:
1. **Code quality checks** (linting, formatting)
2. **Backend tests** (pytest with coverage)
3. **Frontend tests** (vitest)
4. **Security scanning** (Bandit, Safety, CodeQL)
5. **Build verification**

### Debugging CI Failures

When tests fail in CI:

```bash
# 1. Check the logs
# View GitHub Actions logs for the failed job

# 2. Run locally in Docker (matches CI)
docker-compose run backend pytest tests/

# 3. Check for environment differences
# CI uses clean environment, check .env.example

# 4. Use the debugging guide
# See DEBUGGING_GUIDE.md for systematic approach
```

## Writing Good Tests

### Principles

From [DEVELOPMENT_GUIDE.md - Testing Best Practices](../docs/DEVELOPMENT_GUIDE.md#testing-best-practices):

1. **Arrange, Act, Assert** pattern
2. **One assertion per test** (when possible)
3. **Descriptive test names**
4. **Test behavior, not implementation**
5. **Isolate tests** (no dependencies between tests)

### Example: Good Test

```python
def test_create_supplier_validates_required_fields(client, session):
    """Test that supplier creation validates required fields.
    
    Following TDD workflow from DEVELOPMENT_GUIDE.md:
    - Arrange: Prepare invalid data
    - Act: Attempt to create supplier
    - Assert: Verify validation error
    """
    # Arrange
    invalid_data = {
        'name': '',  # Required field is empty
        'email': 'invalid-email'  # Invalid format
    }
    
    # Act
    response = client.post('/suppliers', json=invalid_data)
    
    # Assert
    assert response.status_code == 422
    errors = response.json['errors']
    assert 'name' in errors
    assert 'email' in errors
```

### Example: Testing Service Layer

```python
from src.services.supplier_service import SupplierService

def test_supplier_service_create_with_duplicate_email(session):
    """Test service layer prevents duplicate emails.
    
    Following SOLID principles from DEVELOPMENT_GUIDE.md:
    - Tests business logic in service layer
    - Isolated from HTTP layer
    """
    # Arrange
    existing_supplier = Supplier(name="Existing", email="test@example.com")
    session.add(existing_supplier)
    session.commit()
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email already exists"):
        SupplierService.create({
            'name': 'New',
            'email': 'test@example.com'
        })
```

## Performance Testing

For slow tests:

```bash
# Show slowest tests
pytest --durations=10 tests/

# Profile specific test
pytest --profile tests/test_slow.py
```

## Security Testing

Security scans run automatically. See [DEVELOPMENT_GUIDE.md - Security](../docs/DEVELOPMENT_GUIDE.md#security-scanning).

```bash
# Manual security scan
bandit -r src/ -ll

# Check dependencies
safety check

# Full security scan (like CI)
make security-check
```

## Test Documentation Standards

### Docstrings

All test functions should have docstrings:

```python
def test_create_supplier_success(client, session):
    """Test successful supplier creation with valid data.
    
    Verifies:
    - 201 Created status code
    - Supplier saved to database
    - Correct response format
    
    Follows: DEVELOPMENT_GUIDE.md - RESTful API standards
    """
```

### Comments

Add comments for complex test logic:

```python
def test_complex_scenario(client, session):
    """Test complex multi-step scenario."""
    # Step 1: Create dependencies
    project = create_test_project(session)
    
    # Step 2: Perform action
    response = client.post('/some-endpoint', json={...})
    
    # Step 3: Verify state changes
    assert session.query(Model).count() == expected_count
```

## Continuous Improvement

### Test Metrics to Track

1. **Coverage percentage** (target: 80%+)
2. **Test execution time** (keep under 2 minutes)
3. **Flaky test rate** (target: <1%)
4. **Test count** (should grow with features)

### Regular Reviews

- **Weekly**: Review failing tests
- **Monthly**: Analyze coverage gaps
- **Quarterly**: Refactor slow/flaky tests

## Additional Resources

### Documentation
- **Backend Testing**: [.github/copilot-instructions/backend.md](../.github/copilot-instructions/backend.md)
- **Frontend Testing**: [.github/copilot-instructions/frontend.md](../.github/copilot-instructions/frontend.md)  
- **Test Scripts**: [scripts/testing/README.md](../scripts/testing/README.md)

### Tools
- **pytest**: Python testing framework
- **pytest-flask**: Flask testing utilities
- **pytest-cov**: Coverage reporting
- **Faker**: Test data generation
- **Factory Boy**: Test fixture factories (if added)

### Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `make backend-test` |
| Run specific file | `pytest tests/routes/test_suppliers.py -v` |
| Run with coverage | `pytest --cov=src tests/` |
| Debug test | `pytest tests/test_file.py::test_func -v -s` |
| Last failed only | `pytest --lf` |
| Stop on first fail | `pytest -x` |
| Show fixtures | `pytest --fixtures` |
| Slow tests | `pytest --durations=10` |

---

**Framework Alignment**: This testing approach follows all 5 pillars of the engineering velocity framework documented in DEVELOPMENT_GUIDE.md. For systematic debugging of test failures, always follow the 5-step process in DEBUGGING_GUIDE.md.
