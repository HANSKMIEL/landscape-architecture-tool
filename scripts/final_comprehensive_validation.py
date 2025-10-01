#!/usr/bin/env python3
"""
Final Comprehensive Validation Script for V1.00D Branch
Performs extensive tests and validations on all PR files
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, description, timeout=120):
    """Run a command and capture output"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*80}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

        output = {
            "description": description,
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout[:2000] if result.stdout else "",
            "stderr": result.stderr[:2000] if result.stderr else "",
            "status": "PASS" if result.returncode == 0 else "FAIL",
        }

        # Print summary
        print(f"Status: {output['status']}")
        if result.stdout:
            print(f"Output (first 500 chars): {result.stdout[:500]}")
        if result.stderr and result.returncode != 0:
            print(f"Errors: {result.stderr[:500]}")

        return output

    except subprocess.TimeoutExpired:
        return {
            "description": description,
            "command": cmd,
            "returncode": -1,
            "status": "TIMEOUT",
            "error": f"Command timed out after {timeout} seconds",
        }
    except Exception as e:
        return {"description": description, "command": cmd, "returncode": -1, "status": "ERROR", "error": str(e)}


def main():
    """Run comprehensive validation suite"""

    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "validation_suite": "Final Comprehensive V1.00D Branch Validation",
        "tests": [],
    }

    # Backend tests
    print("\n" + "=" * 80)
    print("PHASE 1: BACKEND TESTING")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/ -v --tb=short --maxfail=5",
            "Backend Unit Tests",
            timeout=240,
        )
    )

    # Code formatting validation
    print("\n" + "=" * 80)
    print("PHASE 2: CODE FORMATTING VALIDATION")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && python -m black --check src/ tests/ scripts/",
            "Black Code Formatting Check",
        )
    )

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && python -m isort --check-only src/ tests/ scripts/",
            "Import Organization Check (isort)",
        )
    )

    # Linting validation
    print("\n" + "=" * 80)
    print("PHASE 3: CODE QUALITY LINTING")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && python -m ruff check src/ tests/ scripts/ --statistics",
            "Ruff Linting Analysis",
        )
    )

    # Security scanning
    print("\n" + "=" * 80)
    print("PHASE 4: SECURITY SCANNING")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && python -m bandit -r src/ -f json -o /tmp/bandit_final.json",
            "Bandit Security Scan",
        )
    )

    # Frontend linting
    print("\n" + "=" * 80)
    print("PHASE 5: FRONTEND VALIDATION")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool/frontend && npm run lint",
            "ESLint Frontend Validation",
            timeout=180,
        )
    )

    # Repository structure validation
    print("\n" + "=" * 80)
    print("PHASE 6: REPOSITORY STRUCTURE VALIDATION")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && find . -name '*.pyc' -o -name '__pycache__' | wc -l",
            "Check for compiled Python files",
        )
    )

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && git status --porcelain | wc -l",
            "Check for uncommitted changes",
        )
    )

    # Dependencies validation
    print("\n" + "=" * 80)
    print("PHASE 7: DEPENDENCIES VALIDATION")
    print("=" * 80)

    validation_results["tests"].append(
        run_command(
            "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && pip check",
            "Python Dependencies Check",
        )
    )

    # Calculate summary statistics
    total_tests = len(validation_results["tests"])
    passed_tests = sum(1 for t in validation_results["tests"] if t["status"] == "PASS")
    failed_tests = sum(1 for t in validation_results["tests"] if t["status"] == "FAIL")
    error_tests = sum(1 for t in validation_results["tests"] if t["status"] in ["ERROR", "TIMEOUT"])

    validation_results["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "errors": error_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
    }

    # Print final summary
    print("\n" + "=" * 80)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    print(f"Success Rate: {validation_results['summary']['success_rate']}")
    print("=" * 80)

    # Save detailed report
    report_path = Path(
        "/home/runner/work/landscape-architecture-tool/landscape-architecture-tool/reports/final_comprehensive_validation.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(validation_results, f, indent=2)

    print(f"\nDetailed report saved to: {report_path}")

    # Return exit code based on critical failures
    if failed_tests > 0 or error_tests > 0:
        print("\n⚠️  Some tests failed or had errors. Review the report for details.")
        return 1
    print("\n✅ All validation tests passed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
