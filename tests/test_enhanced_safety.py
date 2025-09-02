"""
Tests for the enhanced MotherSpace safety manager and fingerprinting system.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

# Add the scripts directory to the path for importing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts'))

from safety_manager import SafetyManager


class TestSafetyManager:
    """Test suite for the enhanced safety manager."""
    
    def test_safety_manager_initialization(self):
        """Test that safety manager initializes correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            assert safety.safety_dir.exists()
            assert safety.config['max_operations_per_hour'] == 5
    
    def test_fingerprint_generation(self):
        """Test issue fingerprint generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            issue1 = {
                'title': 'Test Issue',
                'body': 'Test body content',
                'labels': [{'name': 'bug'}, {'name': 'automated'}]
            }
            
            issue2 = {
                'title': 'Test Issue',
                'body': 'Test body content',
                'labels': [{'name': 'automated'}, {'name': 'bug'}]  # Different order
            }
            
            fp1 = safety.generate_fingerprint(issue1)
            fp2 = safety.generate_fingerprint(issue2)
            
            assert fp1 == fp2, "Same issues should have same fingerprint regardless of label order"
            assert len(fp1) == 16, "Fingerprint should be 16 characters"
    
    def test_fingerprint_normalization(self):
        """Test that fingerprints normalize dynamic content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            issue1 = {
                'title': 'Test failure at 2025-09-02T12:00:00',
                'body': 'Error with issue #123 at 2025-09-02 15:30:00',
                'labels': []
            }
            
            issue2 = {
                'title': 'Test failure at 2025-09-03T08:30:00',
                'body': 'Error with issue #456 at 2025-09-03 10:45:00',
                'labels': []
            }
            
            fp1 = safety.generate_fingerprint(issue1)
            fp2 = safety.generate_fingerprint(issue2)
            
            assert fp1 == fp2, "Issues with different timestamps/issue refs should have same fingerprint"
    
    def test_concurrency_control(self):
        """Test concurrency lock functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            # First lock should succeed
            assert safety.acquire_lock("test_actor", "test_operation")
            
            # Second lock should fail
            assert not safety.acquire_lock("another_actor", "test_operation")
            
            # Release lock
            safety.release_lock("test_operation")
            
            # New lock should now succeed
            assert safety.acquire_lock("test_actor", "test_operation")
    
    def test_actor_cooldown(self):
        """Test actor cooldown functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            # First check should pass
            can_proceed, reason = safety.can_proceed("test_actor", "test_operation")
            assert can_proceed
            
            # Update tracking
            safety.update_tracking("test_actor", "test_operation")
            
            # Second check should fail due to cooldown
            can_proceed, reason = safety.can_proceed("test_actor", "test_operation")
            assert not can_proceed
            assert "cooldown" in reason.lower()
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            # Should be able to proceed initially
            can_proceed, reason = safety.can_proceed("test_actor", "test_operation")
            assert can_proceed
            
            # Simulate multiple operations
            for i in range(5):
                safety.update_tracking(f"actor_{i}", "test_operation")
            
            # Should now be rate limited
            can_proceed, reason = safety.can_proceed("new_actor", "test_operation")
            assert not can_proceed
            assert "rate limit" in reason.lower()
    
    def test_issue_tracking(self):
        """Test issue fingerprint tracking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            fingerprint = "test_fingerprint_123"
            issue_number = 42
            
            # Initially should not find any existing issue
            existing = safety.find_existing_issue(fingerprint)
            assert existing is None
            
            # Register issue
            safety.register_issue(fingerprint, issue_number)
            
            # Should now find the registered issue
            existing = safety.find_existing_issue(fingerprint)
            assert existing == issue_number
    
    def test_cleanup_functionality(self):
        """Test cleanup of old safety data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            # Create some test files
            test_file = safety.safety_dir / "test.json"
            test_file.write_text('{"test": "data"}')
            
            lock_file = safety.safety_dir / "test.lock"
            lock_file.write_text('{"actor": "test"}')
            
            # Files should exist
            assert test_file.exists()
            assert lock_file.exists()
            
            # Run cleanup (should not remove recent files)
            safety.cleanup()
            
            # Files should still exist (they're recent)
            assert test_file.exists()
            assert lock_file.exists()


class TestWorkflowIntegration:
    """Test integration with workflow patterns."""
    
    def test_create_or_update_pattern(self):
        """Test the create-or-update pattern for issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safety = SafetyManager(temp_dir)
            
            # Test issue data
            issue_data = {
                'title': 'Test automated issue',
                'body': 'This is a test issue for create-or-update pattern',
                'labels': [{'name': 'automated'}, {'name': 'test'}]
            }
            
            fingerprint = safety.generate_fingerprint(issue_data)
            
            # First time: should not find existing
            existing = safety.find_existing_issue(fingerprint)
            assert existing is None
            
            # Register new issue
            issue_number = 123
            safety.register_issue(fingerprint, issue_number)
            
            # Second time: should find existing
            existing = safety.find_existing_issue(fingerprint)
            assert existing == issue_number
    
    def test_pr_safety_simulation(self):
        """Test PR safety checking simulation."""
        # This test simulates the logic that would be used in the workflow
        # to check if operations are safe relative to open PRs
        
        issue_to_close = {'number': 5, 'title': 'Test issue'}
        open_prs = [
            {
                'number': 10,
                'title': 'Fix for issue',
                'body': 'This PR addresses issue #5 and resolves the problem'
            }
        ]
        
        def would_interfere_with_prs(issue, prs):
            """Check if closing an issue would interfere with open PRs."""
            issue_ref = f"#{issue['number']}"
            return any(
                issue_ref in pr['body'] or issue_ref in pr['title']
                for pr in prs
            )
        
        # Should detect interference
        assert would_interfere_with_prs(issue_to_close, open_prs)
        
        # Should not detect interference when no references
        assert not would_interfere_with_prs(issue_to_close, [])


def test_command_line_interface():
    """Test the command line interface functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        safety = SafetyManager(temp_dir)
        
        # Test safety check
        can_proceed, reason = safety.can_proceed("test_actor", "test_operation")
        assert can_proceed
        
        # Test fingerprint generation
        test_issue = {
            'title': 'CLI Test Issue',
            'body': 'Testing CLI functionality',
            'labels': [{'name': 'test'}]
        }
        
        fingerprint = safety.generate_fingerprint(test_issue)
        assert len(fingerprint) == 16
        assert fingerprint.isalnum()


if __name__ == "__main__":
    # Run basic tests if called directly
    test_manager = TestSafetyManager()
    test_manager.test_safety_manager_initialization()
    test_manager.test_fingerprint_generation()
    test_manager.test_fingerprint_normalization()
    test_manager.test_concurrency_control()
    
    print("✅ All safety manager tests passed!")