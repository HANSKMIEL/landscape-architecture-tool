#!/usr/bin/env python3
"""
Issue fingerprinting utility for GitHub Actions.

Generates stable fingerprints from structured payloads to identify duplicates
across workflow runs. Normalizes URLs, timestamps, and other variable data
to ensure consistent identification.
"""

import hashlib
import json
import re
from typing import Any
from urllib.parse import urlparse


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a payload by removing or standardizing variable data.
    
    Args:
        payload: Dictionary containing issue/automation data
        
    Returns:
        Normalized dictionary suitable for fingerprinting
    """
    normalized = {}
    
    for key, value in payload.items():
        if key in ["timestamp", "created_at", "updated_at", "run_id", "run_number"]:
            # Skip variable timestamps and run identifiers
            continue
        if key in ["url", "html_url", "api_url"]:
            # Normalize URLs by keeping only the path structure, removing variable IDs
            if isinstance(value, str) and value.startswith("http"):
                parsed = urlparse(value)
                path = parsed.path
                # Remove workflow run IDs
                path = re.sub(r"/runs/\d+", "/runs/[ID]", path)
                # Remove issue/PR numbers
                path = re.sub(r"/issues/\d+", "/issues/[ID]", path)
                path = re.sub(r"/pull/\d+", "/pull/[ID]", path)
                normalized[key] = f"{parsed.netloc}{path}"
            else:
                normalized[key] = value
        elif key == "title" and isinstance(value, str):
            # Normalize titles by removing common variable patterns
            title = value
            # Remove timestamps like "2024-09-02 11:30:45"
            title = re.sub(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", "[TIMESTAMP]", title)
            # Remove ISO timestamps like "2024-09-02T11:30:45Z"
            title = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\.\d]*Z?", "[TIMESTAMP]", title)
            # Remove "Run #12345" patterns
            title = re.sub(r"Run\s+#\d+", "Run #[ID]", title)
            # Remove dates like "September 2, 2024"
            title = re.sub(r"\b[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\b", "[DATE]", title)
            # Remove time patterns like "11:30:45"
            title = re.sub(r"\d{2}:\d{2}:\d{2}", "[TIME]", title)
            normalized[key] = title
        elif key == "body" and isinstance(value, str):
            # Normalize body text similarly to title
            body = value
            # Remove timestamps and run IDs
            body = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\.\d]*Z?", "[TIMESTAMP]", body)
            body = re.sub(r"Run ID:\s*\d+", "Run ID: [ID]", body)
            body = re.sub(r"#\d{4,}", "#[ID]", body)  # Issue/PR numbers
            # Remove workflow run URLs
            body = re.sub(r"https://github\.com/[^/]+/[^/]+/actions/runs/\d+", "[WORKFLOW_URL]", body)
            normalized[key] = body
        elif isinstance(value, dict):
            # Recursively normalize nested dictionaries
            normalized[key] = normalize_payload(value)
        elif isinstance(value, list):
            # Normalize lists by normalizing each element
            normalized_list = []
            for item in value:
                if isinstance(item, dict):
                    normalized_list.append(normalize_payload(item))
                elif isinstance(item, str):
                    # Apply same string normalization as above
                    item = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\.\d]*Z?", "[TIMESTAMP]", item)
                    normalized_list.append(item)
                else:
                    normalized_list.append(item)
            normalized[key] = normalized_list
        else:
            # Keep other values as-is
            normalized[key] = value
    
    return normalized


def generate_fingerprint(payload: dict[str, Any], category: str = "general") -> str:
    """
    Generate a stable fingerprint for the given payload.
    
    Args:
        payload: Dictionary containing issue/automation data
        category: Category to include in fingerprint for scoping
        
    Returns:
        Stable fingerprint string suitable for deduplication
    """
    # Normalize the payload first
    normalized = normalize_payload(payload)
    
    # Add category to ensure different types of issues don't conflict
    normalized["_category"] = category
    
    # Sort keys to ensure consistent ordering
    def sort_dict(d):
        if isinstance(d, dict):
            return {k: sort_dict(v) for k, v in sorted(d.items())}
        if isinstance(d, list):
            return [sort_dict(item) for item in d]
        return d
    
    sorted_payload = sort_dict(normalized)
    
    # Convert to JSON string with consistent formatting
    json_str = json.dumps(sorted_payload, sort_keys=True, separators=(",", ":"))
    
    # Generate SHA-256 hash
    fingerprint = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    
    # Return truncated fingerprint with category prefix
    return f"{category}-{fingerprint[:16]}"


def create_fingerprint_tag(fingerprint: str) -> str:
    """
    Create a hidden HTML comment tag containing the fingerprint.
    
    Args:
        fingerprint: The generated fingerprint
        
    Returns:
        HTML comment tag for embedding in issue body
    """
    return f"<!-- FINGERPRINT:{fingerprint} -->"


def extract_fingerprint_from_body(body: str) -> str:
    """
    Extract fingerprint from an issue body containing a fingerprint tag.
    
    Args:
        body: Issue body text that may contain a fingerprint tag
        
    Returns:
        Extracted fingerprint string, or empty string if not found
    """
    if not body:
        return ""
    
    pattern = r"<!-- FINGERPRINT:([^>]+) -->"
    match = re.search(pattern, body)
    return match.group(1) if match else ""


if __name__ == "__main__":
    # Example usage for testing
    example_payload = {
        "title": "MotherSpace Analysis - September 2, 2024",
        "operation": "harmony_check",
        "harmony_score": 85,
        "timestamp": "2024-09-02T11:30:45Z",
        "run_id": "12345",
        "issues": [
            {"number": 123, "title": "Fix bug"},
            {"number": 124, "title": "Add feature"}
        ],
        "url": "https://github.com/owner/repo/actions/runs/12345"
    }
    
    fingerprint = generate_fingerprint(example_payload, "motherspace")
    tag = create_fingerprint_tag(fingerprint)
    
    print(f"Fingerprint: {fingerprint}")
    print(f"Tag: {tag}")
    
    # Test extraction
    extracted = extract_fingerprint_from_body(f"Some body text {tag} more text")
    print(f"Extracted: {extracted}")
    print(f"Match: {extracted == fingerprint}")