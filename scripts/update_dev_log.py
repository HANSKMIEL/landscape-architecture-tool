#!/usr/bin/env python3
"""
Development Log Update Script
Updates the dev_log.md file with development activities and changes.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path


class DevLogManager:
    """Manages development log entries and formatting"""

    VALID_ACTIONS = {
        "feature_added": "FEATURE_ADDED",
        "bug_fixed": "BUG_FIXED",
        "refactor": "REFACTOR",
        "test_added": "TEST_ADDED",
        "docs_updated": "DOCS_UPDATED",
        "config_changed": "CONFIG_CHANGED",
    }

    def __init__(self, log_file="dev_log.md"):
        """Initialize the dev log manager

        Args:
            log_file (str): Path to the development log file
        """
        self.project_root = Path(__file__).parent.parent
        self.log_file = self.project_root / log_file

    def create_log_header(self):
        """Create the header for a new development log file"""
        header = """# Development Log - Landscape Architecture Tool

This file tracks development activities, changes, and progress for the Landscape Architecture Management Tool.

## Log Format
Each entry follows this format:
- **Timestamp**: When the change was made
- **Action Type**: Category of the change (FEATURE_ADDED, BUG_FIXED, etc.)
- **Author**: Developer who made the change
- **Description**: Detailed description of the change
- **Impact**: Brief assessment of the impact

---

"""
        return header

    def format_log_entry(self, action, description, author, impact=None):
        """Format a new log entry

        Args:
            action (str): The type of action taken
            description (str): Description of the change
            author (str): Author of the change
            impact (str, optional): Impact assessment

        Returns:
            str: Formatted log entry
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_type = self.VALID_ACTIONS.get(action, action.upper())

        entry = f"""## [{timestamp}] - {action_type}
**Author**: {author}
**Description**: {description}"""

        if impact:
            entry += f"\n**Impact**: {impact}"

        entry += "\n\n---\n\n"
        return entry

    def add_entry(self, action, description, author, impact=None):
        """Add a new entry to the development log

        Args:
            action (str): The type of action taken
            description (str): Description of the change
            author (str): Author of the change
            impact (str, optional): Impact assessment

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate action type
            if action not in self.VALID_ACTIONS:
                print(f"Warning: '{action}' is not a standard action type.")
                print(f"Valid actions are: {', '.join(self.VALID_ACTIONS.keys())}")

            # Create log file if it doesn't exist
            if not self.log_file.exists():
                with open(self.log_file, "w") as f:
                    f.write(self.create_log_header())
                print(f"Created new development log: {self.log_file}")

            # Format and add the new entry
            entry = self.format_log_entry(action, description, author, impact)

            # Read existing content
            with open(self.log_file, "r") as f:
                content = f.read()

            # Insert new entry after the header (before first existing entry)
            header_end = content.find("---\n\n") + 5
            if header_end == 4:  # Header not found, append to end
                updated_content = content + entry
            else:
                updated_content = content[:header_end] + entry + content[header_end:]

            # Write updated content
            with open(self.log_file, "w") as f:
                f.write(updated_content)

            print(f"Successfully added {action} entry to development log")
            print(f"Entry: {description}")
            return True

        except Exception as e:
            print(f"Error adding entry to development log: {str(e)}")
            return False

    def list_entries(self, limit=10):
        """List recent log entries

        Args:
            limit (int): Maximum number of entries to show
        """
        try:
            if not self.log_file.exists():
                print("Development log file does not exist yet.")
                return

            with open(self.log_file, "r") as f:
                content = f.read()

            # Extract entries (looking for ## [timestamp] patterns)
            entries = []
            lines = content.split("\n")
            current_entry = []

            for line in lines:
                if line.startswith("## [") and current_entry:
                    entries.append("\n".join(current_entry))
                    current_entry = [line]
                elif line.startswith("## ["):
                    current_entry = [line]
                elif current_entry:
                    current_entry.append(line)

            if current_entry:
                entries.append("\n".join(current_entry))

            # Show recent entries
            if entries:
                print(f"\nRecent Development Log Entries (showing {min(limit, len(entries))} of {len(entries)}):")
                print("=" * 60)
                for entry in entries[:limit]:
                    print(entry)
                    print("-" * 40)
            else:
                print("No entries found in development log.")

        except Exception as e:
            print(f"Error reading development log: {str(e)}")

    def get_stats(self):
        """Get statistics about the development log"""
        try:
            if not self.log_file.exists():
                return {"total_entries": 0, "actions": {}}

            with open(self.log_file, "r") as f:
                content = f.read()

            # Count entries by action type
            action_counts = {}
            total_entries = 0

            for line in content.split("\n"):
                if line.startswith("## [") and "] - " in line:
                    total_entries += 1
                    action = line.split("] - ")[1].strip()
                    action_counts[action] = action_counts.get(action, 0) + 1

            return {"total_entries": total_entries, "actions": action_counts}

        except Exception as e:
            print(f"Error getting log statistics: {str(e)}")
            return {"total_entries": 0, "actions": {}}


def main():
    """Main entry point for the development log script"""
    parser = argparse.ArgumentParser(
        description="Update development log for Landscape Architecture Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_dev_log.py --action feature_added --description "Added plant recommendation system" --author "john_doe"
  python scripts/update_dev_log.py --action bug_fixed --description "Fixed database connection issue" --author "jane_smith" --impact "Resolves production stability issues"
  python scripts/update_dev_log.py --list --count 5
  python scripts/update_dev_log.py --stats
        """,
    )

    parser.add_argument(
        "--action",
        choices=list(DevLogManager.VALID_ACTIONS.keys()),
        help="Type of development action",
    )
    parser.add_argument("--description", help="Description of the change")
    parser.add_argument("--author", help="Author of the change")
    parser.add_argument("--impact", help="Impact assessment (optional)")
    parser.add_argument(
        "--log-file",
        default="dev_log.md",
        help="Path to log file (default: dev_log.md)",
    )
    parser.add_argument("--list", action="store_true", help="List recent log entries")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of entries to show when listing (default: 10)",
    )
    parser.add_argument("--stats", action="store_true", help="Show development log statistics")

    args = parser.parse_args()

    # Initialize log manager
    log_manager = DevLogManager(args.log_file)

    # Handle different operations
    if args.list:
        log_manager.list_entries(args.count)
    elif args.stats:
        stats = log_manager.get_stats()
        print("\nDevelopment Log Statistics:")
        print(f"Total entries: {stats['total_entries']}")
        if stats["actions"]:
            print("\nActions by type:")
            for action, count in sorted(stats["actions"].items()):
                print(f"  {action}: {count}")
    elif args.action and args.description and args.author:
        success = log_manager.add_entry(args.action, args.description, args.author, args.impact)
        if success:
            print("\nDevelopment log updated successfully!")
            # Show recent entries after adding
            print("\nMost recent entries:")
            log_manager.list_entries(3)
        else:
            sys.exit(1)
    else:
        if not args.list and not args.stats:
            print("Error: Missing required arguments for adding an entry.")
            print("Required: --action, --description, --author")
            print("Use --help for more information.")
            sys.exit(1)


if __name__ == "__main__":
    main()
