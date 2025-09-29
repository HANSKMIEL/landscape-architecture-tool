#!/usr/bin/env python3
"""
Comprehensive Validation Script
Runs all tests, linting, and validations as requested by @HANSKMIEL
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description, timeout=300):
    """Run a command and return the result"""
    print(f"\n🔍 {description}")
    print(f"Command: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout.strip():
                print(f"Output: {result.stdout[:500]}...")
        else:
            print(f"⚠️ {description} - ISSUES FOUND")
            if result.stderr.strip():
                print(f"Errors: {result.stderr[:500]}...")
            if result.stdout.strip():
                print(f"Output: {result.stdout[:500]}...")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Run comprehensive validation"""
    print("🚀 Comprehensive Validation Script")
    print("=" * 50)
    
    results = []
    
    # 1. Code formatting with black
    results.append(run_command(
        "black --check src/ tests/ scripts/ --line-length=120",
        "Black code formatting check"
    ))
    
    # 2. Import sorting with isort
    results.append(run_command(
        "isort --check-only src/ tests/ scripts/ --profile=black --line-length=120",
        "Import sorting check (isort)"
    ))
    
    # 3. Linting with ruff
    results.append(run_command(
        "ruff check . --output-format=concise",
        "Code linting (ruff)"
    ))
    
    # 4. Linting with flake8
    results.append(run_command(
        "flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503,F403,C901,W291,E402 --max-complexity=25",
        "Code linting (flake8)"
    ))
    
    # 5. Backend tests
    results.append(run_command(
        "make backend-test",
        "Backend tests",
        timeout=180
    ))
    
    # 6. Frontend linting
    results.append(run_command(
        "cd frontend && npm run lint",
        "Frontend linting (ESLint)",
        timeout=60
    ))
    
    # 7. Frontend tests
    results.append(run_command(
        "cd frontend && npm run test:run",
        "Frontend tests",
        timeout=120
    ))
    
    # 8. Docker file validation
    results.append(run_command(
        "docker build --dry-run -f Dockerfile .",
        "Dockerfile validation"
    ))
    
    # 9. Requirements validation
    results.append(run_command(
        "pip-compile --dry-run requirements.in",
        "Requirements validation"
    ))
    
    # 10. Security check
    results.append(run_command(
        "bandit -r src/ -f json -o bandit-report.json",
        "Security scan (bandit)"
    ))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"⚠️ Issues: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} validations have issues that need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())