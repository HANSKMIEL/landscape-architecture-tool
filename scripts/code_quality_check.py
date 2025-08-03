#!/usr/bin/env python3
"""
Code Quality Check Script
Comprehensive validation of code quality standards for the Landscape Architecture Tool
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status and output"""
    print(f"\n🔍 {description}")
    print("=" * 60)

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0:
            print(f"✅ PASSED: {description}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ FAILED: {description}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description}")
        return False, "Command timed out"
    except Exception as e:
        print(f"💥 ERROR: {description} - {e}")
        return False, str(e)


def main():
    """Run comprehensive code quality checks"""
    print("🚀 Landscape Architecture Tool - Code Quality Check")
    print("=" * 60)

    # Change to project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")

    checks = [
        # Syntax and import validation
        (
            f"python -c 'import src.main; print(\"✅ Main module imports successfully\")'",
            "Main module import validation",
        ),
        # Critical flake8 checks (syntax errors, undefined names)
        (
            "python -m flake8 --count --select=E9,F63,F7,F82 --show-source --statistics src/ tests/",
            "Critical syntax and undefined name checks",
        ),
        # Line length and basic formatting
        (
            "python -m flake8 tests/test_integration.py --max-line-length=88 --extend-ignore=E203,W503,F401,F403,E402,C901,W291",
            "Integration test formatting check",
        ),
        # Black formatting check
        (
            "python -m black --check tests/test_integration.py --diff",
            "Black formatting validation",
        ),
        # Test file syntax validation
        (
            "python -m py_compile tests/test_integration.py",
            "Integration test syntax validation",
        ),
        # Quick integration test run
        (
            "python -m pytest tests/test_integration.py -v --tb=short --maxfail=1",
            "Integration test execution",
        ),
    ]

    results = []

    for cmd, description in checks:
        success, output = run_command(cmd, description)
        results.append((description, success, output))

    # Summary
    print("\n" + "=" * 60)
    print("📊 CODE QUALITY SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for description, success, output in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")

    print(
        f"\n🎯 Overall Score: {passed}/{total} checks passed ({passed/total*100:.1f}%)"
    )

    if passed == total:
        print("🎉 All code quality checks passed!")
        return 0
    else:
        print("⚠️  Some code quality issues detected")
        return 1


if __name__ == "__main__":
    sys.exit(main())
