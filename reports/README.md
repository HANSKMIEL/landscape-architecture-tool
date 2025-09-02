# Reports Directory

This directory contains automatically generated reports organized by category to prevent root directory clutter.

## Structure

```
reports/
├── validation/         # Automated validation reports
│   ├── automated_validation_report_*.json
│   └── clutter_cleanup_report_*.json
├── health/            # Pipeline health monitoring reports  
│   └── pipeline_health_report_*.json
└── security/          # Security scanning reports
    ├── bandit-report.json
    └── safety-report.json
```

## Report Types

### Validation Reports (`validation/`)
- **automated_validation_report_*.json**: Comprehensive validation results from automated testing
- **clutter_cleanup_report_*.json**: File organization and cleanup operation logs

### Health Reports (`health/`)
- **pipeline_health_report_*.json**: CI/CD pipeline monitoring and health status

### Security Reports (`security/`)
- **bandit-report.json**: Python security vulnerability scanning (Bandit)
- **safety-report.json**: Dependency vulnerability scanning (Safety)

## Automatic Organization

Files are automatically organized using:

1. **Gitignore Prevention**: Root-level patterns prevent reports from being committed to wrong locations
2. **Organization Script**: `scripts/organize_clutter.py` can move misplaced files
3. **Makefile Commands**:
   - `make check-clutter` - Check for clutter without organizing
   - `make organize` - Organize files into proper structure
   - `make organize-preview` - Preview organization without moving files

## Usage

### Generate Reports in Correct Location
```python
# Good: Save to appropriate subfolder
report_path = f"reports/validation/automated_validation_report_{timestamp}.json"

# Bad: Save to root directory  
report_path = f"automated_validation_report_{timestamp}.json"
```

### Manual Organization
```bash
# Check for clutter
make check-clutter

# Organize files (safe operation)
make organize

# Preview what would be organized
make organize-preview
```

## Retention

- Reports are kept for analysis and debugging
- Old reports can be archived or removed as needed
- Use `archive/` directory for historical reports no longer actively needed

---

This structure is maintained by the automated clutter management system and space management workflows.