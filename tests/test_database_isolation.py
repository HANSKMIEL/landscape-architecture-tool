#!/usr/bin/env python3
"""
Test database isolation and data contamination prevention
"""

import pytest
from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

from src.models.landscape import Plant
from src.models.user import db


class TestDatabaseIsolation:
    """Test database isolation between tests"""

    def test_database_starts_clean(self, app):
        """Test that database starts with no data"""
        with app.app_context():
            plant_count = db.session.query(Plant).count()
            assert plant_count == 0, f"Database should start clean but found {plant_count} plants"

    def test_create_plant_isolated_1(self, app):
        """First test creating a plant - should not affect other tests"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            # Create a plant
            plant = Plant(
                name="Test Plant 1",
                common_name="Isolated Test Plant 1",
                category="Test",
            )
            db.session.add(plant)
            db.session.commit()

            # Verify it exists
            count = db.session.query(Plant).count()
            assert count == 1

    def test_create_plant_isolated_2(self, app):
        """Second test creating a plant - should start with clean database"""
    # Authentication handled by authenticated_test_user fixture
        with app.app_context():
            # Database should start clean
            initial_count = db.session.query(Plant).count()
            assert initial_count == 0, f"Database should start clean but found {initial_count} plants"

            # Create a different plant
            plant = Plant(
                name="Test Plant 2",
                common_name="Isolated Test Plant 2",
                category="Test",
            )
            db.session.add(plant)
            db.session.commit()

            # Verify only this plant exists
            count = db.session.query(Plant).count()
            assert count == 1

    def test_database_isolation_verification(self, app):
        """Third test to verify isolation is working"""
        with app.app_context():
            # Database should start clean again
            initial_count = db.session.query(Plant).count()
            assert initial_count == 0, f"Database isolation failed - found {initial_count} plants"

    def test_concurrent_operations_simulation(self, app):
        """Test simulating concurrent database operations"""
        with app.app_context():
            # Create multiple plants in rapid succession
            plants = []
            for i in range(5):
                plant = Plant(
                    name=f"Concurrent Plant {i}",
                    common_name=f"Concurrent Test Plant {i}",
                    category="Concurrent",
                )
                plants.append(plant)
                db.session.add(plant)

            db.session.commit()

            # Verify all were created
            count = db.session.query(Plant).count()
            assert count == 5

            # Clean up explicitly (conftest should handle this too)
            for plant in plants:
                db.session.delete(plant)
            db.session.commit()

            # Verify cleanup
            final_count = db.session.query(Plant).count()
            assert final_count == 0

    def test_transaction_rollback_handling(self, app):
        """Test that transaction rollbacks are handled properly"""
        with app.app_context():
            try:
                # Start a transaction
                plant = Plant(
                    name="Rollback Test Plant",
                    common_name="Should Not Persist",
                    category="Rollback",
                )
                db.session.add(plant)

                # Force a rollback
                db.session.rollback()

                # Verify nothing was committed
                count = db.session.query(Plant).count()
                assert count == 0

            except Exception:
                # Ensure session is clean even if exception occurs
                db.session.rollback()
                raise

    def test_session_cleanup_after_error(self, app):
        """Test that session is properly cleaned after errors"""
        with app.app_context():
            # Intentionally cause an error and ensure cleanup works
            try:
                # Create an invalid plant by omitting a required field to guarantee an error
                plant = Plant(common_name="Should Fail", category="ErrorTest")  # Missing 'name' field
                db.session.add(plant)
                db.session.commit()
            except Exception:
                # Rollback and continue - session should be clean
                db.session.rollback()

            # Database should be in a clean state
            count = db.session.query(Plant).count()
            assert count == 0

            # Should be able to create a valid plant after error
            valid_plant = Plant(
                name="Valid Plant After Error",
                common_name="Recovery Test",
                category="Recovery",
            )
            db.session.add(valid_plant)
            db.session.commit()

            count = db.session.query(Plant).count()
            assert count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
