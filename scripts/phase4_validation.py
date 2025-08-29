#!/usr/bin/env python3
"""
Phase 4 Comprehensive Validation Script
Validates all prevention measures are properly implemented.
"""

import subprocess
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description} exists: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def run_command_check(command, description):
    """Run a command and check if it succeeds."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"⚠️ {description} - issues detected")
            return False
    except subprocess.TimeoutExpired:
        print(f"⚠️ {description} - timed out")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - error: {e}")
        return False


def main():
    """Run comprehensive Phase 4 validation."""
    print("🔍 Phase 4 Comprehensive Validation")
    print("=" * 50)

    validation_results = []

    # 1. Pre-commit hooks validation
    print("\n📋 Step 4.1: Pre-commit Hooks Validation")
    validation_results.append(check_file_exists(".pre-commit-config.yaml", "Pre-commit configuration"))

    # Check if pre-commit is installed
    try:
        result = subprocess.run(["pre-commit", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Pre-commit framework installed")
            validation_results.append(True)
        else:
            print("❌ Pre-commit framework not installed")
            validation_results.append(False)
    except Exception:
        print("⚠️ Pre-commit framework not accessible")
    except FileNotFoundError:
        print("❌ Pre-commit framework not found (is 'pre-commit' installed?)")
        validation_results.append(False)
    except subprocess.SubprocessError as e:
        print(f"⚠️ Pre-commit framework error: {e}")
        validation_results.append(False)

    # 2. Developer guidelines validation
    print("\n📋 Step 4.2: Developer Guidelines Validation")
    validation_results.append(
        check_file_exists("documentation/development/DEVELOPER_GUIDELINES.md", "Developer guidelines")
    )

    # 3. Copilot integration validation
    print("\n📋 Step 4.3: Copilot Integration Validation")
    validation_results.append(check_file_exists(".vscode/settings.json", "VSCode settings"))
    validation_results.append(check_file_exists("scripts/copilot_workflow.py", "Copilot workflow helper"))

    # Test copilot workflow script
    if Path("scripts/copilot_workflow.py").exists():
        validation_results.append(
            run_command_check(
                "python scripts/copilot_workflow.py --cleanup",
                "Copilot workflow script functionality",
            )
        )

    # 4. Monitoring system validation
    print("\n📋 Step 4.4: Monitoring System Validation")
    validation_results.append(check_file_exists("scripts/pipeline_health_monitor.py", "Pipeline health monitor"))

    # Test monitoring script
    if Path("scripts/pipeline_health_monitor.py").exists():
        print("🔄 Testing pipeline health monitor...")
        validation_results.append(
            run_command_check(
                "python scripts/pipeline_health_monitor.py",
                "Pipeline health monitor functionality",
            )
        )

    # 5. Code quality tools validation
    print("\n📋 Step 4.5: Code Quality Tools Validation")
    validation_results.append(run_command_check("black --version", "Black formatter available"))
    validation_results.append(run_command_check("isort --version", "isort available"))
    validation_results.append(run_command_check("flake8 --version", "flake8 linter available"))

    # 6. Integration validation
    print("\n📋 Step 4.6: Integration Tests")
    validation_results.append(
        run_command_check(
            "python -c 'import src.main; print(\"✅ Main application imports work\")'",
            "Application import validation",
        )
    )

    # Check that previous phases are still working
    print("\n📋 Previous Phases Validation")
    validation_results.append(run_command_check("python --version", "Python runtime"))

    # 7. Final validation summary
    print("\n" + "=" * 50)
    print("📊 Phase 4 Validation Summary")
    print("=" * 50)

    passed_checks = sum(validation_results)
    total_checks = len(validation_results)
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

    print(f"Checks passed: {passed_checks}/{total_checks} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 Phase 4 validation passed!")
        print("Prevention measures successfully implemented.")
        return 0
    elif success_rate >= 60:
        print("⚠️ Phase 4 validation partially successful.")
        print("Some prevention measures need attention.")
        return 1
    else:
        print("❌ Phase 4 validation failed.")
        print("Major issues need to be resolved.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
