#!/usr/bin/env python3
"""
Repository Clutter Management Script

Automatically organizes generated files into appropriate subfolders to keep
the root directory clean and maintainable.
"""

import argparse
import glob
import os
import shutil
from datetime import datetime
from pathlib import Path


def ensure_directories():
    """Create the standard directory structure for organized file storage."""
    directories = [
        "reports/validation",
        "reports/health",
        "reports/security",
        "docs/solutions",
        "docs/planning",
        "archive",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Ensured directory: {directory}")


def organize_files(dry_run=False):
    """Organize clutter files into appropriate subfolders."""

    # File patterns and their target directories
    file_patterns = {
        "reports/validation": [
            "automated_validation_report_*.json",
            "validation_*.json",
            "*_validation_*.json",
        ],
        "reports/health": ["pipeline_health_report_*.json", "health_*.json", "*_health_*.json"],
        "reports/security": [
            "bandit-report.json",
            "safety-report.json",
            "security_*.json",
            "*_security_*.json",
        ],
        "docs/solutions": [
            "*_SOLUTION*.md",
            "*_SUMMARY*.md",
            "*_IMPLEMENTATION*.md",
            "SOLUTION_*.md",
        ],
        "docs/planning": ["*_PLAN*.md", "*_ROADMAP*.md", "PLANNED_*.md", "dev_log.md"],
    }

    moved_files = []

    for target_dir, patterns in file_patterns.items():
        for pattern in patterns:
            files = glob.glob(pattern)
            for file in files:
                if os.path.isfile(file):
                    target_path = os.path.join(target_dir, os.path.basename(file))

                    if dry_run:
                        print(f"Would move: {file} → {target_path}")
                    else:
                        try:
                            shutil.move(file, target_path)
                            print(f"Moved: {file} → {target_path}")
                            moved_files.append((file, target_path))
                        except Exception as e:
                            print(f"Error moving {file}: {e}")

    return moved_files


def check_clutter():
    """Check for remaining clutter in root directory."""
    clutter_patterns = ["*.md", "*.json"]
    exclude_files = ["README.md", "package-lock.json", ".gitignore"]

    clutter_files = []
    for pattern in clutter_patterns:
        files = glob.glob(pattern)
        clutter_files.extend([f for f in files if f not in exclude_files])

    return clutter_files


def generate_report(moved_files, remaining_clutter):
    """Generate a cleanup report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/validation/clutter_cleanup_report_{timestamp}.json"

    import json

    report = {
        "timestamp": datetime.now().isoformat(),
        "moved_files": [{"from": src, "to": dst} for src, dst in moved_files],
        "moved_count": len(moved_files),
        "remaining_clutter": remaining_clutter,
        "remaining_count": len(remaining_clutter),
        "status": "clean" if len(remaining_clutter) == 0 else "needs_attention",
    }

    Path(report_file).parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nCleanup report saved to: {report_file}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Organize repository clutter")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving files",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check for clutter without organizing"
    )
    parser.add_argument("--report", action="store_true", help="Generate a cleanup report")

    args = parser.parse_args()

    print("🧹 Repository Clutter Management")
    print("=" * 40)

    if args.check_only:
        clutter = check_clutter()
        if clutter:
            print(f"\n⚠️  Found {len(clutter)} clutter files in root:")
            for file in clutter:
                print(f"  - {file}")
        else:
            print("\n✅ No clutter detected in root directory")
        return

    # Ensure directory structure exists
    ensure_directories()

    # Organize files
    moved_files = organize_files(dry_run=args.dry_run)

    # Check remaining clutter
    remaining_clutter = check_clutter()

    # Summary
    print("\n📊 Cleanup Summary:")
    print(f"   Files moved: {len(moved_files)}")
    print(f"   Remaining clutter: {len(remaining_clutter)}")

    if remaining_clutter:
        print("\n⚠️  Remaining clutter files:")
        for file in remaining_clutter:
            print(f"  - {file}")
    else:
        print("\n✅ Root directory is clean!")

    # Generate report if requested
    if args.report and not args.dry_run:
        generate_report(moved_files, remaining_clutter)


if __name__ == "__main__":
    main()
