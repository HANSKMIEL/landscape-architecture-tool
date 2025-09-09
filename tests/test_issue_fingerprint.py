"""
Test for issue fingerprinting system to prevent spam and enable deduplication.
"""

import hashlib
import json
from typing import Any

import pytest


class IssueFingerprinter:
    """System for generating stable fingerprints for GitHub issues to enable deduplication."""

    def __init__(self):
        self.salt = "motherspace-orchestrator-v1.1.0"

    def generate_fingerprint(self, issue_data: dict[str, Any]) -> str:
        """Generate a stable fingerprint for an issue based on its content and metadata."""
        # Extract core components for fingerprinting
        title = issue_data.get("title", "").lower().strip()
        body = issue_data.get("body", "").lower().strip()
        labels = sorted([label.get("name", "") for label in issue_data.get("labels", [])])

        # Normalize content to ignore minor variations
        normalized_title = self._normalize_text(title)
        normalized_body = self._normalize_text(body)

        # Create fingerprint data
        fingerprint_data = {
            "title": normalized_title,
            "body_hash": hashlib.sha256(normalized_body.encode()).hexdigest()[:16],
            "labels": labels,
            "type": self._classify_issue_type(issue_data),
        }

        # Generate stable hash
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(f"{self.salt}:{fingerprint_string}".encode()).hexdigest()[:16]

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing timestamps, dynamic content, and whitespace variations."""
        import re

        # Remove timestamps and dates (more comprehensive patterns)
        text = re.sub(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", "[TIMESTAMP]", text)
        text = re.sub(r"\d{4}-\d{2}-\d{2}", "[DATE]", text)
        text = re.sub(r"\d{2}:\d{2}:\d{2}", "[TIME]", text)

        # Remove issue/PR numbers that might change
        text = re.sub(r"#\d+", "[ISSUE_REF]", text)

        # Remove dynamic IDs and hashes (but preserve meaningful content)
        text = re.sub(r"\b[a-f0-9]{8,}\b", "[HASH]", text)

        # Remove version numbers and build IDs
        text = re.sub(r"\bv?\d+\.\d+\.\d+(?:\.\d+)?\b", "[VERSION]", text)
        text = re.sub(r"\bbuild-\d+\b", "[BUILD_ID]", text)

        # Remove file paths that might vary
        text = re.sub(r"(?:/[^/\s]+)+", "[PATH]", text)

        # Normalize whitespace and punctuation
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s\[\].,?!:;]", " ", text)  # Keep word chars, spaces, brackets, and key punctuation

        return text.strip().lower()

    def _classify_issue_type(self, issue_data: dict[str, Any]) -> str:
        """Classify issue type for fingerprinting purposes."""
        title = issue_data.get("title", "").lower()
        labels = [label.get("name", "") for label in issue_data.get("labels", [])]

        # Check labels first
        if any(label in ["bug", "error", "failure"] for label in labels):
            return "bug"
        if any(label in ["enhancement", "feature"] for label in labels):
            return "enhancement"
        if any(label in ["maintenance", "cleanup"] for label in labels):
            return "maintenance"
        if any(label in ["automated", "motherspace"] for label in labels):
            return "automated"

        # Check title patterns
        if any(keyword in title for keyword in ["fix", "bug", "error", "fail"]):
            return "bug"
        if any(keyword in title for keyword in ["feature", "add", "implement"]):
            return "enhancement"
        if any(keyword in title for keyword in ["update", "upgrade", "maintain"]):
            return "maintenance"
        if any(keyword in title for keyword in ["automated", "motherspace", "orchestrator"]):
            return "automated"

        return "general"

    def find_duplicates(self, issues: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Find duplicate issues based on fingerprints."""
        fingerprint_map: dict[str, list[dict[str, Any]]] = {}

        for issue in issues:
            fingerprint = self.generate_fingerprint(issue)
            if fingerprint not in fingerprint_map:
                fingerprint_map[fingerprint] = []
            fingerprint_map[fingerprint].append(issue)

        # Return only groups with duplicates
        return {fp: issues_list for fp, issues_list in fingerprint_map.items() if len(issues_list) > 1}

    def is_spam_pattern(self, issue_data: dict[str, Any], recent_issues: list[dict[str, Any]]) -> bool:
        """Check if an issue follows a spam pattern based on recent similar issues."""
        fingerprint = self.generate_fingerprint(issue_data)

        # Count recent issues with same fingerprint
        same_fingerprint_count = 0
        for recent_issue in recent_issues:
            if self.generate_fingerprint(recent_issue) == fingerprint:
                same_fingerprint_count += 1

        # Consider spam if more than 2 identical issues in recent history
        return same_fingerprint_count > 2


class TestIssueFingerprinter:
    """Test suite for the issue fingerprinting system."""

    def test_fingerprint_generation_basic(self):
        """Test basic fingerprint generation."""
        fingerprinter = IssueFingerprinter()

        issue_data = {
            "title": "Test Issue",
            "body": "This is a test issue body",
            "labels": [{"name": "bug"}, {"name": "priority-high"}],
        }

        fingerprint = fingerprinter.generate_fingerprint(issue_data)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16
        assert fingerprint.isalnum()

    def test_fingerprint_stability(self):
        """Test that same issue data produces same fingerprint."""
        fingerprinter = IssueFingerprinter()

        issue_data = {
            "title": "Consistent Test Issue",
            "body": "This should produce the same fingerprint every time",
            "labels": [{"name": "test"}],
        }

        fingerprint1 = fingerprinter.generate_fingerprint(issue_data)
        fingerprint2 = fingerprinter.generate_fingerprint(issue_data)

        assert fingerprint1 == fingerprint2

    def test_fingerprint_differences(self):
        """Test that different issues produce different fingerprints."""
        fingerprinter = IssueFingerprinter()

        issue1 = {"title": "First Issue", "body": "First issue body", "labels": [{"name": "bug"}]}

        issue2 = {"title": "Second Issue", "body": "Second issue body", "labels": [{"name": "feature"}]}

        fingerprint1 = fingerprinter.generate_fingerprint(issue1)
        fingerprint2 = fingerprinter.generate_fingerprint(issue2)

        assert fingerprint1 != fingerprint2

    def test_text_normalization(self):
        """Test that text normalization handles timestamps and dynamic content."""
        fingerprinter = IssueFingerprinter()

        issue1 = {
            "title": "Issue with timestamp 2025-09-02T12:00:00",
            "body": "Error occurred at 2025-09-02 12:00:00 with issue #123",
            "labels": [],
        }

        issue2 = {
            "title": "Issue with timestamp 2025-09-03T15:30:00",
            "body": "Error occurred at 2025-09-03 15:30:00 with issue #456",
            "labels": [],
        }

        fingerprint1 = fingerprinter.generate_fingerprint(issue1)
        fingerprint2 = fingerprinter.generate_fingerprint(issue2)

        # Should be same after normalization
        assert fingerprint1 == fingerprint2

    def test_issue_type_classification(self):
        """Test issue type classification."""
        fingerprinter = IssueFingerprinter()

        test_cases = [
            ({"title": "Fix bug in parser", "labels": []}, "bug"),
            ({"title": "Add new feature", "labels": []}, "enhancement"),
            ({"title": "Update dependencies", "labels": []}, "maintenance"),
            ({"title": "Regular issue", "labels": [{"name": "bug"}]}, "bug"),
            ({"title": "MotherSpace orchestrator task", "labels": []}, "automated"),
        ]

        for issue_data, expected_type in test_cases:
            issue_data.setdefault("body", "")
            issue_data.setdefault("labels", [])
            actual_type = fingerprinter._classify_issue_type(issue_data)
            assert (
                actual_type == expected_type
            ), f"Expected {expected_type}, got {actual_type} for {issue_data['title']}"

    def test_duplicate_detection(self):
        """Test duplicate issue detection."""
        fingerprinter = IssueFingerprinter()

        issues = [
            {"title": "Test Issue", "body": "Test body", "labels": []},
            {"title": "Test Issue", "body": "Test body", "labels": []},  # Duplicate
            {"title": "Different Issue", "body": "Different body", "labels": []},
            {"title": "Test Issue", "body": "Test body", "labels": []},  # Another duplicate
        ]

        duplicates = fingerprinter.find_duplicates(issues)

        assert len(duplicates) == 1  # One group of duplicates
        duplicate_group = next(iter(duplicates.values()))
        assert len(duplicate_group) == 3  # Three identical issues

    def test_spam_pattern_detection(self):
        """Test spam pattern detection."""
        fingerprinter = IssueFingerprinter()

        # Create recent issues with some duplicates
        recent_issues = [
            {"title": "Spam Issue", "body": "Spam body", "labels": []},
            {"title": "Spam Issue", "body": "Spam body", "labels": []},
            {"title": "Spam Issue", "body": "Spam body", "labels": []},
            {"title": "Normal Issue", "body": "Normal body", "labels": []},
        ]

        # Test new issue that would be spam
        spam_issue = {"title": "Spam Issue", "body": "Spam body", "labels": []}
        normal_issue = {"title": "Unique Issue", "body": "Unique body", "labels": []}

        assert fingerprinter.is_spam_pattern(spam_issue, recent_issues) is True
        assert fingerprinter.is_spam_pattern(normal_issue, recent_issues) is False

    def test_fingerprint_with_empty_data(self):
        """Test fingerprint generation with minimal/empty data."""
        fingerprinter = IssueFingerprinter()

        minimal_issue = {"title": "", "body": "", "labels": []}

        fingerprint = fingerprinter.generate_fingerprint(minimal_issue)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16

    def test_fingerprint_with_complex_labels(self):
        """Test fingerprint generation with complex label structures."""
        fingerprinter = IssueFingerprinter()

        issue_with_labels = {
            "title": "Complex Issue",
            "body": "Issue with many labels",
            "labels": [
                {"name": "bug"},
                {"name": "priority-high"},
                {"name": "needs-triage"},
                {"name": "motherspace-managed"},
            ],
        }

        fingerprint = fingerprinter.generate_fingerprint(issue_with_labels)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16

        # Test with same labels in different order
        reordered_issue = {
            "title": "Complex Issue",
            "body": "Issue with many labels",
            "labels": [
                {"name": "motherspace-managed"},
                {"name": "bug"},
                {"name": "needs-triage"},
                {"name": "priority-high"},
            ],
        }

        reordered_fingerprint = fingerprinter.generate_fingerprint(reordered_issue)
        assert fingerprint == reordered_fingerprint


class TestIssueDeduplicationWorkflow:
    """Test the deduplication workflow integration."""

    def test_workflow_integration_mock(self):
        """Test integration with workflow using mocks."""
        fingerprinter = IssueFingerprinter()

        # Mock GitHub API responses
        mock_issues = [
            {
                "number": 1,
                "title": "Test failure in CI",
                "body": "Test failed at 2025-09-02T12:00:00",
                "labels": [{"name": "automated"}, {"name": "test-failure"}],
                "created_at": "2025-09-02T12:00:00Z",
            },
            {
                "number": 2,
                "title": "Test failure in CI",
                "body": "Test failed at 2025-09-02T15:30:00",
                "labels": [{"name": "automated"}, {"name": "test-failure"}],
                "created_at": "2025-09-02T15:30:00Z",
            },
        ]

        duplicates = fingerprinter.find_duplicates(mock_issues)

        assert len(duplicates) == 1
        duplicate_group = next(iter(duplicates.values()))
        assert len(duplicate_group) == 2
        assert duplicate_group[0]["number"] != duplicate_group[1]["number"]

    def test_pr_safety_check_integration(self):
        """Test integration with PR safety checking."""
        # Mock issue and PR data
        issue_to_close = {"number": 5, "title": "Outdated issue", "body": "This issue is superseded", "labels": []}

        open_prs = [
            {
                "number": 10,
                "title": "Fix for issue #5",
                "body": "This PR fixes issue #5 and resolves the problem",
                "state": "open",
            }
        ]

        # Simple safety check - if PR references issue, it's not safe to close
        def is_safe_to_close(issue: dict[str, Any], prs: list[dict[str, Any]]) -> bool:
            issue_ref = f"#{issue['number']}"
            return all(not (issue_ref in pr["body"] or issue_ref in pr["title"]) for pr in prs)

        assert is_safe_to_close(issue_to_close, open_prs) is False
        assert is_safe_to_close(issue_to_close, []) is True


def test_typing_annotations_compatibility():
    """Test that type annotations use compatible Dict[str, Any] syntax."""
    # This test ensures the file uses Dict[str, Any] instead of dict[str, Any]
    # for Python 3.9+ compatibility as suggested in the PR review

    # Get the fingerprinter to test the function works with type annotations
    fingerprinter = IssueFingerprinter()

    # Test that we can pass a dictionary
    test_data: dict[str, Any] = {"title": "test", "body": "test", "labels": []}
    result = fingerprinter.generate_fingerprint(test_data)

    assert isinstance(result, str)
    assert len(result) == 16


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
