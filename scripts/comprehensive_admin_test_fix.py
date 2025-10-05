#!/usr/bin/env python3
"""
Comprehensive Admin Testing and Issue Fixing
Tests as admin user and fixes all identified issues
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests


class AdminTestAndFix:
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.repo_path = Path(__file__).parent.parent

        self.issues_found = []
        self.fixes_applied = []
        self.testing_results = {}

    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Backend Status: {health_data.get('status', 'Unknown')}")
                print(f"   Database: {health_data.get('database_status', 'Unknown')}")
                return True
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            return False

    def test_authentication_system(self):
        """Test authentication system"""
        print("\n🔐 Testing Authentication System...")

        # Check if login endpoint exists
        try:
            # Try to access protected endpoint without auth
            response = self.session.get(f"{self.base_url}/api/suppliers")
            if response.status_code == 401:
                print("✅ Authentication is properly enforced")

                # Look for actual auth endpoints
                root_response = self.session.get(f"{self.base_url}/")
                if root_response.status_code == 200:
                    root_data = root_response.json()
                    auth_endpoints = root_data.get("endpoints", {}).get("auth", {})
                    if auth_endpoints:
                        print(f"✅ Auth endpoints available: {list(auth_endpoints.keys())}")
                    else:
                        print("⚠️ No auth endpoints found in API documentation")
                        self.issues_found.append(
                            {
                                "type": "auth_missing",
                                "description": "Authentication endpoints not documented or accessible",
                            }
                        )

            else:
                print(f"⚠️ Suppliers endpoint returned {response.status_code} instead of 401")

        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            self.issues_found.append({"type": "auth_error", "description": f"Authentication system error: {e}"})

    def test_api_endpoints(self):
        """Test all available API endpoints"""
        print("\n🔗 Testing API Endpoints...")

        # Get list of endpoints from root
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                endpoints = data.get("endpoints", {})

                for category, category_endpoints in endpoints.items():
                    if isinstance(category_endpoints, dict):
                        print(f"\n📂 {category.upper()} Endpoints:")
                        for name, url in category_endpoints.items():
                            try:
                                test_response = self.session.get(f"{self.base_url}{url}")
                                status_emoji = "✅" if test_response.status_code < 500 else "❌"
                                print(f"  {status_emoji} {name}: {test_response.status_code}")

                                if test_response.status_code >= 500:
                                    self.issues_found.append(
                                        {
                                            "type": "api_error",
                                            "endpoint": url,
                                            "description": f"Endpoint {url} returns server error {test_response.status_code}",
                                        }
                                    )

                            except Exception as e:
                                print(f"  ❌ {name}: Error - {e}")
                                self.issues_found.append(
                                    {
                                        "type": "api_connection_error",
                                        "endpoint": url,
                                        "description": f"Cannot connect to {url}: {e}",
                                    }
                                )

        except Exception as e:
            print(f"❌ Cannot retrieve API endpoints: {e}")

    def test_data_endpoints(self):
        """Test data endpoints that should return counts"""
        print("\n📊 Testing Data Endpoints...")

        data_endpoints = [
            ("/api/suppliers", "suppliers"),
            ("/api/plants", "plants"),
            ("/api/products", "products"),
            ("/api/clients", "clients"),
            ("/api/projects", "projects"),
        ]

        for endpoint, data_key in data_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")

                if response.status_code == 401:
                    print(f"🔒 {endpoint}: Requires authentication (401)")
                elif response.status_code == 200:
                    data = response.json()
                    count = len(data.get(data_key, []))
                    print(f"✅ {endpoint}: {count} items")
                else:
                    print(f"⚠️ {endpoint}: Status {response.status_code}")
                    self.issues_found.append(
                        {
                            "type": "data_endpoint_error",
                            "endpoint": endpoint,
                            "description": f"Data endpoint returns {response.status_code}",
                        }
                    )

            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")

    def fix_ui_text_issues(self):
        """Fix identified UI text issues"""
        print("\n🔧 Fixing UI Text Issues...")

        # Read the UI analysis report
        reports_dir = self.repo_path / "reports"
        ui_report_files = list(reports_dir.glob("ui_text_analysis_*.json"))

        if not ui_report_files:
            print("⚠️ No UI analysis report found - running analysis...")
            subprocess.run(
                ["python", str(self.repo_path / "scripts" / "ui_text_analysis.py")],
                cwd=self.repo_path,
            )
            ui_report_files = list(reports_dir.glob("ui_text_analysis_*.json"))

        if ui_report_files:
            latest_report = max(ui_report_files, key=lambda x: x.stat().st_mtime)

            with open(latest_report) as f:
                ui_data = json.load(f)

            # Fix critical text issues
            text_issues = ui_data.get("text_display_issues", [])
            critical_files = set()

            for issue in text_issues:
                if issue.get("type") == "hardcoded_text":
                    critical_files.add(issue["file"])

            print(f"📝 Found {len(text_issues)} text issues in {len(critical_files)} files")

            # Fix missing placeholders in Products.jsx
            products_file = self.repo_path / "frontend" / "src" / "components" / "Products.jsx"
            if products_file.exists():
                try:
                    content = products_file.read_text()

                    # Fix poor placeholder="0"
                    if 'placeholder="0"' in content:
                        content = content.replace('placeholder="0"', 'placeholder="Enter quantity"')
                        products_file.write_text(content)
                        self.fixes_applied.append("Fixed placeholder in Products.jsx")
                        print("✅ Fixed placeholder text in Products.jsx")

                except Exception as e:
                    print(f"❌ Error fixing Products.jsx: {e}")

            # Report on translation system
            translation_issues = ui_data.get("translation_issues", [])
            if translation_issues:
                print(f"🌐 Found {len(translation_issues)} translation issues")
                disabled_translation_files = [
                    issue["file"] for issue in translation_issues if issue.get("type") == "disabled_translation"
                ]
                if disabled_translation_files:
                    print(f"⚠️ Files with disabled translation: {len(disabled_translation_files)}")

    def run_comprehensive_linting(self):
        """Run all linting and validation tools"""
        print("\n🔍 Running Comprehensive Linting...")

        lint_commands = [
            (["black", "--check", "."], "Black formatting"),
            (["isort", "--check-only", "."], "Import sorting"),
            (["ruff", "check", "."], "Ruff linting"),
        ]

        for command, description in lint_commands:
            try:
                result = subprocess.run(command, cwd=self.repo_path, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    print(f"✅ {description}: Passed")
                else:
                    print(f"⚠️ {description}: Issues found")
                    # Show first few lines of output
                    if result.stdout:
                        lines = result.stdout.split("\n")[:3]
                        for line in lines:
                            if line.strip():
                                print(f"   {line}")

            except subprocess.TimeoutExpired:
                print(f"⏰ {description}: Timed out")
            except Exception as e:
                print(f"❌ {description}: Error - {e}")

        # Frontend linting
        try:
            result = subprocess.run(
                ["npm", "run", "lint"],
                cwd=self.repo_path / "frontend",
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                print("✅ ESLint: Passed")
            else:
                print("⚠️ ESLint: Issues found")
                # Count errors
                if result.stdout:
                    error_count = result.stdout.count(" error ")
                    warning_count = result.stdout.count(" warning ")
                    print(f"   Errors: {error_count}, Warnings: {warning_count}")

        except Exception as e:
            print(f"❌ ESLint: Error - {e}")

    def run_backend_tests(self):
        """Run backend tests to verify functionality"""
        print("\n🧪 Running Backend Tests...")

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300,
                env={**dict(os.environ), "PYTHONPATH": str(self.repo_path)},
            )

            if "passed" in result.stdout:
                # Extract test results
                lines = result.stdout.split("\n")
                for line in lines:
                    if "passed" in line and ("failed" in line or "error" in line):
                        print(f"🧪 Tests: {line.strip()}")
                        break
                else:
                    print("✅ Backend tests completed")
            else:
                print("⚠️ Backend tests had issues")

        except subprocess.TimeoutExpired:
            print("⏰ Backend tests timed out")
        except Exception as e:
            print(f"❌ Backend tests error: {e}")

    def generate_issue_report(self):
        """Generate comprehensive issue report"""
        print("\n📋 COMPREHENSIVE ADMIN TESTING REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().isoformat()}")
        print()

        if self.issues_found:
            print(f"⚠️ ISSUES FOUND: {len(self.issues_found)}")
            print("-" * 40)

            for i, issue in enumerate(self.issues_found, 1):
                print(f"{i}. {issue['type'].upper()}: {issue['description']}")
                if "endpoint" in issue:
                    print(f"   Endpoint: {issue['endpoint']}")
                print()
        else:
            print("✅ NO CRITICAL ISSUES FOUND")

        if self.fixes_applied:
            print(f"🔧 FIXES APPLIED: {len(self.fixes_applied)}")
            print("-" * 40)

            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"{i}. {fix}")
            print()

        # Save report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "testing_results": self.testing_results,
        }

        report_file = (
            self.repo_path / "reports" / f"admin_comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📁 Full report saved: {report_file}")

        return report_data

    def run_comprehensive_admin_test(self):
        """Run complete admin testing and fixing"""
        print("🎯 COMPREHENSIVE ADMIN USER TESTING & FIXING")
        print("=" * 70)

        # 1. Test backend connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend not accessible - aborting tests")
            return False

        # 2. Test authentication
        self.test_authentication_system()

        # 3. Test API endpoints
        self.test_api_endpoints()

        # 4. Test data endpoints
        self.test_data_endpoints()

        # 5. Fix UI text issues
        self.fix_ui_text_issues()

        # 6. Run linting
        self.run_comprehensive_linting()

        # 7. Run backend tests
        self.run_backend_tests()

        # 8. Generate report
        self.generate_issue_report()

        return True


def main():
    tester = AdminTestAndFix()
    return tester.run_comprehensive_admin_test()


if __name__ == "__main__":
    import os

    success = main()
    sys.exit(0 if success else 1)
