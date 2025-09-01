#!/usr/bin/env python3
"""
Automated Validation Script for Landscape Architecture Tool

This script runs comprehensive validation after any code changes to ensure
the pipeline remains healthy and all systems are working properly.

This addresses the user's frustration about having to constantly check
if everything is working after changes.
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class AutomatedValidator:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "validation_steps": {},
            "summary": {},
            "recommendations": [],
        }

    def run_command(self, cmd, timeout=60, capture_output=True):
        """Run a command and capture its output"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=capture_output, text=True, timeout=timeout, cwd=self.repo_root
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e)}

    def validate_git_status(self):
        """Check git status and recent changes"""
        print("🔍 Validating git status...")

        # Check for uncommitted changes
        result = self.run_command("git status --porcelain")
        uncommitted_files = len(result["stdout"].strip().split("\n")) if result["stdout"].strip() else 0

        # Check recent commits
        recent_commits = self.run_command("git log --oneline -5")

        status = "healthy" if result["success"] else "error"

        self.results["validation_steps"]["git_status"] = {
            "status": status,
            "uncommitted_files": uncommitted_files,
            "recent_commits": recent_commits["stdout"].split("\n")[:5] if recent_commits["success"] else [],
        }

        return status == "healthy"

    def validate_dependencies(self):
        """Check dependency installation and conflicts"""
        print("📦 Validating dependencies...")

        # Check Python dependencies
        pip_check = self.run_command("pip check", timeout=30)

        # Check frontend dependencies
        npm_check = self.run_command("cd frontend && npm ls --depth=0", timeout=30)

        status = "healthy" if pip_check["success"] and npm_check["success"] else "warning"

        self.results["validation_steps"]["dependencies"] = {
            "status": status,
            "pip_check": pip_check["success"],
            "npm_check": npm_check["success"],
            "pip_errors": pip_check["stderr"] if not pip_check["success"] else "",
            "npm_errors": npm_check["stderr"] if not npm_check["success"] else "",
        }

        return status == "healthy"

    def validate_code_quality(self):
        """Run linting and code quality checks"""
        print("🧹 Validating code quality...")

        # Run linting
        lint_result = self.run_command("make lint", timeout=60)

        # Run additional quality checks
        ruff_result = self.run_command("ruff check . --output-format=json", timeout=30)

        status = "healthy" if lint_result["success"] else "error"

        quality_issues = []
        if ruff_result["success"] and ruff_result["stdout"]:
            try:
                ruff_data = json.loads(ruff_result["stdout"])
                quality_issues = ruff_data if isinstance(ruff_data, list) else []
            except (json.JSONDecodeError, ValueError):
                pass

        self.results["validation_steps"]["code_quality"] = {
            "status": status,
            "linting_passed": lint_result["success"],
            "quality_issues_count": len(quality_issues),
            "quality_issues": quality_issues[:10],  # First 10 issues
        }

        if len(quality_issues) > 0:
            self.results["recommendations"].append(
                f"Found {len(quality_issues)} code quality issues. Run 'ruff check .' for details."
            )

        return status == "healthy"

    def validate_tests(self):
        """Run test suite and check for failures with enhanced reliability"""
        print("🧪 Validating test suite...")

        # Run backend tests with enhanced configuration for stability
        backend_test = self.run_command(
            "PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/ "
            "--tb=short --maxfail=10 -q --durations=0 --timeout=60", 
            timeout=300  # Increased timeout for stability
        )

        # Run frontend tests with proper command (same as CI)
        frontend_test = self.run_command("cd frontend && npm run test:coverage", timeout=90)

        # Enhanced result parsing with retry logic
        backend_passed = backend_test["success"]
        frontend_passed = frontend_test["success"]
        
        # If backend tests failed, try one more time to handle transient issues
        if not backend_passed and "timeout" not in backend_test.get("stderr", "").lower():
            print("🔄 Retrying backend tests due to potential transient failure...")
            backend_retry = self.run_command(
                "PYTHONPATH=. FLASK_ENV=testing python -m pytest tests/ "
                "--tb=short --maxfail=5 -v --timeout=60", 
                timeout=300
            )
            if backend_retry["success"]:
                backend_passed = True
                backend_test = backend_retry
                print("✅ Backend tests passed on retry")
            else:
                print("❌ Backend tests failed on retry as well")

        # If frontend tests failed, try one more time  
        if not frontend_passed and "timeout" not in frontend_test.get("stderr", "").lower():
            print("🔄 Retrying frontend tests due to potential transient failure...")
            frontend_retry = self.run_command("cd frontend && npm run test:coverage", timeout=90)
            if frontend_retry["success"]:
                frontend_passed = True
                frontend_test = frontend_retry
                print("✅ Frontend tests passed on retry")
            else:
                print("❌ Frontend tests failed on retry as well")

        # Extract test counts from output
        backend_summary = self._parse_test_output(backend_test["stdout"])
        frontend_summary = self._parse_vitest_output(frontend_test["stdout"])

        overall_status = "healthy" if backend_passed and frontend_passed else "error"

        self.results["validation_steps"]["tests"] = {
            "status": overall_status,
            "backend": {
                "passed": backend_passed,
                "summary": backend_summary,
                "stderr": backend_test["stderr"][:500] if backend_test["stderr"] else "",
            },
            "frontend": {
                "passed": frontend_passed,
                "summary": frontend_summary,
                "stderr": frontend_test["stderr"][:500] if frontend_test["stderr"] else "",
            },
        }

        if not backend_passed:
            self.results["recommendations"].append(
                "Backend tests failing. Run 'make backend-test' for detailed output."
            )

        if not frontend_passed:
            self.results["recommendations"].append(
                "Frontend tests failing. Run 'cd frontend && npm run test:coverage' for details."
            )

        return overall_status == "healthy"

    def validate_application_health(self):
        """Check if the application can start and basic endpoints work"""
        print("🏥 Validating application health...")

        try:
            # Test Flask app creation
            app_test = self.run_command(
                'PYTHONPATH=. python -c "from src.main import create_app; '
                "app = create_app(); print('✅ App created successfully')\"",
                timeout=30,
            )

            # Test basic imports
            import_test = self.run_command(
                'PYTHONPATH=. python -c "from src.models.landscape import Plant, Supplier; '
                "print('✅ Models imported successfully')\"",
                timeout=10,
            )

            app_healthy = app_test["success"]
            imports_healthy = import_test["success"]

            status = "healthy" if app_healthy and imports_healthy else "error"

            self.results["validation_steps"]["application_health"] = {
                "status": status,
                "app_creation": app_healthy,
                "model_imports": imports_healthy,
                "app_error": app_test["stderr"] if not app_healthy else "",
                "import_error": import_test["stderr"] if not imports_healthy else "",
            }

            if not app_healthy:
                self.results["recommendations"].append(
                    "Application cannot start. Check dependencies and configuration."
                )

            return status == "healthy"

        except Exception as e:
            self.results["validation_steps"]["application_health"] = {"status": "error", "error": str(e)}
            return False

    def validate_database_setup(self):
        """Check database configuration and connectivity"""
        print("🗄️ Validating database setup...")

        try:
            # Test database initialization - create a simple script
            script_content = """
from src.main import create_app
from src.utils.db_init import initialize_database
app = create_app()
ctx = app.app_context()
ctx.push()
initialize_database()
ctx.pop()
print('Database initialized')
"""

            # Write temporary script and execute it
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(script_content)
                script_path = f.name

            try:
                db_test = self.run_command(f"PYTHONPATH=. python {script_path}", timeout=30)
            finally:
                # Clean up temporary file
                import os

                try:
                    os.unlink(script_path)
                except OSError:
                    pass

            status = "healthy" if db_test["success"] else "error"

            self.results["validation_steps"]["database"] = {
                "status": status,
                "initialization": db_test["success"],
                "error": db_test["stderr"] if not db_test["success"] else "",
            }

            if not db_test["success"]:
                self.results["recommendations"].append("Database initialization failed. Check database configuration.")

            return status == "healthy"

        except Exception as e:
            self.results["validation_steps"]["database"] = {"status": "error", "error": str(e)}
            return False

    def _parse_test_output(self, output):
        """Parse pytest output to extract test summary with improved robustness"""
        if not output:
            return {"total": 0, "passed": 0, "failed": 0, "errors": 0}

        lines = output.split("\n")
        summary_line = None

        # Try multiple patterns to find the summary line
        patterns = [
            # Standard pytest summary patterns
            lambda line: "passed" in line
            and any(keyword in line for keyword in ["failed", "error", "warning", "skipped"]),
            lambda line: line.strip().endswith("passed"),
            lambda line: line.strip().endswith("failed"),
            lambda line: " passed," in line or " failed," in line,
            # Handle different pytest output formats
            lambda line: "==" in line and any(keyword in line for keyword in ["passed", "failed", "error"]),
        ]

        for pattern in patterns:
            for line in lines:
                try:
                    if pattern(line):
                        summary_line = line
                        break
                except (AttributeError, TypeError):
                    continue
            if summary_line:
                break

        if summary_line:
            # Robust parsing with multiple extraction methods
            summary = {"raw": summary_line.strip()}

            # Try regex-based extraction
            numbers = re.findall(r"(\d+)\s*(passed|failed|error|skipped)", summary_line, re.IGNORECASE)

            for count, status in numbers:
                try:
                    summary[status.lower()] = int(count)
                except (ValueError, KeyError):
                    pass

            # Fallback to simple word-based parsing
            if not any(key in summary for key in ["passed", "failed"]):
                parts = summary_line.split()
                for i, part in enumerate(parts):
                    try:
                        if part.isdigit():
                            next_part = parts[i + 1] if i + 1 < len(parts) else ""
                            if "passed" in next_part.lower():
                                summary["passed"] = int(part)
                            elif "failed" in next_part.lower():
                                summary["failed"] = int(part)
                            elif "error" in next_part.lower():
                                summary["errors"] = int(part)
                    except (ValueError, IndexError):
                        continue

            return summary

        return {"raw": "Could not parse test output", "total": 0}

    def _parse_vitest_output(self, output):
        """Parse vitest output to extract test summary with improved robustness"""
        if not output:
            return {"total": 0, "passed": 0, "failed": 0}

        lines = output.split("\n")

        # Try multiple patterns for vitest output
        patterns = [
            "Test Files",
            "Tests",
            "✓",
            "✗",
            "passed",
            "failed",
        ]

        summary_lines = []
        for line in lines:
            line = line.strip()
            if any(pattern in line for pattern in patterns):
                summary_lines.append(line)

        if summary_lines:
            # Find the most informative summary line
            for line in summary_lines:
                if any(word in line.lower() for word in ["test files", "tests"]) and any(
                    char.isdigit() for char in line
                ):
                    # Extract numbers from the line
                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        return {
                            "raw": line,
                            "total": int(numbers[0]) if numbers else 0,
                            "passed": int(numbers[1]) if len(numbers) > 1 else int(numbers[0]) if numbers else 0,
                        }

            # Fallback to first informative line
            return {"raw": summary_lines[0]}

        return {"raw": "Could not parse vitest output"}

    def generate_overall_status(self):
        """Generate overall status based on all validation steps"""
        statuses = [step.get("status", "error") for step in self.results["validation_steps"].values()]

        if all(status == "healthy" for status in statuses):
            self.results["overall_status"] = "healthy"
        elif any(status == "error" for status in statuses):
            self.results["overall_status"] = "error"
        else:
            self.results["overall_status"] = "warning"

    def generate_summary(self):
        """Generate summary and recommendations"""
        steps = self.results["validation_steps"]

        total_steps = len(steps)
        healthy_steps = sum(1 for step in steps.values() if step.get("status") == "healthy")

        self.results["summary"] = {
            "total_steps": total_steps,
            "healthy_steps": healthy_steps,
            "health_percentage": round((healthy_steps / total_steps) * 100, 1) if total_steps > 0 else 0,
            "status_distribution": {
                "healthy": sum(1 for step in steps.values() if step.get("status") == "healthy"),
                "warning": sum(1 for step in steps.values() if step.get("status") == "warning"),
                "error": sum(1 for step in steps.values() if step.get("status") == "error"),
            },
        }

        # Add general recommendations
        if self.results["overall_status"] == "error":
            self.results["recommendations"].insert(
                0, "❌ Critical issues found. Address errors before continuing development."
            )
        elif self.results["overall_status"] == "warning":
            self.results["recommendations"].insert(0, "⚠️ Some issues found. Review warnings and consider fixing them.")
        else:
            self.results["recommendations"].insert(0, "✅ All validation checks passed! Pipeline is healthy.")

    def save_report(self):
        """Save validation report to file"""
        report_file = self.repo_root / f"automated_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"📊 Full report saved to: {report_file}")
        return report_file

    def print_summary(self):
        """Print a concise summary to console"""
        print("\n" + "=" * 50)
        print("🔍 AUTOMATED VALIDATION SUMMARY")
        print("=" * 50)

        summary = self.results["summary"]
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        health_pct = summary["health_percentage"]
        healthy_steps = summary["healthy_steps"]
        total_steps = summary["total_steps"]
        print(f"Health Score: {health_pct}% ({healthy_steps}/{total_steps} checks passed)")

        print("\nValidation Steps:")
        for step_name, step_data in self.results["validation_steps"].items():
            status_icon = {"healthy": "✅", "warning": "⚠️", "error": "❌"}.get(step_data["status"], "❓")
            print(f"  {status_icon} {step_name}: {step_data['status']}")

        print("\nRecommendations:")
        for i, rec in enumerate(self.results["recommendations"][:5], 1):
            print(f"  {i}. {rec}")

        if len(self.results["recommendations"]) > 5:
            print(f"  ... and {len(self.results['recommendations']) - 5} more recommendations")

        print("=" * 50)

    def run_full_validation(self):
        """Run the complete validation suite"""
        print("🚀 Starting Automated Validation...")
        print("This will comprehensively test the entire pipeline.\n")

        start_time = time.time()

        # Run all validation steps
        validation_steps = [
            ("Git Status", self.validate_git_status),
            ("Dependencies", self.validate_dependencies),
            ("Code Quality", self.validate_code_quality),
            ("Application Health", self.validate_application_health),
            ("Database Setup", self.validate_database_setup),
            ("Test Suite", self.validate_tests),
        ]

        for step_name, step_func in validation_steps:
            try:
                step_func()
            except Exception as e:
                print(f"❌ {step_name} validation failed with exception: {e}")
                self.results["validation_steps"][step_name.lower().replace(" ", "_")] = {
                    "status": "error",
                    "error": str(e),
                }

        # Generate final results
        self.generate_overall_status()
        self.generate_summary()

        # Output results
        duration = time.time() - start_time
        print(f"\n⏱️ Validation completed in {duration:.1f} seconds")

        self.print_summary()
        report_file = self.save_report()

        # Return status for programmatic use
        return {
            "success": self.results["overall_status"] == "healthy",
            "status": self.results["overall_status"],
            "summary": self.results["summary"],
            "report_file": str(report_file),
        }


def main():
    """Main entry point"""
    validator = AutomatedValidator()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            print("🏃‍♂️ Running quick validation (skipping tests)...")
            validator.validate_git_status()
            validator.validate_dependencies()
            validator.validate_code_quality()
            validator.validate_application_health()
        elif sys.argv[1] == "--tests-only":
            print("🧪 Running test validation only...")
            validator.validate_tests()
        else:
            print("Usage: python automated_validation.py [--quick|--tests-only]")
            return
    else:
        # Run full validation
        result = validator.run_full_validation()

        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)

    # For partial runs, still generate results
    validator.generate_overall_status()
    validator.generate_summary()
    validator.print_summary()
    validator.save_report()


if __name__ == "__main__":
    main()
