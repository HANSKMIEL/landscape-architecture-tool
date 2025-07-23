# 🌱 Landscape Architecture Tool

Professional landscape architecture management system with AI-powered features.

## 🚀 Features

- **Supplier Management** - Complete supplier database with contact information
- **Plant Catalog** - Comprehensive plant database with growing requirements
- **Product Inventory** - Track landscape products and materials
- **Client Management** - Manage client information and project history
- **Project Management** - Track projects with budget and timeline management
- **AI Plant Recommendations** - Get intelligent plant suggestions based on criteria
- **Professional Dashboard** - Overview of all business metrics
- **Dutch Sample Data** - Pre-loaded with realistic Dutch business examples

## 🧱 Project Structure

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

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or pnpm

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

## 🌐 Usage

1. **Start Backend**: The Flask API will run on `http://127.0.0.1:5001`
2. **Start Frontend**: The React app will run on `http://localhost:5174`
3. **Access Application**: Open your browser to the frontend URL

## 📊 Sample Data

The application comes pre-loaded with Dutch sample data including:
- 3 Suppliers (Boomkwekerij Peters, Van der Berg Tuinmaterialen, GreenScape Supplies)
- 3 Plants (Acer platanoides, Lavandula angustifolia, Buxus sempervirens)
- 4 Products (Garden soil, Mulch, Irrigation kit, Stone pavers)
- 3 Clients (Gemeente Amsterdam, Villa Roosendaal, Bedrijventerrein Westpoort)
- 3 Projects (Vondelpark renovation, Private garden design, Business park landscaping)

## 🔧 API Endpoints

- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/recent-activity` - Recent activity feed
- `GET /api/suppliers` - List all suppliers
- `GET /api/plants` - List all plants
- `GET /api/products` - List all products
- `GET /api/clients` - List all clients
- `GET /api/projects` - List all projects

## 🐳 Docker Support

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created by Jaap Miel - Professional Landscape Architect

