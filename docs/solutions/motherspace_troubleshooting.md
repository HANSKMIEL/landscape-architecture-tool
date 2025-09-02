# Troubleshooting Guide Updates - MotherSpace Integration

**Last Updated:** September 2, 2025  
**Related Issue:** #361 - Copilot Space Documentation Review

## New MotherSpace-Related Troubleshooting

### MotherSpace Orchestration Issues

#### Harmony Score Below 85%
**Symptoms:** MotherSpace reports harmony score below threshold
**Causes:**
- High number of open issues (>20)
- Many open PRs (>10)
- Space documentation out of date
- Poor delegation efficiency

**Solutions:**
```bash
# Check current harmony status
python scripts/pipeline_health_monitor.py

# Organize repository to improve harmony
make check-clutter
make organize

# Review open issues and PRs for delegation opportunities
# Label issues with 'daughter', 'ui-ux', 'integration-manager' as appropriate
```

#### Cross-Space Communication Failures
**Symptoms:** Daughter or IntegrationManager spaces not triggering
**Causes:**
- Missing or incorrect issue labels
- Workflow permissions issues
- GitHub token limitations

**Solutions:**
```yaml
# Ensure proper labels are applied to issues:
labels: ['daughter', 'ui-ux']        # For Daughter Space
labels: ['integration-manager']       # For IntegrationManager Space  
labels: ['motherspace']              # For MotherSpace coordination
```

### Daughter Space UI/UX Issues

#### Visual Analysis Not Triggering
**Symptoms:** No UI/UX analysis reports generated
**Causes:**
- Missing 'daughter' or 'ui-ux' labels
- Frontend dependencies not installed
- Component analysis failures

**Solutions:**
```bash
# Install frontend dependencies for analysis
cd frontend && npm ci --legacy-peer-deps

# Check frontend component structure
find frontend/src/components -name "*.jsx" | head -5

# Manual trigger Daughter Space analysis
# Use workflow_dispatch with target issue number
```

#### Integration Requirements Not Created
**Symptoms:** No "Daughter-Integration Manager" issues created
**Causes:**
- Analysis doesn't detect major integration needs
- Threshold for integration work not met
- Issue creation permissions missing

**Solutions:**
- Check analysis results for enhancement opportunity counts
- Manually create integration issues if needed
- Verify workflow permissions include issue creation

### IntegrationManager Space Issues

#### Modules Repository Creation Fails
**Symptoms:** landscape-modules repository not created
**Causes:**
- Repository already exists
- Permission issues for repository creation
- GitHub API rate limits

**Solutions:**
```bash
# Check if modules repository already exists
curl -s https://api.github.com/repos/HANSKMIEL/landscape-modules

# Manual repository creation if needed
# Use GitHub web interface or gh CLI tool

# Verify repository synchronization
# Check .github/workflows/integrationmanager-space.yml
```

#### Cross-Profession Analysis Incomplete
**Symptoms:** Missing analysis for some professions
**Causes:**
- Code structure doesn't match expected patterns
- Analysis script errors
- Missing profession-specific patterns

**Solutions:**
```python
# Check current models for profession adaptability
python -c "
from src.models.landscape import Plant, Project, Client, Supplier
print('Models available for profession analysis')
print(f'Plant: {Plant.__tablename__}')
print(f'Project: {Project.__tablename__}')
"
```

### Repository Organization Issues

#### Clutter Management Not Working
**Symptoms:** Files still appearing in root directory
**Causes:**
- .gitignore patterns not covering all cases
- Scripts not running properly
- Manual file creation bypassing organization

**Solutions:**
```bash
# Check current clutter status
make check-clutter

# Run organization script manually
python scripts/organize_clutter.py --dry-run
python scripts/organize_clutter.py

# Update .gitignore if new patterns found
# Add patterns for new file types being generated
```

#### Reports Directory Structure Missing
**Symptoms:** Generated reports saved to root directory
**Causes:**
- Directory structure not created
- Scripts using old file paths
- Permissions issues

**Solutions:**
```bash
# Create proper directory structure
mkdir -p reports/{validation,health,security}
mkdir -p docs/{solutions,planning}
mkdir -p archive

# Update script paths to use new structure
# Example: reports/validation/automated_validation_report_*.json
```

### Testing and Validation Issues

#### Space Validation Prompts Not Working
**Symptoms:** Copilot responses don't match documented patterns
**Causes:**
- Documentation out of sync with code
- Examples in documentation are outdated
- Copilot cache needs refreshing

**Solutions:**
1. **Test each validation prompt:**
   ```
   "Explain the database transaction isolation pattern with code examples"
   "Show me how to add a new API route following our conventions"
   "What's our current testing strategy and how do I add tests?"
   "How should I organize generated reports and prevent clutter?"
   ```

2. **Update documentation if patterns have changed:**
   - Check actual implementation vs documented examples
   - Update copilot-instructions.md with current patterns

3. **Clear Copilot context if needed:**
   - Start new chat session
   - Reference updated documentation explicitly

#### Architecture Pattern Validation Failures
**Symptoms:** Code examples in documentation don't work
**Causes:**
- Code has evolved since documentation was written
- Import paths changed
- Method signatures modified

**Solutions:**
```bash
# Test documented database transaction pattern
python -c "
import sys
sys.path.append('.')
from tests.conftest import connection
print('Transaction pattern imports successfully')
"

# Test documented service layer pattern
python -c "
from src.services.supplier_service import SupplierService
print('Service layer accessible')
"

# Test documented API route pattern
curl -s http://localhost:5000/api/suppliers | head -3
```

### Workflow Automation Issues

#### New Workflows Not Triggering
**Symptoms:** Expected automation workflows don't run
**Causes:**
- Workflow syntax errors
- Trigger conditions not met
- Permissions insufficient

**Solutions:**
```bash
# Validate workflow syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/motherspace-orchestrator.yml'))"

# Check workflow permissions
# Ensure permissions include: issues: write, contents: read, pull-requests: write

# Test manual trigger
# Use workflow_dispatch for manual testing
```

#### Nightly Maintenance Not Running
**Symptoms:** Repository cleanup not happening automatically
**Causes:**
- Cron schedule timezone issues
- REPO_TZ variable not set correctly
- Maintenance script errors

**Solutions:**
```bash
# Check timezone configuration
echo "REPO_TZ=${REPO_TZ:-Europe/Amsterdam}"

# Test maintenance script manually
# Run individual maintenance commands to identify issues

# Check maintenance logs in workflow runs
# Look for specific error messages in GitHub Actions
```

## Emergency Recovery Procedures

### Space System Failure Recovery
If the entire MotherSpace system becomes unresponsive:

1. **Immediate Actions:**
   ```bash
   # Disable automated workflows temporarily
   # Rename workflow files to .yml.disabled
   
   # Continue with manual development process
   make install && make build && make backend-test
   ```

2. **Diagnostic Steps:**
   ```bash
   # Check repository health
   git status
   make check-clutter
   
   # Verify basic functionality
   python scripts/pipeline_health_monitor.py
   
   # Test core application
   PYTHONPATH=. python src/main.py &
   curl http://localhost:5000/health
   ```

3. **Recovery Process:**
   ```bash
   # Re-enable workflows one by one
   # Start with basic CI workflow
   # Add MotherSpace orchestrator last
   
   # Test each workflow with manual triggers
   # Verify harmony score calculation
   ```

### Documentation Recovery
If space documentation becomes inconsistent:

1. **Validation Process:**
   ```bash
   # Test all documented examples
   # Verify each code snippet works
   # Check all file paths exist
   ```

2. **Update Process:**
   ```bash
   # Update copilot-instructions.md
   # Update SPACE_OVERVIEW.md
   # Update ARCHITECTURE.md
   
   # Test Copilot prompts again
   # Verify space effectiveness
   ```

## Prevention Measures

### Regular Maintenance Tasks
- **Daily:** Monitor harmony scores and workflow health
- **Weekly:** Review space documentation accuracy
- **Monthly:** Update architecture documentation if code changes
- **Quarterly:** Comprehensive space effectiveness review

### Monitoring Setup
```bash
# Set up monitoring alerts for:
# - Harmony score drops below 85%
# - Workflow failures increase
# - Repository clutter accumulation
# - Space documentation staleness
```

### Quality Gates
- All new workflows must pass YAML validation
- Documentation updates must include working examples
- Space changes must maintain or improve harmony score
- Clutter management must prevent root directory pollution

---

**Integration with Existing Troubleshooting:**
This guide supplements the existing `PIPELINE_TROUBLESHOOTING.md` with MotherSpace-specific issues and solutions. For general CI/CD issues, continue to use the main troubleshooting guide.