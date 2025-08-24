# Copilot Development Window Fix Guide

## Problem: Copilot Getting Stuck in Development Window

This document provides solutions to prevent GitHub Copilot from getting stuck in its development window and ensure smooth development experience.

## Quick Fix Commands

### 🚑 Emergency Reset
If Copilot is currently stuck, run this command to reset everything:
```bash
bash scripts/reset_dev_environment.sh
```

### 🔧 Quick Copilot Check
```bash
python scripts/copilot_workflow.py --check-env
```

### 🛠️ Fix Environment Issues
```bash
python scripts/copilot_workflow.py --fix-env
```

## Root Causes and Solutions

### 1. **Timeout Issues**
**Problem**: Copilot requests timeout, causing the development window to hang.

**Solution**: VSCode settings now include optimized Copilot timeout configuration:
- `github.copilot.advanced.timeout`: 5000ms (5 seconds)
- Automatic fallback when timeouts occur

### 2. **Temporary File Accumulation**
**Problem**: Copilot temporary files accumulate and cause conflicts.

**Solutions**:
- Pre-commit hooks automatically clean temporary files
- Enhanced cleanup patterns in `scripts/copilot_workflow.py`
- Added to `.gitignore`: `*.copilot.md`, `*_copilot_*`, `temp_*.py`, etc.

### 3. **Development Process Conflicts**
**Problem**: Stuck development servers interfere with Copilot.

**Solution**: Reset script kills stuck processes:
- Flask development servers on port 5000
- Vite/npm servers on port 5174
- Any Copilot-related stuck processes

### 4. **VSCode Workspace State Issues**
**Problem**: Corrupted VSCode workspace state causes Copilot hang.

**Solutions**:
- Automatic cleanup of `.vscode/.ropeproject`, `.vscode/.history`
- Validation of `settings.json` configuration
- Optimized VSCode settings for Copilot performance

### 5. **Python Environment Issues**
**Problem**: Import errors or path issues cause Copilot to hang during code analysis.

**Solutions**:
- Automatic `PYTHONPATH` configuration
- Python cache cleanup
- Dependency validation before Copilot operations

## Prevention Measures

### Automated (No Action Required)
These run automatically with pre-commit hooks:

1. **File Cleanup**: Temporary Copilot files removed before each commit
2. **Code Formatting**: Black/isort ensure consistent formatting
3. **Environment Validation**: Check required environment variables

### Manual Best Practices

1. **Regular Cleanup**:
   ```bash
   python scripts/copilot_workflow.py --cleanup
   ```

2. **Before Major Development Sessions**:
   ```bash
   python scripts/copilot_workflow.py --all
   ```

3. **Weekly Environment Reset**:
   ```bash
   bash scripts/reset_dev_environment.sh
   ```

## VSCode Configuration

The following VSCode settings are now configured to prevent Copilot issues:

### Copilot-Specific Settings
```json
{
  "github.copilot.advanced": {
    "timeout": 5000,
    "temperature": 0.1,
    "length": 500
  },
  "github.copilot.autocomplete": {
    "enable": true,
    "delay": 100,
    "maxCompletions": 10
  }
}
```

### Environment Settings
```json
{
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "."
  },
  "python.defaultInterpreterPath": "./venv/bin/python"
}
```

## Troubleshooting Steps

### If Copilot is Still Stuck After Reset:

1. **Reload VSCode Window**:
   - `Ctrl+Shift+P` → "Developer: Reload Window"

2. **Restart Copilot Service**:
   - `Ctrl+Shift+P` → "GitHub Copilot: Restart"

3. **Clear VSCode Workspace Storage**:
   - Close VSCode
   - Delete: `~/.config/Code/User/workspaceStorage/[workspace-hash]/`
   - Reopen project

4. **Check Network/Proxy Issues**:
   ```bash
   # Test Copilot API connectivity
   curl -H "Authorization: Bearer [token]" https://api.github.com/user
   ```

5. **Disable/Re-enable Copilot**:
   - `Ctrl+Shift+P` → "GitHub Copilot: Disable"
   - Wait 10 seconds
   - `Ctrl+Shift+P` → "GitHub Copilot: Enable"

### Advanced Debugging

#### Check Copilot Logs
1. Open VSCode Developer Tools: `Help` → `Toggle Developer Tools`
2. Check Console for Copilot errors
3. Look for timeout or network errors

#### Environment Validation
```bash
# Check Python environment
python -c "import sys; print(f'Python: {sys.version}')"
python -c "from src.main import create_app; print('✅ App imports OK')"

# Check Git state
git status
git diff --name-only

# Check running processes
ps aux | grep -E "(python|node|flask|vite)"
```

## Script Reference

### `scripts/copilot_workflow.py`
Complete workflow automation:
- `--cleanup`: Clean temporary files
- `--format`: Format code with Black/isort
- `--validate`: Run quality checks
- `--test`: Run basic tests
- `--check-env`: Check Copilot environment
- `--fix-env`: Fix environment issues
- `--all`: Run complete workflow

### `scripts/reset_dev_environment.sh`
Emergency reset script:
- Cleans all temporary files
- Resets Git state
- Kills stuck processes
- Validates environment
- Provides recovery instructions

### VSCode Tasks (Ctrl+Shift+P → "Tasks: Run Task")
- "Clean Copilot Files"
- "Format Code"
- "Validate Code Quality" 
- "Run Tests"
- "Full Copilot Workflow"
- "Reset Development Environment"

## Monitoring and Maintenance

### Weekly Maintenance
```bash
# Check for issues
python scripts/copilot_workflow.py --check-env

# Full cleanup and validation
python scripts/copilot_workflow.py --all

# Environment reset if needed
bash scripts/reset_dev_environment.sh
```

### Signs Copilot Needs Reset
- Suggestions stop appearing
- Development window shows "loading..." indefinitely
- VSCode becomes unresponsive during code editing
- Copilot suggestions are irrelevant or repetitive
- High CPU usage from VSCode processes

## Integration with CI/CD

The prevention measures integrate with the existing CI/CD pipeline:
- Pre-commit hooks prevent problematic files from being committed
- Pipeline health monitoring detects environment issues
- Automated cleanup runs before builds

## Support

If issues persist after trying all solutions:

1. **Create an issue** with:
   - Output of `python scripts/copilot_workflow.py --check-env`
   - VSCode version and Copilot extension version
   - Operating system details
   - Steps to reproduce

2. **Temporary Workaround**:
   - Disable Copilot temporarily
   - Use traditional IDE features
   - Re-enable after environment reset

## Best Practices for Development

1. **Start each session** with environment check
2. **End each session** with cleanup
3. **Before major changes**, run full workflow
4. **After git pulls**, validate environment
5. **Weekly maintenance** prevents most issues

---

This comprehensive guide ensures Copilot runs smoothly and provides quick recovery options when issues occur.