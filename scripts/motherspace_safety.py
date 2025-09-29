#!/usr/bin/env python3
"""
MotherSpace Safety Enhancement Script

This script implements safety features for the MotherSpace orchestrator including:
- Concurrency controls
- Actor guards to prevent bot loops
- Fingerprint-based deduplication
- Single tracking issue pattern
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class MotherSpaceSafetyManager:
    """Manages safety features for MotherSpace operations."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.safety_dir = self.repo_path / ".github" / "motherspace-safety"
        self.safety_dir.mkdir(exist_ok=True)

        # Safety configuration
        self.config = {
            "max_operations_per_hour": 10,
            "bot_loop_detection_window": 3600,  # 1 hour
            "max_similar_issues_per_day": 3,
            "concurrency_timeout": 300,  # 5 minutes
            "fingerprint_cache_ttl": 86400,  # 24 hours
            "actor_cooldown_period": 1800,  # 30 minutes
        }

    def acquire_lock(self, operation_name: str, actor: str = "github-actions") -> bool:
        """Acquire a concurrency lock for an operation."""
        lock_file = self.safety_dir / f"{operation_name}.lock"

        # Check if lock exists and is still valid
        if lock_file.exists():
            try:
                with open(lock_file) as f:
                    lock_data = json.load(f)

                lock_time = datetime.fromisoformat(lock_data.get("timestamp", ""))
                lock_age = (datetime.now() - lock_time).total_seconds()

                # If lock is older than timeout, remove it
                if lock_age > self.config["concurrency_timeout"]:
                    lock_file.unlink()
                    print(f"🔓 Removed stale lock for {operation_name} (age: {lock_age:.0f}s)")
                else:
                    print(
                        f"⏳ Operation {operation_name} is locked by {lock_data.get('actor')} (remaining: {self.config['concurrency_timeout'] - lock_age:.0f}s)"
                    )
                    return False
            except (json.JSONDecodeError, ValueError):
                # Invalid lock file, remove it
                lock_file.unlink()

        # Create new lock
        lock_data = {
            "operation": operation_name,
            "actor": actor,
            "timestamp": datetime.now().isoformat(),
            "pid": os.getpid(),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_data, f, indent=2)

        print(f"🔒 Acquired lock for {operation_name} by {actor}")
        return True

    def release_lock(self, operation_name: str) -> None:
        """Release a concurrency lock."""
        lock_file = self.safety_dir / f"{operation_name}.lock"
        if lock_file.exists():
            lock_file.unlink()
            print(f"🔓 Released lock for {operation_name}")

    def check_actor_cooldown(self, actor: str, operation: str) -> bool:
        """Check if actor is in cooldown period."""
        cooldown_file = self.safety_dir / f"cooldown_{actor}_{operation}.json"

        if cooldown_file.exists():
            try:
                with open(cooldown_file) as f:
                    cooldown_data = json.load(f)

                last_operation = datetime.fromisoformat(cooldown_data.get("last_operation", ""))
                cooldown_remaining = (
                    self.config["actor_cooldown_period"] - (datetime.now() - last_operation).total_seconds()
                )

                if cooldown_remaining > 0:
                    print(f"❄️ Actor {actor} in cooldown for {operation} (remaining: {cooldown_remaining:.0f}s)")
                    return False
            except (json.JSONDecodeError, ValueError):
                # Invalid cooldown file, remove it
                cooldown_file.unlink()

        return True

    def update_actor_cooldown(self, actor: str, operation: str) -> None:
        """Update actor cooldown timestamp."""
        cooldown_file = self.safety_dir / f"cooldown_{actor}_{operation}.json"
        cooldown_data = {"actor": actor, "operation": operation, "last_operation": datetime.now().isoformat()}

        with open(cooldown_file, "w") as f:
            json.dump(cooldown_data, f, indent=2)

    def check_operation_rate_limit(self, operation: str) -> bool:
        """Check if operation rate limit is exceeded."""
        rate_file = self.safety_dir / f"rate_{operation}.json"
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

        if rate_file.exists():
            try:
                with open(rate_file) as f:
                    rate_data = json.load(f)

                rate_hour = datetime.fromisoformat(rate_data.get("hour", ""))

                # If same hour, check count
                if rate_hour == current_hour:
                    count = rate_data.get("count", 0)
                    if count >= self.config["max_operations_per_hour"]:
                        print(
                            f"🚫 Rate limit exceeded for {operation} ({count}/{self.config['max_operations_per_hour']} operations this hour)"
                        )
                        return False

                    # Increment count
                    rate_data["count"] = count + 1
                else:
                    # New hour, reset count
                    rate_data = {"hour": current_hour.isoformat(), "count": 1}
            except (json.JSONDecodeError, ValueError):
                # Invalid rate file, create new
                rate_data = {"hour": current_hour.isoformat(), "count": 1}
        else:
            rate_data = {"hour": current_hour.isoformat(), "count": 1}

        with open(rate_file, "w") as f:
            json.dump(rate_data, f, indent=2)

        return True

    def check_bot_loop_pattern(self, actor: str, issue_title: str) -> bool:
        """Detect potential bot loop patterns."""
        pattern_file = self.safety_dir / f"patterns_{actor}.json"
        current_time = datetime.now()

        if pattern_file.exists():
            try:
                with open(pattern_file) as f:
                    pattern_data = json.load(f)

                # Clean old entries
                recent_operations = []
                for op in pattern_data.get("operations", []):
                    op_time = datetime.fromisoformat(op["timestamp"])
                    if (current_time - op_time).total_seconds() < self.config["bot_loop_detection_window"]:
                        recent_operations.append(op)

                # Check for repeated patterns
                similar_operations = [op for op in recent_operations if op["title"] == issue_title]

                if len(similar_operations) >= 3:
                    print(
                        f"🤖⚠️ Bot loop detected: {actor} has performed similar operation '{issue_title}' {len(similar_operations)} times in the last hour"
                    )
                    return False

                # Update pattern data
                recent_operations.append({"title": issue_title, "timestamp": current_time.isoformat()})

                pattern_data["operations"] = recent_operations[-50:]  # Keep last 50 operations
            except (json.JSONDecodeError, ValueError):
                pattern_data = {"operations": [{"title": issue_title, "timestamp": current_time.isoformat()}]}
        else:
            pattern_data = {"operations": [{"title": issue_title, "timestamp": current_time.isoformat()}]}

        with open(pattern_file, "w") as f:
            json.dump(pattern_data, f, indent=2)

        return True

    def get_issue_fingerprint(self, issue_data: dict[str, Any]) -> str:
        """Generate fingerprint for issue using the fingerprinting system."""
        # Use embedded fingerprinter to avoid pytest dependency
        return self._generate_fingerprint_embedded(issue_data)

    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing timestamps, IDs, and paths while preserving structure."""
        import re

        if not text:
            return ""

        # Remove timestamps
        text = re.sub(
            r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b", "[TIMESTAMP]", text
        )
        text = re.sub(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b", "[DATE]", text)

        # Remove issue/PR numbers
        text = re.sub(r"#\d+", "#[NUM]", text)

        # Remove file paths
        text = re.sub(r"/[a-zA-Z0-9/_.-]+\.(py|js|json|yml|yaml|md|txt)", "/[PATH].[EXT]", text)

        # Remove UUIDs and long hex strings
        text = re.sub(r"\b[a-f0-9]{32,}\b", "[HASH]", text, flags=re.IGNORECASE)
        text = re.sub(
            r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b", "[UUID]", text, flags=re.IGNORECASE
        )

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text.lower()

    def _generate_fingerprint_embedded(self, issue_data: dict[str, Any]) -> str:
        """Generate a stable fingerprint for an issue (embedded implementation)."""
        salt = "motherspace-orchestrator-v1.1.0"

        # Extract and normalize title and body
        title = issue_data.get("title", "")
        body = issue_data.get("body", "")

        normalized_title = self._normalize_text(title)
        normalized_body = self._normalize_text(body)

        # Create content hash from normalized text
        content = f"{normalized_title}|{normalized_body}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Process labels - handle both string labels and label objects
        labels = issue_data.get("labels", [])
        if labels:
            # Handle GitHub API label format (list of dicts with 'name' key)
            if isinstance(labels[0], dict):
                label_names = [label.get("name", "") for label in labels]
            else:
                # Handle simple string list
                label_names = labels
            labels_str = "|".join(sorted(label_names))
        else:
            labels_str = "no_labels"

        # Create final fingerprint
        fingerprint_data = f"{content_hash}|{labels_str}|{salt}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    def get_issue_fingerprint(self, issue_data: dict[str, Any]) -> str:
        """Generate fingerprint for issue using the fingerprinting system."""
        # Use embedded fingerprinter to avoid pytest dependency
        return self._generate_fingerprint_embedded(issue_data)

    def find_existing_tracking_issue(self, fingerprint: str) -> dict[str, Any] | None:
        """Find existing tracking issue with the same fingerprint."""
        tracking_file = self.safety_dir / "tracking_issues.json"

        if tracking_file.exists():
            try:
                with open(tracking_file) as f:
                    tracking_data = json.load(f)

                return tracking_data.get("fingerprints", {}).get(fingerprint)
            except (json.JSONDecodeError, ValueError):
                pass

        return None

    def register_tracking_issue(self, fingerprint: str, issue_number: int, issue_data: dict[str, Any]) -> None:
        """Register a new tracking issue with its fingerprint."""
        tracking_file = self.safety_dir / "tracking_issues.json"

        try:
            if tracking_file.exists():
                with open(tracking_file) as f:
                    tracking_data = json.load(f)
            else:
                tracking_data = {"fingerprints": {}}

            tracking_data["fingerprints"][fingerprint] = {
                "issue_number": issue_number,
                "title": issue_data.get("title", ""),
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "update_count": 1,
            }

            with open(tracking_file, "w") as f:
                json.dump(tracking_data, f, indent=2)

            print(f"📝 Registered tracking issue #{issue_number} with fingerprint {fingerprint[:8]}...")
        except Exception as e:
            print(f"⚠️ Failed to register tracking issue: {e}")

    def update_tracking_issue(self, fingerprint: str, update_data: dict[str, Any]) -> int | None:
        """Update existing tracking issue instead of creating new one."""
        tracking_file = self.safety_dir / "tracking_issues.json"

        try:
            if tracking_file.exists():
                with open(tracking_file) as f:
                    tracking_data = json.load(f)

                if fingerprint in tracking_data.get("fingerprints", {}):
                    issue_info = tracking_data["fingerprints"][fingerprint]
                    issue_info["last_updated"] = datetime.now().isoformat()
                    issue_info["update_count"] = issue_info.get("update_count", 0) + 1

                    with open(tracking_file, "w") as f:
                        json.dump(tracking_data, f, indent=2)

                    issue_number = issue_info["issue_number"]
                    print(f"🔄 Updated existing tracking issue #{issue_number} (update #{issue_info['update_count']})")
                    return issue_number
        except Exception as e:
            print(f"⚠️ Failed to update tracking issue: {e}")

        return None

    def is_safe_operation(self, actor: str, operation: str, issue_data: dict[str, Any]) -> dict[str, Any]:
        """Comprehensive safety check for MotherSpace operations."""
        safety_result = {
            "safe": True,
            "reasons": [],
            "fingerprint": None,
            "existing_tracking_issue": None,
            "action": "proceed",
        }

        # Check concurrency lock
        if not self.acquire_lock(operation, actor):
            safety_result["safe"] = False
            safety_result["reasons"].append("concurrency_lock_failed")
            safety_result["action"] = "wait_and_retry"
            return safety_result

        # Check actor cooldown
        if not self.check_actor_cooldown(actor, operation):
            self.release_lock(operation)
            safety_result["safe"] = False
            safety_result["reasons"].append("actor_in_cooldown")
            safety_result["action"] = "wait"
            return safety_result

        # Check rate limiting
        if not self.check_operation_rate_limit(operation):
            self.release_lock(operation)
            safety_result["safe"] = False
            safety_result["reasons"].append("rate_limit_exceeded")
            safety_result["action"] = "wait"
            return safety_result

        # Check bot loop patterns
        issue_title = issue_data.get("title", "")
        if not self.check_bot_loop_pattern(actor, issue_title):
            self.release_lock(operation)
            safety_result["safe"] = False
            safety_result["reasons"].append("bot_loop_detected")
            safety_result["action"] = "abort"
            return safety_result

        # Generate fingerprint and check for existing tracking issue
        fingerprint = self.get_issue_fingerprint(issue_data)
        safety_result["fingerprint"] = fingerprint

        existing_issue = self.find_existing_tracking_issue(fingerprint)
        if existing_issue:
            safety_result["existing_tracking_issue"] = existing_issue
            safety_result["action"] = "update_existing"
            print(
                f"🔍 Found existing tracking issue #{existing_issue['issue_number']} for fingerprint {fingerprint[:8]}..."
            )

        return safety_result

    def complete_operation(self, actor: str, operation: str, success: bool = True) -> None:
        """Complete an operation and update safety tracking."""
        # Update actor cooldown
        self.update_actor_cooldown(actor, operation)

        # Release lock
        self.release_lock(operation)

        # Log operation completion
        log_file = self.safety_dir / "operations.log"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "operation": operation,
            "success": success,
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"✅ Operation {operation} completed by {actor} (success: {success})")

    def cleanup_old_safety_data(self, max_age_days: int = 7) -> None:
        """Clean up old safety tracking data."""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)

        # Clean up old lock files
        for lock_file in self.safety_dir.glob("*.lock"):
            if lock_file.stat().st_mtime < cutoff_time.timestamp():
                lock_file.unlink()
                print(f"🧹 Cleaned up old lock file: {lock_file.name}")

        # Clean up old cooldown files
        for cooldown_file in self.safety_dir.glob("cooldown_*.json"):
            if cooldown_file.stat().st_mtime < cutoff_time.timestamp():
                cooldown_file.unlink()
                print(f"🧹 Cleaned up old cooldown file: {cooldown_file.name}")


def main():
    """Main function for testing safety manager."""
    import argparse

    parser = argparse.ArgumentParser(description="MotherSpace Safety Manager")
    parser.add_argument("--test", action="store_true", help="Run safety tests")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old safety data")
    parser.add_argument("--check", type=str, help="Check safety for operation")
    parser.add_argument("--actor", type=str, default="github-actions", help="Actor name")

    args = parser.parse_args()

    safety_manager = MotherSpaceSafetyManager()

    if args.cleanup:
        safety_manager.cleanup_old_safety_data()
    elif args.check:
        # Test safety check
        test_issue = {
            "title": f"Test operation: {args.check}",
            "body": "This is a test issue for safety checking",
            "labels": [{"name": "test"}, {"name": "automated"}],
        }

        result = safety_manager.is_safe_operation(args.actor, args.check, test_issue)
        print(f"Safety check result: {json.dumps(result, indent=2)}")

        if result["safe"]:
            safety_manager.complete_operation(args.actor, args.check, True)
    elif args.test:
        # Run comprehensive tests
        print("🧪 Running MotherSpace safety tests...")

        # Test concurrency locks
        print("\n1. Testing concurrency locks...")
        assert safety_manager.acquire_lock("test_operation", "test_actor")
        assert not safety_manager.acquire_lock("test_operation", "another_actor")
        safety_manager.release_lock("test_operation")

        # Test fingerprinting
        print("\n2. Testing fingerprinting...")
        test_issue1 = {"title": "Test Issue", "body": "Test body", "labels": [{"name": "test"}]}
        test_issue2 = {"title": "Test Issue", "body": "Test body", "labels": [{"name": "test"}]}

        fp1 = safety_manager.get_issue_fingerprint(test_issue1)
        fp2 = safety_manager.get_issue_fingerprint(test_issue2)
        assert fp1 == fp2, "Same issues should have same fingerprint"

        # Test tracking issue registration
        print("\n3. Testing tracking issue registration...")
        safety_manager.register_tracking_issue(fp1, 123, test_issue1)
        existing = safety_manager.find_existing_tracking_issue(fp1)
        assert existing is not None, "Should find registered tracking issue"
        assert existing["issue_number"] == 123

        print("\n✅ All safety tests passed!")


if __name__ == "__main__":
    main()
