#!/usr/bin/env python3
"""
Enhanced Safety Manager for MotherSpace Operations

Combines the simplicity of the original approach with robust safety features
to prevent bot loops, spam, and conflicts while maintaining functionality.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class SafetyManager:
    """Lightweight safety manager for MotherSpace operations."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.safety_dir = self.repo_path / ".github" / "safety"
        self.safety_dir.mkdir(exist_ok=True)
        
        # Simple configuration
        self.config = {
            "max_operations_per_hour": 5,
            "actor_cooldown_minutes": 30,
            "concurrency_timeout_minutes": 5,
        }
    
    def can_proceed(self, actor: str, operation: str) -> tuple[bool, str]:
        """Check if operation can proceed safely."""
        # Check for existing lock
        lock_file = self.safety_dir / f"{operation}.lock"
        if lock_file.exists():
            try:
                with open(lock_file) as f:
                    lock_data = json.load(f)
                lock_time = datetime.fromisoformat(lock_data["timestamp"])
                if (datetime.now() - lock_time).total_seconds() < self.config["concurrency_timeout_minutes"] * 60:
                    return False, f"Operation locked by {lock_data['actor']}"
                else:
                    lock_file.unlink()  # Remove stale lock
            except:
                lock_file.unlink()  # Remove invalid lock
        
        # Check actor cooldown
        cooldown_file = self.safety_dir / f"cooldown_{actor}.json"
        if cooldown_file.exists():
            try:
                with open(cooldown_file) as f:
                    cooldown_data = json.load(f)
                last_time = datetime.fromisoformat(cooldown_data["timestamp"])
                if (datetime.now() - last_time).total_seconds() < self.config["actor_cooldown_minutes"] * 60:
                    remaining = self.config["actor_cooldown_minutes"] * 60 - (datetime.now() - last_time).total_seconds()
                    return False, f"Actor in cooldown (remaining: {remaining:.0f}s)"
            except:
                cooldown_file.unlink()  # Remove invalid cooldown
        
        # Check rate limiting
        rate_file = self.safety_dir / f"rate_{operation}.json"
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        if rate_file.exists():
            try:
                with open(rate_file) as f:
                    rate_data = json.load(f)
                rate_hour = datetime.fromisoformat(rate_data["hour"])
                if rate_hour == current_hour and rate_data["count"] >= self.config["max_operations_per_hour"]:
                    return False, f"Rate limit exceeded ({rate_data['count']}/{self.config['max_operations_per_hour']})"
            except:
                pass  # Invalid rate file, continue
        
        return True, "Safe to proceed"
    
    def acquire_lock(self, actor: str, operation: str) -> bool:
        """Acquire operation lock."""
        can_proceed, reason = self.can_proceed(actor, operation)
        if not can_proceed:
            print(f"🚫 Cannot proceed: {reason}")
            return False
        
        # Create lock
        lock_file = self.safety_dir / f"{operation}.lock"
        lock_data = {
            "actor": actor,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(lock_file, "w") as f:
            json.dump(lock_data, f, indent=2)
        
        print(f"🔒 Acquired lock for {operation}")
        return True
    
    def release_lock(self, operation: str):
        """Release operation lock."""
        lock_file = self.safety_dir / f"{operation}.lock"
        if lock_file.exists():
            lock_file.unlink()
            print(f"🔓 Released lock for {operation}")
    
    def update_tracking(self, actor: str, operation: str):
        """Update actor cooldown and rate limiting."""
        # Update cooldown
        cooldown_file = self.safety_dir / f"cooldown_{actor}.json"
        with open(cooldown_file, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat()}, f)
        
        # Update rate limiting
        rate_file = self.safety_dir / f"rate_{operation}.json"
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        rate_data = {"hour": current_hour.isoformat(), "count": 1}
        if rate_file.exists():
            try:
                with open(rate_file) as f:
                    existing_data = json.load(f)
                existing_hour = datetime.fromisoformat(existing_data["hour"])
                if existing_hour == current_hour:
                    rate_data["count"] = existing_data["count"] + 1
            except:
                pass  # Use default data
        
        with open(rate_file, "w") as f:
            json.dump(rate_data, f)
    
    def generate_fingerprint(self, issue_data: dict) -> str:
        """Generate fingerprint for issue deduplication."""
        title = str(issue_data.get("title", "")).lower().strip()
        body = str(issue_data.get("body", "")).lower().strip()
        labels = sorted([str(label.get("name", "")) for label in issue_data.get("labels", [])])
        
        # Normalize content
        import re
        title = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', '[TIMESTAMP]', title)
        title = re.sub(r'#\d+', '[ISSUE_REF]', title)
        body = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', '[TIMESTAMP]', body)
        body = re.sub(r'#\d+', '[ISSUE_REF]', body)
        
        fingerprint_data = {
            "title": title,
            "body_hash": hashlib.sha256(body.encode()).hexdigest()[:16],
            "labels": labels
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(f"motherspace-v1.2.0:{fingerprint_string}".encode()).hexdigest()[:16]
    
    def find_existing_issue(self, fingerprint: str) -> Optional[int]:
        """Find existing issue with the same fingerprint."""
        tracking_file = self.safety_dir / "tracking.json"
        if tracking_file.exists():
            try:
                with open(tracking_file) as f:
                    tracking_data = json.load(f)
                return tracking_data.get("fingerprints", {}).get(fingerprint)
            except:
                pass
        return None
    
    def register_issue(self, fingerprint: str, issue_number: int):
        """Register issue with fingerprint for future deduplication."""
        tracking_file = self.safety_dir / "tracking.json"
        tracking_data = {"fingerprints": {}}
        
        if tracking_file.exists():
            try:
                with open(tracking_file) as f:
                    tracking_data = json.load(f)
            except:
                pass
        
        tracking_data["fingerprints"][fingerprint] = issue_number
        
        with open(tracking_file, "w") as f:
            json.dump(tracking_data, f, indent=2)
        
        print(f"📝 Registered issue #{issue_number} with fingerprint {fingerprint[:8]}...")
    
    def cleanup(self):
        """Clean up old safety data."""
        cutoff = datetime.now() - timedelta(days=7)
        
        for file_path in self.safety_dir.glob("*.json"):
            if file_path.stat().st_mtime < cutoff.timestamp():
                file_path.unlink()
                print(f"🧹 Cleaned up old file: {file_path.name}")
        
        for file_path in self.safety_dir.glob("*.lock"):
            if file_path.stat().st_mtime < cutoff.timestamp():
                file_path.unlink()
                print(f"🧹 Cleaned up old lock: {file_path.name}")


def main():
    """Main function for testing and operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MotherSpace Safety Manager")
    parser.add_argument("--test", action="store_true", help="Run safety tests")
    parser.add_argument("--check", type=str, help="Check if operation can proceed")
    parser.add_argument("--actor", type=str, default="github-actions", help="Actor name")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old data")
    
    args = parser.parse_args()
    
    safety = SafetyManager()
    
    if args.cleanup:
        safety.cleanup()
    elif args.check:
        can_proceed, reason = safety.can_proceed(args.actor, args.check)
        print(f"Can proceed: {can_proceed}")
        print(f"Reason: {reason}")
        sys.exit(0 if can_proceed else 1)
    elif args.test:
        print("🧪 Running safety tests...")
        
        # Test basic functionality
        assert safety.acquire_lock("test_actor", "test_operation")
        assert not safety.acquire_lock("another_actor", "test_operation")
        safety.release_lock("test_operation")
        
        # Test fingerprinting
        issue1 = {"title": "Test Issue", "body": "Test body", "labels": [{"name": "test"}]}
        issue2 = {"title": "Test Issue", "body": "Test body", "labels": [{"name": "test"}]}
        
        fp1 = safety.generate_fingerprint(issue1)
        fp2 = safety.generate_fingerprint(issue2)
        assert fp1 == fp2, "Same issues should have same fingerprint"
        
        print("✅ All safety tests passed!")
    else:
        print("No operation specified. Use --help for options.")


if __name__ == "__main__":
    main()