#!/usr/bin/env python3
"""
Test transaction handling consistency in conftest.py fixtures

This test specifically validates the fix for the transaction handling logic
where both code paths now have consistent cleanup mechanisms.
"""

import os

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
        """Test that connection fixture has proper cleanup mechanism"""
        # This test verifies the fix: unified try/finally block handles both transaction states

        # Read the conftest.py file and verify the unified cleanup approach
        conftest_path = os.path.join(os.path.dirname(__file__), "conftest.py")
        with open(conftest_path) as f:
            content = f.read()

        # Look for the connection fixture
        lines = content.split("\n")
        in_connection_fixture = False
        found_if_transaction = False
        found_else_path = False
        has_unified_finally = False
        has_yield = False

        for _i, line in enumerate(lines):
            if "def connection(engine):" in line:
                in_connection_fixture = True
                continue

            if in_connection_fixture:
                if "if conn.in_transaction():" in line:
                    found_if_transaction = True
                elif line.strip() == "else:" and found_if_transaction:
                    found_else_path = True
                elif "yield conn" in line:
                    has_yield = True
                elif "finally:" in line and has_yield:
                    has_unified_finally = True
                # Exit when we reach the next fixture
                elif "def " in line and not line.strip().startswith("#"):
                    break

        # Verify the unified cleanup approach
        assert found_if_transaction, "Could not find if conn.in_transaction() path"
        assert found_else_path, "Could not find else path"
        assert has_yield, "Could not find yield statement in connection fixture"
        assert has_unified_finally, "Connection fixture should have a unified finally block for cleanup"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
