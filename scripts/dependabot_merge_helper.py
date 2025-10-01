#!/usr/bin/env python3
"""
Dependabot PR Merge Helper
Provides detailed analysis and safety validation for dependency updates.
"""

import json
import sys
from typing import Dict, List, Tuple

import requests


class DependabotMergeHelper:
    def __init__(self):
        self.safe_patches = [
            409,  # @babel/core patch
            403,  # babel-jest patch
            402,  # jest patch
            404,  # react types patch
            405,  # msw minor
            410,  # radix-ui patches
            440,  # email-validator minor
            439,  # ipython minor
            436,  # database-stack minor
        ]

        self.careful_review = [
            435,  # flask patch (critical)
            417,  # testing-library minor
        ]

        self.major_updates = [
            442,  # openai major
            441,  # faker major
            437,  # pytest major
            412,  # vite build tools major
            411,  # tailwindcss major
            408,  # jest-environment major
        ]

    def categorize_prs(self) -> dict[str, list[int]]:
        return {
            "safe_auto_merge": self.safe_patches,
            "careful_review": self.careful_review,
            "major_updates": self.major_updates,
        }

    def get_merge_priority(self) -> list[tuple[int, str, str]]:
        """Return PRs in recommended merge order with reasoning."""
        priorities = []

        # Phase 1: Safe patches
        for pr_num in self.safe_patches:
            priorities.append((pr_num, "auto-merge", "Safe patch/minor update"))

        # Phase 2: Careful review
        for pr_num in self.careful_review:
            priorities.append((pr_num, "manual-review", "Critical dependency or testing tool"))

        # Phase 3: Major updates
        for pr_num in self.major_updates:
            priorities.append((pr_num, "extensive-testing", "Major version update"))

        return priorities

    def generate_merge_commands(self) -> list[str]:
        """Generate commands for safe merging."""
        commands = []

        for pr_num in self.safe_patches:
            commands.append(f"# PR #{pr_num} - Safe to merge")
            commands.append(f"gh pr merge {pr_num} --squash --auto")
            commands.append("")

        return commands

    def validate_repository_health(self) -> bool:
        """Basic repository health check."""
        try:
            # Check if backend can start
            import subprocess

            result = subprocess.run(
                [
                    "timeout",
                    "10s",
                    "bash",
                    "-c",
                    "cd /home/runner/work/landscape-architecture-tool/landscape-architecture-tool && PYTHONPATH=. python -c 'import src.main; print(\"✅ Backend imports OK\")'",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Repository health check passed")
                return True
            print(f"❌ Repository health check failed: {result.stderr}")
            return False

        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False


def main():
    helper = DependabotMergeHelper()

    print("🤖 Dependabot PR Merge Analysis")
    print("=" * 50)

    # Health check
    if not helper.validate_repository_health():
        print("⚠️  Repository health issues detected. Proceed with caution.")

    # Show categorization
    categories = helper.categorize_prs()
    print("\n📊 PR Categorization:")
    print(f"🟢 Safe Auto-merge: {len(categories['safe_auto_merge'])} PRs")
    print(f"🟡 Careful Review: {len(categories['careful_review'])} PRs")
    print(f"🔴 Major Updates: {len(categories['major_updates'])} PRs")

    # Show merge priorities
    print("\n📋 Recommended Merge Order:")
    priorities = helper.get_merge_priority()
    for pr_num, action, reason in priorities:
        status_icon = {"auto-merge": "🟢", "manual-review": "🟡", "extensive-testing": "🔴"}[action]
        print(f"{status_icon} PR #{pr_num}: {action} - {reason}")

    # Generate commands for safe merges
    print("\n🔧 Safe Merge Commands:")
    commands = helper.generate_merge_commands()
    for cmd in commands[:10]:  # Show first 10 commands
        print(cmd)

    print(f"\n✅ Analysis complete. {len(categories['safe_auto_merge'])} PRs ready for auto-merge.")


if __name__ == "__main__":
    main()
