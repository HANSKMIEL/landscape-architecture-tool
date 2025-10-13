#!/usr/bin/env python3
"""
Test that all required configuration keys are accessible
"""

import pytest

from src.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig


class TestConfigurationKeys:
    """Test that all required configuration keys exist"""

    def test_secret_key_exists(self):
        """Test that SECRET_KEY exists in config"""
        config = Config()
        assert hasattr(config, "SECRET_KEY")
        assert config.SECRET_KEY is not None

    def test_jwt_secret_key_exists(self):
        """Test that JWT_SECRET_KEY exists in config"""
        config = Config()
        assert hasattr(config, "JWT_SECRET_KEY")

    def test_encryption_key_exists(self):
        """Test that ENCRYPTION_KEY exists in config"""
        config = Config()
        assert hasattr(config, "ENCRYPTION_KEY")

    def test_openai_api_key_exists(self):
        """Test that OPENAI_API_KEY exists in config"""
        config = Config()
        assert hasattr(config, "OPENAI_API_KEY")

    def test_vectorworks_api_key_exists(self):
        """Test that VECTORWORKS_API_KEY exists in config"""
        config = Config()
        assert hasattr(config, "VECTORWORKS_API_KEY")

    def test_weather_api_key_exists(self):
        """Test that WEATHER_API_KEY exists in config"""
        config = Config()
        assert hasattr(config, "WEATHER_API_KEY")

    def test_plant_database_api_key_exists(self):
        """Test that PLANT_DATABASE_API_KEY exists in config"""
        config = Config()
        assert hasattr(config, "PLANT_DATABASE_API_KEY")

    def test_mail_username_exists(self):
        """Test that MAIL_USERNAME exists in config"""
        config = Config()
        assert hasattr(config, "MAIL_USERNAME")

    def test_mail_password_exists(self):
        """Test that MAIL_PASSWORD exists in config"""
        config = Config()
        assert hasattr(config, "MAIL_PASSWORD")

    def test_aws_access_key_id_exists(self):
        """Test that AWS_ACCESS_KEY_ID exists in config"""
        config = Config()
        assert hasattr(config, "AWS_ACCESS_KEY_ID")

    def test_aws_secret_access_key_exists(self):
        """Test that AWS_SECRET_ACCESS_KEY exists in config"""
        config = Config()
        assert hasattr(config, "AWS_SECRET_ACCESS_KEY")

    def test_aws_s3_bucket_exists(self):
        """Test that AWS_S3_BUCKET exists in config"""
        config = Config()
        assert hasattr(config, "AWS_S3_BUCKET")

    def test_sentry_dsn_exists(self):
        """Test that SENTRY_DSN exists in config"""
        config = Config()
        assert hasattr(config, "SENTRY_DSN")

    def test_google_analytics_id_exists(self):
        """Test that GOOGLE_ANALYTICS_ID exists in config"""
        config = Config()
        assert hasattr(config, "GOOGLE_ANALYTICS_ID")

    def test_all_config_classes_inherit_keys(self):
        """Test that all config classes have the required keys"""
        required_keys = [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "ENCRYPTION_KEY",
            "OPENAI_API_KEY",
            "VECTORWORKS_API_KEY",
            "WEATHER_API_KEY",
            "PLANT_DATABASE_API_KEY",
            "MAIL_USERNAME",
            "MAIL_PASSWORD",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_S3_BUCKET",
            "SENTRY_DSN",
            "GOOGLE_ANALYTICS_ID",
        ]

        for config_class in [Config, DevelopmentConfig, TestingConfig]:
            config = config_class()
            for key in required_keys:
                assert hasattr(config, key), f"{config_class.__name__} missing {key}"
