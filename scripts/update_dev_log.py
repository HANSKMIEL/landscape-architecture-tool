#!/usr/bin/env python3
"""Command-line entry point for maintaining the development log."""

import argparse
import sys
from pathlib import Path

try:
    from scripts.development.update_dev_log import DevLogManager
except ModuleNotFoundError:  # Script executed directly, ensure package import works
    CURRENT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = CURRENT_DIR.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.development.update_dev_log import DevLogManager


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser used by the CLI."""

    parser = argparse.ArgumentParser(
        description="Update development log for Landscape Architecture Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_dev_log.py --action feature_added --description "Added user auth" --author "dev"
  python scripts/update_dev_log.py --list --count 5
  python scripts/update_dev_log.py --stats
        """,
    )

    parser.add_argument(
        "--action",
        choices=list(DevLogManager.VALID_ACTIONS.keys()),
        help="Type of development action to record",
    )
    parser.add_argument("--description", help="Description of the change")
    parser.add_argument("--author", help="Name of the author for the entry")
    parser.add_argument("--impact", help="Optional impact summary for the change")
    parser.add_argument(
        "--log-file",
        default="dev_log.md",
        help="Path to dev log file (default: dev_log.md)",
    )
    parser.add_argument("--list", action="store_true", help="List recent entries")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of entries to list (default: 10)",
    )
    parser.add_argument("--stats", action="store_true", help="Display development log statistics")

    return parser


def main() -> None:
    """Main function handling CLI invocation."""

    parser = build_parser()
    args = parser.parse_args()

    manager = DevLogManager(log_file=args.log_file)

    exit_code = 0

    if args.list:
        manager.list_entries(limit=args.count)
    elif args.stats:
        stats = manager.get_stats()
        print("\nDevelopment Log Statistics:")
        print(f"Total entries: {stats['total_entries']}")
        if stats["actions"]:
            print("\nActions by type:")
            for action, count in sorted(stats["actions"].items()):
                print(f"  {action}: {count}")
    elif args.action is not None:
        missing = []
        if not args.description:
            missing.append("--description")
        if not args.author:
            missing.append("--author")

        if missing:
            print("Missing required arguments: " + ", ".join(missing))
            exit_code = 1
        else:
            success = manager.add_entry(args.action, args.description, args.author, args.impact)
            if not success:
                exit_code = 1
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
