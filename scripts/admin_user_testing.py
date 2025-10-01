#!/usr/bin/env python3
"""
Comprehensive Admin User Testing Script
Tests the running software from an admin user perspective
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests


class AdminUserTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "api_tests": {},
            "auth_tests": {},
            "crud_tests": {},
            "ui_tests": {},
            "text_display_tests": {},
            "input_field_tests": {},
            "issues_found": [],
            "recommendations": [],
        }

    def test_health_endpoint(self):
        """Test the health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.test_results["api_tests"]["health"] = {
                    "status": "PASS",
                    "response_code": 200,
                    "data": data,
                }
                return True
            self.test_results["api_tests"]["health"] = {
                "status": "FAIL",
                "response_code": response.status_code,
                "error": "Health endpoint not responding correctly",
            }
            return False
        except Exception as e:
            self.test_results["api_tests"]["health"] = {"status": "ERROR", "error": str(e)}
            return False

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard/stats")
            if response.status_code == 200:
                data = response.json()
                self.test_results["api_tests"]["dashboard_stats"] = {
                    "status": "PASS",
                    "response_code": 200,
                    "data": data,
                }
                return True
            self.test_results["api_tests"]["dashboard_stats"] = {
                "status": "FAIL",
                "response_code": response.status_code,
                "error": "Dashboard stats not accessible",
            }
            return False
        except Exception as e:
            self.test_results["api_tests"]["dashboard_stats"] = {"status": "ERROR", "error": str(e)}
            return False

    def test_crud_operations(self):
        """Test CRUD operations for all main entities"""
        entities = ["suppliers", "plants", "products", "clients", "projects"]

        for entity in entities:
            try:
                # Test GET (Read)
                response = self.session.get(f"{self.base_url}/api/{entity}")
                if response.status_code == 200:
                    data = response.json()
                    self.test_results["crud_tests"][f"{entity}_read"] = {
                        "status": "PASS",
                        "response_code": 200,
                        "count": len(data.get(entity, [])),
                    }
                else:
                    self.test_results["crud_tests"][f"{entity}_read"] = {
                        "status": "FAIL",
                        "response_code": response.status_code,
                        "error": f"Cannot read {entity}",
                    }

                # Test POST (Create) - only for suppliers as example
                if entity == "suppliers":
                    create_data = {
                        "name": "Test Supplier Admin",
                        "contact_person": "Admin Test",
                        "email": "admin@test.com",
                        "phone": "123-456-7890",
                        "address": "Test Address",
                        "city": "Test City",
                        "postal_code": "12345",
                        "country": "Netherlands",
                    }

                    response = self.session.post(
                        f"{self.base_url}/api/{entity}",
                        json=create_data,
                        headers={"Content-Type": "application/json"},
                    )

                    if response.status_code in [200, 201]:
                        self.test_results["crud_tests"][f"{entity}_create"] = {
                            "status": "PASS",
                            "response_code": response.status_code,
                        }
                    else:
                        self.test_results["crud_tests"][f"{entity}_create"] = {
                            "status": "FAIL",
                            "response_code": response.status_code,
                            "error": f"Cannot create {entity}",
                        }

            except Exception as e:
                self.test_results["crud_tests"][f"{entity}_error"] = {
                    "status": "ERROR",
                    "error": str(e),
                }

    def test_authentication_endpoints(self):
        """Test authentication related endpoints"""
        auth_endpoints = ["/auth/forgot-password", "/api/users"]

        for endpoint in auth_endpoints:
            try:
                if "forgot-password" in endpoint:
                    # Test POST for forgot password
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"email": "test@example.com"},
                        headers={"Content-Type": "application/json"},
                    )
                else:
                    # Test GET for other endpoints
                    response = self.session.get(f"{self.base_url}{endpoint}")

                self.test_results["auth_tests"][endpoint] = {
                    "status": "TESTED",
                    "response_code": response.status_code,
                    "accessible": response.status_code < 500,
                }

            except Exception as e:
                self.test_results["auth_tests"][endpoint] = {"status": "ERROR", "error": str(e)}

    def analyze_issues(self):
        """Analyze test results and identify issues"""
        issues = []

        # Check API test failures
        for test, result in self.test_results["api_tests"].items():
            if result.get("status") == "FAIL":
                issues.append(
                    {
                        "category": "API",
                        "severity": "HIGH",
                        "description": f"{test} endpoint failing",
                        "details": result.get("error", "Unknown error"),
                    }
                )

        # Check CRUD operation failures
        for test, result in self.test_results["crud_tests"].items():
            if result.get("status") == "FAIL":
                issues.append(
                    {
                        "category": "CRUD",
                        "severity": "HIGH" if "create" in test else "MEDIUM",
                        "description": f"CRUD operation {test} failing",
                        "details": result.get("error", "Unknown error"),
                    }
                )

        # Check authentication issues
        for test, result in self.test_results["auth_tests"].items():
            if not result.get("accessible", False):
                issues.append(
                    {
                        "category": "AUTH",
                        "severity": "MEDIUM",
                        "description": f"Authentication endpoint {test} not accessible",
                        "details": f"Status code: {result.get('response_code', 'Unknown')}",
                    }
                )

        self.test_results["issues_found"] = issues
        return issues

    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []

        issues = self.test_results["issues_found"]

        if any(issue["category"] == "API" for issue in issues):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Fix API Endpoint Issues",
                    "description": "Critical API endpoints are failing - investigate and fix immediately",
                }
            )

        if any(issue["category"] == "CRUD" for issue in issues):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Fix CRUD Operations",
                    "description": "Data management operations are failing - check database connectivity and API routes",
                }
            )

        if any(issue["category"] == "AUTH" for issue in issues):
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Review Authentication System",
                    "description": "Authentication endpoints need review - may require login tokens",
                }
            )

        # General recommendations
        recommendations.append(
            {
                "priority": "LOW",
                "action": "Implement Comprehensive UI Testing",
                "description": "Add automated UI testing to catch issues early",
            }
        )

        self.test_results["recommendations"] = recommendations
        return recommendations

    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🔍 COMPREHENSIVE ADMIN USER TESTING")
        print("=" * 60)
        print(f"Started: {self.test_results['timestamp']}")
        print()

        # Test health endpoint first
        print("1. Testing Health Endpoint...")
        health_ok = self.test_health_endpoint()
        if not health_ok:
            print("❌ Health endpoint failed - aborting further tests")
            return self.test_results
        print("✅ Health endpoint working")

        # Test dashboard stats
        print("\n2. Testing Dashboard Statistics...")
        dashboard_ok = self.test_dashboard_stats()
        if dashboard_ok:
            print("✅ Dashboard stats working")
        else:
            print("❌ Dashboard stats failed")

        # Test CRUD operations
        print("\n3. Testing CRUD Operations...")
        self.test_crud_operations()

        crud_passes = sum(1 for result in self.test_results["crud_tests"].values() if result.get("status") == "PASS")
        crud_total = len(self.test_results["crud_tests"])
        print(f"✅ CRUD Operations: {crud_passes}/{crud_total} passing")

        # Test authentication
        print("\n4. Testing Authentication Endpoints...")
        self.test_authentication_endpoints()

        auth_passes = sum(1 for result in self.test_results["auth_tests"].values() if result.get("accessible", False))
        auth_total = len(self.test_results["auth_tests"])
        print(f"✅ Auth Endpoints: {auth_passes}/{auth_total} accessible")

        # Analyze issues
        print("\n5. Analyzing Issues...")
        issues = self.analyze_issues()
        if issues:
            print(f"⚠️ Found {len(issues)} issues:")
            for issue in issues:
                severity_emoji = (
                    "🔴" if issue["severity"] == "HIGH" else "🟡" if issue["severity"] == "MEDIUM" else "🟢"
                )
                print(f"  {severity_emoji} {issue['category']}: {issue['description']}")
        else:
            print("✅ No critical issues found")

        # Generate recommendations
        print("\n6. Generating Recommendations...")
        recommendations = self.generate_recommendations()
        for rec in recommendations:
            priority_emoji = "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
            print(f"  {priority_emoji} {rec['action']}: {rec['description']}")

        # Summary
        print("\n📊 SUMMARY")
        print("-" * 30)
        print(f"• API Tests: {len(self.test_results['api_tests'])} completed")
        print(f"• CRUD Tests: {crud_passes}/{crud_total} passing")
        print(f"• Auth Tests: {auth_passes}/{auth_total} accessible")
        print(f"• Issues Found: {len(issues)}")
        print(f"• Recommendations: {len(recommendations)}")

        # Save report
        report_file = (
            Path(__file__).parent.parent
            / "reports"
            / f"admin_user_testing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"\n📁 Detailed report saved: {report_file}")

        return self.test_results


def main():
    tester = AdminUserTester()

    # Check if backend is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend server not accessible at http://localhost:5000")
        print("Please start the backend server first with: PYTHONPATH=. python src/main.py")
        return False

    # Run comprehensive testing
    results = tester.run_comprehensive_test()
    return results


if __name__ == "__main__":
    main()
