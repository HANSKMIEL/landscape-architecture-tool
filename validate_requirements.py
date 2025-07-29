#!/usr/bin/env python3
"""
Validation script to test requirements files installation and basic functionality.
"""

import sys
import subprocess
import tempfile
import os


def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def test_requirements_installation():
    """Test that requirements files can be parsed and dependencies checked"""
    print("Testing requirements files...")
    
    # Test requirements.txt syntax by checking it can be parsed
    try:
        with open("requirements.txt", "r") as f:
            lines = f.readlines()
        # Basic validation - check for obvious syntax errors
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                if "==" in line or ">=" in line or "<=" in line or ">" in line or "<" in line:
                    continue
                elif line.replace("-", "").replace("_", "").replace(".", "").isalnum():
                    continue
                else:
                    print(f"❌ requirements.txt line {i} has invalid syntax: {line}")
                    return False
        print("✅ requirements.txt syntax is valid")
    except Exception as e:
        print(f"❌ requirements.txt cannot be read: {e}")
        return False
    
    # Test requirements-dev.txt syntax  
    try:
        with open("requirements-dev.txt", "r") as f:
            lines = f.readlines()
        # Basic validation - check for obvious syntax errors
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                if "==" in line or ">=" in line or "<=" in line or ">" in line or "<" in line:
                    continue
                elif line.replace("-", "").replace("_", "").replace(".", "").isalnum():
                    continue
                else:
                    print(f"❌ requirements-dev.txt line {i} has invalid syntax: {line}")
                    return False
        print("✅ requirements-dev.txt syntax is valid")
    except Exception as e:
        print(f"❌ requirements-dev.txt cannot be read: {e}")
        return False
    
    # Test requirements-azure.txt syntax
    try:
        with open("requirements-azure.txt", "r") as f:
            lines = f.readlines()
        # Basic validation - check for obvious syntax errors
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                if "==" in line or ">=" in line or "<=" in line or ">" in line or "<" in line:
                    continue
                elif line.replace("-", "").replace("_", "").replace(".", "").isalnum():
                    continue
                else:
                    print(f"❌ requirements-azure.txt line {i} has invalid syntax: {line}")
                    return False
        print("✅ requirements-azure.txt syntax is valid")
    except Exception as e:
        print(f"❌ requirements-azure.txt cannot be read: {e}")
        return False
    
    return True


def test_app_imports():
    """Test that the application can import with current dependencies"""
    print("\nTesting application imports...")
    
    # Test Flask app creation
    test_code = """
import sys
sys.path.insert(0, '.')
try:
    from src.main import create_app
    app = create_app()
    print('Flask app creation: SUCCESS')
except Exception as e:
    print(f'Flask app creation: FAILED - {e}')
    sys.exit(1)
"""
    
    success, stdout, stderr = run_command(f"python3 -c \"{test_code}\"")
    if not success:
        print("❌ Flask app cannot be created")
        print(f"Error: {stderr}")
        return False
    print("✅ Flask app can be created successfully")
    
    # Test pandas import (used in products route)
    test_code = """
import sys
sys.path.insert(0, '.')
try:
    from src.routes.products import get_products
    print('Pandas import in products route: SUCCESS')
except Exception as e:
    print(f'Pandas import: FAILED - {e}')
    sys.exit(1)
"""
    
    success, stdout, stderr = run_command(f"python3 -c \"{test_code}\"")
    if not success:
        print("❌ Products route cannot import pandas")
        print(f"Error: {stderr}")
        return False
    print("✅ Products route imports pandas successfully")
    
    return True


def test_factory_boy():
    """Test factory_boy functionality for tests"""
    print("\nTesting factory_boy for test fixtures...")
    
    test_code = """
import sys
sys.path.insert(0, '.')
try:
    from tests.fixtures.test_data import UserFactory, SupplierFactory
    print('Factory fixtures import: SUCCESS')
except Exception as e:
    print(f'Factory fixtures import: FAILED - {e}')
    sys.exit(1)
"""
    
    success, stdout, stderr = run_command(f"python3 -c \"{test_code}\"")
    if not success:
        print("❌ Factory fixtures cannot be imported")
        print(f"Error: {stderr}")
        return False
    print("✅ Factory fixtures import successfully")
    
    return True


def main():
    """Run all validation tests"""
    print("🔍 Validating requirements files and dependencies...\n")
    
    tests = [
        test_requirements_installation,
        test_app_imports,
        test_factory_boy,
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All validation tests passed!")
        print("✅ Requirements files are correctly structured")
        print("✅ Application dependencies are satisfied")
        print("✅ Test infrastructure is working")
        return 0
    else:
        print("❌ Some validation tests failed!")
        print("Please check the requirements files and dependencies")
        return 1


if __name__ == "__main__":
    sys.exit(main())