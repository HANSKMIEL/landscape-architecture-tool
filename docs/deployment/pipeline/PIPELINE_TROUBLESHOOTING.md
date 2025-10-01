# CI/CD Pipeline Troubleshooting Guide

This guide provides systematic troubleshooting procedures for the Landscape Architecture Tool CI/CD pipeline, based on comprehensive analysis and optimization recommendations.

## Quick Reference

### Pipeline Health Status
- **EXCELLENT (100%)**: All jobs passing, ready for deployment
- **GOOD (80-99%)**: Minor issues, review before deployment
- **FAIR (60-79%)**: Moderate failures, investigation required
- **POOR (<60%)**: Significant failures, address before proceeding

### Common Issues Quick Fix

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| Backend Test Failures | 500 errors, database connection issues | Check service health, verify migrations |
| Frontend Build Failures | npm build errors, dependency issues | Clear cache, reinstall dependencies |
| Code Quality Failures | Black/flake8/isort violations | Run `make lint` locally, fix formatting |
| Service Startup Issues | Health check timeouts | Increase wait times, check resource constraints |
| Integration Test Failures | API endpoint failures | Verify backend startup, check logs |

## Diagnostic Methodology

### 1. Initial Assessment
When investigating pipeline failures:

1. **Check Pipeline Status**: Review the monitoring job output for health assessment
2. **Identify Failed Jobs**: Look for specific job failures and error patterns
3. **Examine Timing**: Check if failures occur at specific times or with specific changes
4. **Review Artifacts**: Download and examine test artifacts and logs

### 2. Job-Specific Diagnostics

#### Backend Test Failures (`test-backend`)

**Common Issues:**
- PostgreSQL connection failures
- Database migration errors
- Test data setup issues
- Import/dependency problems

**Debugging Steps:**
```bash
# Test PostgreSQL connection
pg_isready -h localhost -p 5432 -U postgres

# Test Python database connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres_password@localhost:5432/landscape_test')
conn.close()
print('✅ PostgreSQL connection successful')
"

# Check database migrations
PYTHONPATH=. flask --app src.main db current
PYTHONPATH=. flask --app src.main db upgrade --verbose

# Run specific failing tests
PYTHONPATH=. python -m pytest tests/specific_test.py -v --tb=long
```

#### Frontend Test Failures (`test-frontend`)

**Common Issues:**
- Dependency conflicts
- Security vulnerabilities
- Build configuration errors
- Test execution failures

**Debugging Steps:**
```bash
# Clean and reinstall dependencies
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Check for security issues
npm audit --audit-level=moderate

# Run tests locally
npm test -- --watchAll=false --ci --coverage
```

#### Code Quality Failures (`code-quality`)

**Common Issues:**
- Python formatting violations (black)
- Import sorting issues (isort)
- Linting errors (flake8)
- Security vulnerabilities (bandit/safety)

**Debugging Steps:**
```bash
# Fix formatting automatically
black --line-length 88 src/ tests/
isort --profile black src/ tests/

# Check specific issues
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,F401,F403,E402,C901,W291
bandit -r src/ -f json -o bandit-report.json
safety check --json
```

#### Integration Test Failures (`integration-tests`)

**Common Issues:**
- Service orchestration problems
- API endpoint connectivity
- Application startup failures
- CRUD operation errors

**Debugging Steps:**
```bash
# Test individual components
curl -f http://localhost:5000/health
curl -f http://localhost:5000/api/dashboard/stats

# Test CRUD operations manually
curl -X POST http://localhost:5000/api/suppliers \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Supplier","email":"test@example.com"}'
```

## Optimization Strategies

### 1. Service Performance
The pipeline uses optimized service configurations:

```yaml
# PostgreSQL optimization
postgres:
  image: postgres:15-alpine  # 25% smaller image
  env:
    POSTGRES_INITDB_ARGS: "--auth-host=trust"  # Faster init
  options: >-
    --health-interval 5s    # More responsive
    --health-timeout 3s     # Faster failure detection
    --health-retries 5      # Fewer retries
    --health-start-period 15s  # Reduced startup time
```

### 2. Dependency Management
Enhanced caching strategies reduce build times:

```yaml
# Dedicated linting tool cache
- name: Cache linting tools
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-linting-tools-v1
```

### 3. Monitoring and Alerting
Comprehensive pipeline monitoring provides:

- **Success Rate Calculation**: Percentage of passing jobs
- **Failed Job Tracking**: Specific failure identification
- **Health Assessment**: Four-tier health classification
- **System Metrics**: Resource usage and performance data

## Preventive Maintenance

### Regular Health Checks

**Weekly Tasks:**
```bash
# Dependency updates check
pip list --outdated
cd frontend && npm outdated

# Security audit
pip install safety && safety check
cd frontend && npm audit
```

**Monthly Tasks:**
```bash
# Configuration review
# Review .github/workflows/ci.yml for optimization opportunities
# Review requirements.txt and package.json for cleanup
# Review Docker configurations for improvements
```

### Performance Monitoring

Track these metrics for trend analysis:
- Pipeline execution times (target: <5 minutes)
- Success rates (target: >95%)
- Job-specific performance patterns
- Service startup times
- Resource utilization

## Error Resolution Procedures

### Systematic Problem Resolution

1. **Pattern Analysis**: Identify if failures are recurring or isolated
2. **Root Cause Investigation**: Trace failures to specific changes or conditions
3. **Environment Validation**: Ensure consistency between development and CI
4. **Configuration Verification**: Check service definitions and health checks
5. **Resource Assessment**: Monitor memory, CPU, and disk usage

### Recovery Procedures

**For Service Connectivity Issues:**
```bash
# Verify service health
docker compose ps
docker compose logs postgres
docker compose logs redis

# Restart services if needed
docker compose down -v
docker compose up -d --wait
```

**For Test Environment Issues:**
```bash
# Reset test database
PYTHONPATH=. flask --app src.main db downgrade base
PYTHONPATH=. flask --app src.main db upgrade

# Clear test caches
python -c "
import tempfile, shutil
shutil.rmtree(tempfile.gettempdir() + '/pytest-*', ignore_errors=True)
"
```

## Pipeline Metrics

### Success Criteria
- **Excellent Pipeline**: 100% success rate, <3 minute execution
- **Good Pipeline**: 95%+ success rate, <5 minute execution
- **Needs Attention**: <95% success rate or >5 minute execution

### Monitoring Outputs
The monitoring job exports these GitHub outputs:
- `success_rate`: Percentage of passing jobs
- `pipeline_health`: EXCELLENT/GOOD/FAIR/POOR classification
- `total_jobs`: Total number of pipeline jobs
- `successful_jobs`: Number of passing jobs
- `failed_jobs`: Number of failing jobs

## Escalation Procedures

### When to Escalate
- Pipeline success rate drops below 80% for multiple runs
- Critical security vulnerabilities detected
- Service infrastructure issues (not code-related)
- Systematic failures across multiple job types

### Information to Collect
- Pipeline run URLs and IDs
- Job logs and artifacts
- Error messages and stack traces
- Recent changes and commit history
- Environment and dependency versions

## Additional Resources

- **Repository Documentation**: See `README.md` and `SETUP_INSTRUCTIONS.md`
- **Development Guidelines**: See `CONTRIBUTING.md`
- **Production Deployment**: See `PRODUCTION.md`
- **Security Considerations**: Review bandit reports and safety checks

---

*This troubleshooting guide is maintained alongside pipeline changes to ensure accuracy and relevance. Last updated: $(date)*