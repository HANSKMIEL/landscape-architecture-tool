# Deployment Guide

This document provides multiple options for deploying and viewing the Landscape Architecture Tool.

## 🚀 Quick Demo Options

### 1. GitHub Pages (Frontend Only)
The frontend is automatically deployed to GitHub Pages on every push to main:

**Live Demo:** `https://hanskmiel.github.io/landscape-architecture-tool/`

- ✅ **Automatic deployment** via GitHub Actions
- ✅ **Free hosting** on GitHub infrastructure  
- ✅ **Custom domain** support available
- ⚠️ **Frontend only** (no backend API functionality)

### 2. GitHub Codespaces (Full Development Environment)
Open a complete development environment in your browser:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/HANSKMIEL/landscape-architecture-tool)

- ✅ **Full-stack development** environment
- ✅ **Pre-configured** with all dependencies
- ✅ **Automatic port forwarding** for frontend and backend
- ✅ **VS Code in browser** with extensions
- ⚠️ **Requires GitHub account** and Codespaces quota

### 3. Local Development
Clone and run locally:

```bash
# Clone the repository
git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
cd landscape-architecture-tool

# Backend setup
pip install -r requirements.txt
export FLASK_ENV=development
python -m src.main

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

## 🔧 Production Deployment Options

### Vercel (Recommended for Frontend)
1. Connect your GitHub repository to Vercel
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/dist`
4. Deploy automatically on push

### Railway (Full-Stack)
1. Connect repository to Railway
2. Configure environment variables
3. Deploy both frontend and backend

### Heroku
1. Create Heroku app
2. Add buildpacks for Python and Node.js
3. Configure environment variables
4. Deploy via Git

### Docker Deployment
Use the included Docker configuration:

```bash
docker-compose up --build
```

## 🌐 Environment Variables

For production deployment, configure these environment variables:

```env
FLASK_ENV=production
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
CORS_ORIGINS=your_frontend_domain
```

## 📊 Features Available in Each Environment

| Feature | GitHub Pages | Codespaces | Local Dev | Production |
|---------|-------------|------------|-----------|------------|
| Frontend UI | ✅ | ✅ | ✅ | ✅ |
| Backend API | ❌ | ✅ | ✅ | ✅ |
| Database | ❌ | ✅ | ✅ | ✅ |
| Authentication | ❌ | ✅ | ✅ | ✅ |
| File Upload | ❌ | ✅ | ✅ | ✅ |
| Real-time Features | ❌ | ✅ | ✅ | ✅ |

## 🎯 Recommended Approach

1. **Quick Preview**: Use GitHub Pages for a fast frontend demo
2. **Development**: Use GitHub Codespaces for full-featured development
3. **Production**: Deploy to Vercel (frontend) + Railway/Heroku (backend)

## 🔗 Useful Links

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Vercel Deployment Guide](https://vercel.com/docs)
- [Railway Deployment Guide](https://docs.railway.app/)
