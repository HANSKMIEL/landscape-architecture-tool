#!/usr/bin/env python3
"""
Test suite for the development logging system
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

# Add project root to Python path using relative paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.update_dev_log import DevLogManager  # noqa: E402


class TestDevLogManager:
    """Test the DevLogManager class functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def log_manager(self, temp_dir):
        """Create a DevLogManager instance with a temporary log file"""
        log_file = Path(temp_dir) / "test_dev_log.md"
        manager = DevLogManager(str(log_file))
        manager.log_file = log_file  # Override the path calculation
        return manager

    def test_valid_actions(self, log_manager):
        """Test that valid actions are properly defined"""
        expected_actions = {
            "feature_added": "FEATURE_ADDED",
            "bug_fixed": "BUG_FIXED",
            "refactor": "REFACTOR",
            "test_added": "TEST_ADDED",
            "docs_updated": "DOCS_UPDATED",
            "config_changed": "CONFIG_CHANGED",
        }
        assert expected_actions == log_manager.VALID_ACTIONS

    def test_create_log_header(self, log_manager):
        """Test log header creation"""
    # Authentication handled by authenticated_test_user fixture
        header = log_manager.create_log_header()

        assert "Development Log - Landscape Architecture Tool" in header
        assert "Log Format" in header
        assert "Timestamp" in header
        assert "Action Type" in header
        assert "---" in header

    def test_format_log_entry_basic(self, log_manager):
        """Test basic log entry formatting"""
        with patch("scripts.update_dev_log.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00"

            entry = log_manager.format_log_entry("feature_added", "Test feature implementation", "test_author")

            expected_lines = [
                "## [2025-01-01 12:00:00] - FEATURE_ADDED",
                "**Author**: test_author",
                "**Description**: Test feature implementation",
                "",
                "---",
                "",
            ]

            assert entry == "\n".join(expected_lines) + "\n"

    def test_format_log_entry_with_impact(self, log_manager):
        """Test log entry formatting with impact assessment"""
        with patch("scripts.update_dev_log.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2025-01-01 12:00:00"

            entry = log_manager.format_log_entry(
                "bug_fixed",
                "Fixed critical bug",
                "bug_fixer",
                "Resolves production issues",
            )

            assert "**Impact**: Resolves production issues" in entry
            assert "BUG_FIXED" in entry

    def test_add_entry_creates_new_file(self, log_manager):
        """Test that adding an entry creates a new log file if it doesn't exist"""
    # Authentication handled by authenticated_test_user fixture
        assert not log_manager.log_file.exists()

        success = log_manager.add_entry("feature_added", "Initial feature", "developer")

        assert success
        assert log_manager.log_file.exists()

        # Verify file content
        with open(log_manager.log_file) as f:
            content = f.read()

        assert "Development Log - Landscape Architecture Tool" in content
        assert "Initial feature" in content
        assert "developer" in content
        assert "FEATURE_ADDED" in content

    def test_add_entry_appends_to_existing_file(self, log_manager):
        """Test that adding entries to existing file works correctly"""
    # Authentication handled by authenticated_test_user fixture
# Create initial entry
        log_manager.add_entry("feature_added", "First feature", "dev1")

        # Add second entry
        log_manager.add_entry("bug_fixed", "Fixed bug", "dev2")

        # Verify both entries exist and are in correct order (newest first)
        with open(log_manager.log_file) as f:
            content = f.read()

        # Find positions of entries
        first_pos = content.find("Fixed bug")
        second_pos = content.find("First feature")

        assert first_pos < second_pos  # Newer entry should come first
        assert "BUG_FIXED" in content
        assert "FEATURE_ADDED" in content

    def test_add_entry_invalid_action(self, log_manager):
        """Test that invalid actions are handled gracefully"""
    # Authentication handled by authenticated_test_user fixture
        with patch("builtins.print") as mock_print:
            success = log_manager.add_entry("invalid_action", "Test description", "test_author")

            assert success  # Should still succeed but warn
            mock_print.assert_any_call("Warning: 'invalid_action' is not a standard action type.")

    def test_list_entries_empty_log(self, log_manager):
        """Test listing entries when log file doesn't exist"""
        with patch("builtins.print") as mock_print:
            log_manager.list_entries()
            mock_print.assert_called_with("Development log file does not exist yet.")

    def test_list_entries_with_content(self, log_manager):
        """Test listing entries from populated log"""
        # Add test entries
        log_manager.add_entry("feature_added", "Feature 1", "dev1")
        log_manager.add_entry("bug_fixed", "Bug fix 1", "dev2")

        with patch("builtins.print") as mock_print:
            log_manager.list_entries(limit=5)

            # Check that entries were printed
            calls = [call[0][0] for call in mock_print.call_args_list]
            printed_content = "\n".join(calls)

            assert "Feature 1" in printed_content
            assert "Bug fix 1" in printed_content
            assert "FEATURE_ADDED" in printed_content
            assert "BUG_FIXED" in printed_content

    def test_get_stats_empty_log(self, log_manager):
        """Test statistics for empty log"""
        stats = log_manager.get_stats()

        assert stats["total_entries"] == 0
        assert stats["actions"] == {}

    def test_get_stats_with_entries(self, log_manager):
        """Test statistics calculation with entries"""
        # Add test entries
        log_manager.add_entry("feature_added", "Feature 1", "dev1")
        log_manager.add_entry("feature_added", "Feature 2", "dev1")
        log_manager.add_entry("bug_fixed", "Bug fix 1", "dev2")

        stats = log_manager.get_stats()

        assert stats["total_entries"] == 3
        assert stats["actions"]["FEATURE_ADDED"] == 2
        assert stats["actions"]["BUG_FIXED"] == 1

    def test_error_handling_file_permissions(self, log_manager):
        """Test error handling for file permission issues"""
        # Create log file first
        log_manager.add_entry("test_added", "Test entry", "tester")

        # Make file read-only
        os.chmod(log_manager.log_file, 0o444)

        try:
            success = log_manager.add_entry("feature_added", "New feature", "dev")
            assert not success  # Should fail due to permissions
        finally:
            # Restore permissions for cleanup
            os.chmod(log_manager.log_file, 0o644)


class TestDevLogScript:
    """Test the command-line script functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_script_help_output(self):
        """Test that the script provides help output"""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/update_dev_log.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        assert result.returncode == 0
        assert "Update development log" in result.stdout
        assert "--action" in result.stdout
        assert "--description" in result.stdout
        assert "--author" in result.stdout

    def test_script_missing_arguments(self):
        """Test script behavior with missing required arguments"""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/update_dev_log.py", "--action", "feature_added"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        assert result.returncode == 1
        assert "Missing required arguments" in result.stdout


class TestLogFormatValidation:
    """Test log format and placement validation"""

    def test_log_file_placement(self):
        """Test that log file is created in the correct location"""
        project_root = Path(__file__).parent.parent
        expected_log_path = project_root / "dev_log.md"

        # The log file should exist from our previous tests
        assert expected_log_path.exists()

    def test_log_format_consistency(self):
        """Test that log entries follow consistent formatting"""
        project_root = Path(__file__).parent.parent
        log_file = project_root / "dev_log.md"

        if log_file.exists():
            with open(log_file) as f:
                content = f.read()

            # Check for required format elements
            assert "# Development Log - Landscape Architecture Tool" in content
            assert "## Log Format" in content

            # Check entry format
            entries = [line for line in content.split("\n") if line.startswith("## [")]
            for entry in entries:
                # Each entry should have timestamp and action
                assert "] - " in entry
                # Timestamp should be in correct format
                timestamp_part = entry.split("] - ")[0].replace("## [", "")
                try:
                    datetime.strptime(timestamp_part, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pytest.fail(f"Invalid timestamp format in entry: {entry}")

    def test_roadmap_file_exists(self):
        """Test that the development roadmap file exists and has required content"""
        project_root = Path(__file__).parent.parent
        roadmap_file = project_root / "PLANNED_DEVELOPMENT_ROADMAP.md"

        assert roadmap_file.exists(), "PLANNED_DEVELOPMENT_ROADMAP.md file is missing"

        with open(roadmap_file) as f:
            content = f.read()

        # Check for required sections
        assert "# Development Roadmap" in content
        assert "Testing Instructions" in content
        assert "Running the Development Log System" in content
        assert "Validation Checklist" in content
        assert "scripts/update_dev_log.py" in content

    def test_documentation_matches_behavior(self):
        """Test that documentation accurately describes the system behavior"""
        project_root = Path(__file__).parent.parent
        roadmap_file = project_root / "PLANNED_DEVELOPMENT_ROADMAP.md"

        with open(roadmap_file) as f:
            roadmap_content = f.read()

        # Check that documented actions match actual valid actions
        documented_actions = [
            "feature_added",
            "bug_fixed",
            "refactor",
            "test_added",
            "docs_updated",
        ]

        for action in documented_actions:
            assert action in roadmap_content or action.replace("_", " ") in roadmap_content

        # Check that script path is correctly documented
        assert "scripts/update_dev_log.py" in roadmap_content
        assert "dev_log.md" in roadmap_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
