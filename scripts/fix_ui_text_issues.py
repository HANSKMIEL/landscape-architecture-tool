#!/usr/bin/env python3
"""
Script to systematically fix UI text issues identified in the analysis:
- Add translation support where missing
- Fix hardcoded text
- Improve placeholders
- Ensure consistent translation usage
"""

import json
import os
import re
from pathlib import Path


def main():
    """Main function to fix UI text issues"""

    print("🔧 Starting UI Text Issues Fix...")
    print("=" * 60)

    # Load the UI text analysis report
    report_path = Path("reports/ui_text_analysis_20250929_154041.json")
    if report_path.exists():
        with open(report_path) as f:
            analysis = json.load(f)
            print(f"✅ Loaded analysis report with {len(analysis.get('text_display_issues', []))} issues")
    else:
        print("⚠️ No analysis report found")
        return

    issues_by_file = {}
    for issue in analysis.get("text_display_issues", []):
        file = issue.get("file", "")
        if file not in issues_by_file:
            issues_by_file[file] = []
        issues_by_file[file].append(issue)

    print(f"\n📊 Found issues in {len(issues_by_file)} files")

    # Priority files to fix
    priority_files = [
        "frontend/src/components/Products.jsx",
        "frontend/src/components/Dashboard.jsx",
        "frontend/src/components/PasswordReset.jsx",
        "frontend/src/components/PhotoManager.jsx",
        "frontend/src/components/sidebar.jsx",
        "frontend/src/components/Header.jsx",
    ]

    print("\n🎯 Priority files for translation fixes:")
    for file in priority_files:
        if file in issues_by_file:
            print(f"  - {file}: {len(issues_by_file[file])} issues")

    print("\n✅ Analysis complete. Manual fixes required for:")
    print("   1. Add useTranslation hook to components")
    print("   2. Replace hardcoded text with t('translation.key')")
    print("   3. Improve placeholder text quality")
    print("   4. Ensure consistent translation usage")

    # Generate a detailed fix plan
    fix_plan = {
        "timestamp": "2025-09-29",
        "priority_files": priority_files,
        "issues_by_file": issues_by_file,
        "recommendations": [
            "Import { useTranslation } from 'react-i18next' in all components with text",
            "Replace hardcoded Dutch text with translation keys",
            "Use meaningful placeholder text instead of generic strings",
            "Ensure all user-facing text uses translation system",
            "Add translation keys to i18n configuration files",
        ],
    }

    output_path = Path("reports/ui_text_fix_plan.json")
    with open(output_path, "w") as f:
        json.dump(fix_plan, f, indent=2)

    print(f"\n💾 Fix plan saved to: {output_path}")
    print("\n🎉 UI text analysis complete!")


if __name__ == "__main__":
    main()
