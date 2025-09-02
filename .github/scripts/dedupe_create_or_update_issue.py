#!/usr/bin/env python3
"""
Deduplicated create-or-update issue utility for GitHub Actions.

Searches for existing open issues containing a fingerprint tag, and either
comments on the existing issue or creates a new one. Caps creation to 1 per run.
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from issue_fingerprint import generate_fingerprint, create_fingerprint_tag, extract_fingerprint_from_body


class IssueManager:
    """Manages deduplicated issue creation and updates."""
    
    def __init__(self, github_client, owner: str, repo: str):
        """
        Initialize the issue manager.
        
        Args:
            github_client: GitHub API client (from actions/github-script)
            owner: Repository owner
            repo: Repository name
        """
        self.github = github_client
        self.owner = owner
        self.repo = repo
        self.issues_created_this_run = 0
        self.max_issues_per_run = 1
    
    async def find_existing_issue(self, fingerprint: str, labels: list = None) -> dict:
        """
        Find an existing open issue with the given fingerprint.
        
        Args:
            fingerprint: The fingerprint to search for
            labels: Optional list of labels to filter by
            
        Returns:
            Issue data if found, None otherwise
        """
        # Search open issues - look for fingerprint in body
        search_params = {
            'owner': self.owner,
            'repo': self.repo,
            'state': 'open',
            'per_page': 100  # Should be enough for most repositories
        }
        
        if labels:
            search_params['labels'] = ','.join(labels)
        
        try:
            issues_response = await self.github.rest.issues.listForRepo(search_params)
            issues = issues_response.data
            
            for issue in issues:
                if issue.body and f"FINGERPRINT:{fingerprint}" in issue.body:
                    return issue
                    
        except Exception as e:
            print(f"Error searching for existing issues: {e}")
        
        return None
    
    async def create_or_update_issue(self, 
                                   title: str,
                                   body: str,
                                   labels: list,
                                   fingerprint: str,
                                   assignees: list = None,
                                   update_strategy: str = "append") -> dict:
        """
        Create a new issue or update an existing one with the same fingerprint.
        
        Args:
            title: Issue title
            body: Issue body content
            labels: List of labels to apply
            fingerprint: Unique fingerprint for deduplication
            assignees: Optional list of assignees
            update_strategy: How to handle updates ("append", "replace", "prepend")
            
        Returns:
            Dictionary with operation result and issue data
        """
        # Add fingerprint tag to body
        fingerprint_tag = create_fingerprint_tag(fingerprint)
        body_with_fingerprint = f"{body}\n\n{fingerprint_tag}"
        
        # Look for existing issue
        existing_issue = await self.find_existing_issue(fingerprint, labels)
        
        if existing_issue:
            # Update existing issue
            result = await self._update_existing_issue(
                existing_issue, title, body_with_fingerprint, labels, assignees, update_strategy
            )
            return {
                'action': 'updated',
                'issue': result,
                'issue_number': existing_issue['number'],
                'fingerprint': fingerprint
            }
        else:
            # Create new issue (if under limit)
            if self.issues_created_this_run >= self.max_issues_per_run:
                return {
                    'action': 'skipped',
                    'reason': f'Issue creation limit reached ({self.max_issues_per_run} per run)',
                    'fingerprint': fingerprint
                }
            
            result = await self._create_new_issue(
                title, body_with_fingerprint, labels, assignees
            )
            self.issues_created_this_run += 1
            
            return {
                'action': 'created',
                'issue': result,
                'issue_number': result['number'],
                'fingerprint': fingerprint
            }
    
    async def _create_new_issue(self, title: str, body: str, labels: list, assignees: list = None) -> dict:
        """Create a new issue."""
        issue_data = {
            'owner': self.owner,
            'repo': self.repo,
            'title': title,
            'body': body,
            'labels': labels or []
        }
        
        if assignees:
            issue_data['assignees'] = assignees
        
        try:
            response = await self.github.rest.issues.create(issue_data)
            return response.data
        except Exception as e:
            raise Exception(f"Failed to create issue: {e}")
    
    async def _update_existing_issue(self, 
                                   existing_issue: dict,
                                   title: str,
                                   body: str,
                                   labels: list,
                                   assignees: list = None,
                                   update_strategy: str = "append") -> dict:
        """Update an existing issue."""
        issue_number = existing_issue['number']
        
        # Determine update approach
        if update_strategy == "replace":
            # Replace entire body
            new_body = body
        elif update_strategy == "prepend":
            # Add new content at the beginning
            separator = "\n\n---\n**🔄 UPDATE** *(automated)*:\n\n"
            new_body = body + separator + existing_issue['body']
        else:  # append (default)
            # Add new content as a comment instead of modifying body
            await self._add_update_comment(issue_number, title, body)
            return existing_issue
        
        # Update the issue
        update_data = {
            'owner': self.owner,
            'repo': self.repo,
            'issue_number': issue_number,
            'title': title,
            'body': new_body,
            'labels': labels or []
        }
        
        if assignees:
            update_data['assignees'] = assignees
        
        try:
            response = await self.github.rest.issues.update(update_data)
            return response.data
        except Exception as e:
            raise Exception(f"Failed to update issue #{issue_number}: {e}")
    
    async def _add_update_comment(self, issue_number: int, title: str, body: str):
        """Add an update comment to an existing issue."""
        comment_body = [
            f"## 🔄 Automated Update",
            f"",
            f"**Update Time:** {self._get_current_timestamp()}",
            f"**Updated Title:** {title}",
            f"",
            f"{body}",
            f"",
            f"---",
            f"*This update was automatically generated to avoid duplicate issues.*"
        ]
        
        try:
            await self.github.rest.issues.createComment({
                'owner': self.owner,
                'repo': self.repo,
                'issue_number': issue_number,
                'body': '\n'.join(comment_body)
            })
        except Exception as e:
            print(f"Warning: Failed to add update comment to issue #{issue_number}: {e}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


# Convenience function for use in GitHub Actions
async def create_or_update_automated_issue(github_client,
                                         owner: str,
                                         repo: str,
                                         payload: dict,
                                         category: str,
                                         title: str,
                                         body: str,
                                         labels: list,
                                         assignees: list = None,
                                         update_strategy: str = "append") -> dict:
    """
    Convenience function to create or update an automated issue with fingerprinting.
    
    Args:
        github_client: GitHub API client
        owner: Repository owner
        repo: Repository name
        payload: Data to generate fingerprint from
        category: Category for fingerprint scoping
        title: Issue title
        body: Issue body
        labels: Issue labels
        assignees: Optional assignees
        update_strategy: How to handle updates
        
    Returns:
        Operation result dictionary
    """
    # Generate fingerprint from payload
    fingerprint = generate_fingerprint(payload, category)
    
    # Create issue manager and process
    manager = IssueManager(github_client, owner, repo)
    result = await manager.create_or_update_issue(
        title=title,
        body=body,
        labels=labels,
        fingerprint=fingerprint,
        assignees=assignees,
        update_strategy=update_strategy
    )
    
    return result


if __name__ == "__main__":
    # Example usage for testing
    print("Issue deduplication utility loaded successfully")
    print("Use create_or_update_automated_issue() in GitHub Actions workflows")