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

## 🚀 Quick Start

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
landscape-architecture-complete/
├── src/                          # Backend (Python/Flask)
│   ├── main.py                   # Main Flask application
│   ├── models/
│   │   └── landscape.py          # Database models
│   ├── routes/                   # API routes
│   │   ├── dashboard.py
│   │   ├── suppliers.py
│   │   ├── plants.py
│   │   ├── products.py
│   │   ├── clients.py
│   │   └── projects.py
│   └── utils/
│       └── sample_data.py        # Sample data initialization
├── frontend/                     # Frontend (React/Vite)
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/
│   │   │   └── api.js           # API service layer
│   │   └── lib/
│   │       └── utils.js         # Utility functions
│   ├── package.json
│   └── vite.config.js
├── requirements.txt              # Python dependencies
└── README.md
```

## 🔧 API Endpoints

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity feed

### Suppliers
- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Create new supplier
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Delete supplier

### Plants
- `GET /api/plants` - List all plants
- `POST /api/plants` - Create new plant
- `PUT /api/plants/{id}` - Update plant
- `DELETE /api/plants/{id}` - Delete plant

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Clients
- `GET /api/clients` - List all clients
- `POST /api/clients` - Create new client
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

## 🛠️ Development

### Running Tests
```bash
# Backend tests
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

### Using Docker (Recommended)
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
- Review the sample data in `src/utils/sample_data.py`

## 🔄 Updates

### Latest Changes
- Fixed GitHub Actions CI/CD pipeline to use npm instead of pnpm
- Updated package.json with compatible dependencies
- Enhanced utils.js with comprehensive utility functions
- Improved error handling and logging
- Added Dutch localization and sample data

