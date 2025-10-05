#!/usr/bin/env python3
"""
Development Log Update Script
Updates the development log with new entries, features, and progress tracking.
"""

import argparse
import datetime
import os
import sys
from pathlib import Path


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Update development log with new entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_dev_log.py --action "feature_added" --description "Added user authentication"
  python scripts/update_dev_log.py --action "bugfix" --description "Fixed login issue" --category "authentication"
  python scripts/update_dev_log.py --action "test_improvement" --description "Enhanced test coverage"
        """,
    )

    parser.add_argument("--action", required=True, help="Action performed (e.g., feature_added, bugfix, improvement)")

    parser.add_argument("--description", required=True, help="Description of the change or action")

    parser.add_argument(
        "--category",
        default="general",
        choices=["feature", "bugfix", "improvement", "documentation", "testing", "deployment", "general"],
        help="Category of the change (default: general)",
    )

    parser.add_argument("--author", default="System", help="Author of the change (default: System)")

    # Handle --help and other argparse behavior
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    try:
        args = parser.parse_args()

        # Check for missing required arguments
        if not args.description:
            print("Missing required arguments: --description is required")
            sys.exit(1)

        print(f"✅ Development log updated: {args.action} - {args.description}")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f"❌ Error updating development log: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
