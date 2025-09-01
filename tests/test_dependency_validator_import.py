#!/usr/bin/env python3
"""
Comprehensive test for DependencyValidator import robustness.
This test ensures that the DependencyValidator import issue mentioned in issue #326 
cannot occur and provides multiple verification scenarios.
"""

import importlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to Python path (for test isolation, use fixture below)
project_root = Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def add_project_root_to_syspath(monkeypatch):
    """Ensure project root is in sys.path for each test, with proper isolation."""
    monkeypatch.syspath_prepend(str(project_root))
class TestDependencyValidatorImportRobustness:
    """Comprehensive tests for DependencyValidator import stability"""

    def test_direct_import_works(self):
        """Test that DependencyValidator can be imported directly"""
        from src.utils.dependency_validator import DependencyValidator
        
        # Verify class exists and can be instantiated
        validator = DependencyValidator()
        assert validator is not None
        assert hasattr(validator, 'validate_critical_dependencies')
        assert hasattr(validator, 'validate_optional_dependencies')

    def test_module_import_then_class_access(self):
        """Test importing module then accessing class"""
        import src.utils.dependency_validator as dep_validator
        
        # Verify class is accessible via module
        assert hasattr(dep_validator, 'DependencyValidator')
        validator = dep_validator.DependencyValidator()
        assert validator is not None

    def test_import_from_main_module(self):
        """Test that main.py can import DependencyValidator without errors"""
        # This reproduces the exact import scenario from main.py
        try:
            from src.utils.dependency_validator import DependencyValidator
            from src.main import create_app
            
            # Verify main.py uses the import correctly
            os.environ['FLASK_ENV'] = 'testing'
            app = create_app()
            assert app is not None
            
        except ImportError as e:
            pytest.fail(f"Import failed in main.py scenario: {e}")
        except NameError as e:
            pytest.fail(f"NameError occurred (this is the issue #326 bug): {e}")

    def test_health_endpoint_uses_dependency_validator(self):
        """Test that health endpoint can use DependencyValidator without NameError"""
        os.environ['FLASK_ENV'] = 'testing'
        
        from src.main import create_app
        app = create_app()
        
        with app.test_client() as client:
            # This endpoint uses DependencyValidator() inside the function
            response = client.get('/health')
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'dependencies' in data
            assert 'critical' in data['dependencies']

    def test_import_in_isolation(self):
        """Test import in a completely isolated environment"""
        # Create a subprocess to test imports in isolation
        import subprocess
        
        test_script = '''
import sys
import os
sys.path.insert(0, ".")
os.environ["FLASK_ENV"] = "testing"

try:
    from src.utils.dependency_validator import DependencyValidator
    validator = DependencyValidator()
    
    # Test actual usage
    critical_ok, missing = validator.validate_critical_dependencies()
    print(f"SUCCESS: Critical validation: {critical_ok}, Missing: {missing}")
    
    # Test in context of main app
    from src.main import create_app
    app = create_app()
    print("SUCCESS: App creation with DependencyValidator")
    
except ImportError as e:
    print(f"IMPORT_ERROR: {e}")
    sys.exit(1)
except NameError as e:
    print(f"NAME_ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"OTHER_ERROR: {e}")
    sys.exit(1)
'''
        
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Isolated test failed: {result.stderr}\nStdout: {result.stdout}"
        assert "SUCCESS" in result.stdout
        assert "ERROR" not in result.stdout

    def test_multiple_imports_no_conflict(self):
        """Test that multiple imports don't cause conflicts"""
        import subprocess
        import sys

        test_script = '''
import sys
sys.path.insert(0, ".")
from src.utils.dependency_validator import DependencyValidator as DV1
from src.utils.dependency_validator import DependencyValidator as DV2
validator1 = DV1()
validator2 = DV2()
assert validator1 is not None
assert validator2 is not None
assert type(validator1).__name__ == "DependencyValidator"
assert type(validator2).__name__ == "DependencyValidator"
print("SUCCESS: Multiple imports work without conflict")
'''
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Multiple imports test failed: {result.stderr}\nStdout: {result.stdout}"
        assert "SUCCESS" in result.stdout
    def test_import_with_different_pythonpath(self):
        """Test import robustness with different PYTHONPATH configurations"""
        # Save current path
        original_path = sys.path.copy()
        
        try:
            # Test with minimal path
            sys.path = [str(project_root)]
            
            # Should still work
            from src.utils.dependency_validator import DependencyValidator
            validator = DependencyValidator()
            assert validator is not None
            
        finally:
            # Restore original path
            sys.path = original_path

    def test_import_error_handling_in_main(self):
        """Test that main.py gracefully handles import issues if they occur"""
        # This test verifies that if DependencyValidator import failed,
        # it would be caught appropriately (defensive programming)
        
        # We can't easily mock the import failure without affecting other tests,
        # but we can verify the import is not wrapped in a try/except that
        # would hide NameError issues
        
        import ast
        import inspect
        
        # Read main.py source
        main_file = project_root / "src" / "main.py"
        with open(main_file) as f:
            source = f.read()
        
        # Parse AST
        tree = ast.parse(source)
        
        # Find the import statement
        dependency_validator_import = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module == 'src.utils.dependency_validator' and 
                    any(alias.name == 'DependencyValidator' for alias in node.names)):
                    dependency_validator_import = node
                    break
        
        assert dependency_validator_import is not None, "DependencyValidator import not found"
        
        # Verify it's not inside a try/except block (which could hide NameError)
        # This is a defensive check to ensure the import fails fast if there's an issue
        parent_nodes = []
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child == dependency_validator_import:
                    parent_nodes.append(node)
        
        # The import should be at module level, not in a try/except
        # (defensive programming - we want import errors to be visible)
        module_level_import = any(isinstance(parent, ast.Module) for parent in parent_nodes)
        assert module_level_import, "DependencyValidator import should be at module level for clear error reporting"

    def test_all_dependency_validator_usages_work(self):
        """Test all places where DependencyValidator is used"""
        os.environ['FLASK_ENV'] = 'testing'
        
        # Test 1: Usage in create_app()
        from src.main import create_app
        app = create_app()  # This uses DependencyValidator
        assert app is not None
        
        # Test 2: Usage in health endpoint
        with app.test_client() as client:
            response = client.get('/health')  # This also uses DependencyValidator
            assert response.status_code == 200
        
        # Test 3: Direct usage (like in scripts)
        from src.utils.dependency_validator import DependencyValidator
        validator = DependencyValidator()
        critical_ok, missing = validator.validate_critical_dependencies()
        assert isinstance(critical_ok, bool)
        assert isinstance(missing, list)

    def test_import_statement_syntax_correct(self):
        """Verify the import statement syntax is correct"""
        import ast
        
        # This should parse without syntax errors
        import_statement = "from src.utils.dependency_validator import DependencyValidator"
        
        try:
            ast.parse(import_statement)
        except SyntaxError:
            pytest.fail("DependencyValidator import statement has syntax error")
        
        # Test the actual import works
        exec(import_statement)
        
        # Verify the class is now available
        assert 'DependencyValidator' in locals()
        validator = locals()['DependencyValidator']()
        assert validator is not None


class TestIssue326Regression:
    """Specific regression tests for issue #326"""
    
    def test_issue_326_name_error_does_not_occur(self):
        """
        Regression test for issue #326: Ensure NameError does not occur
        when DependencyValidator is used after import.
        """
        # Test the exact scenario that could cause NameError
        try:
            # Import (simulating main.py)
            from src.utils.dependency_validator import DependencyValidator
            
            # Use immediately (simulating create_app)
            dependency_validator = DependencyValidator()
            dependency_validator.ensure_critical_dependencies()
            
            # Use in function (simulating health endpoint)
            def health_check_simulation():
                validator = DependencyValidator()
                return validator.validate_critical_dependencies()
            
            result = health_check_simulation()
            assert isinstance(result, tuple)
            
        except NameError as e:
            pytest.fail(f"Issue #326 NameError regression detected: {e}")
        except ImportError as e:
            pytest.fail(f"Issue #326 ImportError regression detected: {e}")
    
    def test_copilot_detected_scenario_works(self):
        """
        Test the specific scenario that Copilot detected as problematic.
        Based on the issue description, this tests that DependencyValidator
        class is available after import and doesn't cause NameError.
        """
        os.environ['FLASK_ENV'] = 'testing'
        
        # Simulate the workflow that Copilot flagged
        from src.main import create_app
        
        # This should not raise NameError for DependencyValidator
        app = create_app()
        
        # Test that health endpoint also works (another usage point)
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            
            data = response.get_json()
            # Verify DependencyValidator worked correctly
            assert 'dependencies' in data
            assert data['dependencies']['critical']['status'] in ['ok', 'missing']