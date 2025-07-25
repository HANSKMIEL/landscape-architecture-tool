#!/usr/bin/env python3
"""
Development Log Update Script
Automatically appends formatted log entries to dev_log.md
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Optional


class DevLogUpdater:
    """Handles updating the development log with new entries"""
    
    def __init__(self, log_file_path: str = "dev_log.md"):
        self.log_file_path = log_file_path
        self.categories = ["FEATURE", "BUGFIX", "TESTING", "DOCUMENTATION", "DEPLOYMENT"]
        self.test_statuses = ["PASSED", "FAILED", "PENDING", "N/A"]
        
    def validate_category(self, category: str) -> bool:
        """Validate that category is one of the allowed values"""
        return category.upper() in self.categories
    
    def validate_test_status(self, status: str) -> bool:
        """Validate that test status is one of the allowed values"""
        return status.upper() in self.test_statuses
    
    def format_log_entry(self, 
                        category: str, 
                        description: str,
                        phase: Optional[int] = None,
                        test_status: str = "N/A",
                        notes: Optional[str] = None) -> str:
        """Format a log entry according to the standard format"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"""
### {timestamp}
- **Category**: {category.upper()}"""
        
        if phase:
            entry += f"\n- **Phase**: {phase}"
        else:
            entry += f"\n- **Phase**: N/A"
            
        entry += f"""
- **Description**: {description}
- **Testing Status**: {test_status.upper()}"""
        
        if notes:
            entry += f"\n- **Notes**: {notes}"
        else:
            entry += f"\n- **Notes**: -"
            
        return entry
    
    def add_entry(self, 
                  category: str, 
                  description: str,
                  phase: Optional[int] = None,
                  test_status: str = "N/A",
                  notes: Optional[str] = None) -> bool:
        """Add a new entry to the development log"""
        
        # Validate inputs
        if not self.validate_category(category):
            print(f"Error: Invalid category '{category}'. Must be one of: {', '.join(self.categories)}")
            return False
            
        if not self.validate_test_status(test_status):
            print(f"Error: Invalid test status '{test_status}'. Must be one of: {', '.join(self.test_statuses)}")
            return False
        
        # Create the log file if it doesn't exist
        if not os.path.exists(self.log_file_path):
            print(f"Warning: {self.log_file_path} not found. Creating new log file.")
            self._create_initial_log_file()
        
        # Format the new entry
        new_entry = self.format_log_entry(category, description, phase, test_status, notes)
        
        try:
            # Read the current log file
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the position to insert the new entry (after "## Development Entries")
            entries_section = "## Development Entries"
            if entries_section not in content:
                print(f"Error: Could not find '{entries_section}' section in log file")
                return False
            
            # Insert the new entry at the beginning of the entries section
            insertion_point = content.find(entries_section) + len(entries_section)
            new_content = content[:insertion_point] + new_entry + content[insertion_point:]
            
            # Write the updated content back to the file
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Successfully added log entry to {self.log_file_path}")
            print(f"  Category: {category.upper()}")
            print(f"  Description: {description}")
            if phase:
                print(f"  Phase: {phase}")
            print(f"  Testing Status: {test_status.upper()}")
            
            return True
            
        except Exception as e:
            print(f"Error updating log file: {e}")
            return False
    
    def _create_initial_log_file(self):
        """Create an initial log file if one doesn't exist"""
        initial_content = """# Development Log - Landscape Architecture Management Tool

## Purpose
This log tracks major development updates, milestones, and testing results for the Landscape Architecture Management Tool project.

## Log Format
Each entry follows this format:
- **Date**: [YYYY-MM-DD HH:MM:SS]
- **Category**: [FEATURE | BUGFIX | TESTING | DOCUMENTATION | DEPLOYMENT]
- **Phase**: [Phase number from roadmap]
- **Description**: [Detailed description of work]
- **Testing Status**: [PASSED | FAILED | PENDING | N/A]
- **Notes**: [Additional context, blockers, next steps]

---

## Development Entries

---

*This log is automatically updated using the update_dev_log.py script*"""
        
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    
    def add_milestone(self, title: str, completion: int, achievements: str, next_steps: str) -> bool:
        """Add a milestone entry to the log"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        milestone_entry = f"""
### {title}
- **Date**: {timestamp}
- **Completion**: {completion}%
- **Key Achievements**: {achievements}
- **Next Steps**: {next_steps}"""
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find milestones section
            milestones_section = "## Milestones"
            if milestones_section not in content:
                print(f"Error: Could not find '{milestones_section}' section in log file")
                return False
            
            # Insert after the milestones header
            insertion_point = content.find(milestones_section) + len(milestones_section)
            new_content = content[:insertion_point] + milestone_entry + content[insertion_point:]
            
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✓ Successfully added milestone '{title}' to {self.log_file_path}")
            return True
            
        except Exception as e:
            print(f"Error adding milestone: {e}")
            return False


def main():
    """Main CLI interface for the development log updater"""
    parser = argparse.ArgumentParser(
        description="Update the development log with new entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_dev_log.py -c FEATURE -d "Added user authentication" -p 1 -t PASSED
  python update_dev_log.py -c BUGFIX -d "Fixed database connection issue" -n "Required restart"
  python update_dev_log.py --milestone "Phase 1 Complete" -comp 100 -a "All core features implemented"
        """
    )
    
    # Regular log entry arguments
    parser.add_argument("-c", "--category", 
                       choices=["FEATURE", "BUGFIX", "TESTING", "DOCUMENTATION", "DEPLOYMENT"],
                       help="Category of the log entry")
    parser.add_argument("-d", "--description", 
                       help="Description of the work completed")
    parser.add_argument("-p", "--phase", 
                       type=int, 
                       help="Development phase number (1-5)")
    parser.add_argument("-t", "--test-status", 
                       choices=["PASSED", "FAILED", "PENDING", "N/A"],
                       default="N/A",
                       help="Testing status (default: N/A)")
    parser.add_argument("-n", "--notes", 
                       help="Additional notes or context")
    
    # Milestone arguments
    parser.add_argument("--milestone", 
                       help="Add a milestone entry with the given title")
    parser.add_argument("-comp", "--completion", 
                       type=int, 
                       help="Completion percentage for milestone")
    parser.add_argument("-a", "--achievements", 
                       help="Key achievements for milestone")
    parser.add_argument("--next-steps", 
                       help="Next steps for milestone")
    
    # File path argument
    parser.add_argument("-f", "--file", 
                       default="dev_log.md",
                       help="Path to the log file (default: dev_log.md)")
    
    args = parser.parse_args()
    
    # Create updater instance
    updater = DevLogUpdater(args.file)
    
    # Handle milestone addition
    if args.milestone:
        if not all([args.completion is not None, args.achievements]):
            print("Error: Milestone entries require --completion and --achievements")
            sys.exit(1)
        
        next_steps = args.next_steps or "To be determined"
        success = updater.add_milestone(args.milestone, args.completion, 
                                      args.achievements, next_steps)
        sys.exit(0 if success else 1)
    
    # Handle regular log entry
    if not all([args.category, args.description]):
        print("Error: Regular entries require --category and --description")
        parser.print_help()
        sys.exit(1)
    
    success = updater.add_entry(
        category=args.category,
        description=args.description,
        phase=args.phase,
        test_status=args.test_status,
        notes=args.notes
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()