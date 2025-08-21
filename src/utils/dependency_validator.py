#!/usr/bin/env python3
"""
Dependency Validation Utility
Ensures critical production dependencies are available and provides graceful degradation
for optional dependencies while alerting to any missing critical components.
"""

import importlib.util
import logging
import sys
import warnings
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DependencyValidator:
    """
    Validates application dependencies and provides graceful handling
    for missing optional dependencies while ensuring critical ones are available.
    """

    # Critical dependencies required for basic application functionality
    CRITICAL_DEPENDENCIES = {
        "flask": "Flask web framework - core application functionality",
        "sqlalchemy": "SQLAlchemy ORM - database operations",
        "werkzeug": "Werkzeug WSGI - web server interface",
        "psycopg2": "PostgreSQL adapter - production database connectivity",
        "redis": "Redis client - caching and session management",
        "python-dotenv": "Environment variable management",
        "flask_cors": "Cross-Origin Resource Sharing support",
        "flask_migrate": "Database migration support",
        "flask_sqlalchemy": "Flask-SQLAlchemy integration",
    }

    # Optional dependencies that enhance functionality but aren't critical
    OPTIONAL_DEPENDENCIES = {
        "factory_boy": "Test data generation - development/testing only",
        "faker": "Test data generation - development/testing only",
        "pytest": "Testing framework - development/testing only",
        "black": "Code formatting - development only",
        "flake8": "Code linting - development only",
        "bandit": "Security scanning - development only",
        "sphinx": "Documentation generation - development only",
    }

    def __init__(self):
        self.missing_critical: List[str] = []
        self.missing_optional: List[str] = []
        self.validation_results: Dict[str, bool] = {}

    def _check_dependency(self, dependency_name: str) -> bool:
        """
        Check if a specific dependency is available.

        Args:
            dependency_name: Name of the dependency to check

        Returns:
            bool: True if dependency is available, False otherwise
        """
        try:
            # Handle special cases for package names that differ from import names
            import_name = dependency_name
            if dependency_name == "python-dotenv":
                import_name = "dotenv"
            elif dependency_name == "factory_boy":
                import_name = "factory"
            elif dependency_name == "flask_cors":
                import_name = "flask_cors"
            elif dependency_name == "flask_migrate":
                import_name = "flask_migrate"
            elif dependency_name == "flask_sqlalchemy":
                import_name = "flask_sqlalchemy"

            spec = importlib.util.find_spec(import_name)
            return spec is not None
        except (ImportError, ValueError, AttributeError):
            return False

    def validate_critical_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Validate all critical dependencies required for application functionality.

        Returns:
            Tuple[bool, List[str]]: (success, list of missing dependencies)
        """
        logger.info("Validating critical production dependencies...")

        for dep_name, description in self.CRITICAL_DEPENDENCIES.items():
            is_available = self._check_dependency(dep_name)
            self.validation_results[dep_name] = is_available

            if not is_available:
                self.missing_critical.append(dep_name)
                logger.error(f"CRITICAL DEPENDENCY MISSING: {dep_name} - {description}")
            else:
                logger.debug(f"✅ {dep_name} available")

        success = len(self.missing_critical) == 0

        if success:
            logger.info("✅ All critical dependencies validated successfully")
        else:
            logger.error(
                f"❌ {len(self.missing_critical)} critical dependencies missing"
            )

        return success, self.missing_critical

    def validate_optional_dependencies(self) -> Tuple[int, List[str]]:
        """
        Validate optional dependencies and warn about missing ones.

        Returns:
            Tuple[int, List[str]]: (number of available optional deps, list of missing)
        """
        logger.info("Checking optional dependencies...")

        available_count = 0
        for dep_name, description in self.OPTIONAL_DEPENDENCIES.items():
            is_available = self._check_dependency(dep_name)
            self.validation_results[dep_name] = is_available

            if is_available:
                available_count += 1
                logger.debug(f"✅ {dep_name} available")
            else:
                self.missing_optional.append(dep_name)
                logger.warning(
                    f"Optional dependency missing: {dep_name} - {description}"
                )

        if self.missing_optional:
            warnings.warn(
                f"Some optional dependencies are missing: {', '.join(self.missing_optional)}. "
            install_cmds = [
                f"  {dep}: pip install {dep.replace('_', '-')}"
                for dep in self.missing_optional
            ]
            warning_msg = (
                f"Some optional dependencies are missing: {', '.join(self.missing_optional)}.\n"
                "This may limit development/testing features but won't affect core functionality.\n"
                "To install the missing dependencies, run:\n"
                + "\n".join(install_cmds)
            )
            warnings.warn(
                warning_msg,
                UserWarning,
            )

        logger.info(
            f"Optional dependencies: {available_count}/{len(self.OPTIONAL_DEPENDENCIES)} available"
        )
        return available_count, self.missing_optional

    def get_validation_report(self) -> str:
        """
        Generate a comprehensive validation report.

        Returns:
            str: Formatted validation report
        """
        report_lines = [
            "Dependency Validation Report",
            "=" * 50,
            "",
            "Critical Dependencies (Required for Production):",
        ]

        for dep_name, description in self.CRITICAL_DEPENDENCIES.items():
            status = (
                "✅ AVAILABLE"
                if self.validation_results.get(dep_name, False)
                else "❌ MISSING"
            )
            report_lines.append(f"  {dep_name}: {status}")
            if not self.validation_results.get(dep_name, False):
                report_lines.append(f"    → {description}")

        report_lines.extend(
            [
                "",
                "Optional Dependencies (Development/Testing):",
            ]
        )

        for dep_name, description in self.OPTIONAL_DEPENDENCIES.items():
            status = (
                "✅ AVAILABLE"
                if self.validation_results.get(dep_name, False)
                else "⚠️  MISSING"
            )
            report_lines.append(f"  {dep_name}: {status}")

        report_lines.extend(
            [
                "",
                "Summary:",
                f"  Critical: {len(self.CRITICAL_DEPENDENCIES) - len(self.missing_critical)}/{len(self.CRITICAL_DEPENDENCIES)} available",
                f"  Optional: {len(self.OPTIONAL_DEPENDENCIES) - len(self.missing_optional)}/{len(self.OPTIONAL_DEPENDENCIES)} available",
            ]
        )

        if self.missing_critical:
            report_lines.extend(
                [
                    "",
                    "🚨 ACTION REQUIRED:",
                    "  Missing critical dependencies will prevent application from functioning.",
                    "  Install missing dependencies with: pip install -r requirements.txt",
                ]
            )
        elif self.missing_optional:
            report_lines.extend(
                [
                    "",
                    "ℹ️  INFORMATION:",
                    "  Missing optional dependencies may limit development features.",
                    "  Install with: pip install -r requirements-dev.txt",
                ]
            )
        else:
            report_lines.extend(
                [
                    "",
                    "🎉 All dependencies validated successfully!",
                ]
            )

        return "\n".join(report_lines)

    def validate_all(self) -> bool:
        """
        Perform complete dependency validation.

        Returns:
            bool: True if all critical dependencies are available
        """
        critical_success, _ = self.validate_critical_dependencies()
        self.validate_optional_dependencies()

        # Log the full report
        logger.info("\n" + self.get_validation_report())

        return critical_success

    def ensure_critical_dependencies(self) -> None:
        """
        Ensure critical dependencies are available, exit if not.
        This should be called early in application startup.
        """
        critical_success, missing = self.validate_critical_dependencies()

        if not critical_success:
            error_msg = (
                f"Application cannot start due to missing critical dependencies: {', '.join(missing)}\n"
                "Please install required dependencies with: pip install -r requirements.txt"
            )
            logger.critical(error_msg)
            print(f"🚨 CRITICAL ERROR: {error_msg}", file=sys.stderr)
            sys.exit(1)


def validate_dependencies() -> DependencyValidator:
    """
    Convenience function to create and run dependency validation.

    Returns:
        DependencyValidator: Configured validator with results
    """
    validator = DependencyValidator()
    validator.validate_all()
    return validator


if __name__ == "__main__":
    # Command-line usage
    validator = validate_dependencies()

    if validator.missing_critical:
        sys.exit(1)
    else:
        print("✅ Dependency validation completed successfully")
        sys.exit(0)
