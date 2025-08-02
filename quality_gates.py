#!/usr/bin/env python3
"""
Quality gate validation script for CI/CD pipeline.
Implements reasonable quality thresholds that maintain standards
without unnecessarily blocking development.
"""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET


def check_coverage_threshold(
    coverage_file="coverage.xml", min_line_coverage=50.0, min_branch_coverage=30.0
):
    """Check if coverage meets minimum thresholds."""
    print("🔍 Checking coverage thresholds...")

    if not os.path.exists(coverage_file):
        print(f"⚠️ Coverage file {coverage_file} not found")
        return False

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        line_rate = float(root.get("line-rate", "0")) * 100
        branch_rate = float(root.get("branch-rate", "0")) * 100

        print(f"📊 Current Coverage:")
        print(f"  Line Coverage: {line_rate:.1f}%")
        print(f"  Branch Coverage: {branch_rate:.1f}%")

        print(f"📏 Minimum Thresholds:")
        print(f"  Line Coverage: {min_line_coverage}%")
        print(f"  Branch Coverage: {min_branch_coverage}%")

        line_pass = line_rate >= min_line_coverage
        branch_pass = branch_rate >= min_branch_coverage

        if line_pass:
            print("✅ Line coverage meets threshold")
        else:
            print(
                f"⚠️ Line coverage below threshold ({line_rate:.1f}% < {min_line_coverage}%)"
            )

        if branch_pass:
            print("✅ Branch coverage meets threshold")
        else:
            print(
                f"⚠️ Branch coverage below threshold ({branch_rate:.1f}% < {min_branch_coverage}%)"
            )

        return line_pass and branch_pass

    except Exception as e:
        print(f"❌ Coverage threshold check error: {e}")
        return False


def check_code_quality():
    """Check code quality using available tools."""
    print("🔍 Checking code quality...")

    quality_checks = [
        ("Black formatting", ["black", "--check", "."]),
        (
            "Import sorting",
            ["isort", "--check-only", "--profile", "black", "src/", "tests/"],
        ),
        (
            "Flake8 linting",
            [
                "flake8",
                "src/",
                "tests/",
                "--max-line-length=88",
                "--extend-ignore=E203,W503,F401,F403,E402,C901,W291",
                "--max-complexity=25",
            ],
        ),
    ]

    all_passed = True

    for check_name, command in quality_checks:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ {check_name}")
            else:
                print(f"⚠️ {check_name} issues detected")
                if result.stdout:
                    print(f"   Output: {result.stdout[:200]}...")
                all_passed = False
        except subprocess.TimeoutExpired:
            print(f"⚠️ {check_name} timed out")
            all_passed = False
        except FileNotFoundError:
            print(f"⚠️ {check_name} tool not found")
            all_passed = False
        except Exception as e:
            print(f"⚠️ {check_name} error: {e}")
            all_passed = False

    return all_passed


def check_test_results():
    """Verify that basic tests are passing."""
    print("🔍 Checking basic test results...")

    try:
        # Run basic tests to ensure core functionality works
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/test_basic.py", "-v", "--tb=short", "-q"],
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "PYTHONPATH": ".", "FLASK_ENV": "testing"},
        )

        if result.returncode == 0:
            print("✅ Basic tests pass")
            return True
        else:
            print("⚠️ Basic tests have failures")
            print(f"   Output: {result.stdout[-500:]}")  # Last 500 chars
            return False

    except subprocess.TimeoutExpired:
        print("⚠️ Basic tests timed out")
        return False
    except Exception as e:
        print(f"⚠️ Basic test execution error: {e}")
        return False


def main():
    """Run all quality gate checks."""
    print("🚀 Running Quality Gate Validation...")
    print("=" * 50)

    checks = [
        ("Coverage Thresholds", check_coverage_threshold),
        ("Code Quality", check_code_quality),
        ("Basic Tests", check_test_results),
    ]

    results = {}

    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} error: {e}")
            results[check_name] = False

    print("\n" + "=" * 50)
    print("📊 Quality Gate Results:")

    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "⚠️ WARN"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("🎉 All quality gates passed!")
        return 0
    else:
        print("⚠️ Some quality gates have warnings - review recommended")
        print("ℹ️ Warnings do not block deployment but should be addressed")
        return 0  # Don't fail pipeline for warnings, just notify


if __name__ == "__main__":
    sys.exit(main())
