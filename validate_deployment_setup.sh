#!/bin/bash
# Deployment Setup Validation Script
# This script validates that all components are ready for deployment

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
  echo -e "${BLUE}[SECTION]${NC} $1"
}

# Initialize counters
PASSED=0
FAILED=0

# Function to check and report test results
check_result() {
  if [ $1 -eq 0 ]; then
    print_status "✅ $2"
    ((PASSED++))
  else
    print_error "❌ $2"
    ((FAILED++))
  fi
}

print_header "Deployment Setup Validation"
echo "This script validates the deployment configuration and readiness."
echo ""

# 1. Check local repository structure
print_header "1. Repository Structure Validation"

# Check if we're in the right directory
if [ -f "pyproject.toml" ] && [ -d "frontend" ] && [ -d "src" ]; then
  check_result 0 "Repository structure is correct"
else
  check_result 1 "Repository structure is incorrect - missing key directories/files"
fi

# Check workflow file
if [ -f ".github/workflows/manual-deploy.yml" ]; then
  check_result 0 "Manual deployment workflow exists"
else
  check_result 1 "Manual deployment workflow is missing"
fi

# Check requirements files
if [ -f "requirements.txt" ] && [ -f "requirements-dev.txt" ]; then
  check_result 0 "Requirements files exist"
else
  check_result 1 "Requirements files are missing"
fi

# 2. Check frontend build capability
print_header "2. Frontend Build Validation"

cd frontend 2>/dev/null
if [ $? -eq 0 ]; then
  if [ -f "package.json" ]; then
    check_result 0 "Frontend package.json exists"
    
    # Check if node_modules exists or can be installed
    if [ -d "node_modules" ] || npm list > /dev/null 2>&1; then
      check_result 0 "Frontend dependencies are available"
    else
      print_warning "Frontend dependencies not installed, attempting install..."
      npm install > /dev/null 2>&1
      check_result $? "Frontend dependency installation"
    fi
    
    # Test build process
    print_status "Testing frontend build process..."
    npm run build > /dev/null 2>&1
    check_result $? "Frontend build process"
    
  else
    check_result 1 "Frontend package.json is missing"
  fi
else
  check_result 1 "Frontend directory is not accessible"
fi

cd .. 2>/dev/null

# 3. Check backend dependencies
print_header "3. Backend Dependencies Validation"

# Check Python version
python3 --version > /dev/null 2>&1
check_result $? "Python 3 is available"

# Check if virtual environment exists
if [ -d "venv" ]; then
  check_result 0 "Virtual environment exists"
  
  # Activate and check dependencies
  source venv/bin/activate 2>/dev/null
  if [ $? -eq 0 ]; then
    pip list | grep -q "flask"
    check_result $? "Flask is installed in virtual environment"
    
    pip list | grep -q "pytest"
    check_result $? "Pytest is installed in virtual environment"
  else
    check_result 1 "Cannot activate virtual environment"
  fi
else
  print_warning "Virtual environment not found, creating one..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt > /dev/null 2>&1
  check_result $? "Virtual environment creation and dependency installation"
fi

# 4. Test critical functionality
print_header "4. Critical Tests Validation"

# Run a subset of critical tests
if [ -d "tests" ]; then
  print_status "Running critical tests..."
  python -m pytest tests/database/ tests/utils/test_db_init.py -v --maxfail=3 --timeout=10 > /dev/null 2>&1
  check_result $? "Critical tests execution"
else
  check_result 1 "Tests directory not found"
fi

# 5. Check deployment configuration files
print_header "5. Deployment Configuration Validation"

# Check if security scripts exist
if [ -f "scripts/secure_vps_setup.sh" ]; then
  check_result 0 "VPS setup script exists"
else
  check_result 1 "VPS setup script is missing"
fi

# Check if security check script exists
if [ -f "scripts/security/check_credentials.sh" ]; then
  check_result 0 "Security check script exists"
else
  check_result 1 "Security check script is missing"
fi

# 6. Validate workflow syntax
print_header "6. Workflow Syntax Validation"

# Basic YAML syntax check for workflow
if command -v python3 > /dev/null; then
  python3 -c "
import yaml
import sys
try:
    with open('.github/workflows/manual-deploy.yml', 'r') as f:
        yaml.safe_load(f)
    sys.exit(0)
except Exception as e:
    print(f'YAML syntax error: {e}')
    sys.exit(1)
" 2>/dev/null
  check_result $? "Workflow YAML syntax is valid"
else
  print_warning "Cannot validate YAML syntax - Python not available"
fi

# 7. Generate summary report
print_header "7. Validation Summary"

echo ""
echo "Validation Results:"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  print_status "🎉 All validations passed! Deployment setup is ready."
  echo ""
  echo "Next steps:"
  echo "1. Ensure SSH key authentication is configured on VPS"
  echo "2. Verify all GitHub secrets are properly set"
  echo "3. Run the manual deployment workflow"
  exit 0
else
  print_error "⚠️  Some validations failed. Please address the issues above before deploying."
  echo ""
  echo "Common fixes:"
  echo "- Install missing dependencies"
  echo "- Fix repository structure"
  echo "- Ensure all required files are present"
  echo "- Check file permissions"
  exit 1
fi
