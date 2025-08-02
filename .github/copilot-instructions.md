## Code Standards

### Required Before Each Commit
- **Phase 4 Prevention Measures**: Use automated prevention tools implemented to avoid CI/CD issues
- **Pre-commit Hooks**: Run automatically via `.pre-commit-config.yaml` (Black, isort, flake8, security checks)
- **Copilot Workflow**: Use `python scripts/copilot_workflow.py --all` for comprehensive validation
- **Developer Guidelines**: Follow standards in `DEVELOPER_GUIDELINES.md`
- Check if the Requirement text files are correct (there are multiple files)
- Check coding is in the right format and the right syntax is used using pyproject.toml configuration  
- If there is an issue that arises in the test then resolve
- Test and debug
- fix errors without loss of advancements or goals with regard to the software
- Make sure the CI will pass
- Update documentation files (.github/copilot-instructions.md, README.md, CI workflow files) to reflect any changes
- Update instructions and make adjustments where necessary to allow codespace to run without error. This must not influence or change the other aspects of the software.

### Code Quality Standards

#### Python Code Formatting
- **Phase 4 Prevention**: Pre-commit hooks automatically enforce formatting standards
- **pyproject.toml Configuration**: All formatting tools are configured in `pyproject.toml` for consistency
- **Pre-commit Integration**: `.pre-commit-config.yaml` runs Black, isort, flake8, and security checks automatically
- **VSCode Integration**: `.vscode/settings.json` provides Copilot-optimized development environment
- **Workflow Automation**: Use `python scripts/copilot_workflow.py` for formatting and validation tasks
- Use black with line length 88: `black --line-length 88 src/ tests/`
- Use isort with black profile: `isort src/ tests/ --profile black`
- Follow flake8 rules: `flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,F401,F403,E402,C901,W291 --max-complexity=25`
- Pass bandit security scan: `bandit -r src/ -f json -o bandit-report.json`
- Check Python security: `safety check --json`
- **Automated Configuration**: All tool settings are centralized in `pyproject.toml` to ensure consistent formatting across development environments

#### CI/CD Pipeline Requirements  
- All code quality checks must pass before merge
- Backend and frontend tests must pass independently
- Database migrations must be tested
- Docker build must succeed
- Integration tests must pass after unit tests
- **Enhanced Service Reliability**: PostgreSQL and Redis services have enhanced health checks with 10-15 retry attempts and extended timeout periods
- **Environment Variable Validation**: All required environment variables are validated before tests run
- **Connection Validation**: Database connections are tested with 15-attempt retry logic and 5-second intervals

### Development Flow  
- **Phase 4 Prevention Tools**: Use monitoring and validation scripts for early issue detection
- **Pipeline Health**: `python scripts/pipeline_health_monitor.py` for system status checking
- **Validation**: `python scripts/phase4_validation.py` for comprehensive prevention measure validation
- Build: `make build`
- Test: `make test`
- Full CI check: `make ci` (includes build, database, lint, test,)

### Database Management

#### Migration Procedures
- Always test migrations locally before commit: `flask --app src.main db upgrade`
- Use `flask db upgrade` for applying migrations
- Ensure database cleanup in tests for isolation
- Verify PostgreSQL and Redis service connectivity

#### Test Database Management
- Clean up test data after each test
- Use transaction rollback for test isolation
- Verify service health before running tests
- Handle connection retries gracefully

#### Service Dependencies
- **PostgreSQL**: Required for production and CI testing
- **Redis**: Required for caching and session management
- **Connection strings**:
  - PostgreSQL: `postgresql://user:pass@host:port/db?connect_timeout=30&application_name=app_name`
  - Redis: `redis://host:port/db_number`

## Repository Structure
landscape-architecture-tool/
├── .devcontainer/             # VS Code devcontainer & Codespaces config
│   └── devcontainer.json      # Development environment specification
├── .github/                   # GitHub automation & workflows
│   ├── workflows/
│   │   └── ci.yml            # CI/CD pipeline with PostgreSQL testing
│   └── dependabot.yml       # Automated dependency updates
├── src/                       # Backend (Python/Flask)
│   ├── main.py               # Main Flask application (refactored)
│   ├── models/
│   │   ├── user.py          # Database configuration
│   │   └── landscape.py     # Database models (updated)
│   ├── routes/              # API routes (blueprints for future use)
│   │   ├── dashboard.py
│   │   ├── suppliers.py
│   │   ├── plants.py
│   │   ├── products.py
│   │   ├── clients.py
│   │   └── projects.py
│   ├── services/            # Business logic layer (NEW)
│   │   └── __init__.py     # Service classes for all entities
│   ├── schemas/             # Pydantic validation schemas (NEW)
│   │   └── __init__.py     # Request/response schemas
│   └── utils/               # Utilities
│       ├── sample_data.py   # Sample data initialization (legacy)
│       ├── db_init.py      # Database initialization (NEW)
│       └── error_handlers.py # Error handling framework (NEW)
├── frontend/                # Frontend (React/Vite)
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/
│   │   │   └── api.js      # API service layer
│   │   └── lib/
│   │       └── utils.js    # Utility functions
│   ├── Dockerfile          # Multi-stage frontend container
│   ├── package.json
│   └── vite.config.js
├── migrations/              # Database migrations (NEW)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                   # Backend tests
├── Dockerfile              # Multi-stage backend container
├── docker-compose.yml      # Multi-service orchestration
├── .env.example            # Environment configuration template
├── SETUP_INSTRUCTIONS.md   # Comprehensive setup guide
├── ONEDRIVE_GUIDE.md       # Cloud integration guide
├── requirements.txt        # Python dependencies (updated)
└── README.md

## Docker and Deployment

### Required Endpoints
- Implement `/health` endpoint for Docker health checks
- Return JSON with status and timestamp
- Ensure endpoint is accessible without authentication

### Production Configuration
- Verify gunicorn.conf.py exists and is properly configured
- Test Docker build locally before CI/CD: `docker compose build`
- Ensure all environment variables are documented in `.env.example`
- Validate multi-stage build optimization

### Environment Variables
- **DATABASE_URL**: PostgreSQL connection string
- **REDIS_URL**: Redis connection string  
- **SECRET_KEY**: Flask secret key (never commit actual secrets)
- **FLASK_ENV**: Environment setting (development/testing/production)

## Testing Standards

### Backend Testing (Python/Flask)
- Use pytest for all backend tests: `python -m pytest tests/ -v`
- Test with both SQLite (fast) and PostgreSQL (production-like)
- Use fixtures for test data setup and cleanup
- Ensure test isolation with database rollbacks
- Write integration tests for API endpoints

### Frontend Testing (React/Vite)
- Use npm test suite: `cd frontend && npm test`
- Maintain test coverage: `npm run test:coverage`
- Test components and API integration
- Use CI-compatible test modes: `--watchAll=false --ci`

### Error Handling Requirements
- Handle database connection failures gracefully
- Implement service health checks for external dependencies
- Use proper logging for debugging CI/CD failures
- Ensure tests clean up resources (database connections, temporary files)

## Key Guidelines
1. Follow Python best practices and PEP 8 standards
2. Use Flask application patterns and conventions
3. Maintain existing code structure and organization
4. Use dependency injection patterns where appropriate
5. Write unit tests for new functionality. Use pytest patterns and fixtures.
6. Document public APIs and complex logic. Suggest changes to the `docs/` folder when appropriate
7. Suggest changes to the repository structure when appropriate with focus on clean and logical development and user environment.
8. When faced with a complex problem, choose the option that will advance software towards goals.

## Standard Documentation Update Workflow
As a standard practice for each commit:
1. **Review Configuration Files**: Check if `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` need updates
2. **Update Documentation**: Ensure `.github/copilot-instructions.md`, `README.md`, and workflow files reflect changes
3. **Validate Requirements**: Ensure all requirement files are consistent and properly documented
4. **CI/CD Alignment**: Verify workflow files match current configurations and capabilities
5. **Environment Consistency**: Ensure `.env.example` includes all required variables mentioned in documentation

## Phase 4 Prevention Measures (CI/CD Problem-Hopping Cycle Prevention)

### Overview
Comprehensive prevention measures have been implemented to eliminate the CI/CD problem-hopping cycle and ensure sustainable development practices. These measures are documented in `PHASE_4_PREVENTION_MEASURES.md` and actively protect the development workflow.

### Prevention Components

#### Pre-commit Hooks (.pre-commit-config.yaml)
- **Automatic Code Quality**: Black formatting, isort import organization, flake8 linting
- **Security Scanning**: Bandit security checks, configuration validation
- **File Quality**: Trailing whitespace removal, line ending fixes, large file detection
- **Environment Validation**: Required environment variables checked
- **Copilot Integration**: Automatic cleanup of temporary Copilot files
- **Import Validation**: Ensures application imports work correctly

#### Developer Guidelines (DEVELOPER_GUIDELINES.md)
- **Comprehensive Standards**: Complete development workflow documentation
- **Copilot Best Practices**: Guidelines for working effectively with GitHub Copilot
- **Database Procedures**: Migration, testing, and connection standards
- **Code Quality Requirements**: Python standards, testing, security practices
- **Emergency Procedures**: How to handle CI/CD and database issues
- **Landscape Architecture Context**: Professional practice considerations

#### VSCode Integration (.vscode/settings.json)
- **Format on Save**: Automatic Black formatting and import organization
- **Copilot Optimization**: Configured for effective Copilot integration
- **Linting Integration**: Real-time flake8 feedback
- **Consistent Environment**: Standardized editor configuration

#### Workflow Automation Scripts
- **copilot_workflow.py**: Automated formatting, validation, cleanup, and testing
- **pipeline_health_monitor.py**: System health monitoring with JSON reporting
- **phase4_validation.py**: Comprehensive validation of all prevention measures

### Usage Guidelines

#### Daily Development Workflow
1. **Pre-commit**: Hooks run automatically on `git commit` (no manual intervention needed)
2. **Copilot Integration**: Use VSCode settings and workflow helper for optimal experience
3. **Health Monitoring**: Run `python scripts/pipeline_health_monitor.py` for system status
4. **Validation**: Use `python scripts/phase4_validation.py` to verify prevention measures

#### Emergency Procedures
- **Bypass pre-commit** (emergencies only): `git commit --no-verify`
- **Skip environment validation**: `export SKIP_ENV_CHECK=1`
- **Pipeline health check**: `python scripts/pipeline_health_monitor.py`
- **Full validation**: `python scripts/phase4_validation.py`

#### Maintenance Tasks
- **Weekly**: Review pipeline health reports and address warnings
- **Monthly**: Update pre-commit hooks with `pre-commit autoupdate`
- **Quarterly**: Review and update developer guidelines based on lessons learned

### Success Metrics
- **Pre-commit Hooks**: Automatically prevent problematic commits
- **Developer Guidelines**: Comprehensive documentation available and followed
- **VSCode Integration**: Consistent development environment across team
- **Monitoring Systems**: Active health monitoring with reporting
- **Validation**: 92.3% success rate on comprehensive validation checks

### Documentation References
- **Complete Implementation Plan**: `PHASE_4_PREVENTION_MEASURES.md`
- **Developer Standards**: `DEVELOPER_GUIDELINES.md`
- **VSCode Configuration**: `.vscode/settings.json`
- **Pre-commit Configuration**: `.pre-commit-config.yaml`

**Result**: The problem-hopping cycle has been systematically eliminated through comprehensive prevention measures that actively protect the development workflow and ensure long-term stability.
