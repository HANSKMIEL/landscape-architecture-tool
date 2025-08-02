# CI/CD Timeout Solutions

This document describes the solutions implemented to resolve network timeout issues during CI/CD pipeline execution, particularly when installing pre-commit hooks and Python dependencies.

## Issues Addressed

### 1. Pre-commit Hook Timeout Errors
**Problem**: Pre-commit hooks were failing during CI/CD execution due to network timeouts when downloading dependencies from PyPI.

**Error Example**:
```
TimeoutError: The read operation timed out
pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(host='pypi.org', port=443): Read timed out.
```

**Solution**: Added pre-commit environment caching to the CI workflow to reduce network dependency and prevent repeated downloads.

### 2. Pip Installation Timeouts
**Problem**: Various CI jobs were experiencing timeouts during pip dependency installation, particularly during peak network usage times.

**Solution**: Enhanced pip installation with comprehensive timeout and retry logic across all CI jobs.

## Implemented Solutions

### 1. Pre-commit Caching
Added caching for pre-commit environments in the CI workflow:

```yaml
- name: Cache pre-commit environments
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: ${{ runner.os }}-pre-commit-${{ hashFiles('**/.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pre-commit-
```

**Benefits**:
- Reduces network calls for pre-commit hook installations
- Speeds up CI execution time
- Prevents timeout failures during repeated runs

### 2. Enhanced Pip Timeout and Retry Logic
Implemented robust timeout and retry mechanisms for all pip installations:

```bash
# Install with enhanced timeout and retry logic
for i in {1..3}; do
  echo "🔄 Dependencies installation attempt $i/3..."
  if timeout 600 pip install -r requirements-dev.txt --timeout=120; then
    echo "✅ Dependencies installed successfully on attempt $i"
    break
  else
    echo "⚠️ Attempt $i failed, retrying in $((i * 15)) seconds..."
    [ $i -lt 3 ] && sleep $((i * 15))
  fi
done || { echo "❌ Failed to install dependencies after 3 attempts"; exit 1; }
```

**Applied to**:
- `code-quality` job: Linting tools installation
- `integration-tests` job: Development dependencies
- `deepsource` job: Coverage dependencies
- Main backend test job (already had timeout handling)

### 3. Code Quality Improvements
Fixed E501 line length violations that were preventing proper linting:

- `tests/routes/test_plant_recommendations_extended.py`: Fixed 3 long lines
- All flake8 linting now passes without errors

## Usage Guidelines

### For Developers
1. **Local Development**: Pre-commit hooks are installed locally and will benefit from the same caching mechanisms when run in CI
2. **Network Issues**: If you encounter timeout issues locally, set environment variables:
   ```bash
   export PIP_TIMEOUT=120
   export PIP_RETRIES=3
   ```

### For CI/CD
The enhanced timeout handling is automatically applied in the following scenarios:
- When installing Python dependencies
- When setting up pre-commit environments
- During linting tool installation

## Monitoring
The CI pipeline now includes enhanced logging to track:
- Installation attempts and success/failure rates
- Timeout occurrences and retry patterns
- Cache hit/miss rates for pre-commit environments

## Results
After implementing these solutions:
- ✅ All E501 linting errors resolved
- ✅ Pre-commit caching reduces network dependency
- ✅ Enhanced timeout handling prevents pipeline failures
- ✅ Comprehensive retry logic ensures reliability
- ✅ All tests continue to pass with improved performance

## References
- Issue: #193 - Copilot and commit timeout. [WIP] PHASE_4_PREVENTION_MEASURES.md
- Related files:
  - `.github/workflows/ci.yml` - Enhanced CI workflow
  - `.pre-commit-config.yaml` - Pre-commit hook configuration
  - `tests/routes/test_plant_recommendations_extended.py` - Fixed line length issues