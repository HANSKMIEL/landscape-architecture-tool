#!/usr/bin/env python3
"""
Test transaction handling consistency in conftest.py fixtures

This test specifically validates the fix for the transaction handling logic
where both code paths now have consistent cleanup mechanisms.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


class TestTransactionHandlingConsistency:
    """Test transaction handling consistency in fixture code"""

    def test_transaction_state_detection_with_real_db(self):
        """Test transaction state detection with real SQLite connection"""
        # Create a real in-memory SQLite database to test transaction states
        engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )

        conn = engine.connect()

        # Initially, connection should not be in transaction
        assert not conn.in_transaction()

        # Start a transaction
        tx = conn.begin()
        assert conn.in_transaction()

        # Clean up
        tx.rollback()
        assert not conn.in_transaction()

        conn.close()

    def test_both_code_paths_have_cleanup_mechanisms(self):
        """Test that both code paths in connection fixture have proper cleanup"""
        # This test verifies the fix: both paths should now have try/finally blocks

        # Read the conftest.py file and verify both paths have cleanup
        conftest_path = (
            "/home/runner/work/landscape-architecture-tool/"
            "landscape-architecture-tool/tests/conftest.py"
        )
        with open(conftest_path, "r") as f:
            content = f.read()

        # Look for the connection fixture
        lines = content.split("\n")
        in_connection_fixture = False
        found_if_transaction = False
        found_else_path = False
        if_has_finally = False
        else_has_finally = False

        for i, line in enumerate(lines):
            if "def connection(engine):" in line:
                in_connection_fixture = True
                continue

            if in_connection_fixture:
                if "if conn.in_transaction():" in line:
                    found_if_transaction = True
                    # Check if the if block has a finally
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if "finally:" in lines[j]:
                            if_has_finally = True
                            break
                        if "else:" in lines[j]:
                            break

                elif line.strip() == "else:" and found_if_transaction:
                    found_else_path = True
                    # Check if the else block has a finally
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if "finally:" in lines[j]:
                            else_has_finally = True
                            break
                        if (
                            line.strip()
                            and not line.startswith(" ")
                            and not line.startswith("\t")
                        ):
                            break

                # Exit when we reach the next fixture
                elif "def " in line and not line.strip().startswith("#"):
                    break

        # Verify both paths have cleanup mechanisms
        assert found_if_transaction, "Could not find if conn.in_transaction() path"
        assert found_else_path, "Could not find else path"
        assert (
            if_has_finally
        ), "The if conn.in_transaction() path should have a finally block for cleanup"
        assert else_has_finally, "The else path should have a finally block for cleanup"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
