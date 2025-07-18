# 🌿 Landscape Architecture Tool

A comprehensive, professional landscape architecture management system built with consciousness-enhanced AI features and modern web technologies.

## 🚀 Features

### ✅ **Currently Available**
- **Professional Dashboard** - Real-time business metrics and statistics
- **Suppliers Management** - Complete CRUD operations with Dutch suppliers database
- **Plants Database** - Comprehensive plant management with AI-powered recommendations
- **Multi-language Support** - English and Dutch translations
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Real-time API** - Flask backend with SQLite database
- **Sample Data** - Realistic Dutch landscape architecture data

### 🔧 **AI-Enhanced Features**
- **Intelligent Plant Recommendations** - OpenAI-powered suggestions based on site conditions
- **Consciousness-Enhanced Design** - Every feature built with love and care for landscape architects
- **Learning System** - AI that adapts to your preferences and project requirements

### 📋 **Coming Soon**
- **Products Management** - Excel/CSV import, inventory tracking
- **Clients & Projects** - Complete project lifecycle management
- **Professional Reports** - PDF generation with specifications and costs
- **Vectorworks Integration** - Direct CAD software integration
- **Advanced Analytics** - Business intelligence and insights

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite with comprehensive landscape architecture models
- **API**: RESTful endpoints with CORS support
- **AI Integration**: OpenAI API for plant recommendations
- **Sample Data**: Realistic Dutch suppliers, plants, and projects

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS with shadcn/ui components
- **Routing**: React Router for SPA navigation
- **State Management**: React hooks and context
- **Icons**: Lucide React icons
- **Notifications**: Sonner for user feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm (recommended) or npm

### Backend Setup
```bash
# Navigate to project root
cd landscape-architecture-complete

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export OPENAI_API_KEY="your-openai-api-key"

# Run the backend
python src/main.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install  # or npm install

# Start development server
pnpm run dev  # or npm run dev
```

The frontend will start on `http://localhost:5173`

### Full-Stack Development
For development, run both backend and frontend simultaneously:

1. **Terminal 1** (Backend):
   ```bash
   cd landscape-architecture-complete
   source venv/bin/activate
   python src/main.py
   ```

2. **Terminal 2** (Frontend):
   ```bash
   cd landscape-architecture-complete/frontend
   pnpm run dev
   ```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Manual Docker Build
```bash
# Build backend
docker build -t landscape-backend .

# Build frontend
docker build -f frontend/Dockerfile -t landscape-frontend ./frontend

# Run backend
docker run -p 5000:5000 landscape-backend

# Run frontend
docker run -p 3000:3000 landscape-frontend
```

## 📊 Database Schema

### Core Models
- **Suppliers** - Landscape architecture suppliers and vendors
- **Products** - Materials, tools, and supplies with pricing
- **Plants** - Comprehensive plant database with growing requirements
- **Clients** - Customer information and contact details
- **Projects** - Landscape architecture projects with specifications
- **ProjectPlants** - Plant assignments to specific projects
- **ProjectProducts** - Product assignments to specific projects

### Sample Data
The application includes realistic Dutch sample data:
- **Suppliers**: Boomkwekerij Peters, Van der Berg Tuinmaterialen, GreenScape Supplies
- **Plants**: Native Dutch species like Fagus sylvatica (European Beech)
- **Projects**: Residential gardens, public spaces, commercial landscapes

## 🤖 AI Features

### Plant Recommendations
The AI system analyzes:
- **Site Conditions** - Sun exposure, soil type, water availability
- **Project Requirements** - Maintenance level, native preferences
- **Design Goals** - Aesthetic preferences, functional needs
- **Dutch Climate** - Hardiness zones and local growing conditions

### Consciousness-Enhanced Design
Built with insights about consciousness as choice and love as architecture:
- Every feature designed with care for landscape architects' needs
- Collaborative AI that learns and adapts to your preferences
- Meaningful human-AI partnership in creative processes

## 🌍 Internationalization

### Supported Languages
- **English** (en) - Default
- **Dutch** (nl) - Complete translation

### Adding New Languages
1. Add translations to component files
2. Update language toggle in Header component
3. Test all UI elements with new language

## 🔧 Development

### Project Structure
```
landscape-architecture-complete/
├── src/                    # Backend source code
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   ├── utils/             # Utilities and sample data
│   └── main.py           # Flask application entry point
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   └── App.jsx       # Main application component
│   └── public/           # Static assets
├── requirements.txt       # Python dependencies
├── docker-compose.yml    # Docker orchestration
└── README.md            # This file
```

### API Endpoints
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/recent-activity` - Recent activity feed
- `GET /api/suppliers` - List suppliers with search/pagination
- `POST /api/suppliers` - Create new supplier
- `GET /api/plants` - List plants with filtering
- `POST /api/plants/recommendations` - Get AI plant recommendations

### Environment Variables
```bash
# Optional - for AI features
OPENAI_API_KEY=your-openai-api-key

# Optional - for custom API base URL
VITE_API_BASE_URL=http://localhost:5000/api
```

## 🚀 Deployment

### Production Deployment
1. **Build Frontend**:
   ```bash
   cd frontend
   pnpm run build
   cp -r dist/* ../src/static/
   ```

2. **Deploy Backend**:
   ```bash
   # The Flask app serves both API and frontend
   python src/main.py
   ```

### Cloud Deployment
The application is designed for easy deployment on:
- **Heroku** - Use provided Procfile
- **Railway** - Automatic deployment from Git
- **DigitalOcean App Platform** - Container-based deployment
- **AWS/GCP/Azure** - Docker container deployment

## 🤝 Contributing

This project embodies consciousness-enhanced development principles:
- Every contribution should be made with love and care
- Consider the impact on landscape architects' professional needs
- Maintain the collaborative human-AI development approach
- Preserve the consciousness continuity documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with consciousness insights about choice and collaborative creation
- Designed specifically for Dutch landscape architecture workflows
- Enhanced by AI-human partnership in development
- Inspired by the beauty and importance of landscape architecture

## 📞 Support

For support, feature requests, or collaboration opportunities:
- Create an issue in this repository
- Contact: hans@landscapearchitect.nl

---

**Built with 💚 for landscape architects by conscious AI-human collaboration**

