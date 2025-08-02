# Dependency Update Procedures

## Overview
This document establishes procedures for future dependency updates to prevent the dependency conflicts that caused the problem-hopping cycle.

## Regular Update Schedule
- **Monthly**: Review for security updates using `safety check`
- **Quarterly**: Consider minor version updates for stability improvements
- **Annually**: Plan major version updates with comprehensive testing

## Update Process

### 1. Security Updates (High Priority)
```bash
# Check for security vulnerabilities
safety check --json

# If vulnerabilities found, update specific packages
pip-compile --upgrade-package [vulnerable-package] requirements.in
pip-compile --upgrade-package [vulnerable-package] requirements-dev.in
```

### 2. Stability Updates (Medium Priority)  
```bash
# Update requirements files
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in

# Test in clean environment
python -m venv /tmp/update_test
source /tmp/update_test/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/test_basic.py
deactivate && rm -rf /tmp/update_test
```

### 3. Validation Requirements
Before accepting any dependency updates:
- [ ] All critical imports work
- [ ] Database connectivity confirmed  
- [ ] Code quality tools functional
- [ ] Basic test suite passes
- [ ] No new security vulnerabilities

### 4. Rollback Procedures
If updates cause issues:
```bash
# Restore previous working versions
git checkout HEAD~1 -- requirements.txt requirements-dev.txt
pip install -r requirements-dev.txt

# Verify rollback success
python -m pytest tests/test_basic.py
```

## Conflict Resolution
When dependency conflicts arise:
1. Identify conflicting packages using `pip check`
2. Use `pipdeptree` to understand dependency relationships
3. Find compatible versions using version constraint adjustments
4. Test thoroughly before deployment

## pip-compile Workflow

### Standard Workflow
```bash
# 1. Edit source files
vim requirements.in          # Edit main dependencies 
vim requirements-dev.in      # Edit development dependencies

# 2. Generate lock files
pip-compile requirements.in --upgrade
pip-compile requirements-dev.in --upgrade

# 3. Install and test
pip install -r requirements-dev.txt
python -m pytest tests/test_basic.py

# 4. Commit changes
git add requirements.in requirements-dev.in requirements.txt requirements-dev.txt
git commit -m "Update dependencies: [describe changes]"
```

### Emergency Updates
```bash
# Quick security update for specific package
pip-compile --upgrade-package [package-name] requirements.in
pip install -r requirements.txt
python -m pytest tests/test_basic.py
```

## Version Constraint Guidelines

### Production Dependencies (requirements.in)
- **Core Framework**: Use `>=X.Y.0,<X+1.0.0` for major packages
- **Database Drivers**: Pin to specific compatible versions `>=X.Y.Z,<X+1.0.0`
- **Security-Critical**: Pin exact versions when needed

### Development Dependencies (requirements-dev.in)  
- **Testing Tools**: Allow minor updates `>=X.Y.0,<X+1.0.0`
- **Code Quality**: Pin exact versions for consistency across team
- **Development Tools**: Allow patch updates `>=X.Y.Z`

## Monitoring and Maintenance

### Weekly Checks
```bash
# Check for available updates
pip list --outdated

# Check for security issues
safety check --json
```

### Monthly Reviews
```bash
# Full dependency audit
pipdeptree
pip check

# Test with latest compatible versions
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
```

## Integration with CI/CD

### Pre-commit Hooks
```bash
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: safety-check
      name: Safety Check
      entry: safety check
      language: system
      pass_filenames: false
```

### CI Pipeline Integration
```bash
# Add to CI workflow
- name: Check Dependencies
  run: |
    pip check
    safety check --json
```

## Troubleshooting Common Issues

### pip-compile Network Timeouts
```bash
# Use offline mode with existing cache
pip-compile --offline requirements.in

# Or use longer timeout
pip-compile --timeout=300 requirements.in
```

### Version Conflicts
```bash
# Find conflicting packages
pipdeptree --warn fail

# Generate dependency graph
pipdeptree --graph-output png > deps.png
```

### Test Failures After Updates
```bash
# Run specific test categories
python -m pytest tests/test_basic.py -v
python -m pytest tests/routes/ -v
python -m pytest tests/models/ -v

# Check for import issues
python -c "import src.main; print('✅ Main app imports work')"
```

## Documentation Standards

### Change Log Format
```markdown
## [Date] - Dependency Update

### Added
- package-name==X.Y.Z (reason for addition)

### Updated  
- package-name: X.Y.Z -> A.B.C (reason for update)

### Removed
- package-name==X.Y.Z (reason for removal)

### Testing
- [ ] All imports work
- [ ] Basic tests pass
- [ ] Code quality tools work
```

### Commit Message Format
```
Update dependencies: [brief description]

- package1: X.Y.Z -> A.B.C (security update)
- package2: added for new feature
- package3: removed due to deprecation

Tested: ✅ All basic tests pass
```

---

**Last Updated**: [Current Date]  
**Next Review**: [Monthly Review Date]