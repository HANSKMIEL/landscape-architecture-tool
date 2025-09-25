#!/usr/bin/env python3
"""
Tests for the PR Analyzer module
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from tests.fixtures.auth_fixtures import authenticated_test_user, setup_test_authentication

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.pr_analyzer import PRAnalyzer, PRInfo, create_validation_report


class TestPRInfo:
    """Test the PRInfo dataclass."""
    
    def test_pr_info_creation(self):
        """Test creating PRInfo objects."""
        pr = PRInfo(
            number=123,
            title="bump package from 1.0.0 to 1.0.1",
            state="open",
            labels=["dependencies"],
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            author="dependabot[bot]",
            is_draft=False,
            mergeable_state="clean"
        )
        
        assert pr.number == 123
        assert pr.is_dependabot() is True
        assert pr.has_label("dependencies") is True
        assert pr.has_label("nonexistent") is False
    
    def test_update_type_detection(self):
        """Test update type detection from PR titles."""
    # Authentication handled by authenticated_test_user fixture
# Patch update
        pr_patch = PRInfo(
            number=1, title="bump package from 1.0.0 to 1.0.1", state="open",
            labels=[], created_at="", updated_at="", author="dependabot[bot]",
            is_draft=False, mergeable_state="clean"
        )
        assert pr_patch.get_update_type() == "patch"
        
        # Minor update
        pr_minor = PRInfo(
            number=2, title="bump package from 1.0.0 to 1.1.0", state="open",
            labels=[], created_at="", updated_at="", author="dependabot[bot]",
            is_draft=False, mergeable_state="clean"
        )
        assert pr_minor.get_update_type() == "minor"
        
        # Major update
        pr_major = PRInfo(
            number=3, title="bump package from 1.0.0 to 2.0.0", state="open",
            labels=[], created_at="", updated_at="", author="dependabot[bot]",
            is_draft=False, mergeable_state="clean"
        )
        assert pr_major.get_update_type() == "major"
        
        # Unknown format
        pr_unknown = PRInfo(
            number=4, title="Some other PR title", state="open",
            labels=[], created_at="", updated_at="", author="user",
            is_draft=False, mergeable_state="clean"
        )
        assert pr_unknown.get_update_type() == "unknown"
    
    def test_security_update_detection(self):
        """Test security update detection."""
    # Authentication handled by authenticated_test_user fixture
# Security in title
        pr_security = PRInfo(
            number=1, title="bump package from 1.0.0 to 1.0.1 (security)", state="open",
            labels=[], created_at="", updated_at="", author="dependabot[bot]",
            is_draft=False, mergeable_state="clean"
        )
        assert pr_security.is_security_update() is True
        
        # Security in labels
        pr_security_label = PRInfo(
            number=2, title="bump package from 1.0.0 to 1.0.1", state="open",
            labels=["security", "dependencies"], created_at="", updated_at="", 
            author="dependabot[bot]", is_draft=False, mergeable_state="clean"
        )
        assert pr_security_label.is_security_update() is True
        
        # No security indicators
        pr_normal = PRInfo(
            number=3, title="bump package from 1.0.0 to 1.0.1", state="open",
            labels=["dependencies"], created_at="", updated_at="", 
            author="dependabot[bot]", is_draft=False, mergeable_state="clean"
        )
        assert pr_normal.is_security_update() is False


class TestPRAnalyzer:
    """Test the PRAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test PRAnalyzer initialization."""
        analyzer = PRAnalyzer()
        assert analyzer.owner == "HANSKMIEL"
        assert analyzer.repo == "landscape-architecture-tool"
        assert "flask" in analyzer.critical_dependencies
    
    def test_headers_without_token(self):
        """Test header generation without token."""
        analyzer = PRAnalyzer()
        headers = analyzer.get_headers()
        assert "Authorization" not in headers
        assert headers["Accept"] == "application/vnd.github.v3+json"
    
    def test_headers_with_token(self):
        """Test header generation with token."""
        test_token = "fake_token_for_testing"  # noqa: S105
        analyzer = PRAnalyzer(github_token=test_token)
        headers = analyzer.get_headers()
        assert headers["Authorization"] == f"token {test_token}"
    
    @patch("src.utils.pr_analyzer.requests.get")
    def test_fetch_pull_requests_success(self, mock_get):
        """Test successful PR fetching."""
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 123,
                "title": "Test PR",
                "state": "open",
                "labels": [{"name": "dependencies"}],
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "user": {"login": "dependabot[bot]"},
                "draft": False,
                "mergeable_state": "clean"
            }
        ]
        mock_get.return_value = mock_response
        
        # Mock second call returns empty (pagination end)
        mock_response_empty = Mock()
        mock_response_empty.status_code = 200
        mock_response_empty.json.return_value = []
        mock_get.side_effect = [mock_response, mock_response_empty]
        
        analyzer = PRAnalyzer()
        prs = analyzer.fetch_pull_requests()
        
        assert len(prs) == 1
        assert prs[0].number == 123
        assert prs[0].title == "Test PR"
        assert prs[0].is_dependabot() is True
    
    @patch("src.utils.pr_analyzer.requests.get")
    def test_fetch_pull_requests_error(self, mock_get):
        """Test PR fetching with API error."""
        mock_get.side_effect = Exception("API Error")
        
        analyzer = PRAnalyzer()
        prs = analyzer.fetch_pull_requests()
        
        assert prs == []
    
    def test_categorize_dependabot_prs(self):
        """Test PR categorization logic."""
        analyzer = PRAnalyzer()
        
        # Create test PRs
        prs = [
            # Safe patch update
            PRInfo(1, "bump lodash from 1.0.0 to 1.0.1", "open", ["dependencies"], 
                   "", "", "dependabot[bot]", False, "clean"),
            # Critical dependency
            PRInfo(2, "bump flask from 2.0.0 to 2.0.1", "open", ["dependencies"], 
                   "", "", "dependabot[bot]", False, "clean"),
            # Major update
            PRInfo(3, "bump package from 1.0.0 to 2.0.0", "open", ["dependencies"], 
                   "", "", "dependabot[bot]", False, "clean"),
            # Security patch
            PRInfo(4, "bump package from 1.0.0 to 1.0.1", "open", ["security"], 
                   "", "", "dependabot[bot]", False, "clean"),
            # Non-dependabot PR
            PRInfo(5, "Feature update", "open", [], "", "", "user", False, "clean")
        ]
        
        categorized = analyzer.categorize_dependabot_prs(prs)
        
        # Check categories
        assert len(categorized["safe_auto_merge"]) == 2  # lodash patch + security patch
        assert len(categorized["manual_review"]) == 1   # flask critical dependency
        assert len(categorized["major_updates"]) == 1   # major version update
        
        # Verify specific PRs in categories
        safe_numbers = [pr.number for pr in categorized["safe_auto_merge"]]
        assert 1 in safe_numbers  # lodash patch
        assert 4 in safe_numbers  # security patch
        
        manual_numbers = [pr.number for pr in categorized["manual_review"]]
        assert 2 in manual_numbers  # flask critical
        
        major_numbers = [pr.number for pr in categorized["major_updates"]]
        assert 3 in major_numbers  # major update
    
    @patch.object(PRAnalyzer, "fetch_pull_requests")
    def test_generate_pr_counts(self, mock_fetch):
        """Test PR count generation."""
        # Mock PRs
        mock_prs = [
            PRInfo(1, "bump lodash from 1.0.0 to 1.0.1", "open", ["dependencies"], 
                   "", "", "dependabot[bot]", False, "clean"),
            PRInfo(2, "bump flask from 2.0.0 to 2.0.1", "open", ["dependencies"], 
                   "", "", "dependabot[bot]", False, "clean"),
            PRInfo(3, "Feature PR", "open", [], "", "", "user", False, "clean")
        ]
        mock_fetch.return_value = mock_prs
        
        analyzer = PRAnalyzer()
        counts = analyzer.generate_pr_counts()
        
        assert counts["total_open_prs"] == 3
        assert counts["dependabot_prs"]["total"] == 2
        assert counts["non_dependabot_prs"] == 1
        assert "timestamp" in counts
        assert "pr_numbers" in counts
    
    @patch.object(PRAnalyzer, "generate_pr_counts")
    def test_generate_validation_report(self, mock_counts):
        """Test validation report generation."""
    # Authentication handled by authenticated_test_user fixture
        mock_counts.return_value = {
            "timestamp": "2025-01-01T00:00:00Z",
            "total_open_prs": 5,
            "dependabot_prs": {
                "total": 3,
                "safe_auto_merge": 2,
                "manual_review_required": 1,
                "major_updates_requiring_testing": 0
            },
            "non_dependabot_prs": 2,
            "pr_numbers": {
                "safe_auto_merge": [1, 2],
                "manual_review": [3],
                "major_updates": []
            }
        }
        
        analyzer = PRAnalyzer()
        report = analyzer.generate_validation_report(
            backend_status="passed",
            frontend_status="passed",
            database_status="functional",
            security_status="completed"
        )
        
        assert report["repository_status"] == "functional"
        assert report["component_status"]["backend_tests"] == "passed"
        assert "pr_analysis" in report
        assert "next_steps" in report
        assert len(report["next_steps"]) > 0


class TestConvenienceFunction:
    """Test the convenience function."""
    
    @patch("src.utils.pr_analyzer.PRAnalyzer")
    def test_create_validation_report(self, mock_analyzer_class):
        """Test the convenience function."""
    # Authentication handled by authenticated_test_user fixture
# Mock analyzer instance
        mock_analyzer = Mock()
        mock_analyzer.generate_validation_report.return_value = {
            "timestamp": "2025-01-01T00:00:00Z",
            "validation_type": "dynamic_pr_analysis"
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        # Test function call
        report = create_validation_report(
            backend_status="passed",
            frontend_status="passed"
        )
        
        # Verify analyzer was created and called correctly
        mock_analyzer_class.assert_called_once()
        mock_analyzer.generate_validation_report.assert_called_once()
        assert "timestamp" in report


class TestIntegration:
    """Integration tests with mock data."""
    
    def test_end_to_end_scenario(self):
        """Test a complete end-to-end scenario with mock data."""
        # This test uses the actual logic but with controlled data
        analyzer = PRAnalyzer()
        
        # Create realistic test PRs
        test_prs = [
            # Safe updates
            PRInfo(409, "bump @babel/core from 7.28.0 to 7.28.3", "open", 
                   ["dependencies", "auto-merge-candidate"], "", "", "dependabot[bot]", False, "clean"),
            PRInfo(403, "bump babel-jest from 30.0.5 to 30.1.2", "open", 
                   ["dependencies", "auto-merge-candidate"], "", "", "dependabot[bot]", False, "clean"),
            
            # Manual review (critical dependency)
            PRInfo(435, "bump flask from 3.1.1 to 3.1.2", "open", 
                   ["dependencies", "auto-merge-candidate"], "", "", "dependabot[bot]", False, "clean"),
            
            # Major updates
            PRInfo(442, "bump openai from 1.98.0 to 1.106.1", "open", 
                   ["dependencies", "auto-merge-candidate"], "", "", "dependabot[bot]", False, "clean"),
            PRInfo(441, "bump faker from 19.6.0 to 37.6.0", "open", 
                   ["dependencies", "auto-merge-candidate"], "", "", "dependabot[bot]", False, "clean"),
            
            # Non-dependabot PR
            PRInfo(444, "Configure Dependabot auto-merge", "open", 
                   ["enhancement"], "", "", "Copilot", False, "clean")
        ]
        
        # Test categorization
        categorized = analyzer.categorize_dependabot_prs(test_prs)
        
        assert len(categorized["safe_auto_merge"]) == 2  # babel updates
        assert len(categorized["manual_review"]) == 1    # flask critical
        assert len(categorized["major_updates"]) == 2    # openai, faker
        
        # Test count generation with pre-categorized data
        counts = analyzer.generate_pr_counts(categorized)
        
        assert counts["dependabot_prs"]["safe_auto_merge"] == 2
        assert counts["dependabot_prs"]["manual_review_required"] == 1
        assert counts["dependabot_prs"]["major_updates_requiring_testing"] == 2
        
        # Test validation report
        report = analyzer.generate_validation_report(
            backend_status="passed",
            frontend_status="passed", 
            database_status="functional",
            security_status="completed"
        )
        
        assert report["repository_status"] == "functional"
        assert "Auto-merge 2 safe PRs" in str(report["next_steps"])
        assert "Manual review required for 1 PRs" in str(report["next_steps"])
        assert "Extensive testing needed for 2 major updates" in str(report["next_steps"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])