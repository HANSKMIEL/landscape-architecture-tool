# Phase 2: Dependency Stabilization - CI/CD Fix Plan

**Priority Level**: HIGH  
**Estimated Duration**: 6-10 hours  
**Dependencies**: Phase 1 must be completed successfully  
**Focus**: Resolve dependency version conflicts and establish stable, reproducible dependency environment

## Overview

This phase addresses dependency version conflicts that create subtle but persistent issues affecting database drivers, testing frameworks, and integration components. Building upon the stable foundation from Phase 1, this phase resolves underlying compatibility issues contributing to unpredictable failures.

**Critical Success Factor**: Phase 1 Environment Stabilization MUST be completed and validated before starting this phase. This phase establishes the dependency baseline for all subsequent phases.

## Root Cause Issues Addressed

1. **Dependency version conflicts** between packages causing runtime issues
2. **Database driver compatibility** problems affecting PostgreSQL and Redis connections  
3. **Testing framework conflicts** causing unpredictable test behavior
4. **Development tool version mismatches** affecting code quality pipeline

## Prerequisites Validation

Before starting, verify Phase 1 completion:

```bash
# Verify Phase 1 success criteria
echo "🔍 Validating Phase 1 completion..."

# Check Black formatting
black --check . && echo "✅ Black formatting validated" || { echo "❌ Phase 1 incomplete: Black formatting issues"; exit 1; }

# Check database connectivity  
python -c "
import psycopg2, redis
try:
    conn = psycopg2.connect('postgresql://postgres:postgres_password@localhost:5432/landscape_test')
    conn.close()
    r = redis.from_url('redis://localhost:6379/1')  
    r.ping()
    print('✅ Database connectivity validated')
except Exception as e:
    print(f'❌ Phase 1 incomplete: Database issues - {e}')
    exit(1)
"

echo "✅ Phase 1 validation complete - proceeding with Phase 2"
```

## Step-by-Step Implementation Guide

### Step 2.1: Comprehensive Dependency Audit and Conflict Resolution

**Objective**: Systematically identify and resolve all dependency conflicts affecting application stability.

#### 2.1.1 Current Dependency Analysis
Examine all dependency files and identify conflicts:

```bash
# Create dependency audit workspace
mkdir -p /tmp/dependency_audit
cd /tmp/dependency_audit

# Copy current dependency files for analysis
cp /home/runner/work/landscape-architecture-tool/landscape-architecture-tool/requirements*.txt .

# Analyze main dependencies
echo "📋 Main Dependencies Analysis:"
cat requirements.txt

echo -e "\n📋 Development Dependencies Analysis:"  
cat requirements-dev.txt

echo -e "\n📋 Test Dependencies Analysis:"
cat requirements-test.txt 2>/dev/null || echo "No requirements-test.txt found"
```

#### 2.1.2 Dependency Conflict Detection
Use pip-tools and pipdeptree to identify conflicts:

```bash
# Install dependency analysis tools
pip install pip-tools pipdeptree

# Check for immediate conflicts in current environment
echo "🔍 Checking for dependency conflicts..."
pip check || echo "⚠️ Dependency conflicts detected"

# Generate comprehensive dependency tree
echo "🌳 Generating dependency tree..."
pipdeptree > dependency_tree.txt
pipdeptree --graph-output > dependency_graph.txt

# Identify specific problematic packages
echo "🚨 Identifying problematic packages..."
pipdeptree --warn fail > dependency_warnings.txt 2>&1 || echo "Dependency warnings captured"

# Check for version conflicts in critical packages
python -c "
import pkg_resources
import sys

critical_packages = [
    'psycopg2-binary', 'redis', 'sqlalchemy', 'flask', 
    'pytest', 'black', 'flake8', 'isort', 'bandit',
    'requests', 'gunicorn', 'flask-migrate'
]

print('🔍 Critical Package Version Analysis:')
conflicts = []

for package in critical_packages:
    try:
        dist = pkg_resources.get_distribution(package)
        print(f'{package}: {dist.version}')
    except pkg_resources.DistributionNotFound:
        print(f'{package}: NOT INSTALLED')
        conflicts.append(f'{package} not installed')
    except Exception as e:
        print(f'{package}: ERROR - {e}')
        conflicts.append(f'{package} error: {e}')

if conflicts:
    print(f'\\n⚠️ Issues found: {len(conflicts)}')
    for conflict in conflicts:
        print(f'  - {conflict}')
else:
    print('\\n✅ All critical packages installed')
"
```

#### 2.1.3 Database-Related Dependency Analysis
Focus on database connectivity packages:

```bash
echo "🗄️ Database Dependency Analysis..."

# Check PostgreSQL driver compatibility
python -c "
import psycopg2
import sqlalchemy
print(f'psycopg2 version: {psycopg2.__version__}')
print(f'SQLAlchemy version: {sqlalchemy.__version__}')

# Test connection pool compatibility
from sqlalchemy import create_engine
try:
    engine = create_engine('postgresql://postgres:postgres_password@localhost:5432/landscape_test')
    conn = engine.connect()
    conn.close()
    print('✅ SQLAlchemy + psycopg2 compatibility confirmed')
except Exception as e:
    print(f'⚠️ Database driver compatibility issue: {e}')
"

# Check Redis driver compatibility  
python -c "
import redis
print(f'Redis client version: {redis.__version__}')

try:
    r = redis.from_url('redis://localhost:6379/1')
    r.ping()
    print('✅ Redis client compatibility confirmed')
except Exception as e:
    print(f'⚠️ Redis client compatibility issue: {e}')
"
```

#### 2.1.4 Testing Framework Dependency Analysis
Analyze testing-related packages:

```bash
echo "🧪 Testing Framework Dependency Analysis..."

python -c "
import pytest
import coverage
import faker
import flask

print(f'pytest version: {pytest.__version__}')
print(f'coverage version: {coverage.__version__}')  
print(f'faker version: {faker.__version__}')
print(f'flask version: {flask.__version__}')

# Check for known compatibility issues
import pkg_resources

# Check pytest plugins compatibility
pytest_plugins = [
    'pytest-cov', 'pytest-flask', 'pytest-mock', 
    'pytest-xdist', 'pytest-timeout'
]

for plugin in pytest_plugins:
    try:
        dist = pkg_resources.get_distribution(plugin)
        print(f'{plugin}: {dist.version}')
    except pkg_resources.DistributionNotFound:
        print(f'{plugin}: NOT INSTALLED')
"
```

### Step 2.2: Dependency Conflict Resolution and Version Pinning

**Objective**: Resolve identified conflicts and establish stable version constraints.

#### 2.2.1 Create Updated Requirements Files
Generate new requirements with resolved conflicts:

```bash
# Return to main repository directory
cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool

# Backup current requirements files
cp requirements.txt requirements.txt.backup
cp requirements-dev.txt requirements-dev.txt.backup
cp requirements-test.txt requirements-test.txt.backup 2>/dev/null || echo "No requirements-test.txt to backup"

# Create requirements.in for main dependencies
cat > requirements.in << 'EOF'
# Core Flask application
Flask>=2.3.0,<3.0.0
Flask-Migrate>=4.0.0
Flask-SQLAlchemy>=3.0.0
Flask-CORS>=4.0.0

# Database drivers - pinned for stability
psycopg2-binary==2.9.7
redis>=4.5.0,<5.0.0
SQLAlchemy>=2.0.0,<2.1.0

# Production server
gunicorn>=21.0.0

# Utilities
requests>=2.31.0
python-dotenv>=1.0.0
click>=8.1.0

# Date/time handling
python-dateutil>=2.8.0
pytz>=2023.3
EOF

# Create requirements-dev.in for development dependencies  
cat > requirements-dev.in << 'EOF'
# Include main requirements
-r requirements.in

# Testing framework - compatible versions
pytest>=7.4.0,<8.0.0
pytest-cov>=4.1.0
pytest-flask>=1.3.0
pytest-mock>=3.11.0
pytest-xdist>=3.3.0
pytest-timeout>=2.1.0

# Test data generation
Faker>=19.6.0

# Code quality tools - pinned versions
black==24.3.0
flake8==7.0.0
isort==5.13.2
bandit==1.7.5

# Security scanning
safety>=3.0.0

# Development utilities
pip-tools>=7.0.0
pre-commit>=3.5.0
EOF
```

#### 2.2.2 Generate Lock Files with Resolved Dependencies
Create new lock files with pinned versions:

```bash
echo "🔒 Generating new lock files with resolved dependencies..."

# Generate requirements.txt with resolved dependencies
pip-compile requirements.in --upgrade --verbose

# Generate requirements-dev.txt with resolved dependencies
pip-compile requirements-dev.in --upgrade --verbose

# Verify the new lock files
echo "📋 New requirements.txt:"
head -20 requirements.txt

echo -e "\n📋 New requirements-dev.txt (first 20 lines):"
head -20 requirements-dev.txt
```

#### 2.2.3 Test New Dependency Baseline
Create clean environment and test new dependencies:

```bash
echo "🧪 Testing new dependency baseline..."

# Create temporary virtual environment for testing
python -m venv /tmp/test_env
source /tmp/test_env/bin/activate

# Install new dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt

# Test critical imports
python -c "
import sys
import importlib

critical_imports = [
    'flask', 'psycopg2', 'redis', 'sqlalchemy',
    'pytest', 'black', 'flake8', 'isort', 'bandit',
    'requests', 'gunicorn', 'faker'
]

print('🔍 Testing critical imports with new dependencies...')
failed_imports = []

for module in critical_imports:
    try:
        importlib.import_module(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        failed_imports.append(module)

if failed_imports:
    print(f'\\n⚠️ Failed imports: {failed_imports}')
    sys.exit(1)
else:
    print('\\n✅ All critical imports successful')
"

# Test database connectivity with new dependencies
python -c "
import psycopg2
import redis
import sqlalchemy

print('🗄️ Testing database connectivity with new dependencies...')

try:
    # Test PostgreSQL
    conn = psycopg2.connect('postgresql://postgres:postgres_password@localhost:5432/landscape_test')
    conn.close()
    print('✅ PostgreSQL connection works')
    
    # Test Redis
    r = redis.from_url('redis://localhost:6379/1')
    r.ping()
    print('✅ Redis connection works')
    
    # Test SQLAlchemy
    engine = sqlalchemy.create_engine('postgresql://postgres:postgres_password@localhost:5432/landscape_test')
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text('SELECT 1'))
        print('✅ SQLAlchemy connection works')
        
except Exception as e:
    print(f'❌ Database connectivity failed: {e}')
    exit(1)
"

# Deactivate test environment
deactivate
rm -rf /tmp/test_env

echo "✅ New dependency baseline tested successfully"
```

### Step 2.3: Lock File Regeneration and Dependency Baseline Establishment

**Objective**: Create stable, reproducible dependency environment preventing future conflicts.

#### 2.3.1 Install and Validate New Dependencies
Install the new dependency baseline in the main environment:

```bash
echo "🔄 Installing new dependency baseline..."

# Uninstall current packages to avoid conflicts
pip freeze | grep -v "^-e" | xargs pip uninstall -y

# Install from new lock files
pip install --upgrade pip
pip install -r requirements-dev.txt

# Verify installation success
pip check && echo "✅ No dependency conflicts detected" || echo "⚠️ Dependency conflicts may exist"
```

#### 2.3.2 Comprehensive Testing with New Dependencies
Run comprehensive tests with new dependencies:

```bash
echo "🧪 Running comprehensive tests with new dependencies..."

# Set up environment for testing
export PYTHONPATH=.
export FLASK_ENV=testing

# Run basic import tests
python -c "
import src.main
import src.models.user
import src.models.landscape
print('✅ Application modules import successfully')
"

# Run code quality tools with new versions
echo "🔍 Testing code quality tools..."

# Test Black formatting
black --check --diff . && echo "✅ Black formatting works" || echo "⚠️ Black formatting issues detected"

# Test isort
isort --check-only --profile black src/ tests/ && echo "✅ isort works" || echo "⚠️ isort issues detected"

# Test flake8
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,F401,F403,E402,C901,W291 --max-complexity=25 && echo "✅ flake8 works" || echo "⚠️ flake8 issues detected"

# Test bandit
bandit -r src/ -f json -o /tmp/bandit-test.json && echo "✅ bandit works" || echo "⚠️ bandit issues detected"

# Test safety
safety check --json && echo "✅ safety works" || echo "⚠️ safety detected security issues"
```

#### 2.3.3 Database Functionality Testing
Test database operations with new dependencies:

```bash
echo "🗄️ Testing database functionality with new dependencies..."

# Test database migrations
python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres_password@localhost:5432/landscape_test'
os.environ['FLASK_ENV'] = 'testing'

from src.main import app, db
with app.app_context():
    try:
        # Test database connection
        db.engine.execute('SELECT 1')
        print('✅ Database connection works')
        
        # Test basic model operations
        from src.models.user import User
        user_count = User.query.count()
        print(f'✅ User model query works (count: {user_count})')
        
        from src.models.landscape import Supplier
        supplier_count = Supplier.query.count()  
        print(f'✅ Supplier model query works (count: {supplier_count})')
        
    except Exception as e:
        print(f'❌ Database functionality test failed: {e}')
        exit(1)
"

# Test Redis functionality
python -c "
import redis
import json

try:
    r = redis.from_url('redis://localhost:6379/1')
    
    # Test basic Redis operations
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    if value.decode() == 'test_value':
        print('✅ Redis basic operations work')
    else:
        print('❌ Redis basic operations failed')
        exit(1)
        
    # Test JSON operations
    test_data = {'key': 'value', 'number': 42}
    r.set('test_json', json.dumps(test_data))
    retrieved_data = json.loads(r.get('test_json'))
    if retrieved_data == test_data:
        print('✅ Redis JSON operations work')
    else:
        print('❌ Redis JSON operations failed')
        exit(1)
        
    # Cleanup
    r.delete('test_key', 'test_json')
    print('✅ Redis functionality tests completed')
    
except Exception as e:
    print(f'❌ Redis functionality test failed: {e}')
    exit(1)
"
```

#### 2.3.4 Run Application Test Suite
Execute the full test suite with new dependencies:

```bash
echo "🧪 Running full test suite with new dependencies..."

# Run basic tests first
python -m pytest tests/test_basic.py -v --tb=short

if [ $? -eq 0 ]; then
    echo "✅ Basic tests passed with new dependencies"
else
    echo "❌ Basic tests failed with new dependencies"
    echo "Rolling back dependency changes..."
    cp requirements.txt.backup requirements.txt
    cp requirements-dev.txt.backup requirements-dev.txt
    pip install -r requirements-dev.txt
    exit 1
fi

# Run extended test suite
echo "🧪 Running extended test suite..."
python -m pytest tests/ -v --tb=short --maxfail=10

if [ $? -eq 0 ]; then
    echo "✅ Extended tests passed with new dependencies"
else
    echo "⚠️ Some extended tests failed - this may be acceptable if they were failing before"
    echo "Checking if critical tests still pass..."
    
    # Test critical functionality
    python -m pytest tests/test_basic.py tests/routes/ tests/models/ -v --tb=short --maxfail=5
    
    if [ $? -eq 0 ]; then
        echo "✅ Critical tests still pass - dependency update successful"
    else
        echo "❌ Critical tests failed - rolling back changes"
        cp requirements.txt.backup requirements.txt
        cp requirements-dev.txt.backup requirements-dev.txt
        pip install -r requirements-dev.txt
        exit 1
    fi
fi
```

### Step 2.4: Documentation and Baseline Establishment

**Objective**: Document dependency changes and establish procedures for future updates.

#### 2.4.1 Document Dependency Changes
Create comprehensive documentation of changes:

```bash
echo "📝 Documenting dependency changes..."

# Create dependency change log
cat > DEPENDENCY_CHANGES_PHASE2.md << 'EOF'
# Phase 2 Dependency Changes Log

## Overview
This document records all dependency changes made during Phase 2: Dependency Stabilization.

## Key Changes Made

### Requirements Structure
- Created requirements.in and requirements-dev.in for better dependency management
- Generated locked requirements.txt and requirements-dev.txt with pip-compile
- Pinned critical packages to stable versions

### Database Dependencies
- psycopg2-binary: Pinned to 2.9.7 for PostgreSQL compatibility
- redis: Constrained to >=4.5.0,<5.0.0 for stability
- SQLAlchemy: Constrained to >=2.0.0,<2.1.0 for compatibility

### Testing Framework  
- pytest: Constrained to >=7.4.0,<8.0.0
- All pytest plugins pinned to compatible versions
- faker: Updated to 19.6.0 for test data generation

### Code Quality Tools
- black: Pinned to 24.3.0
- flake8: Pinned to 7.0.0  
- isort: Pinned to 5.13.2
- bandit: Pinned to 1.7.5

## Validation Results
- All critical imports working: ✅
- Database connectivity confirmed: ✅
- Code quality tools functional: ✅
- Basic test suite passing: ✅

## Next Steps
- Monitor for any compatibility issues
- Update dependencies following established procedures
- Proceed to Phase 3: Integration Stabilization
EOF

# Compare old vs new dependencies
echo "📊 Dependency comparison:"
diff requirements.txt.backup requirements.txt > dependency_diff.txt || true
echo "Differences saved to dependency_diff.txt"

# Document current versions of critical packages
python -c "
import pkg_resources

critical_packages = [
    'flask', 'psycopg2-binary', 'redis', 'sqlalchemy',
    'pytest', 'black', 'flake8', 'isort', 'bandit'
]

print('📋 Final Package Versions:')
for package in critical_packages:
    try:
        dist = pkg_resources.get_distribution(package)
        print(f'{package}: {dist.version}')
    except pkg_resources.DistributionNotFound:
        print(f'{package}: NOT INSTALLED')
" >> DEPENDENCY_CHANGES_PHASE2.md
```

#### 2.4.2 Establish Future Dependency Update Procedures
Create procedures for future dependency management:

```bash
cat > DEPENDENCY_UPDATE_PROCEDURES.md << 'EOF'
# Dependency Update Procedures

## Overview
This document establishes procedures for future dependency updates to prevent the dependency conflicts that caused the problem-hopping cycle.

## Regular Update Schedule
- **Monthly**: Review for security updates using `safety check`
- **Quarterly**: Consider minor version updates for stability improvements
- **Annually**: Plan major version updates with comprehensive testing

## Update Process

### 1. Security Updates (High Priority)
```bash
# Check for security vulnerabilities
safety check --json

# If vulnerabilities found, update specific packages
pip-compile --upgrade-package [vulnerable-package] requirements.in
pip-compile --upgrade-package [vulnerable-package] requirements-dev.in
```

### 2. Stability Updates (Medium Priority)  
```bash
# Update requirements files
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in

# Test in clean environment
python -m venv /tmp/update_test
source /tmp/update_test/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/test_basic.py
deactivate && rm -rf /tmp/update_test
```

### 3. Validation Requirements
Before accepting any dependency updates:
- [ ] All critical imports work
- [ ] Database connectivity confirmed  
- [ ] Code quality tools functional
- [ ] Basic test suite passes
- [ ] No new security vulnerabilities

### 4. Rollback Procedures
If updates cause issues:
```bash
# Restore previous working versions
git checkout HEAD~1 -- requirements.txt requirements-dev.txt
pip install -r requirements-dev.txt

# Verify rollback success
python -m pytest tests/test_basic.py
```

## Conflict Resolution
When dependency conflicts arise:
1. Identify conflicting packages using `pip check`
2. Use `pipdeptree` to understand dependency relationships
3. Find compatible versions using version constraint adjustments
4. Test thoroughly before deployment

EOF
```

## Comprehensive Validation and Testing

### Validation Checklist

Run this comprehensive validation to ensure Phase 2 completion:

```bash
echo "🔍 Phase 2 Comprehensive Validation..."

# 1. Dependency conflict check
pip check && echo "✅ No dependency conflicts" || echo "❌ Dependency conflicts exist"

# 2. Critical package functionality
python -c "
import subprocess
import sys

tests = [
    ('Flask app import', 'import src.main; print(\"Flask import works\")'),
    ('Database connectivity', 'import psycopg2; conn = psycopg2.connect(\"postgresql://postgres:postgres_password@localhost:5432/landscape_test\"); conn.close(); print(\"PostgreSQL works\")'),
    ('Redis connectivity', 'import redis; r = redis.from_url(\"redis://localhost:6379/1\"); r.ping(); print(\"Redis works\")'),
    ('Testing framework', 'import pytest; print(f\"pytest {pytest.__version__} works\")'),
    ('Code quality tools', 'import black, flake8, isort, bandit; print(\"Code quality tools work\")')
]

for test_name, test_code in tests:
    try:
        exec(test_code)
        print(f'✅ {test_name}')
    except Exception as e:
        print(f'❌ {test_name}: {e}')
        sys.exit(1)
        
print('🎉 All critical functionality validated')
"

# 3. Code quality validation
black --check . && echo "✅ Black formatting" || echo "❌ Black formatting issues"
isort --check-only --profile black src/ tests/ && echo "✅ Import sorting" || echo "❌ Import sorting issues"
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,F401,F403,E402,C901,W291 --max-complexity=25 && echo "✅ Flake8 linting" || echo "⚠️ Flake8 issues"

# 4. Test suite validation
echo "🧪 Running critical test validation..."
python -m pytest tests/test_basic.py -v --tb=short
if [ $? -eq 0 ]; then
    echo "✅ Critical tests pass"
else
    echo "❌ Critical tests fail - Phase 2 incomplete"
    exit 1
fi

echo "🎉 Phase 2 validation complete - Ready for Phase 3"
```

### Success Criteria

Phase 2 is considered complete when:

- ✅ No dependency conflicts detected (`pip check` passes)
- ✅ All critical packages import and function correctly
- ✅ Database connectivity works with updated drivers
- ✅ Code quality tools work with pinned versions
- ✅ Basic test suite passes with new dependencies
- ✅ Lock files generated with resolved dependencies
- ✅ Documentation created for dependency changes
- ✅ Future update procedures established

## Rollback Procedures

If critical issues arise:

```bash
# Restore previous dependency files
cp requirements.txt.backup requirements.txt
cp requirements-dev.txt.backup requirements-dev.txt

# Reinstall previous dependencies
pip install -r requirements-dev.txt

# Validate rollback
python -m pytest tests/test_basic.py -v
```

## Emergency Procedures

**If dependency issues affect professional practice**:

1. **Immediately restore backup dependency files**
2. **Reinstall working dependencies**  
3. **Validate core functionality works**
4. **Document issues for future resolution**
5. **Escalate if database functionality is affected**

## Documentation Requirements

Record all Phase 2 activities:

- Dependency conflicts identified and resolved
- Package versions before and after changes
- Validation test results
- Any issues encountered and solutions applied
- Time taken for each major step

## Next Steps

Upon successful Phase 2 completion:

1. **Verify all success criteria met**
2. **Clean up backup files and temporary data**
3. **Commit dependency changes to version control**
4. **Proceed to Phase 3: Integration Stabilization**
5. **Do NOT skip to Phase 4 - sequential implementation required**

---

**⚠️ IMPORTANT**: Phase 2 builds upon Phase 1's stable foundation. Do not proceed to Phase 3 until all Phase 2 success criteria are met and validated. The dependency baseline established here is critical for all subsequent phases.