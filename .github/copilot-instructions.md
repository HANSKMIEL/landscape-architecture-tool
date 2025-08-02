## Code Standards

### Required Before Each Commit
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
- **pyproject.toml Configuration**: All formatting tools are configured in `pyproject.toml` for consistency
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
