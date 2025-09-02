"""
Unit tests for the issue fingerprint functionality.
Tests fingerprint generation, normalization, and deduplication logic.
"""

import sys
from pathlib import Path

import pytest

# Add .github/scripts to path for imports
scripts_path = Path(__file__).parent.parent / ".github" / "scripts"
sys.path.insert(0, str(scripts_path))

from issue_fingerprint import (  # noqa: E402
    create_fingerprint_tag,
    extract_fingerprint_from_body,
    generate_fingerprint,
    normalize_payload,
)


class TestFingerprintNormalization:
    """Test payload normalization functionality."""

    def test_timestamp_normalization(self):
        """Test that timestamps are properly removed/normalized."""
        payload = {
            "title": "Report - 2024-09-02 11:30:45",
            "timestamp": "2024-09-02T11:30:45Z",
            "created_at": "2024-09-02T11:30:45.123Z",
            "body": "Generated at 2024-09-02T11:30:45Z with run ID 12345",
        }

        normalized = normalize_payload(payload)

        # Timestamps should be removed or normalized
        assert "timestamp" not in normalized
        assert "created_at" not in normalized
        assert "[TIMESTAMP]" in normalized["title"]
        assert "[TIMESTAMP]" in normalized["body"]
        assert "[ID]" in normalized["body"]

    def test_url_normalization(self):
        """Test that URLs are normalized to remove variable parts."""
        payload = {
            "url": "https://github.com/owner/repo/actions/runs/12345",
            "html_url": "https://github.com/owner/repo/issues/123",
            "api_url": "https://api.github.com/repos/owner/repo/issues/123",
        }

        normalized = normalize_payload(payload)

        # URLs should be normalized to remove protocol and keep path
        assert normalized["url"] == "github.com/owner/repo/actions/runs/12345"
        assert normalized["html_url"] == "github.com/owner/repo/issues/123"
        assert normalized["api_url"] == "api.github.com/repos/owner/repo/issues/123"

    def test_run_id_normalization(self):
        """Test that run IDs and numbers are excluded."""
        payload = {
            "run_id": "123456789",
            "run_number": "42",
            "title": "MotherSpace Report - Run #42",
            "important_data": "keep this",
        }

        normalized = normalize_payload(payload)

        # Run identifiers should be excluded
        assert "run_id" not in normalized
        assert "run_number" not in normalized
        # But normalized in titles
        assert "Run #[ID]" in normalized["title"]
        # Important data should be preserved
        assert normalized["important_data"] == "keep this"

    def test_nested_normalization(self):
        """Test that nested dictionaries are properly normalized."""
        payload = {
            "metadata": {
                "timestamp": "2024-09-02T11:30:45Z",
                "stable_value": "important",
                "nested": {"run_id": "12345", "keep_this": "value"},
            },
            "items": [
                {"url": "https://github.com/test", "name": "item1"},
                {"timestamp": "2024-09-02T11:30:45Z", "name": "item2"},
            ],
        }

        normalized = normalize_payload(payload)

        # Check nested dictionary normalization
        metadata = normalized["metadata"]
        assert "timestamp" not in metadata
        assert metadata["stable_value"] == "important"
        assert "run_id" not in metadata["nested"]
        assert metadata["nested"]["keep_this"] == "value"

        # Check list normalization
        items = normalized["items"]
        assert items[0]["url"] == "github.com/test"
        assert items[0]["name"] == "item1"
        assert "timestamp" not in items[1]
        assert items[1]["name"] == "item2"


class TestFingerprintGeneration:
    """Test fingerprint generation and stability."""

    def test_fingerprint_stability(self):
        """Test that identical normalized payloads produce identical fingerprints."""
        payload1 = {
            "operation": "harmony_check",
            "harmony_score": 85,
            "timestamp": "2024-09-02T11:30:45Z",  # This will be normalized out
            "issues": [{"number": 123, "title": "Fix bug"}],
        }

        payload2 = {
            "operation": "harmony_check",
            "harmony_score": 85,
            "timestamp": "2024-09-02T15:45:30Z",  # Different timestamp
            "issues": [{"number": 123, "title": "Fix bug"}],
        }

        fingerprint1 = generate_fingerprint(payload1, "test")
        fingerprint2 = generate_fingerprint(payload2, "test")

        # Should be identical despite different timestamps
        assert fingerprint1 == fingerprint2

    def test_fingerprint_uniqueness(self):
        """Test that different payloads produce different fingerprints."""
        payload1 = {"operation": "harmony_check", "harmony_score": 85}

        payload2 = {"operation": "task_delegation", "harmony_score": 85}

        fingerprint1 = generate_fingerprint(payload1, "test")
        fingerprint2 = generate_fingerprint(payload2, "test")

        # Should be different
        assert fingerprint1 != fingerprint2

    def test_category_scoping(self):
        """Test that categories properly scope fingerprints."""
        payload = {"operation": "harmony_check", "harmony_score": 85}

        fingerprint_mother = generate_fingerprint(payload, "motherspace")
        fingerprint_daughter = generate_fingerprint(payload, "daughter")

        # Should be different due to category
        assert fingerprint_mother != fingerprint_daughter
        # Should have category prefix
        assert fingerprint_mother.startswith("motherspace-")
        assert fingerprint_daughter.startswith("daughter-")

    def test_fingerprint_format(self):
        """Test that fingerprint has expected format."""
        payload = {"test": "data"}
        fingerprint = generate_fingerprint(payload, "test")

        # Should match pattern: category-hash16
        parts = fingerprint.split("-", 1)
        assert len(parts) == 2
        assert parts[0] == "test"
        assert len(parts[1]) == 16  # 16-character hash
        assert all(c in "0123456789abcdef" for c in parts[1])  # Hex characters


class TestFingerprintTags:
    """Test fingerprint tag creation and extraction."""

    def test_tag_creation(self):
        """Test fingerprint tag creation."""
        fingerprint = "test-1234567890abcdef"
        tag = create_fingerprint_tag(fingerprint)

        expected = "<!-- FINGERPRINT:test-1234567890abcdef -->"
        assert tag == expected

    def test_tag_extraction(self):
        """Test fingerprint extraction from body text."""
        fingerprint = "test-1234567890abcdef"
        tag = create_fingerprint_tag(fingerprint)

        body = f"Some issue body content\n\n{tag}\n\nMore content"
        extracted = extract_fingerprint_from_body(body)

        assert extracted == fingerprint

    def test_tag_extraction_not_found(self):
        """Test fingerprint extraction when tag is not present."""
        body = "Some issue body content without fingerprint"
        extracted = extract_fingerprint_from_body(body)

        assert extracted == ""

    def test_tag_extraction_empty_body(self):
        """Test fingerprint extraction with empty or None body."""
        assert extract_fingerprint_from_body("") == ""
        assert extract_fingerprint_from_body(None) == ""

    def test_tag_extraction_multiple_tags(self):
        """Test that only the first fingerprint tag is extracted."""
        tag1 = create_fingerprint_tag("test-first123456789")
        tag2 = create_fingerprint_tag("test-second12345678")

        body = f"Content {tag1} more content {tag2} end"
        extracted = extract_fingerprint_from_body(body)

        assert extracted == "test-first123456789"


class TestFingerprintEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_payload(self):
        """Test fingerprint generation with empty payload."""
        fingerprint = generate_fingerprint({}, "empty")

        # Should still generate valid fingerprint
        assert fingerprint.startswith("empty-")
        assert len(fingerprint) == len("empty-") + 16

    def test_payload_with_none_values(self):
        """Test normalization with None values."""
        payload = {"valid_key": "valid_value", "none_key": None, "empty_string": "", "zero_value": 0}

        normalized = normalize_payload(payload)

        # None and other values should be preserved
        assert normalized["valid_key"] == "valid_value"
        assert normalized["none_key"] is None
        assert normalized["empty_string"] == ""
        assert normalized["zero_value"] == 0

    def test_payload_with_special_characters(self):
        """Test normalization with special characters in strings."""
        payload = {"title": "Test with émojis 🎯 and spëcial çhars", "body": "Content with\nnewlines\tand\ttabs"}

        normalized = normalize_payload(payload)

        # Special characters should be preserved
        assert "émojis 🎯" in normalized["title"]
        assert "\n" in normalized["body"]
        assert "\t" in normalized["body"]

    def test_very_large_payload(self):
        """Test fingerprint generation with large payload."""
        # Create a large payload
        large_payload = {
            "operation": "test",
            "large_list": [f"item_{i}" for i in range(1000)],
            "large_dict": {f"key_{i}": f"value_{i}" for i in range(100)},
        }

        fingerprint = generate_fingerprint(large_payload, "large")

        # Should still generate valid fingerprint
        assert fingerprint.startswith("large-")
        assert len(fingerprint) == len("large-") + 16


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
