#!/usr/bin/env python3
"""
Pipeline Health Monitoring System
Tracks CI/CD pipeline performance and identifies potential issues early.
"""

import datetime
import json
import os
import subprocess
import sys
from typing import Any, Dict


class PipelineHealthMonitor:
    def __init__(self):
        self.health_data = {}
        self.alerts = []
        self.thresholds = {
            "max_failure_rate": 0.20,
            "max_avg_duration": 1800,
            "min_success_rate": 0.80,
            "max_consecutive_failures": 3,
        }

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        checks = {
            "git_status": self._check_git_status,
            "dependencies": self._check_dependencies,
            "database": self._check_database,
            "code_quality": self._check_code_quality,
            "tests": self._check_tests,
        }

        results = {}
        overall_healthy = True

        for check_name, check_func in checks.items():
            try:
                result = check_func()
                results[check_name] = result
                if result.get("status") != "healthy":
                    overall_healthy = False
            except (subprocess.CalledProcessError, OSError) as e:
                results[check_name] = {"status": "error", "error": str(e)}
                overall_healthy = False

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "overall_status": "healthy" if overall_healthy else "warning",
            "checks": results,
        }

    def _check_git_status(self) -> Dict[str, Any]:
        """Check Git repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )
            uncommitted = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            return {
                "status": "healthy" if len(uncommitted) == 0 else "warning",
                "uncommitted_files": len(uncommitted),
            }
        except OSError as e:
            return {"status": "error", "error": str(e)}

    def _check_dependencies(self) -> Dict[str, Any]:
        """Check dependency health."""
        try:
            result = subprocess.run(["pip", "check"], capture_output=True, text=True)
            return {
                "status": "healthy" if result.returncode == 0 else "error",
                "conflicts": result.returncode != 0,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # Test basic import
            import psycopg2
            import redis

            # Test connections if services available
            postgres_ok = True
            redis_ok = True

            try:
                conn = psycopg2.connect(
                    "postgresql://postgres:postgres_password@localhost:5432/"
                    "landscape_test"
                )
                conn.close()
            except psycopg2.OperationalError:
                postgres_ok = False
            except psycopg2.DatabaseError:
                postgres_ok = False
            except Exception:
                postgres_ok = False

            try:
                r = redis.from_url("redis://localhost:6379/1")
                r.ping()
            except redis.ConnectionError:
                redis_ok = False
            except redis.RedisError:
                redis_ok = False

            if postgres_ok and redis_ok:
                status = "healthy"
            elif postgres_ok or redis_ok:
                status = "warning"
            else:
                status = "error"

            return {"status": status, "postgres": postgres_ok, "redis": redis_ok}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_code_quality(self) -> Dict[str, Any]:
        """Check code quality tools."""
        try:
            black_result = subprocess.run(
                ["black", "--check", "."], capture_output=True
            )
            isort_result = subprocess.run(
                ["isort", "--check-only", "--profile", "black", "."],
                capture_output=True,
            )

            black_ok = black_result.returncode == 0
            isort_ok = isort_result.returncode == 0

            return {
                "status": "healthy" if (black_ok and isort_ok) else "warning",
                "black": black_ok,
                "isort": isort_ok,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
        except FileNotFoundError as e:
            return {"status": "error", "error": f"File not found: {e}"}
        except OSError as e:
            return {"status": "error", "error": f"OS error: {e}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_tests(self) -> Dict[str, Any]:
        """Check basic test functionality."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/test_basic.py", "-q"],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "PYTHONPATH": ".", "FLASK_ENV": "testing"},
            )

            return {
                "status": "healthy" if result.returncode == 0 else "error",
                "tests_passing": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Tests timed out"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "error": f"Subprocess error: {e}"}
        except Exception as e:
            return {"status": "error", "error": f"Unexpected error: {e}"}


def main():
    """Main monitoring function."""
    monitor = PipelineHealthMonitor()
    health_report = monitor.check_system_health()

    print("🔍 Pipeline Health Report")
    print("=" * 40)
    print(f"Overall Status: {health_report['overall_status'].upper()}")
    print(f"Timestamp: {health_report['timestamp']}")
    print()

    for check_name, result in health_report["checks"].items():
        status = result.get("status", "unknown")
        icon = "✅" if status == "healthy" else "⚠️" if status == "warning" else "❌"
        print(f"{icon} {check_name}: {status}")
        if "error" in result:
            print(f"   Error: {result['error']}")

    # Save report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pipeline_health_report_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(health_report, f, indent=2)

    print(f"\n📊 Report saved to {filename}")

    return 0 if health_report["overall_status"] == "healthy" else 1


if __name__ == "__main__":
    sys.exit(main())
