"""
Database Testing Framework

This directory contains the comprehensive database testing framework for the landscape architecture tool.

Structure:
- conftest.py - Database test configuration with isolated test environments
- factories.py - Test data factories for creating realistic test objects
- test_database_operations.py - CRUD operations and relationship testing
- test_migrations.py - Database schema and migration testing

Features:
- Isolated Test Environment: Each test runs in its own transaction that is rolled back
- Test Data Factories: Generate realistic test data using factory_boy
- Comprehensive Testing: Covers CRUD operations, relationships, constraints, and performance
- Migration Testing: Validates database schema matches models
"""