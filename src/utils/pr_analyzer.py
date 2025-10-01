#!/usr/bin/env python3
"""
Pull Request Analyzer for Dynamic Validation Reports

This module provides dynamic PR counting and categorization for validation reports,
replacing hardcoded values with real-time calculated data.
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


@dataclass
class PRInfo:
    """Information about a single pull request."""

    number: int
    title: str
    state: str
    labels: list[str]
    created_at: str
    updated_at: str
    author: str
    is_draft: bool
    mergeable_state: str

    def is_dependabot(self) -> bool:
        """Check if this PR is from Dependabot."""
        return self.author in ["dependabot[bot]", "dependabot"]

    def has_label(self, label: str) -> bool:
        """Check if this PR has a specific label."""
        return label in self.labels

    def get_update_type(self) -> str:
        """Determine update type from PR title (patch/minor/major)."""
        # Pattern to match Dependabot PR titles: "bump package from x.y.z to a.b.c"
        pattern = r"bump .+ from ([\d.]+) to ([\d.]+)"
        match = re.search(pattern, self.title, re.IGNORECASE)

        if match:
            from_version, to_version = match.groups()
            try:
                from_parts = [int(x) for x in from_version.split(".")]
                to_parts = [int(x) for x in to_version.split(".")]

                # Compare semantic version parts
                if len(from_parts) >= 1 and len(to_parts) >= 1:
                    if from_parts[0] != to_parts[0]:
                        return "major"
                    if len(from_parts) >= 2 and len(to_parts) >= 2 and from_parts[1] != to_parts[1]:
                        return "minor"
                    return "patch"
            except ValueError:
                pass

        return "unknown"

    def is_security_update(self) -> bool:
        """Check if this is a security-related update."""
        security_indicators = ["security", "vulnerability", "cve"]
        title_lower = self.title.lower()

        # Check title and labels for security indicators
        return any(indicator in title_lower for indicator in security_indicators) or any(
            indicator in label.lower() for label in self.labels for indicator in security_indicators
        )


class PRAnalyzer:
    """Analyzes pull requests for validation reporting."""

    def __init__(self, github_token: str | None = None, owner: str | None = None, repo: str | None = None):
        """
        Initialize PR analyzer.

        Args:
            github_token: GitHub API token (optional, can use env var GITHUB_TOKEN)
            owner: Repository owner (defaults to HANSKMIEL, can use env var GITHUB_OWNER)
            repo: Repository name (defaults to landscape-architecture-tool, can use env var GITHUB_REPO)
        """
        self.owner = owner or os.getenv("GITHUB_OWNER", "HANSKMIEL")
        self.repo = repo or os.getenv("GITHUB_REPO", "landscape-architecture-tool")
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        # Default categorization rules
        self.critical_dependencies = [
            "flask",
            "django",
            "react",
            "express",
            "webpack",
            "babel",
            "typescript",
            "eslint",
            "pytest",
            "requests",
            "sqlalchemy",
            "alembic",
            "gunicorn",
            "redis",
            "psycopg2",
        ]

    def get_headers(self) -> dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "landscape-architecture-tool-pr-analyzer",
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    def fetch_pull_requests(self, state: str = "open", per_page: int = 100) -> list[PRInfo]:
        """
        Fetch pull requests from GitHub API.

        Args:
            state: PR state ('open', 'closed', 'all')
            per_page: Number of PRs per page (max 100)

        Returns:
            List of PRInfo objects
        """
        prs = []
        page = 1

        while True:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls"
            params = {
                "state": state,
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc",
            }

            try:
                response = requests.get(url, headers=self.get_headers(), params=params, timeout=60)
                response.raise_for_status()
                data = response.json()

                if not data:  # No more PRs
                    break

                for pr_data in data:
                    pr_info = PRInfo(
                        number=pr_data["number"],
                        title=pr_data["title"],
                        state=pr_data["state"],
                        labels=[label["name"] for label in pr_data.get("labels", [])],
                        created_at=pr_data["created_at"],
                        updated_at=pr_data["updated_at"],
                        author=pr_data["user"]["login"],
                        is_draft=pr_data.get("draft", False),
                        mergeable_state=pr_data.get("mergeable_state", "unknown"),
                    )
                    prs.append(pr_info)

                page += 1

            except requests.RequestException as e:
                logger.error(f"Failed to fetch PRs: {e}")
                break

        return prs

    def categorize_dependabot_prs(self, prs: list[PRInfo]) -> dict[str, list[PRInfo]]:
        """
        Categorize Dependabot PRs by safety level.

        Args:
            prs: List of PRInfo objects

        Returns:
            Dictionary with categorized PRs
        """
        dependabot_prs = [pr for pr in prs if pr.is_dependabot()]

        safe_auto_merge = []
        manual_review = []
        major_updates = []

        for pr in dependabot_prs:
            update_type = pr.get_update_type()

            # Check if it contains critical dependencies
            has_critical_dep = any(dep.lower() in pr.title.lower() for dep in self.critical_dependencies)

            if has_critical_dep:
                manual_review.append(pr)
            elif update_type == "major":
                major_updates.append(pr)
            elif pr.is_security_update():
                # Security updates: auto-merge if patch/minor, manual if major
                if update_type in ["patch", "minor"]:
                    safe_auto_merge.append(pr)
                else:
                    manual_review.append(pr)
            elif update_type in ["patch", "minor"]:
                safe_auto_merge.append(pr)
            else:
                manual_review.append(pr)

        return {
            "safe_auto_merge": safe_auto_merge,
            "manual_review": manual_review,
            "major_updates": major_updates,
        }

    def generate_pr_counts(
        self,
        categorized_prs: dict[str, list[PRInfo]] | None = None,
        all_prs: list[PRInfo] | None = None,
    ) -> dict[str, Any]:
        """
        Generate PR count statistics.

        Args:
            categorized_prs: Pre-categorized PRs (optional, will fetch if not provided)
            all_prs: All PRs for context (optional, will fetch if not provided)

        Returns:
            Dictionary with PR count statistics
        """
        if categorized_prs is None or all_prs is None:
            all_prs = self.fetch_pull_requests()
            categorized_prs = self.categorize_dependabot_prs(all_prs)

        safe_count = len(categorized_prs["safe_auto_merge"])
        manual_count = len(categorized_prs["manual_review"])
        major_count = len(categorized_prs["major_updates"])

        # Additional statistics
        total_dependabot = safe_count + manual_count + major_count
        total_open_prs = len(all_prs)
        non_dependabot_prs = total_open_prs - total_dependabot

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_open_prs": total_open_prs,
            "dependabot_prs": {
                "total": total_dependabot,
                "safe_auto_merge": safe_count,
                "manual_review_required": manual_count,
                "major_updates_requiring_testing": major_count,
            },
            "non_dependabot_prs": non_dependabot_prs,
            "pr_numbers": {
                "safe_auto_merge": [pr.number for pr in categorized_prs["safe_auto_merge"]],
                "manual_review": [pr.number for pr in categorized_prs["manual_review"]],
                "major_updates": [pr.number for pr in categorized_prs["major_updates"]],
            },
        }

    def generate_validation_report(
        self,
        backend_status: str = "unknown",
        frontend_status: str = "unknown",
        database_status: str = "unknown",
        security_status: str = "unknown",
        additional_data: dict | None = None,
    ) -> dict[str, Any]:
        """
        Generate a comprehensive validation report with dynamic PR counts.

        Args:
            backend_status: Backend validation status
            frontend_status: Frontend validation status
            database_status: Database validation status
            security_status: Security scan status
            additional_data: Additional data to include in report

        Returns:
            Complete validation report dictionary
        """
        pr_counts = self.generate_pr_counts()

        report = {
            "validation_timestamp": datetime.now(UTC).isoformat(),
            "validation_type": "dynamic_pr_analysis",
            "repository_status": (
                "functional"
                if all(
                    status in ["passed", "healthy", "functional"]
                    for status in [backend_status, frontend_status, database_status]
                )
                else "needs_attention"
            ),
            "component_status": {
                "backend_tests": backend_status,
                "frontend_build": frontend_status,
                "database_operations": database_status,
                "security_scan": security_status,
            },
            "pr_analysis": pr_counts,
            "next_steps": self._generate_next_steps(pr_counts),
            "validation_script": "src.utils.pr_analyzer",
        }

        if additional_data:
            report.update(additional_data)

        return report

    def _generate_next_steps(self, pr_counts: dict[str, Any]) -> list[str]:
        """Generate next steps based on PR analysis."""
        steps = []

        dependabot_data = pr_counts["dependabot_prs"]

        if dependabot_data["safe_auto_merge"] > 0:
            safe_prs = pr_counts["pr_numbers"]["safe_auto_merge"]
            steps.append(f"Auto-merge {dependabot_data['safe_auto_merge']} safe PRs: {safe_prs}")

        if dependabot_data["manual_review_required"] > 0:
            manual_prs = pr_counts["pr_numbers"]["manual_review"]
            steps.append(f"Manual review required for {dependabot_data['manual_review_required']} PRs: {manual_prs}")

        if dependabot_data["major_updates_requiring_testing"] > 0:
            major_prs = pr_counts["pr_numbers"]["major_updates"]
            steps.append(
                f"Extensive testing needed for {dependabot_data['major_updates_requiring_testing']} major updates: {major_prs}"
            )

        if pr_counts["non_dependabot_prs"] > 0:
            steps.append(f"Review {pr_counts['non_dependabot_prs']} non-Dependabot PRs separately")

        return steps


def create_validation_report(
    backend_status: str = "unknown",
    frontend_status: str = "unknown",
    database_status: str = "unknown",
    security_status: str = "unknown",
    output_file: str | None = None,
    github_token: str | None = None,
) -> dict[str, Any]:
    """
    Convenience function to create a validation report with dynamic PR counts.

    Args:
        backend_status: Backend test status
        frontend_status: Frontend build status
        database_status: Database operation status
        security_status: Security scan status
        output_file: Optional file path to save the report
        github_token: GitHub API token

    Returns:
        Generated validation report
    """
    analyzer = PRAnalyzer(github_token=github_token)
    report = analyzer.generate_validation_report(
        backend_status=backend_status,
        frontend_status=frontend_status,
        database_status=database_status,
        security_status=security_status,
    )

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Validation report saved to {output_file}")

    return report


if __name__ == "__main__":
    # CLI usage example
    import argparse

    parser = argparse.ArgumentParser(description="Generate dynamic PR validation report")
    parser.add_argument("--backend", default="unknown", help="Backend status")
    parser.add_argument("--frontend", default="unknown", help="Frontend status")
    parser.add_argument("--database", default="unknown", help="Database status")
    parser.add_argument("--security", default="unknown", help="Security status")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--token", help="GitHub API token")

    args = parser.parse_args()

    report = create_validation_report(
        backend_status=args.backend,
        frontend_status=args.frontend,
        database_status=args.database,
        security_status=args.security,
        output_file=args.output,
        github_token=args.token,
    )

    print(json.dumps(report, indent=2))
