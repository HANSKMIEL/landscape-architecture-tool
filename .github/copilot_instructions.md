## Code Standards

### Required Before Each Commit
- Check if the Requirement text files are correct (there are multiple files)
- Check coding is in the right format and the right syntax is used
- If there is an issue that arises in the test then resolve
- Test and debug
- fix errors without loss of advancements or goals with regard to the software
- Make sure the CI will pass
- Update instructions and make adjustments where necessary to allow codespace to run without error. This must not influence or change the other aspects of the software.

### Development Flow
- Build: `make build`
- Test: `make test`
- Full CI check: `make ci` (includes build, database, lint, test,)

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

## Key Guidelines
1. Follow Go best practices and idiomatic patterns
2. Maintain existing code structure and organization
3. Use dependency injection patterns where appropriate
4. Write unit tests for new functionality. Use table-driven unit tests when possible.
5. Document public APIs and complex logic. Suggest changes to the `docs/` folder when appropriate
6. suggest changes to the repository structure when appropriate with focus on clean and logical development and user environment.
7. When faced with a complex problem, choose the option that will advance software towards goals.
