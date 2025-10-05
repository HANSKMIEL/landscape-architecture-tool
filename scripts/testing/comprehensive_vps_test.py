#!/usr/bin/env python3
"""
Comprehensive VPS Testing Script
Tests all user functions on the VPS deployment at http://72.60.176.200:8080
"""

import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup


class VPSUserFunctionTester:
    def __init__(self, base_url="http://72.60.176.200:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {"test": test_name, "status": status, "details": details}
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")

    def test_homepage_headers_and_meta(self):
        """Test homepage headers, language, and meta information"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                self.log_test("Homepage Access", "FAIL", f"Status code: {response.status_code}")
                return False

            soup = BeautifulSoup(response.text, "html.parser")

            # Test HTML lang attribute
            html_tag = soup.find("html")
            lang = html_tag.get("lang") if html_tag else None
            if lang == "en":
                self.log_test("HTML Language", "PASS", f"Language set to: {lang}")
            else:
                self.log_test("HTML Language", "WARN", f"Language: {lang}, expected 'en'")

            # Test title
            title = soup.find("title")
            if title and "devdeploy" in title.text:
                self.log_test("Page Title", "PASS", f"Title: {title.text}")
            else:
                self.log_test("Page Title", "FAIL", f"Title: {title.text if title else 'None'}")

            # Test meta viewport
            viewport = soup.find("meta", attrs={"name": "viewport"})
            if viewport:
                self.log_test("Viewport Meta", "PASS", f"Content: {viewport.get('content')}")
            else:
                self.log_test("Viewport Meta", "FAIL", "Viewport meta tag missing")

            # Test charset
            charset = soup.find("meta", attrs={"charset": True})
            if charset and charset.get("charset") == "UTF-8":
                self.log_test("Character Encoding", "PASS", "UTF-8")
            else:
                self.log_test("Character Encoding", "WARN", f"Charset: {charset.get('charset') if charset else 'None'}")

            # Test favicon
            favicon = soup.find("link", attrs={"rel": "icon"})
            if favicon:
                self.log_test("Favicon", "PASS", f"Type: {favicon.get('type')}")
            else:
                self.log_test("Favicon", "WARN", "Favicon link not found")

            return True

        except Exception as e:
            self.log_test("Homepage Headers Test", "FAIL", str(e))
            return False

    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("API Health", "PASS", f"Version: {data.get('version')}")

                    # Test database connectivity
                    if data.get("database", {}).get("status") == "connected":
                        self.log_test("Database Connection", "PASS", "Database connected")
                    else:
                        self.log_test("Database Connection", "FAIL", "Database not connected")

                    return True
                self.log_test("API Health", "FAIL", f"Status: {data.get('status')}")
            else:
                self.log_test("API Health", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Health", "FAIL", str(e))
        return False

    def test_authentication_system(self):
        """Test authentication functionality"""
        try:
            # Test login endpoint
            login_data = {"username": "admin", "password": "admin123"}

            response = self.session.post(
                f"{self.base_url}/api/auth/login", json=login_data, headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Login successful":
                    self.log_test("Authentication Login", "PASS", f"User: {data.get('user', {}).get('username')}")

                    # Test authenticated endpoint
                    stats_response = self.session.get(f"{self.base_url}/api/dashboard/stats")
                    if stats_response.status_code == 200:
                        self.log_test("Authenticated API Access", "PASS", "Dashboard stats accessible")
                        return True
                    self.log_test("Authenticated API Access", "FAIL", f"Status: {stats_response.status_code}")
                else:
                    self.log_test("Authentication Login", "FAIL", f"Message: {data.get('message')}")
            else:
                self.log_test("Authentication Login", "FAIL", f"Status code: {response.status_code}")

        except Exception as e:
            self.log_test("Authentication System", "FAIL", str(e))
        return False

    def test_crud_operations(self):
        """Test CRUD operations on various endpoints"""
        endpoints_to_test = [
            ("suppliers", "Suppliers"),
            ("plants", "Plants"),
            ("products", "Products"),
            ("clients", "Clients"),
            ("projects", "Projects"),
        ]

        all_passed = True

        for endpoint, name in endpoints_to_test:
            try:
                # Test GET (Read)
                response = self.session.get(f"{self.base_url}/api/{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if endpoint in data or f"{endpoint[:-1]}" in data:  # Handle singular/plural
                        items = data.get(endpoint, data.get(f"{endpoint[:-1]}", []))
                        count = len(items) if isinstance(items, list) else data.get("total", "unknown")
                        self.log_test(f"{name} GET", "PASS", f"Retrieved {count} items")
                    else:
                        self.log_test(f"{name} GET", "PASS", "Data retrieved")
                else:
                    self.log_test(f"{name} GET", "FAIL", f"Status: {response.status_code}")
                    all_passed = False

            except Exception as e:
                self.log_test(f"{name} CRUD", "FAIL", str(e))
                all_passed = False

        return all_passed

    def test_excel_import_functionality(self):
        """Test Excel import system"""
        try:
            response = self.session.get(f"{self.base_url}/api/import/status")
            if response.status_code == 200:
                data = response.json()
                supported_formats = data.get("supported_formats", [])
                if "xlsx" in supported_formats and "csv" in supported_formats:
                    self.log_test("Excel Import Status", "PASS", f"Formats: {', '.join(supported_formats)}")
                    return True
                self.log_test("Excel Import Status", "WARN", f"Limited formats: {supported_formats}")
            else:
                self.log_test("Excel Import Status", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Excel Import", "FAIL", str(e))
        return False

    def test_language_and_localization(self):
        """Test language settings and localization"""
        try:
            # Test dashboard stats for Dutch content
            response = self.session.get(f"{self.base_url}/api/dashboard/stats")
            if response.status_code == 200:
                data = response.json()

                # Check for Dutch project statuses
                project_statuses = data.get("projects_by_status", {})
                dutch_statuses = ["Afgerond", "In uitvoering", "Planning"]
                found_dutch = any(status in project_statuses for status in dutch_statuses)

                if found_dutch:
                    self.log_test("Dutch Localization", "PASS", f"Statuses: {list(project_statuses.keys())}")
                else:
                    self.log_test("Dutch Localization", "WARN", f"Statuses: {list(project_statuses.keys())}")

                return True
        except Exception as e:
            self.log_test("Language/Localization", "FAIL", str(e))
        return False

    def test_user_input_validation(self):
        """Test input validation and placeholders"""
        try:
            # Test invalid login
            invalid_login = {"username": "invalid_user", "password": "wrong_password"}

            response = self.session.post(
                f"{self.base_url}/api/auth/login", json=invalid_login, headers={"Content-Type": "application/json"}
            )

            if response.status_code == 401:
                self.log_test("Input Validation", "PASS", "Invalid credentials properly rejected")
                return True
            self.log_test("Input Validation", "WARN", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Input Validation", "FAIL", str(e))
        return False

    def test_system_performance(self):
        """Test system performance and response times"""
        endpoints = ["/health", "/api/dashboard/stats", "/api/suppliers"]

        all_fast = True
        for endpoint in endpoints:
            try:
                start_time = time.time()
                self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # Convert to ms

                if response_time < 1000:  # Less than 1 second
                    self.log_test(f"Performance {endpoint}", "PASS", f"{response_time:.0f}ms")
                elif response_time < 3000:  # Less than 3 seconds
                    self.log_test(f"Performance {endpoint}", "WARN", f"{response_time:.0f}ms")
                else:
                    self.log_test(f"Performance {endpoint}", "FAIL", f"{response_time:.0f}ms")
                    all_fast = False

            except Exception as e:
                self.log_test(f"Performance {endpoint}", "FAIL", str(e))
                all_fast = False

        return all_fast

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])

        print("\n" + "=" * 60)
        print("VPS COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        print(f"🌐 VPS URL: {self.base_url}")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")

        if warning_tests > 0:
            print("\n⚠️ WARNINGS:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"  - {result['test']}: {result['details']}")

        print("\n" + "=" * 60)

        # Save detailed report
        with open("vps_test_report.json", "w") as f:
            json.dump(
                {
                    "vps_url": self.base_url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "summary": {
                        "total": total_tests,
                        "passed": passed_tests,
                        "failed": failed_tests,
                        "warnings": warning_tests,
                        "success_rate": (passed_tests / total_tests) * 100,
                    },
                    "detailed_results": self.test_results,
                },
                f,
                indent=2,
            )

        return failed_tests == 0

    def run_all_tests(self):
        """Run all comprehensive user function tests"""
        print("🚀 Starting Comprehensive VPS User Function Testing...")
        print(f"🌐 Testing VPS at: {self.base_url}")
        print("-" * 60)

        # Run all test categories
        self.test_homepage_headers_and_meta()
        self.test_api_health()
        self.test_authentication_system()
        self.test_crud_operations()
        self.test_excel_import_functionality()
        self.test_language_and_localization()
        self.test_user_input_validation()
        self.test_system_performance()

        # Generate final report
        return self.generate_report()


def main():
    tester = VPSUserFunctionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
