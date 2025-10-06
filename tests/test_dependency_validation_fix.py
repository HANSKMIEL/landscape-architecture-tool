#!/usr/bin/env python3
"""
Test for the dependency validation fix to ensure it works correctly
when moved from module import time to create_app() function.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

# Add project root to Python path using relative paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDependencyValidationFix:
    """Test that dependency validation is properly moved to create_app()"""

    def setup_method(self):
        """Setup method called before each test method"""
        self.PROJECT_ROOT = project_root

    def test_module_import_without_validation(self):
        """Test that the main module can be imported without triggering validation"""
        # Import the module - this should NOT trigger dependency validation
        import src.main

        # Verify basic attributes are available
        assert hasattr(src.main, "create_app"), "create_app function should be available"
        assert hasattr(src.main, "__version__"), "Version should be available"
        assert src.main.__version__ == "2.0.0", "Version should be correct"

    def test_app_creation_triggers_validation(self):
        """Test that creating the app triggers dependency validation"""
        os.environ["FLASK_ENV"] = "testing"
        import src.main

        # Create app - this SHOULD trigger dependency validation
        app = src.main.create_app()

        # Verify app was created successfully
        assert app is not None, "App should be created"
        assert app.name == "src.main", "App name should be correct"

    def test_module_import_isolation(self):
        """Test module import in a subprocess to ensure clean isolation"""
        # Use subprocess to test clean import without validation
        current_dir = str(self.PROJECT_ROOT).replace("\\", "\\\\")
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"""
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
            """,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "SUCCESS: Module imported without SystemExit" in result.stdout
        assert "create_app available: True" in result.stdout
        assert "version available: True" in result.stdout

    def test_app_creation_in_subprocess(self):
        """Test app creation in subprocess to verify validation runs"""
        current_dir = str(project_root).replace("\\", "\\\\")
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"""
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
            """,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"
        assert "SUCCESS: App created successfully" in result.stdout
        assert "App name: src.main" in result.stdout

    def test_no_module_level_validation_code(self):
        """Test that the problematic module-level validation code is removed"""
        # Read the main.py file to verify the fix
        main_py_path = project_root / "src" / "main.py"

        with open(main_py_path) as f:
            content = f.read()

        # Parse the file using ast
        tree = ast.parse(content, filename=main_py_path)

        # Check for module-level dependency_validator instantiation and validation call
        module_level_instantiation = False
        module_level_validation_call = False
        create_app_instantiation = False
        create_app_validation_call = False

        for node in tree.body:
            # Check for module-level assignment
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "dependency_validator"
                        and isinstance(node.value, ast.Call)
                        and getattr(node.value.func, "id", None) == "DependencyValidator"
                    ):
                        module_level_instantiation = True
            # Check for module-level validation call
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func = node.value.func
                if (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "dependency_validator"
                    and func.attr == "ensure_critical_dependencies"
                ):
                    module_level_validation_call = True
            # Find the create_app function
            if isinstance(node, ast.FunctionDef) and node.name == "create_app":
                for stmt in ast.walk(node):
                    # Assignment inside create_app
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if (
                                isinstance(target, ast.Name)
                                and target.id == "dependency_validator"
                                and isinstance(stmt.value, ast.Call)
                                and getattr(stmt.value.func, "id", None) == "DependencyValidator"
                            ):
                                create_app_instantiation = True
                    # Call inside create_app
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        func = stmt.value.func
                        if (
                            isinstance(func, ast.Attribute)
                            and isinstance(func.value, ast.Name)
                            and func.value.id == "dependency_validator"
                            and func.attr == "ensure_critical_dependencies"
                        ):
                            create_app_validation_call = True

        assert not module_level_instantiation, "Module-level dependency validator instantiation should be removed"
        assert not module_level_validation_call, "Module-level dependency validation call should be removed"
        assert create_app_instantiation, "Dependency validator should be instantiated inside create_app()"
        assert create_app_validation_call, "Dependency validation should be called inside create_app()"
