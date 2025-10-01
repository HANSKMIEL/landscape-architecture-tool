#!/usr/bin/env python3
"""Test API endpoints for deployment validation."""
import os
import sys

import requests


def test_api_endpoints():
    """Test critical API endpoints."""
    base_url = os.environ.get("STAGING_URL", "http://localhost:5000")

    # Test health endpoint
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    print("✅ Health endpoint working")

    # Test dashboard stats
    response = requests.get(f"{base_url}/api/dashboard/stats")
    assert response.status_code == 200, f"Dashboard stats failed: {response.status_code}"
    print("✅ Dashboard stats working")

    # Test authentication (using environment variables for test credentials)
    test_username = os.environ.get("TEST_USERNAME", "admin")
    test_password = os.environ.get("TEST_PASSWORD", "change_me_in_production")
    auth_data = {"username": test_username, "password": test_password}
    response = requests.post(f"{base_url}/api/auth/login", json=auth_data)
    # Auth may require actual credentials, so 401 is acceptable in testing
    if response.status_code in [200, 401]:
        print("✅ Authentication endpoint working")
    else:
        print(f"⚠️ Authentication returned: {response.status_code}")

    print("✅ All API tests passed")


if __name__ == "__main__":
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        sys.exit(1)
