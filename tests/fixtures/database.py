"""
Database testing fixtures and utilities (minimal version)
"""

from src.models.user import db


class DatabaseTestMixin:
    """Mixin class for database testing utilities"""

    def assert_record_count(self, model, expected_count):
        """Assert the number of records for a model"""
        actual_count = db.session.query(model).count()
        assert (
            actual_count == expected_count
        ), f"Expected {expected_count} {model.__name__} records, got {actual_count}"

    def assert_record_exists(self, model, **kwargs):
        """Assert that a record exists with given attributes"""
        record = db.session.query(model).filter_by(**kwargs).first()
        assert record is not None, f"No {model.__name__} record found with {kwargs}"
        return record

    def assert_record_not_exists(self, model, **kwargs):
        """Assert that a record does not exist with given attributes"""
        record = db.session.query(model).filter_by(**kwargs).first()
        assert (
            record is None
        ), f"{model.__name__} record found with {kwargs} when none expected"
