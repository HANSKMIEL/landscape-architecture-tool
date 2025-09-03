#!/usr/bin/env python3
"""
GitHub Labels Setup Script for Dependabot Integration

This script helps create the required GitHub labels that Dependabot references
in .github/dependabot.yml. These labels are used to categorize dependency update PRs.

Usage:
    python scripts/setup_github_labels.py --help
    python scripts/setup_github_labels.py --dry-run
    python scripts/setup_github_labels.py --create

Note: This script requires the GitHub CLI (gh) to be installed and authenticated.
"""

import argparse
import json
import subprocess
import sys

# Labels required by dependabot.yml
REQUIRED_LABELS = [
    {
        "name": "dependencies",
        "description": "Updates to project dependencies",
        "color": "0366d6"  # Blue
    },
    {
        "name": "javascript", 
        "description": "JavaScript/Node.js related changes",
        "color": "f1e05a"  # Yellow
    },
    {
        "name": "python",
        "description": "Python related changes", 
        "color": "3572A5"  # Python blue
    },
    {
        "name": "security",
        "description": "Security related updates",
        "color": "d73a49"  # Red
    },
    {
        "name": "frontend",
        "description": "Frontend/UI related changes",
        "color": "7057ff"  # Purple  
    },
    {
        "name": "docker",
        "description": "Docker/containerization changes",
        "color": "0db7ed"  # Docker blue
    },
    {
        "name": "infrastructure", 
        "description": "Infrastructure and deployment changes",
        "color": "5319e7"  # Purple
    },
    {
        "name": "github-actions",
        "description": "GitHub Actions workflow changes", 
        "color": "2088ff"  # GitHub blue
    },
    {
        "name": "ci-cd",
        "description": "Continuous integration and deployment",
        "color": "28a745"  # Green
    }
]


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode == 0:
            print("✅ GitHub CLI is installed and authenticated")
            return True
        print("❌ GitHub CLI authentication failed")
        print(f"Error: {result.stderr}")
        return False
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) is not installed")
        print("Install it from: https://cli.github.com/")
        return False


def get_existing_labels() -> list[dict]:
    """Get existing labels from the GitHub repository."""
    try:
        result = subprocess.run(
            ["gh", "label", "list", "--json", "name,description,color"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch existing labels: {e}")
        return []


def create_label(label: dict) -> bool:
    """Create a single label in the GitHub repository."""
    try:
        cmd = [
            "gh", "label", "create", 
            label["name"],
            "--description", label["description"],
            "--color", label["color"]
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"✅ Created label: {label['name']}")
            return True
        if "already exists" in result.stderr:
            print(f"ℹ️  Label already exists: {label['name']}")
            return True
        print(f"❌ Failed to create label {label['name']}: {result.stderr}")
        return False
            
    except Exception as e:
        print(f"❌ Error creating label {label['name']}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Setup GitHub labels required for Dependabot integration"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what labels would be created without actually creating them"
    )
    parser.add_argument(
        "--create",
        action="store_true", 
        help="Create the missing labels"
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.create:
        parser.print_help()
        return 1
        
    print("🏷️  GitHub Labels Setup for Dependabot Integration")
    print("=" * 50)
    
    # Check prerequisites
    if not check_gh_cli():
        print("\n📋 Manual Setup Instructions:")
        print("1. Install GitHub CLI: https://cli.github.com/")
        print("2. Authenticate: gh auth login")
        print("3. Run this script again with --create")
        return 1
        
    # Get existing labels
    existing_labels = get_existing_labels()
    existing_names = {label["name"] for label in existing_labels}
    
    # Determine what needs to be created
    missing_labels = [
        label for label in REQUIRED_LABELS 
        if label["name"] not in existing_names
    ]
    
    print("\n📊 Label Status:")
    print(f"   Required: {len(REQUIRED_LABELS)}")
    print(f"   Existing: {len(REQUIRED_LABELS) - len(missing_labels)}")
    print(f"   Missing:  {len(missing_labels)}")
    
    if not missing_labels:
        print("\n✅ All required labels already exist!")
        return 0
        
    print("\n🏷️  Missing Labels:")
    for label in missing_labels:
        print(f"   - {label['name']}: {label['description']}")
        
    if args.dry_run:
        print(f"\n🔍 Dry run complete. Use --create to actually create {len(missing_labels)} missing labels.")
        return 0
        
    if args.create:
        print(f"\n🚀 Creating {len(missing_labels)} missing labels...")
        success_count = 0
        
        for label in missing_labels:
            if create_label(label):
                success_count += 1
                
        print("\n📊 Results:")
        print(f"   Successfully created: {success_count}/{len(missing_labels)} labels")
        
        if success_count == len(missing_labels):
            print("\n✅ All labels created successfully!")
            print("Dependabot should now be able to create PRs with proper labels.")
            return 0
        print("\n⚠️  Some labels failed to create. Check the errors above.")
        return 1
        
    # Should not reach here, but return error code for safety
    return 1


if __name__ == "__main__":
    sys.exit(main())