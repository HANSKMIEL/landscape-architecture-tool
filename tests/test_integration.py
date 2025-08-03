#!/usr/bin/env python3
"""
Integration tests for the Landscape Architecture Management System
These tests simulate the CI integration test scenarios locally
"""

import requests
import time
import subprocess
import os
import signal
from unittest import TestCase
import sys


class IntegrationTestCase(TestCase):
    """Base class for integration tests that start the actual Flask application"""
    
    @classmethod
    def setUpClass(cls):
        """Start the Flask application for integration testing"""
        # Set testing environment
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['PYTHONPATH'] = '.'
        
        # Start the Flask application
        cls.flask_process = subprocess.Popen(
            [sys.executable, 'src/main.py'],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the server to start
        cls._wait_for_server()
    
    @classmethod
    def tearDownClass(cls):
        """Stop the Flask application"""
        if hasattr(cls, 'flask_process') and cls.flask_process:
            cls.flask_process.terminate()
            try:
                cls.flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.flask_process.kill()
                cls.flask_process.wait()
    
    @classmethod
    def _wait_for_server(cls, timeout=30):
        """Wait for the Flask server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://localhost:5000/health', timeout=2)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        raise RuntimeError("Flask server did not start within timeout period")


class TestIntegrationEndpoints(IntegrationTestCase):
    """Test the main integration test scenarios from the CI workflow"""
    
    def test_health_endpoint(self):
        """Test the health endpoint returns expected response"""
        response = requests.get('http://localhost:5000/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['environment'], 'testing')
        self.assertEqual(data['version'], '2.0.0')
        self.assertEqual(data['database_status'], 'connected')
        self.assertIn('timestamp', data)
    
    def test_dashboard_stats_endpoint(self):
        """Test the dashboard stats endpoint"""
        response = requests.get('http://localhost:5000/api/dashboard/stats')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the expected structure
        self.assertIn('totals', data)
        self.assertIn('projects_by_status', data)
        self.assertIn('recent_activity', data)
        self.assertIn('financial', data)
        
        # Verify sample data is loaded
        totals = data['totals']
        self.assertEqual(totals['suppliers'], 3)
        self.assertEqual(totals['plants'], 3)
        self.assertEqual(totals['projects'], 3)
        self.assertEqual(totals['clients'], 3)
    
    def test_supplier_crud_operations(self):
        """Test supplier CRUD operations as done in CI"""
        # Test listing suppliers first
        response = requests.get('http://localhost:5000/api/suppliers')
        self.assertEqual(response.status_code, 200)
        initial_data = response.json()
        initial_count = initial_data['total']
        
        # Test creating a supplier with the same data as CI
        supplier_data = {
            "name": "Test Supplier",
            "contact_person": "John Doe",
            "email": "john@test.com",
            "phone": "123-456-7890",
            "address": "123 Test St"
        }
        
        response = requests.post(
            'http://localhost:5000/api/suppliers',
            json=supplier_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 201)
        created_supplier = response.json()
        
        # Verify the created supplier data
        self.assertEqual(created_supplier['name'], supplier_data['name'])
        self.assertEqual(created_supplier['contact_person'], supplier_data['contact_person'])
        self.assertEqual(created_supplier['email'], supplier_data['email'])
        self.assertEqual(created_supplier['phone'], supplier_data['phone'])
        self.assertEqual(created_supplier['address'], supplier_data['address'])
        self.assertIsNotNone(created_supplier['id'])
        self.assertIsNotNone(created_supplier['created_at'])
        
        # Test listing suppliers again to verify the new supplier is included
        response = requests.get('http://localhost:5000/api/suppliers')
        self.assertEqual(response.status_code, 200)
        updated_data = response.json()
        
        # Should have one more supplier
        self.assertEqual(updated_data['total'], initial_count + 1)
        
        # Verify the new supplier is in the list
        supplier_names = [s['name'] for s in updated_data['suppliers']]
        self.assertIn('Test Supplier', supplier_names)
    
    def test_api_documentation_endpoint(self):
        """Test the API documentation endpoint"""
        response = requests.get('http://localhost:5000/api/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['name'], 'Landscape Architecture Management API')
        self.assertEqual(data['version'], '2.0.0')
        self.assertEqual(data['status'], 'operational')
        self.assertEqual(data['database'], 'persistent')
        self.assertIn('endpoints', data)


if __name__ == '__main__':
    import unittest
    
    # Run the integration tests
    unittest.main(verbosity=2)