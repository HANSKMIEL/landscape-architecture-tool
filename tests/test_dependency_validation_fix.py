#!/usr/bin/env python3
"""
Test for the dependency validation fix to ensure it works correctly
when moved from module import time to create_app() function.
"""

import os
import sys
import pytest
import importlib
import subprocess

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDependencyValidationFix:
    """Test that dependency validation is properly moved to create_app()"""

    def test_module_import_without_validation(self):
        """Test that the main module can be imported without triggering validation"""
        # Import the module - this should NOT trigger dependency validation
        import src.main
        
        # Verify basic attributes are available
        assert hasattr(src.main, 'create_app'), "create_app function should be available"
        assert hasattr(src.main, '__version__'), "Version should be available"
        assert src.main.__version__ == "2.0.0", "Version should be correct"

    def test_app_creation_triggers_validation(self):
        """Test that creating the app triggers dependency validation"""
        os.environ['FLASK_ENV'] = 'testing'
        import src.main
        
        # Create app - this SHOULD trigger dependency validation
        app = src.main.create_app()
        
        # Verify app was created successfully
        assert app is not None, "App should be created"
        assert app.name == "src.main", "App name should be correct"

    def test_module_import_isolation(self):
        """Test module import in a subprocess to ensure clean isolation"""
        # Use subprocess to test clean import without validation
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run([
            sys.executable, '-c',
            f'''
import sys
import os
sys.path.insert(0, "{current_dir}")
try:
    import src.main
    print("SUCCESS: Module imported without SystemExit")
    print("create_app available:", hasattr(src.main, "create_app"))
    print("version available:", hasattr(src.main, "__version__"))
except SystemExit as e:
    print("FAILURE: Module import triggered SystemExit:", e)
    sys.exit(1)
except Exception as e:
    print("ERROR: Module import failed:", e)
    sys.exit(2)
            '''
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "SUCCESS: Module imported without SystemExit" in result.stdout
        assert "create_app available: True" in result.stdout
        assert "version available: True" in result.stdout

    def test_app_creation_in_subprocess(self):
        """Test app creation in subprocess to verify validation runs"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run([
            sys.executable, '-c',
            f'''
import sys
import os
os.environ["FLASK_ENV"] = "testing"
sys.path.insert(0, "{current_dir}")
try:
    import src.main
    print("Module imported successfully")
    app = src.main.create_app()
    print("SUCCESS: App created successfully")
    print("App name:", app.name)
except SystemExit as e:
    print("FAILURE: Dependency validation failed during app creation:", e)
    sys.exit(1)
except Exception as e:
    print("ERROR: App creation failed:", e)
    import traceback
    traceback.print_exc()
    sys.exit(2)
            '''
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "SUCCESS: App created successfully" in result.stdout
        assert "App name: src.main" in result.stdout

    def test_no_module_level_validation_code(self):
        """Test that the problematic module-level validation code is removed"""
        # Read the main.py file to verify the fix
        main_py_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'src', 'main.py'
        )
        
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Check that module-level validation is removed
        assert "dependency_validator = DependencyValidator()" not in content.split("def create_app()")[0], \
            "Module-level dependency validator instantiation should be removed"
        assert "dependency_validator.ensure_critical_dependencies()" not in content.split("def create_app()")[0], \
            "Module-level dependency validation call should be removed"
        
        # Check that validation is inside create_app function
        create_app_section = content.split("def create_app()")[1].split("def ")[0]
        assert "dependency_validator = DependencyValidator()" in create_app_section, \
            "Dependency validator should be instantiated inside create_app()"
        assert "dependency_validator.ensure_critical_dependencies()" in create_app_section, \
            "Dependency validation should be called inside create_app()"