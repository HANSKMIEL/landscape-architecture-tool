# Landscape Architecture Tool - System Architecture

**Version:** 1.0.0  
**Last Updated:** September 2, 2025  
**System:** Flask Backend + React Frontend + MotherSpace Orchestration

## 🏗️ System Overview

The Landscape Architecture Tool is a comprehensive web application designed for managing landscape architecture projects, suppliers, plants, products, and clients. The system implements a modern microservice-oriented architecture with AI-assisted development patterns.

## 🎯 Architecture Principles

### Core Design Principles
1. **Separation of Concerns:** Clear boundaries between presentation, business logic, and data layers
2. **Transaction Isolation:** Enhanced SAVEPOINT-based patterns for data consistency
3. **Service Layer Pattern:** Business logic encapsulation with proper error handling
4. **API-First Design:** RESTful APIs with standardized error handling
5. **Orchestrated Development:** Multi-space coordination for optimal development harmony

### Quality Assurance
- **Test-Driven Development:** Comprehensive test coverage with isolation patterns
- **Automated Validation:** Pre-commit hooks and CI/CD quality gates
- **Clutter Management:** Organized file structure preventing repository pollution
- **Documentation Currency:** Architecture patterns match actual implementation

## 🏛️ System Components

### Backend Architecture (Python Flask)

#### Application Factory Pattern
```python
# Enhanced application factory with configuration management
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from src.routes import register_blueprints
    register_blueprints(app)
    
    return app
```

#### Database Layer
- **Primary Database:** SQLite (development/testing), PostgreSQL (production)
- **ORM:** SQLAlchemy with Flask-SQLAlchemy integration
- **Migration System:** Flask-Migrate for database versioning
- **Transaction Isolation:** Enhanced SAVEPOINT-based patterns

**Core Models:**
```
src/models/
├── user.py              # User authentication and database setup
└── landscape.py         # Business domain models
    ├── Supplier         # Supplier management
    ├── Plant            # Plant catalog and specifications
    ├── Product          # Product inventory
    ├── Client           # Client relationship management
    └── Project          # Project management and coordination
```

#### Service Layer Architecture
```python
# Service layer pattern with transaction management
class BaseService:
    def __init__(self, db_session):
        self.db = db_session
    
    def create(self, data):
        try:
            instance = self.model(**data)
            self.db.add(instance)
            self.db.commit()
            return instance
        except Exception:
            self.db.rollback()
            raise
```

**Service Components:**
```
src/services/
├── analytics.py         # Analytics and reporting
├── client_service.py    # Client management business logic
├── dashboard_service.py # Dashboard data aggregation
├── performance.py       # Performance monitoring
├── plant_service.py     # Plant catalog management
├── project_service.py   # Project coordination
├── supplier_service.py  # Supplier relationship management
└── recommendation_*.py  # Plant recommendation algorithms
```

#### API Route Architecture
```python
# Standardized API route pattern
@blueprint.route('/', methods=['POST'])
def create_resource():
    try:
        data = request.get_json()
        # Validate with schema
        resource = resource_service.create(data)
        return jsonify({"resource": resource.to_dict()}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Resource creation failed: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

**API Endpoints:**
```
src/routes/
├── dashboard.py         # /api/dashboard/* - Analytics endpoints
├── suppliers.py         # /api/suppliers/* - Supplier CRUD operations
├── plants.py           # /api/plants/* - Plant catalog management
├── products.py         # /api/products/* - Product inventory
├── clients.py          # /api/clients/* - Client management
└── projects.py         # /api/projects/* - Project coordination
```

### Frontend Architecture (React + Vite)

#### Modern React Setup
- **Build Tool:** Vite for fast development and optimized builds
- **Framework:** React 19+ with functional components and hooks
- **Styling:** Tailwind CSS with component design system
- **State Management:** React hooks and context for local state

#### Component Architecture
```
frontend/src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (buttons, forms, etc.)
│   ├── layout/         # Layout components (header, sidebar, etc.)
│   ├── dashboard/      # Dashboard-specific components
│   ├── suppliers/      # Supplier management components
│   ├── plants/         # Plant catalog components
│   └── projects/       # Project management components
├── services/           # API communication layer
│   └── api.js          # Centralized API service
├── lib/               # Utility functions
│   └── utils.js        # Common utilities
└── pages/             # Page-level components
```

#### API Communication Layer
```javascript
// Centralized API service with error handling
class ApiService {
  constructor(baseURL = import.meta.env.VITE_API_BASE_URL) {
    this.baseURL = baseURL;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }
}
```

### Database Architecture

#### Enhanced Transaction Isolation
```python
# SAVEPOINT-based transaction isolation for tests
@pytest.fixture(scope="session")
def connection(engine):
    conn = engine.connect()
    
    # Always create reversible outer transaction for consistent isolation
    if conn.in_transaction():
        # Connection already in transaction - create savepoint for isolation
        outer_tx = conn.begin_nested()
    else:
        # Connection not in transaction - create regular transaction
        outer_tx = conn.begin()
    
    try:
        yield conn
    finally:
        if outer_tx and outer_tx.is_active:
            outer_tx.rollback()
        if not conn.closed:
            conn.close()
```

#### Data Model Relationships
```
Supplier 1:N Product
Supplier 1:N Plant
Client 1:N Project
Project N:M Plant (through ProjectPlant association)
Project 1:N ProjectMilestone
Plant 1:N PlantRecommendation
```

#### Schema Design Principles
- **Normalization:** Third normal form with strategic denormalization for performance
- **Indexing:** Strategic indexes on frequently queried columns
- **Constraints:** Foreign key relationships with cascade rules
- **Auditing:** Created/updated timestamps on all entities

## 🔧 MotherSpace Orchestration System

### Multi-Space Architecture

#### MotherSpace Orchestrator
- **Purpose:** Master orchestrator ensuring development harmony ≥85%
- **Components:**
  - Harmony score calculation and monitoring
  - Task delegation in chronological order
  - Quality and security checkpoint enforcement
  - Cross-space communication coordination

#### Daughter Space - UI/UX Manager
- **Purpose:** Visual appeal and user experience optimization
- **Capabilities:**
  - Component accessibility analysis
  - User workflow optimization
  - Data import/export evaluation
  - Integration requirement reporting

#### IntegrationManager Space
- **Purpose:** External system integration and module development
- **Functions:**
  - Modules repository creation (`landscape-modules`)
  - Cross-profession adaptation (Architecture, Engineering, Planning, Design)
  - External API integration (Vectorworks, CRM, AI services)
  - Repository synchronization every 6 hours

### Automation Workflows

#### CI/CD Pipeline Architecture
```yaml
# Workflow coordination pattern
trigger: [push, pull_request, schedule, workflow_dispatch]
permissions: [contents: read, issues: write, pull-requests: write]
strategy:
  - quality_checks: [formatting, linting, testing, security]
  - harmony_monitoring: continuous
  - failure_recovery: automated_issue_creation
```

**Workflow Components:**
1. **CI Workflow:** Core build, test, and quality validation
2. **MotherSpace Orchestrator:** Harmony monitoring and task delegation
3. **Daughter Space UI/UX:** Visual analysis and user experience optimization
4. **IntegrationManager:** External system integration and module development
5. **Nightly Maintenance:** Repository cleanup and health monitoring
6. **Post-Merge Automation:** Follow-up task creation
7. **Space Management:** Documentation currency monitoring
8. **Test Failure Automation:** Systematic failure resolution

## 🧪 Testing Architecture

### Testing Strategy
- **Backend Tests:** 521 tests with 99%+ pass rate, ~50 second execution
- **Frontend Tests:** 47 tests with 96%+ pass rate, ~8 second execution
- **Integration Tests:** End-to-end API and UI validation
- **Performance Tests:** Load testing with analytics service

### Test Isolation Patterns
```python
# Enhanced test isolation with SAVEPOINT management
def test_with_isolation(connection):
    # Each test gets isolated transaction context
    with connection.begin() as trans:
        # Test operations here
        trans.rollback()  # Automatic cleanup
```

### Validation Scenarios
1. **Basic Application Functionality:** Health endpoints and API responses
2. **Frontend Integration:** React application loading and API communication
3. **CRUD Operations:** Create, read, update, delete workflow validation
4. **End-to-End Application:** Complete user workflow testing
5. **Development Workflow:** Build, test, and deployment pipeline validation

## 📁 Repository Organization

### File Structure
```
landscape-architecture-tool/
├── .github/                    # GitHub workflows and templates
│   ├── workflows/             # 8 specialized automation workflows
│   └── copilot-instructions.md # Comprehensive development guide
├── src/                       # Python backend source code
│   ├── models/               # Database models and schemas
│   ├── routes/               # API route definitions
│   ├── services/             # Business logic layer
│   └── utils/                # Utility functions and helpers
├── frontend/                  # React frontend application
│   ├── src/components/       # React components
│   ├── src/services/         # API communication layer
│   └── src/lib/              # Frontend utilities
├── tests/                     # Comprehensive test suite
├── scripts/                   # Development and automation scripts
├── documentation/             # Organized documentation
├── reports/                   # Generated reports and validation results
│   ├── validation/           # Validation and review reports
│   ├── health/               # Pipeline health monitoring
│   └── security/             # Security scan results
├── docs/                      # High-level documentation
│   ├── solutions/            # Solution documentation
│   └── planning/             # Development planning documents
└── n8n-workflows/            # N8n automation workflow templates
```

### Clutter Management
```python
# Automated file organization
def organize_files():
    patterns = {
        'reports/validation/': '*_validation_report_*.json',
        'reports/health/': '*_health_report_*.json',
        'reports/security/': 'bandit-report.json, safety-report.json',
        'docs/solutions/': '*_SOLUTION*.md',
        'docs/planning/': '*_PLAN*.md, dev_log.md'
    }
    # Automatic organization prevents root directory clutter
```

## 🔗 Integration Architecture

### N8n Workflow Integration
```javascript
// Webhook-based automation integration
function triggerWorkflow(workflowType, data) {
  return fetch(`http://n8n:5678/webhook/${workflowType}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...data,
      timestamp: new Date().toISOString()
    })
  });
}
```

**Available Workflows:**
- **Client Onboarding:** Automated welcome and setup process
- **Project Milestone Tracking:** Progress monitoring and notifications
- **Inventory Management:** Stock level monitoring and alerts

### External System Integration
- **Vectorworks Integration:** CAD file import/export and project synchronization
- **CRM System Integration:** Customer relationship management synchronization
- **AI Service Integration:** Design assistance and plant recommendation systems
- **Weather API Integration:** Climate data for plant selection optimization

## 📊 Performance Architecture

### Monitoring and Analytics
```python
# Performance monitoring service
class PerformanceMonitor:
    def track_request(self, endpoint, duration, status):
        # Real-time metrics collection
        # Health scoring based on response time and cache performance
        # Performance recommendations with actionable insights
```

### Caching Strategy
- **Application Level:** Service layer caching for frequently accessed data
- **Database Level:** Query result caching with intelligent invalidation
- **Frontend Level:** API response caching with cache management endpoints

### Scalability Considerations
- **Database:** Connection pooling and query optimization
- **API:** Rate limiting and request queuing
- **Frontend:** Component lazy loading and code splitting

## 🛡️ Security Architecture

### Authentication and Authorization
- **Session Management:** Flask-Session with secure cookie configuration
- **API Security:** Token-based authentication for API endpoints
- **CORS Configuration:** Secure cross-origin resource sharing

### Data Protection
- **Input Validation:** Pydantic schemas for request validation
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **XSS Prevention:** React's built-in protection and content sanitization

### Security Monitoring
- **Automated Scanning:** Bandit for Python security issues
- **Dependency Monitoring:** Safety checks for known vulnerabilities
- **Code Analysis:** Continuous security validation in CI/CD pipeline

## 🔄 Development Workflow

### Local Development
```bash
# Standard development workflow
make install          # Install all dependencies
make build           # Build frontend and backend
make backend-test    # Run comprehensive test suite
make lint           # Code quality validation
make check-clutter  # Repository organization check
```

### Deployment Architecture
- **Development:** Local SQLite with hot-reload development servers
- **Production:** PostgreSQL with Redis caching and load balancing
- **Docker:** Multi-stage builds with production optimization
- **CI/CD:** Automated testing, building, and deployment validation

## 📚 Documentation Architecture

### Documentation Strategy
- **Code Documentation:** Inline docstrings and type hints
- **API Documentation:** OpenAPI/Swagger specification generation
- **Architecture Documentation:** This comprehensive architecture guide
- **Development Guidelines:** Copilot-assisted development patterns

### Maintenance Process
- **Continuous Updates:** Architecture documentation updated with code changes
- **Validation Process:** Regular verification that documentation matches implementation
- **Space Management:** Automated monitoring of documentation currency

---

**Maintained by:** MotherSpace Orchestration System  
**Architecture Review:** Quarterly or when major changes occur  
**Status:** ✅ Current and actively maintained  
**Next Review:** December 2025 or when significant architectural changes are made