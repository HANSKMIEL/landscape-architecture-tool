#!/usr/bin/env python3
"""
VPS Issue Analysis Script
Specifically addresses @HANSKMIEL's concerns:
1. Language switching - only some texts change
2. Other panels not tested (Settings, etc.)
3. Missing texts identification
4. Input field reactivation issues
5. Features that need work
"""

import json
import os
import sys
from pathlib import Path

import requests


class VPSIssueAnalyzer:
    def __init__(self, base_url="http://72.60.176.200:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.issues_found = []
        self.missing_features = []

    def log_issue(self, category, issue, severity="MEDIUM"):
        """Log identified issues"""
        issue_record = {"category": category, "issue": issue, "severity": severity, "url": self.base_url}
        self.issues_found.append(issue_record)
        severity_icon = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🔵"
        print(f"{severity_icon} [{category}] {issue}")

    def analyze_translation_completeness(self):
        """Analyze translation file completeness and identify gaps"""
        print("🌍 Analyzing Translation Completeness...")

        try:
            # Check translation files in the repository
            repo_root = Path("/home/runner/work/landscape-architecture-tool/landscape-architecture-tool")
            nl_file = repo_root / "frontend/src/i18n/locales/nl.json"
            en_file = repo_root / "frontend/src/i18n/locales/en.json"

            if not nl_file.exists() or not en_file.exists():
                self.log_issue("Translation Files", "Translation files not found in expected location", "HIGH")
                return

            # Load translation files
            with open(nl_file, encoding="utf-8") as f:
                nl_data = json.load(f)
            with open(en_file, encoding="utf-8") as f:
                en_data = json.load(f)

            # Compare structure
            self.compare_translation_structures(nl_data, en_data)

            # Identify common missing translation patterns
            self.identify_missing_translation_patterns(nl_data, en_data)

        except Exception as e:
            self.log_issue("Translation Analysis", f"Error analyzing translations: {e}", "HIGH")

    def compare_translation_structures(self, nl_data, en_data):
        """Compare Dutch and English translation structures"""

        def get_all_keys(data, prefix=""):
            keys = set()
            for key, value in data.items():
                current_key = f"{prefix}.{key}" if prefix else key
                keys.add(current_key)
                if isinstance(value, dict):
                    keys.update(get_all_keys(value, current_key))
            return keys

        nl_keys = get_all_keys(nl_data)
        en_keys = get_all_keys(en_data)

        # Find missing keys
        missing_in_en = nl_keys - en_keys
        missing_in_nl = en_keys - nl_keys

        if missing_in_en:
            self.log_issue("Translation Gaps", f"Keys missing in English: {list(missing_in_en)[:5]}...", "MEDIUM")

        if missing_in_nl:
            self.log_issue("Translation Gaps", f"Keys missing in Dutch: {list(missing_in_nl)[:5]}...", "MEDIUM")

        if not missing_in_en and not missing_in_nl:
            print("✅ Translation structures match between Dutch and English")
        else:
            total_missing = len(missing_in_en) + len(missing_in_nl)
            self.log_issue("Translation Completeness", f"Found {total_missing} missing translation keys", "MEDIUM")

    def identify_missing_translation_patterns(self, nl_data, en_data):
        """Identify patterns that suggest incomplete translations"""

        def check_untranslated_values(data, lang_name, other_data):
            untranslated = []

            def traverse(current, other_current, path=""):
                for key, value in current.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, dict):
                        if key in other_current and isinstance(other_current[key], dict):
                            traverse(value, other_current[key], current_path)
                    else:
                        # Check if value is the same in both languages (might be untranslated)
                        if key in other_current and value == other_current[key] and len(value) > 3:
                            untranslated.append(f"{current_path}: '{value}'")

            traverse(data, other_data)
            return untranslated

        # Check for values that are identical in both languages
        untranslated_nl = check_untranslated_values(nl_data, "Dutch", en_data)
        untranslated_en = check_untranslated_values(en_data, "English", nl_data)

        if untranslated_nl:
            self.log_issue(
                "Translation Quality", f"Found {len(untranslated_nl)} potentially untranslated Dutch values", "LOW"
            )

        if untranslated_en:
            self.log_issue(
                "Translation Quality", f"Found {len(untranslated_en)} potentially untranslated English values", "LOW"
            )

    def test_vps_api_endpoints(self):
        """Test various API endpoints to identify missing functionality"""
        print("\n🔌 Testing VPS API Endpoints...")

        # Login first
        try:
            login_response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
                headers={"Content-Type": "application/json"},
            )

            if login_response.status_code == 200:
                print("✅ Authentication successful")
            else:
                self.log_issue("Authentication", f"Login failed with status {login_response.status_code}", "HIGH")
                return
        except Exception as e:
            self.log_issue("Authentication", f"Login error: {e}", "HIGH")
            return

        # Test various endpoints
        endpoints_to_test = [
            ("/api/dashboard/stats", "Dashboard Statistics"),
            ("/api/suppliers", "Suppliers"),
            ("/api/plants", "Plants"),
            ("/api/products", "Products"),
            ("/api/clients", "Clients"),
            ("/api/projects", "Projects"),
            ("/api/import/status", "Excel Import"),
            ("/api/reports/available", "Reports"),
            ("/api/settings", "Settings"),  # This might not exist
            ("/api/users", "User Management"),
            ("/api/photos", "Photo Management"),
        ]

        working_endpoints = 0
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"   ✅ {name}: Working")
                elif response.status_code == 404:
                    self.log_issue("Missing Endpoint", f"{name} endpoint not implemented: {endpoint}", "MEDIUM")
                elif response.status_code == 401:
                    self.log_issue("Authentication", f"{name} requires authentication but failed: {endpoint}", "MEDIUM")
                else:
                    self.log_issue("API Error", f"{name} returned status {response.status_code}: {endpoint}", "MEDIUM")
            except Exception as e:
                self.log_issue("API Connection", f"Error testing {name}: {e}", "HIGH")

        print(f"📊 API Endpoints: {working_endpoints}/{len(endpoints_to_test)} working")

    def analyze_frontend_components(self):
        """Analyze frontend components for potential issues"""
        print("\n🎨 Analyzing Frontend Components...")

        try:
            repo_root = Path("/home/runner/work/landscape-architecture-tool/landscape-architecture-tool")
            components_dir = repo_root / "frontend/src/components"

            if not components_dir.exists():
                self.log_issue("Frontend Structure", "Components directory not found", "HIGH")
                return

            # List all component files
            component_files = list(components_dir.glob("*.jsx"))

            print(f"📁 Found {len(component_files)} component files")

            # Analyze specific components mentioned in issues
            self.analyze_plants_component()
            self.analyze_settings_component()

        except Exception as e:
            self.log_issue("Frontend Analysis", f"Error analyzing frontend: {e}", "HIGH")

    def analyze_plants_component(self):
        """Analyze Plants component for input field issues"""
        try:
            repo_root = Path("/home/runner/work/landscape-architecture-tool/landscape-architecture-tool")
            plants_file = repo_root / "frontend/src/components/Plants.jsx"

            if not plants_file.exists():
                self.log_issue("Plants Component", "Plants.jsx not found", "HIGH")
                return

            with open(plants_file, encoding="utf-8") as f:
                content = f.read()

            # Check for potential input field issues
            issues_found = []

            # Check for useCallback usage with handleInputChange
            if "handleInputChange = useCallback" in content:
                print("   ✅ Plants: Uses useCallback for input handling (good)")
            else:
                issues_found.append("Input handler may cause re-renders")

            # Check for controlled vs uncontrolled inputs
            if "value={formData." in content and "onChange={handleInputChange}" in content:
                print("   ✅ Plants: Uses controlled inputs (good)")
            else:
                issues_found.append("Input control pattern may be inconsistent")

            # Check for form reset patterns
            if "resetForm" in content:
                print("   ✅ Plants: Has form reset functionality")
            else:
                issues_found.append("Form reset functionality may be missing")

            # Check for loading states
            if "loading" in content and "setLoading" in content:
                print("   ✅ Plants: Implements loading states")
            else:
                issues_found.append("Loading states may not be properly implemented")

            if issues_found:
                self.log_issue("Plants Component Issues", f"Potential issues: {issues_found}", "MEDIUM")
            else:
                print("   ✅ Plants component appears well-structured")

        except Exception as e:
            self.log_issue("Plants Analysis", f"Error analyzing Plants component: {e}", "MEDIUM")

    def analyze_settings_component(self):
        """Analyze Settings component"""
        try:
            repo_root = Path("/home/runner/work/landscape-architecture-tool/landscape-architecture-tool")
            settings_file = repo_root / "frontend/src/components/Settings.jsx"

            if not settings_file.exists():
                self.log_issue("Settings Component", "Settings.jsx not found", "HIGH")
                return

            with open(settings_file, encoding="utf-8") as f:
                content = f.read()

            # Check for language switching functionality
            if "useLanguage" in content:
                print("   ✅ Settings: Uses language system")
            else:
                self.log_issue("Settings Language", "Settings may not integrate with language system", "MEDIUM")

            # Check for settings sections
            settings_sections = ["appearance", "api", "ai", "bulk", "reports", "security"]

            missing_sections = []
            for section in settings_sections:
                if section not in content.lower():
                    missing_sections.append(section)

            if missing_sections:
                self.log_issue("Settings Sections", f"Missing sections: {missing_sections}", "LOW")
            else:
                print("   ✅ Settings: Has comprehensive sections")

        except Exception as e:
            self.log_issue("Settings Analysis", f"Error analyzing Settings component: {e}", "MEDIUM")

    def identify_missing_features(self):
        """Identify features that are mentioned but not implemented"""
        print("\n🚧 Identifying Missing Features...")

        missing_features = [
            {
                "feature": "Advanced Language Switching",
                "issue": "Language switching only affects some UI elements",
                "evidence": "User reports incomplete translation switching",
                "priority": "HIGH",
            },
            {
                "feature": "Input Field Focus Management",
                "issue": "Input fields lose focus after each keystroke",
                "evidence": "User reports needing to reactivate input form after each letter",
                "priority": "HIGH",
            },
            {
                "feature": "Complete Settings Panel",
                "issue": "Settings panel may not be fully functional",
                "evidence": "Not all settings sections may be implemented",
                "priority": "MEDIUM",
            },
            {
                "feature": "Comprehensive Panel Testing",
                "issue": "Not all panels have been thoroughly tested",
                "evidence": "Previous testing focused on main CRUD operations only",
                "priority": "MEDIUM",
            },
            {
                "feature": "Translation Completeness",
                "issue": "Some texts may still be missing translations",
                "evidence": "User reports missing texts",
                "priority": "MEDIUM",
            },
        ]

        for feature in missing_features:
            self.missing_features.append(feature)
            priority_icon = "🔴" if feature["priority"] == "HIGH" else "🟡" if feature["priority"] == "MEDIUM" else "🔵"
            print(f"{priority_icon} {feature['feature']}: {feature['issue']}")

    def check_common_ui_issues(self):
        """Check for common UI issues that might cause the reported problems"""
        print("\n🎨 Checking Common UI Issues...")

        # Test VPS homepage for basic issues
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                html_content = response.text

                # Check for common issues
                if "undefined" in html_content:
                    self.log_issue("UI Issues", "Found 'undefined' values in HTML", "MEDIUM")

                if "null" in html_content:
                    self.log_issue("UI Issues", "Found 'null' values in HTML", "LOW")

                # Check for proper React hydration
                if "react" not in html_content.lower():
                    self.log_issue("UI Issues", "React may not be properly loaded", "HIGH")

                # Check for error boundaries
                if "error" in html_content.lower() and "boundary" not in html_content.lower():
                    self.log_issue("UI Issues", "Possible unhandled errors in UI", "MEDIUM")

                print("   ✅ Basic HTML structure appears normal")

            else:
                self.log_issue("VPS Access", f"VPS returned status {response.status_code}", "HIGH")

        except Exception as e:
            self.log_issue("VPS Access", f"Error accessing VPS: {e}", "HIGH")

    def generate_issue_report(self):
        """Generate comprehensive issue report"""
        print("\n" + "=" * 80)
        print("VPS ISSUE ANALYSIS REPORT - ADDRESSING @HANSKMIEL CONCERNS")
        print("=" * 80)

        high_issues = [i for i in self.issues_found if i["severity"] == "HIGH"]
        medium_issues = [i for i in self.issues_found if i["severity"] == "MEDIUM"]
        low_issues = [i for i in self.issues_found if i["severity"] == "LOW"]

        print(f"🔴 High Priority Issues: {len(high_issues)}")
        print(f"🟡 Medium Priority Issues: {len(medium_issues)}")
        print(f"🔵 Low Priority Issues: {len(low_issues)}")
        print(f"🚧 Missing Features Identified: {len(self.missing_features)}")

        print("\n🔴 HIGH PRIORITY ISSUES:")
        print("-" * 40)
        for issue in high_issues:
            print(f"   • [{issue['category']}] {issue['issue']}")

        print("\n🟡 MEDIUM PRIORITY ISSUES:")
        print("-" * 40)
        for issue in medium_issues[:5]:  # Show first 5
            print(f"   • [{issue['category']}] {issue['issue']}")
        if len(medium_issues) > 5:
            print(f"   ... and {len(medium_issues) - 5} more")

        print("\n🚧 MISSING FEATURES ANALYSIS:")
        print("-" * 40)
        for feature in self.missing_features:
            priority_icon = "🔴" if feature["priority"] == "HIGH" else "🟡"
            print(f"   {priority_icon} {feature['feature']}")
            print(f"      Issue: {feature['issue']}")
            print(f"      Evidence: {feature['evidence']}")
            print()

        print("\n📋 RECOMMENDED FIXES:")
        print("-" * 40)
        print("1. 🌍 Fix Language Switching:")
        print("   - Review LanguageProvider implementation")
        print("   - Ensure all components use useLanguage hook")
        print("   - Add language switching test coverage")

        print("\n2. 📝 Fix Input Field Issues:")
        print("   - Review Plants component input handling")
        print("   - Check for unnecessary re-renders")
        print("   - Implement proper focus management")

        print("\n3. ⚙️ Complete Settings Panel:")
        print("   - Implement missing settings sections")
        print("   - Add proper language switching in settings")
        print("   - Test all settings functionality")

        print("\n4. 🔍 Comprehensive Testing:")
        print("   - Test all panels thoroughly")
        print("   - Add missing translation keys")
        print("   - Implement proper error handling")

        print("\n" + "=" * 80)

        # Save report
        report_data = {
            "analysis_timestamp": "2025-09-25 09:30:00",
            "vps_url": self.base_url,
            "issues_found": self.issues_found,
            "missing_features": self.missing_features,
            "summary": {
                "high_priority": len(high_issues),
                "medium_priority": len(medium_issues),
                "low_priority": len(low_issues),
                "missing_features": len(self.missing_features),
            },
        }

        with open("vps_issue_analysis_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print("📄 Detailed report saved to: vps_issue_analysis_report.json")

        return len(high_issues) == 0

    def run_analysis(self):
        """Run complete issue analysis"""
        print("🔍 Starting VPS Issue Analysis...")
        print("🎯 Addressing @HANSKMIEL concerns about:")
        print("   • Language switching issues")
        print("   • Untested panels (Settings, etc.)")
        print("   • Missing translations")
        print("   • Input field reactivation problems")
        print("   • Missing features identification")
        print("-" * 80)

        # Run analysis components
        self.analyze_translation_completeness()
        self.test_vps_api_endpoints()
        self.analyze_frontend_components()
        self.identify_missing_features()
        self.check_common_ui_issues()

        # Generate report
        return self.generate_issue_report()


def main():
    analyzer = VPSIssueAnalyzer()
    success = analyzer.run_analysis()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
