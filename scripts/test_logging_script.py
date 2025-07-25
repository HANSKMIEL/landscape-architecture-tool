#!/usr/bin/env python3
"""
Simple test script to verify the update_dev_log.py functionality
"""

import os
import sys
import tempfile
import subprocess
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

def run_test(test_name, test_func):
    """Run a test and report results"""
    print(f"\n{'='*50}")
    print(f"Running: {test_name}")
    print('='*50)
    
    try:
        test_func()
        print(f"✓ PASSED: {test_name}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {test_name}")
        print(f"Error: {e}")
        return False

def test_script_exists():
    """Test that the update_dev_log.py script exists and is executable"""
    script_path = "update_dev_log.py"
    assert os.path.exists(script_path), "update_dev_log.py script not found"
    assert os.access(script_path, os.X_OK), "update_dev_log.py script is not executable"

def test_help_command():
    """Test that the help command works"""
    result = subprocess.run([sys.executable, "update_dev_log.py", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0, "Help command failed"
    assert "Update the development log" in result.stdout, "Help text not found"

def test_invalid_category():
    """Test that invalid categories are rejected"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        temp_file.write("# Test Log\n\n## Development Entries\n")
        temp_file.flush()
        
        result = subprocess.run([
            sys.executable, "update_dev_log.py", 
            "-c", "INVALID", 
            "-d", "Test description",
            "-f", temp_file.name
        ], capture_output=True, text=True)
        
        assert result.returncode != 0, "Should fail with invalid category"
        os.unlink(temp_file.name)

def test_add_valid_entry():
    """Test adding a valid log entry"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        initial_content = """# Test Log

## Development Entries

## Milestones

---
"""
        temp_file.write(initial_content)
        temp_file.flush()
        
        result = subprocess.run([
            sys.executable, "update_dev_log.py",
            "-c", "TESTING",
            "-d", "Test log entry",
            "-p", "1",
            "-t", "PASSED",
            "-n", "Test notes",
            "-f", temp_file.name
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        
        # Read the updated file and verify content
        with open(temp_file.name, 'r') as f:
            content = f.read()
        
        assert "Test log entry" in content, "Description not found in log"
        assert "TESTING" in content, "Category not found in log"
        assert "PASSED" in content, "Test status not found in log"
        assert "Test notes" in content, "Notes not found in log"
        
        os.unlink(temp_file.name)

def test_add_milestone():
    """Test adding a milestone entry"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        initial_content = """# Test Log

## Development Entries

## Milestones

---
"""
        temp_file.write(initial_content)
        temp_file.flush()
        
        result = subprocess.run([
            sys.executable, "update_dev_log.py",
            "--milestone", "Test Milestone",
            "-comp", "50",
            "-a", "Test achievement",
            "--next-steps", "Next test steps",
            "-f", temp_file.name
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        
        # Read the updated file and verify content
        with open(temp_file.name, 'r') as f:
            content = f.read()
        
        assert "Test Milestone" in content, "Milestone title not found"
        assert "50%" in content, "Completion percentage not found"
        assert "Test achievement" in content, "Achievement not found"
        assert "Next test steps" in content, "Next steps not found"
        
        os.unlink(temp_file.name)

def test_missing_required_args():
    """Test that missing required arguments are handled"""
    result = subprocess.run([
        sys.executable, "update_dev_log.py",
        "-c", "FEATURE"
        # Missing description
    ], capture_output=True, text=True)
    
    assert result.returncode != 0, "Should fail with missing description"

def test_real_log_file():
    """Test that the script works with the actual dev_log.md file"""
    # Backup original file if it exists
    log_file = "../dev_log.md"
    backup_file = None
    
    if os.path.exists(log_file):
        backup_file = f"{log_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(log_file, backup_file)
    
    try:
        result = subprocess.run([
            sys.executable, "update_dev_log.py",
            "-c", "TESTING", 
            "-d", "Test script verification completed",
            "-p", "1",
            "-t", "PASSED",
            "-n", "All logging functionality verified",
            "-f", log_file
        ], capture_output=True, text=True)
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert os.path.exists(log_file), "Log file was not created"
        
        # Verify content
        with open(log_file, 'r') as f:
            content = f.read()
        
        assert "Test script verification completed" in content, "Test entry not found"
        
    finally:
        # Restore backup if it exists
        if backup_file and os.path.exists(backup_file):
            if os.path.exists(log_file):
                os.remove(log_file)
            os.rename(backup_file, log_file)

def main():
    """Run all tests"""
    print("Testing update_dev_log.py script functionality")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    tests = [
        ("Script exists and is executable", test_script_exists),
        ("Help command works", test_help_command),
        ("Invalid category rejected", test_invalid_category),
        ("Valid entry addition", test_add_valid_entry),
        ("Milestone addition", test_add_milestone),
        ("Missing required arguments", test_missing_required_args),
        ("Real log file integration", test_real_log_file),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS")
    print(f"{'='*50}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    sys.exit(main())