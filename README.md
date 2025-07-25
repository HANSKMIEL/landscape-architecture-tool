# Landscape Architecture Management Tool

A comprehensive web application for managing landscape architecture projects, suppliers, plants, products, and clients.

## 🌱 Features

### Core Functionality
- **Dashboard** - Overview with statistics and recent activity
- **Suppliers Management** - Complete CRUD operations for suppliers
- **Plants Catalog** - Manage plant inventory with detailed information
- **Products Management** - Track products and inventory
- **Clients Database** - Manage client information and projects
- **Projects Management** - Create and manage landscape projects

### Advanced Features
- **Plant Recommendations** - Smart suggestions based on project criteria
- **Budget Tracking** - Project cost management and reporting
- **Search & Filtering** - Advanced search across all entities
- **Dutch Localization** - Sample data and formatting for Dutch market
- **Responsive Design** - Works on desktop and mobile devices

### New in v2.0 (Backend Refactoring)
- **Modular Architecture** - Separated models, services, routes, and utilities
- **Persistent Database** - SQLite database with SQLAlchemy ORM
- **Data Validation** - Pydantic schemas for request validation
- **Database Migrations** - Flask-Migrate for schema management
- **Structured Error Handling** - Comprehensive error handling framework
- **Service Layer** - Business logic separation from API routes

## 🚀 Quick Start

### 🌐 Start in GitHub Codespaces (Recommended for Cloud Development)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/HANSKMIEL/landscape-architecture-tool)

GitHub Codespaces provides a complete, cloud-based development environment that runs directly in your browser. No local setup required!

**Features:**
- 🏗️ **Pre-configured Environment**: Python 3.11, Node.js 20, and all dependencies automatically installed
- 🗄️ **Database Ready**: SQLite database with sample data pre-loaded
- 🔧 **VS Code Integration**: Full IDE with extensions for Python, React, and Tailwind CSS
- ⚡ **Port Forwarding**: Frontend (5174) and Backend (5001) automatically accessible
- 🐳 **Docker Support**: Optional full-stack setup with PostgreSQL and Redis

**Getting Started with Codespaces:**

1. **Create a Codespace:**
   - Click the "Open in GitHub Codespaces" badge above, or
   - Go to the repository → Click "Code" → "Codespaces" → "Create codespace on main"

2. **Wait for Setup (2-3 minutes):**
   - The environment will automatically install dependencies
   - Database will be initialized with sample data
   - You'll see: "Codespace is ready! 🚀"

3. **Start Development:**
   ```bash
   # Terminal 1: Start backend API
   start-backend

   # Terminal 2: Start frontend
   start-frontend
   ```

4. **Access Your Application:**
   - Frontend: Click on the "Frontend (Vite)" port forwarding notification
   - Backend API: Access via "Backend API (Development)" port
   - Health Check: Visit `/health` endpoint to verify backend is running

5. **Available Commands:**
   ```bash
   help-dev          # Show all available commands
   start-backend     # Start Flask API server (port 5001)
   start-frontend    # Start Vite dev server (port 5174)
   start-docker      # Optional: Start full stack with Docker
   ```

**Codespaces Environment:**
- **Database**: SQLite (development) with sample data
- **Frontend**: React + Vite with hot reloading
- **Backend**: Flask with auto-restart
- **Ports**: Automatically forwarded and accessible via GitHub's secure URLs

**🐳 Advanced: Full Docker Stack in Codespaces (Optional)**

For testing the complete production-like environment with PostgreSQL and Redis:

```bash
# Start full stack with Docker Compose
docker-compose up -d

# The following services will be available:
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379  
# - Backend: localhost:5000 (Docker version)
# - Nginx: localhost:80 (full proxy setup)
```

This gives you the exact same environment as production, but requires more resources and setup time.

### 🏠 Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm or yarn

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
set PYTHONPATH=. && python src/main.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start development server
npm run dev
```

### Access the Application
- **Frontend:** http://localhost:5174
- **Backend API:** http://127.0.0.1:5001
- **API Documentation:** http://127.0.0.1:5001/api/

## 📁 Project Structure

```
landscape-architecture-tool/
├── src/                          # Backend (Python/Flask)
│   ├── main.py                   # Main Flask application (refactored)
│   ├── models/
│   │   ├── user.py               # Database configuration
│   │   └── landscape.py          # Database models (updated)
│   ├── routes/                   # API routes (blueprints for future use)
│   │   ├── dashboard.py
│   │   ├── suppliers.py
│   │   ├── plants.py
│   │   ├── products.py
│   │   ├── clients.py
│   │   └── projects.py
│   ├── services/                 # Business logic layer (NEW)
│   │   └── __init__.py           # Service classes for all entities
│   ├── schemas/                  # Pydantic validation schemas (NEW)
│   │   └── __init__.py           # Request/response schemas
│   └── utils/                    # Utilities
│       ├── sample_data.py        # Sample data initialization (legacy)
│       ├── db_init.py            # Database initialization (NEW)
│       └── error_handlers.py     # Error handling framework (NEW)
├── migrations/                   # Database migrations (NEW)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── frontend/                     # Frontend (React/Vite)
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/
│   │   │   └── api.js           # API service layer
│   │   └── lib/
│   │       └── utils.js         # Utility functions
│   ├── package.json
│   └── vite.config.js
├── requirements.txt              # Python dependencies (updated)
└── README.md
```

## 🏗️ Architecture Overview

### Backend Architecture (v2.0)

The backend has been completely refactored from a monolithic structure to a modular, production-ready architecture:

#### **Models Layer** (`src/models/`)
- **SQLAlchemy Models**: Persistent database entities with relationships
- **Database Configuration**: Centralized database setup and configuration

#### **Services Layer** (`src/services/`)
- **Business Logic**: Core business operations separated from API routes
- **CRUD Operations**: Standardized create, read, update, delete operations
- **Data Processing**: Complex data operations and calculations

#### **Schemas Layer** (`src/schemas/`)
- **Pydantic Validation**: Input validation and data sanitization
- **Type Safety**: Strong typing for API requests and responses
- **Documentation**: Auto-generated API documentation from schemas

#### **Utilities Layer** (`src/utils/`)
- **Error Handling**: Structured error responses and logging
- **Database Initialization**: Automated database setup and sample data
- **Helper Functions**: Reusable utility functions

#### **Database Layer**
- **SQLite Database**: Persistent storage with relational integrity
- **Migrations**: Version-controlled database schema changes
- **Relationships**: Foreign key constraints and data consistency

### Key Improvements

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Scalability**: Modular structure allows for easy expansion
3. **Maintainability**: Clear code organization and documentation
4. **Data Persistence**: No more data loss on server restart
5. **Validation**: Input validation prevents data corruption
6. **Error Handling**: Consistent error responses across all endpoints
7. **Migration Support**: Database schema changes are managed and versioned

## 🔧 API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity feed

### Suppliers
- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Create new supplier (with validation)
- `PUT /api/suppliers/{id}` - Update supplier (with validation)
- `DELETE /api/suppliers/{id}` - Delete supplier

### Plants
- `GET /api/plants` - List all plants
- `POST /api/plants` - Create new plant (with validation)
- `PUT /api/plants/{id}` - Update plant (with validation)
- `DELETE /api/plants/{id}` - Delete plant

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product (with validation)
- `PUT /api/products/{id}` - Update product (with validation)
- `DELETE /api/products/{id}` - Delete product

### Clients
- `GET /api/clients` - List all clients
- `POST /api/clients` - Create new client (with validation)
- `PUT /api/clients/{id}` - Update client (with validation)
- `DELETE /api/clients/{id}` - Delete client

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project (with validation)
- `PUT /api/projects/{id}` - Update project (with validation)
- `DELETE /api/projects/{id}` - Delete project

## 🛠️ Development

### Database Operations

#### Initialize Database
```bash
# Initialize migration repository (one time)
PYTHONPATH=. flask --app src.main db init

# Create migration for schema changes
PYTHONPATH=. flask --app src.main db migrate -m "Description of changes"

# Apply migrations to database
PYTHONPATH=. flask --app src.main db upgrade
```

#### Sample Data
```bash
# Sample data is automatically loaded on first run
# Database will be created at: landscape_architecture.db
```

### Running Tests
```bash
# Backend tests (when available)
python -m pytest tests/

# Frontend tests
cd frontend
npm run test
```

### Building for Production
```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/dist/
```

### Code Quality
```bash
# Python linting
flake8 src/

# Python formatting
black src/

# Import sorting
isort src/
```

## 🚀 Deployment

### 🌐 GitHub Codespaces (Development)
Perfect for testing, development, and collaboration:
```bash
# Already set up! Just click the Codespaces badge in README
# Everything runs in the cloud with zero local setup
```

### Using Docker (Recommended for Production)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
1. Build the frontend: `cd frontend && npm run build`
2. Copy built files to Flask static directory
3. Configure production WSGI server (gunicorn, uWSGI)
4. Set up reverse proxy (nginx, Apache)
5. Configure SSL certificates

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV` - Set to 'production' for production deployment
- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `SECRET_KEY` - Flask secret key for sessions

### Database
The application uses SQLite by default for development. For production, configure PostgreSQL or MySQL via the `DATABASE_URL` environment variable.

## 📝 Sample Data

The application includes comprehensive Dutch sample data:
- **3 Suppliers** - Dutch garden suppliers with realistic contact information
- **3 Plants** - Common Dutch landscape plants (Acer platanoides, Lavandula, Buxus)
- **4 Products** - Garden supplies and materials
- **3 Clients** - Dutch municipalities and private clients
- **3 Projects** - Realistic landscape projects

Data is automatically loaded on first application startup and persisted in the database.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/api/`
- Review the sample data initialization in `src/utils/db_init.py`

## 🔄 Updates

### Version 2.0 - Backend Refactoring (Latest)
- Complete backend architecture refactoring
- Modular structure with services, schemas, and utilities
- Persistent SQLite database with SQLAlchemy ORM
- Pydantic validation for all API requests
- Structured error handling framework
- Database migrations with Flask-Migrate
- Comprehensive logging and monitoring

### Version 1.0 - Initial Release
- Fixed GitHub Actions CI/CD pipeline to use npm instead of pnpm
- Updated package.json with compatible dependencies
- Enhanced utils.js with comprehensive utility functions
- Improved error handling and logging
- Added Dutch localization and sample data

