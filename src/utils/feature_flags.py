"""
Feature Flags System for Safe Feature Isolation
Enables safe development and gradual rollout of new features
"""

import json
import os
from enum import Enum
from typing import Any, Dict, Optional


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class FeatureFlags:
    """
    Feature flags system for safe feature isolation and gradual rollout.

    Features are enabled/disabled based on environment and configuration.
    Development environment allows experimental features by default.
    Production environment requires explicit feature enablement.
    """

    def __init__(self, environment: str | None = None):
        self.environment = self._detect_environment(environment)
        self.flags = self._load_feature_flags()
        self._log_initialization()

    def _detect_environment(self, environment: str | None = None) -> Environment:
        """Detect current environment from various sources"""
        if environment:
            return Environment(environment.lower())

        # Check environment variables
        env_var = os.getenv("FLASK_ENV", "").lower()
        if env_var in ["development", "dev"]:
            return Environment.DEVELOPMENT
        if env_var in ["production", "prod"]:
            return Environment.PRODUCTION
        if env_var in ["staging", "stage"]:
            return Environment.STAGING

        # Check for devdeploy indicators
        if os.getenv("DEVDEPLOY_MODE") == "true":
            return Environment.DEVELOPMENT

        # Check port (development uses 5001, production uses 5000)
        port = os.getenv("PORT", "5000")
        if port == "5001":
            return Environment.DEVELOPMENT

        # Default to production for safety
        return Environment.PRODUCTION

    def _load_feature_flags(self) -> dict[str, Any]:
        """Load feature flags from configuration"""
        # Default feature flags
        default_flags = {
            # UI/UX Features
            "new_dashboard_layout": self.environment == Environment.DEVELOPMENT,
            "advanced_plant_filters": self.environment != Environment.PRODUCTION,
            "experimental_ui_components": self.environment == Environment.DEVELOPMENT,
            "dark_mode_support": False,
            # API Features
            "ai_plant_recommendations": self.environment == Environment.DEVELOPMENT,
            "advanced_project_analytics": False,
            "bulk_data_operations": self.environment != Environment.PRODUCTION,
            "api_rate_limiting": self.environment == Environment.PRODUCTION,
            # Integration Features
            "external_weather_api": False,
            "crm_integration": False,
            "email_notifications": self.environment != Environment.DEVELOPMENT,
            "sms_notifications": False,
            # Performance Features
            "database_query_caching": True,
            "image_optimization": True,
            "lazy_loading": True,
            "compression_middleware": self.environment == Environment.PRODUCTION,
            # Security Features
            "enhanced_authentication": self.environment == Environment.PRODUCTION,
            "audit_logging": True,
            "request_validation": True,
            "csrf_protection": self.environment == Environment.PRODUCTION,
            # Development Features
            "debug_toolbar": self.environment == Environment.DEVELOPMENT,
            "sql_query_logging": self.environment == Environment.DEVELOPMENT,
            "performance_profiling": self.environment != Environment.PRODUCTION,
            "test_data_generation": self.environment == Environment.DEVELOPMENT,
        }

        # Try to load from configuration file
        config_file = os.path.join(os.path.dirname(__file__), "..", "..", "config", "feature_flags.json")
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    file_flags = json.load(f)
                    default_flags.update(file_flags.get(self.environment.value, {}))
            except (json.JSONDecodeError, KeyError):
                pass  # Use defaults if config file is invalid

        # Override with environment variables
        for flag_name in default_flags:
            env_var = f"FEATURE_{flag_name.upper()}"
            env_value = os.getenv(env_var)
            if env_value is not None:
                default_flags[flag_name] = env_value.lower() in ["true", "1", "yes", "on"]

        return default_flags

    def is_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature_name: Name of the feature to check

        Returns:
            True if feature is enabled, False otherwise
        """
        return self.flags.get(feature_name, False)

    def enable_feature(self, feature_name: str, enabled: bool = True):
        """
        Enable or disable a feature at runtime.

        Args:
            feature_name: Name of the feature
            enabled: Whether to enable (True) or disable (False) the feature
        """
        self.flags[feature_name] = enabled

    def get_enabled_features(self) -> dict[str, bool]:
        """Get all enabled features"""
        return {name: enabled for name, enabled in self.flags.items() if enabled}

    def get_all_features(self) -> dict[str, bool]:
        """Get all features with their status"""
        return self.flags.copy()

    def _log_initialization(self):
        """Log feature flags initialization for debugging"""
        if self.is_enabled("debug_toolbar"):
            enabled_count = sum(1 for enabled in self.flags.values() if enabled)
            total_count = len(self.flags)
            print(
                f"FeatureFlags initialized for {self.environment.value}: "
                f"{enabled_count}/{total_count} features enabled"
            )


# Global feature flags instance
feature_flags = FeatureFlags()


def require_feature(feature_name: str):
    """
    Decorator to require a feature flag for a route or function.

    Usage:
        @app.route('/api/experimental')
        @require_feature('experimental_api')
        def experimental_endpoint():
            return jsonify({'status': 'experimental'})
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not feature_flags.is_enabled(feature_name):
                from flask import jsonify

                return (
                    jsonify(
                        {
                            "error": "Feature not available",
                            "feature": feature_name,
                            "environment": feature_flags.environment.value,
                        }
                    ),
                    404,
                )
            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return decorator


def feature_enabled(feature_name: str) -> bool:
    """
    Simple function to check if a feature is enabled.

    Usage:
        if feature_enabled('new_dashboard_layout'):
            # Use new layout
        else:
            # Use old layout
    """
    return feature_flags.is_enabled(feature_name)


# Example usage patterns
if __name__ == "__main__":
    # Example usage
    flags = FeatureFlags()

    print(f"Environment: {flags.environment.value}")
    print(f"AI recommendations enabled: {flags.is_enabled('ai_plant_recommendations')}")
    print(f"Debug toolbar enabled: {flags.is_enabled('debug_toolbar')}")

    print("\nEnabled features:")
    for feature, _enabled in flags.get_enabled_features().items():
        print(f"  - {feature}")
