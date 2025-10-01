#!/usr/bin/env python3
"""
UI Text Display Analysis
Analyzes all UI components for text display issues, input field problems, and functionality
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path


class UITextAnalyzer:
    def __init__(self):
        self.repo_path = Path(__file__).parent.parent
        self.frontend_path = self.repo_path / "frontend" / "src"
        self.components_path = self.frontend_path / "components"

        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "text_display_issues": [],
            "input_field_issues": [],
            "translation_issues": [],
            "ui_functionality_issues": [],
            "recommendations": [],
        }

    def analyze_component_file(self, file_path):
        """Analyze a single component file for text and input issues"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            relative_path = file_path.relative_to(self.repo_path)
            component_issues = {
                "file": str(relative_path),
                "text_issues": [],
                "input_issues": [],
                "translation_issues": [],
                "functionality_issues": [],
            }

            # Check for text display issues
            self._check_text_display_issues(content, component_issues)

            # Check for input field issues
            self._check_input_field_issues(content, component_issues)

            # Check for translation issues
            self._check_translation_issues(content, component_issues)

            # Check for functionality issues
            self._check_functionality_issues(content, component_issues)

            return component_issues

        except Exception as e:
            return {"file": str(file_path), "error": f"Could not analyze file: {e!s}"}

    def _check_text_display_issues(self, content, component_issues):
        """Check for text display issues"""

        # Check for hardcoded text that should be translatable
        hardcoded_text_patterns = [
            r'"[A-Z][a-zA-Z\s]{10,}"',  # Long hardcoded strings
            r"'[A-Z][a-zA-Z\s]{10,}'",  # Long hardcoded strings with single quotes
        ]

        for pattern in hardcoded_text_patterns:
            matches = re.findall(pattern, content)
            if matches:
                component_issues["text_issues"].append(
                    {
                        "type": "hardcoded_text",
                        "description": "Long hardcoded text found - should use translation system",
                        "examples": matches[:3],  # First 3 examples
                    }
                )

        # Check for missing translation function usage
        if "t(" in content or "useTranslation" in content:
            # Good - using translation system
            pass
        else:
            # Check if component has translatable text
            text_content = re.findall(r">[^<]{5,}<", content)
            if text_content:
                component_issues["text_issues"].append(
                    {
                        "type": "missing_translation",
                        "description": "Component contains text but doesn't use translation system",
                        "suggestion": "Import and use useTranslation hook",
                    }
                )

        # Check for placeholder text issues
        placeholder_patterns = [
            r'placeholder\s*=\s*["\'][^"\']{1,3}["\']',  # Very short placeholders
            r'placeholder\s*=\s*["\']TODO["\']',  # TODO placeholders
            r'placeholder\s*=\s*["\'].*\.\.\.["\']',  # Incomplete placeholders
        ]

        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content)
            if matches:
                component_issues["text_issues"].append(
                    {
                        "type": "poor_placeholder",
                        "description": "Poor or incomplete placeholder text",
                        "examples": matches,
                    }
                )

    def _check_input_field_issues(self, content, component_issues):
        """Check for input field issues"""

        # Check for input fields without proper labels
        input_pattern = r"<input[^>]*>"
        inputs = re.findall(input_pattern, content)

        for input_tag in inputs:
            # Check if input has id but no corresponding label
            if "id=" in input_tag:
                id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', input_tag)
                if id_match:
                    input_id = id_match.group(1)
                    label_pattern = f"htmlFor=[\"']?{input_id}[\"']?"
                    if not re.search(label_pattern, content):
                        component_issues["input_issues"].append(
                            {
                                "type": "missing_label",
                                "description": f"Input field with id '{input_id}' has no corresponding label",
                                "accessibility_impact": "HIGH",
                            }
                        )

            # Check for inputs without validation
            if "required" not in input_tag and "validation" not in input_tag:
                component_issues["input_issues"].append(
                    {
                        "type": "missing_validation",
                        "description": "Input field appears to lack validation",
                        "input": input_tag[:100] + "..." if len(input_tag) > 100 else input_tag,
                    }
                )

        # Check for form submission without proper handling
        if "<form" in content:
            if "onSubmit" not in content and "handleSubmit" not in content:
                component_issues["input_issues"].append(
                    {
                        "type": "unhandled_form",
                        "description": "Form found without proper submit handler",
                        "functionality_impact": "HIGH",
                    }
                )

    def _check_translation_issues(self, content, component_issues):
        """Check for translation system issues"""

        # Check for disabled translation variables
        disabled_t_patterns = [
            r"const\s+_t\s*=",
            r"const\s+{[^}]*_t[^}]*}\s*=",
            r"_t\(",
        ]

        for pattern in disabled_t_patterns:
            if re.search(pattern, content):
                component_issues["translation_issues"].append(
                    {
                        "type": "disabled_translation",
                        "description": "Translation function appears to be disabled (prefixed with _)",
                        "impact": "Users may see untranslated text",
                    }
                )

        # Check for mixed translation usage
        if "t(" in content and '"' in content:
            # Both translation and hardcoded text present
            hardcoded_count = len(re.findall(r'"[A-Za-z\s]{5,}"', content))
            if hardcoded_count > 2:
                component_issues["translation_issues"].append(
                    {
                        "type": "mixed_translation",
                        "description": "Component mixes translation system with hardcoded text",
                        "recommendation": "Consistently use translation system",
                    }
                )

    def _check_functionality_issues(self, content, component_issues):
        """Check for functionality issues"""

        # Check for disabled state variables
        disabled_state_patterns = [
            r"const\s+\[_[a-zA-Z]+,\s*_set[a-zA-Z]+\]",
            r"useState\([^)]*\)\s*//.*disabled",
        ]

        for pattern in disabled_state_patterns:
            matches = re.findall(pattern, content)
            if matches:
                component_issues["functionality_issues"].append(
                    {
                        "type": "disabled_state",
                        "description": "State variables appear to be disabled",
                        "examples": matches,
                        "impact": "Functionality may be broken",
                    }
                )

        # Check for commented out functionality
        commented_patterns = [
            r"//\s*(TODO|FIXME|BUG)",
            r"/\*.*?(TODO|FIXME|BUG).*?\*/",
        ]

        for pattern in commented_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                component_issues["functionality_issues"].append(
                    {
                        "type": "incomplete_functionality",
                        "description": "Code contains TODO/FIXME/BUG comments",
                        "count": len(matches),
                    }
                )

        # Check for error boundaries
        if "try" in content and "catch" in content:
            # Good - has error handling
            pass
        elif "useState" in content or "useEffect" in content:
            # Component has state but no error handling
            component_issues["functionality_issues"].append(
                {
                    "type": "missing_error_handling",
                    "description": "Component has state management but lacks error handling",
                    "recommendation": "Add try-catch blocks and error boundaries",
                }
            )

    def analyze_all_components(self):
        """Analyze all UI components"""

        component_files = []

        # Find all .jsx and .js files in components directory
        for file_path in self.components_path.rglob("*.jsx"):
            if "__tests__" not in str(file_path):
                component_files.append(file_path)

        for file_path in self.components_path.rglob("*.js"):
            if "__tests__" not in str(file_path):
                component_files.append(file_path)

        print(f"🔍 Analyzing {len(component_files)} UI component files...")

        all_issues = []

        for file_path in component_files:
            print(f"  Analyzing {file_path.name}...")
            component_analysis = self.analyze_component_file(file_path)

            # Collect issues by type
            if component_analysis.get("text_issues"):
                self.analysis_results["text_display_issues"].extend(
                    [
                        {**issue, "file": component_analysis["file"]}
                        for issue in component_analysis["text_issues"]
                    ]
                )

            if component_analysis.get("input_issues"):
                self.analysis_results["input_field_issues"].extend(
                    [
                        {**issue, "file": component_analysis["file"]}
                        for issue in component_analysis["input_issues"]
                    ]
                )

            if component_analysis.get("translation_issues"):
                self.analysis_results["translation_issues"].extend(
                    [
                        {**issue, "file": component_analysis["file"]}
                        for issue in component_analysis["translation_issues"]
                    ]
                )

            if component_analysis.get("functionality_issues"):
                self.analysis_results["ui_functionality_issues"].extend(
                    [
                        {**issue, "file": component_analysis["file"]}
                        for issue in component_analysis["functionality_issues"]
                    ]
                )

            all_issues.append(component_analysis)

        return all_issues

    def generate_recommendations(self):
        """Generate recommendations for fixing issues"""

        recommendations = []

        # Text display recommendations
        if self.analysis_results["text_display_issues"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Text Display",
                    "action": "Implement Consistent Translation System",
                    "description": "Fix hardcoded text and ensure all components use translation system",
                    "affected_files": len(
                        set(issue["file"] for issue in self.analysis_results["text_display_issues"])
                    ),
                }
            )

        # Input field recommendations
        if self.analysis_results["input_field_issues"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Input Fields",
                    "action": "Fix Input Field Accessibility and Validation",
                    "description": "Add proper labels, validation, and form handling to all input fields",
                    "affected_files": len(
                        set(issue["file"] for issue in self.analysis_results["input_field_issues"])
                    ),
                }
            )

        # Translation recommendations
        if self.analysis_results["translation_issues"]:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Translation",
                    "action": "Restore and Standardize Translation Usage",
                    "description": "Fix disabled translation functions and standardize translation usage",
                    "affected_files": len(
                        set(issue["file"] for issue in self.analysis_results["translation_issues"])
                    ),
                }
            )

        # Functionality recommendations
        if self.analysis_results["ui_functionality_issues"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Functionality",
                    "action": "Restore Disabled Functionality and Add Error Handling",
                    "description": "Fix disabled state variables and add proper error handling",
                    "affected_files": len(
                        set(
                            issue["file"]
                            for issue in self.analysis_results["ui_functionality_issues"]
                        )
                    ),
                }
            )

        self.analysis_results["recommendations"] = recommendations
        return recommendations

    def generate_report(self):
        """Generate comprehensive UI analysis report"""

        print("🎨 UI TEXT AND FUNCTIONALITY ANALYSIS REPORT")
        print("=" * 70)
        print(f"Generated: {self.analysis_results['timestamp']}")
        print()

        # Analyze components
        self.analyze_all_components()

        # Text Display Issues
        print("📝 TEXT DISPLAY ISSUES")
        print("-" * 40)
        text_issues = self.analysis_results["text_display_issues"]
        if text_issues:
            for issue in text_issues:
                print(f"• {issue['file']}: {issue['type']}")
                print(f"  {issue['description']}")
                if "examples" in issue:
                    print(f"  Examples: {', '.join(issue['examples'][:2])}")
                print()
        else:
            print("✅ No critical text display issues found")

        # Input Field Issues
        print("📋 INPUT FIELD ISSUES")
        print("-" * 40)
        input_issues = self.analysis_results["input_field_issues"]
        if input_issues:
            for issue in input_issues:
                impact_emoji = "🔴" if issue.get("accessibility_impact") == "HIGH" else "🟡"
                print(f"{impact_emoji} {issue['file']}: {issue['type']}")
                print(f"  {issue['description']}")
                print()
        else:
            print("✅ No critical input field issues found")

        # Translation Issues
        print("🌐 TRANSLATION ISSUES")
        print("-" * 40)
        translation_issues = self.analysis_results["translation_issues"]
        if translation_issues:
            for issue in translation_issues:
                print(f"⚠️ {issue['file']}: {issue['type']}")
                print(f"  {issue['description']}")
                print(f"  Impact: {issue.get('impact', 'Unknown')}")
                print()
        else:
            print("✅ No translation issues found")

        # Functionality Issues
        print("⚙️ FUNCTIONALITY ISSUES")
        print("-" * 40)
        functionality_issues = self.analysis_results["ui_functionality_issues"]
        if functionality_issues:
            for issue in functionality_issues:
                print(f"🔧 {issue['file']}: {issue['type']}")
                print(f"  {issue['description']}")
                if "impact" in issue:
                    print(f"  Impact: {issue['impact']}")
                print()
        else:
            print("✅ No functionality issues found")

        # Generate recommendations
        recommendations = self.generate_recommendations()

        print("🎯 RECOMMENDATIONS")
        print("-" * 30)
        for rec in recommendations:
            priority_emoji = (
                "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
            )
            print(f"{priority_emoji} {rec['priority']}: {rec['action']}")
            print(f"  Category: {rec['category']}")
            print(f"  Description: {rec['description']}")
            print(f"  Affected Files: {rec['affected_files']}")
            print()

        # Summary
        print("📊 SUMMARY")
        print("-" * 20)
        print(f"• Text Display Issues: {len(text_issues)}")
        print(f"• Input Field Issues: {len(input_issues)}")
        print(f"• Translation Issues: {len(translation_issues)}")
        print(f"• Functionality Issues: {len(functionality_issues)}")
        print(f"• Total Recommendations: {len(recommendations)}")

        # Save report
        report_file = (
            self.repo_path
            / "reports"
            / f"ui_text_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"\n📁 Detailed report saved: {report_file}")

        return self.analysis_results


def main():
    analyzer = UITextAnalyzer()
    results = analyzer.generate_report()
    return results


if __name__ == "__main__":
    main()
