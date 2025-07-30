# GitHub Workflows

This directory contains the CI/CD workflows for the landscape architecture tool.

## Active Workflows

- **ci.yml**: Main CI/CD pipeline that runs on push/PR to main and develop branches
  - Backend testing with SQLite and PostgreSQL
  - Frontend building and testing 
  - Code quality checks (linting, formatting, security)
  - Integration tests
  - Docker builds
  - Deployment notifications

## Backup Files

- **ci-enhanced.yml.backup**: Enhanced version with additional monitoring and security features
  - Contains duplicate jobs that need to be resolved before activation:
    - Remove or consolidate duplicate testing jobs for SQLite and PostgreSQL.
    - Ensure that frontend build and test steps are not repeated.
    - Verify that integration tests are not duplicated across workflows.
  - Includes advanced reporting, vulnerability scanning, and monitoring
  - Can be used as a reference for future improvements

## Recent Changes

- Fixed missing redis-cli installation in ci.yml
- Resolved duplicate CI workflow names that were causing conflicts
- Moved enhanced version to backup to prevent conflicts