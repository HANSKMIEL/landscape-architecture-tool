# Developer Guidelines - Landscape Architecture Tool

## Overview
These guidelines prevent the CI/CD issues that caused the problem-hopping cycle and ensure sustainable development practices.

## Pre-Commit Requirements

### Automated Checks (via pre-commit hooks)
Before every commit, the following checks run automatically:
- **Black formatting**: Code must be properly formatted
- **Import sorting**: Imports must be organized with isort
- **Flake8 linting**: Code must pass linting standards
- **Security scanning**: No obvious security issues (Bandit)
- **File quality**: No trailing whitespace, proper line endings
- **Configuration validation**: YAML, TOML, JSON files must be valid

### Manual Verification
Before committing, developers should:
1. **Run tests locally**: `make test` or `python -m pytest tests/test_basic.py`
2. **Check database connectivity**: Ensure local database is running
3. **Review Copilot suggestions**: Ensure generated code meets standards
4. **Validate environment variables**: Required vars are set or documented

## Working with GitHub Copilot

### Best Practices
1. **Review all suggestions**: Don't accept without understanding
2. **Format generated code**: Run Black on Copilot-generated files
3. **Test generated code**: Ensure it works with existing codebase
4. **Document complex logic**: Add comments for non-obvious code

### Common Issues to Avoid
- **Formatting conflicts**: Always run `black .` after accepting suggestions
- **Import issues**: Ensure imports are properly organized with `isort`
- **Configuration changes**: Review any config file modifications carefully
- **Dependency additions**: Coordinate dependency changes with team

### Copilot-Generated Files
- **Temporary files**: Will be automatically cleaned up by pre-commit hooks
- **Markdown files**: Review for formatting before committing
- **Code suggestions**: Must pass all quality checks before commit

## Database Development

### Local Development
- **Always run migrations**: `flask db upgrade` before testing
- **Use test database**: Never test against production data
- **Clean up test data**: Ensure tests are isolated and don't interfere

### Migration Guidelines
- **Test migrations locally**: Before committing migration files
- **Review migration SQL**: Understand what changes are being made
- **Backup considerations**: Consider impact on production data
- **Rollback planning**: Ensure migrations can be safely reversed

## Code Quality Standards

### Python Code
- **Line length**: Maximum 88 characters (Black standard)
- **Import organization**: Use isort with Black profile
- **Docstrings**: Document public functions and classes
- **Type hints**: Use where appropriate for clarity
- **Error handling**: Include appropriate exception handling

### Testing Requirements
- **Basic tests must pass**: Core functionality always working
- **New features need tests**: Don't commit untested code
- **Database tests**: Use test database, clean up after tests
- **Mock external services**: Don't depend on external APIs in tests

### Security Practices
- **No secrets in code**: Use environment variables
- **Validate inputs**: Sanitize all user inputs
- **SQL injection prevention**: Use parameterized queries
- **Authentication required**: Protect sensitive endpoints

## CI/CD Pipeline

### Pipeline Stages
1. **Code Quality**: Black, isort, flake8, bandit checks
2. **Backend Tests**: Python tests with SQLite and PostgreSQL
3. **Frontend Tests**: JavaScript/React tests
4. **Integration Tests**: Full application testing
5. **Quality Gates**: Coverage and quality validation

### Pipeline Failures
- **Don't ignore failures**: Investigate and fix root causes
- **Check logs carefully**: Look for actual error messages
- **Test locally first**: Reproduce issues in local environment
- **Ask for help**: Don't struggle alone with complex issues

### Deployment
- **All checks must pass**: No exceptions for "quick fixes"
- **Review deployment logs**: Ensure successful deployment
- **Monitor after deployment**: Watch for errors or issues
- **Rollback plan ready**: Know how to revert if needed

## Emergency Procedures

### CI/CD Pipeline Issues
1. **Check recent changes**: What was committed recently?
2. **Review pipeline logs**: Look for specific error messages
3. **Test locally**: Can you reproduce the issue locally?
4. **Rollback if needed**: Revert problematic commits
5. **Document issues**: Help prevent future occurrences

### Database Issues
1. **Check service status**: Are PostgreSQL/Redis running?
2. **Verify connections**: Test database connectivity
3. **Review recent migrations**: Any recent schema changes?
4. **Check environment vars**: Are database URLs correct?
5. **Escalate if critical**: Don't delay for production issues

### Professional Practice Considerations

### Landscape Architecture Context
- **Data integrity critical**: Client data must be protected
- **Reliability required**: System must be available for client work
- **Performance matters**: Slow systems impact productivity
- **Backup essential**: Always have data recovery options

---

**Remember**: These guidelines exist to prevent the problem-hopping cycle that was disrupting development. Following them consistently ensures a stable, reliable development environment that supports professional landscape architecture practice.