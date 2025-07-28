#!/usr/bin/env python3
"""
Configuration settings for the Landscape Architecture Management System
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///landscape_architecture.db"
    )

    # Security configurations
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL") or "memory://"
    RATELIMIT_DEFAULT = "100 per hour"

    # CORS settings
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5174,http://127.0.0.1:5174"
    ).split(",")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Performance monitoring
    PERFORMANCE_MONITORING_ENABLED = True
    SLOW_REQUEST_THRESHOLD = float(os.environ.get("SLOW_REQUEST_THRESHOLD", "1.0"))
    SLOW_QUERY_THRESHOLD = float(os.environ.get("SLOW_QUERY_THRESHOLD", "0.1"))
    MEMORY_MONITORING_ENABLED = True
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", "300"))


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Production database - use SQLite for demo, PostgreSQL in real production
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///landscape_architecture_prod.db"
    )

    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Stricter rate limiting in production
    RATELIMIT_DEFAULT = "50 per hour"

    # Production logging
    LOG_LEVEL = "WARNING"

    # Production performance settings
    SLOW_REQUEST_THRESHOLD = 0.5  # Stricter in production
    SLOW_QUERY_THRESHOLD = 0.05   # Stricter in production


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable"""
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
