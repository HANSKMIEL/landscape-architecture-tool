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
    RATELIMIT_STORAGE_OPTIONS = {"host": "localhost", "port": 6379, "db": 0}
    RATELIMIT_STRATEGY = "moving-window"

    # CORS settings
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5174,http://127.0.0.1:5174"
    ).split(",")

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # N8n Integration Configuration
    N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
    N8N_WEBHOOK_SECRET = os.environ.get("N8N_WEBHOOK_SECRET")
    N8N_BASIC_AUTH_USER = os.environ.get("N8N_BASIC_AUTH_USER", "admin")
    N8N_BASIC_AUTH_PASSWORD = os.environ.get("N8N_BASIC_AUTH_PASSWORD")

    # Webhook timeout settings
    N8N_WEBHOOK_TIMEOUT = int(os.environ.get("N8N_WEBHOOK_TIMEOUT", "30"))


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


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DEBUG = True
    # Use DATABASE_URL if provided (for CI integration tests),
    # otherwise use in-memory SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///:memory:"
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
