# Architecture: Public API-Only Design

**Date**: October 2, 2025  
**Version**: V1.00D  
**Requirement**: NO localhost URLs - Everything via public APIs

---

## 🎯 Design Principle

**The application MUST work entirely through public-facing URLs and APIs.**

- ❌ NO `localhost` URLs in frontend code
- ❌ NO `127.0.0.1` references in production
- ✅ ALL communication via public domain/IP
- ✅ Frontend → Backend always through external API endpoints

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Internet / External Clients                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │   VPS Firewall     │  Port 8080 (HTTP)
         │  72.60.176.200     │  Port 443 (HTTPS - future)
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │      Nginx         │  Listen: 0.0.0.0:8080
         │  (Reverse Proxy)   │  
         └────┬───────────┬───┘
              │           │
    ┌─────────┘           └──────────┐
    │                                │
    ▼                                ▼
┌───────────┐                 ┌──────────────┐
│ Frontend  │                 │   Backend    │
│ (Static)  │                 │  (Gunicorn)  │
│           │    HTTP/API     │              │
│ Port 8080 │◄────────────────│  Port 5001   │
│           │  via /api path  │              │
└───────────┘                 └──────────────┘
     │                               │
     │                               ▼
     │                        ┌─────────────┐
     │                        │   SQLite    │
     │                        │  Database   │
     │                        └─────────────┘
     │
     └──► Client Browser makes ALL requests to:
          http://72.60.176.200:8080/
          http://72.60.176.200:8080/api/*
```

---

## 📡 API Communication Flow

### How It Works

1. **User accesses**: `http://72.60.176.200:8080/`
2. **Nginx serves**: Frontend static files (React/Vite build)
3. **Frontend loads** in user's browser
4. **Frontend makes API calls** to: `http://72.60.176.200:8080/api/*`
5. **Nginx proxies** `/api/*` requests to backend at `127.0.0.1:5001`
6. **Backend processes** and responds
7. **Response goes back** through Nginx to browser

### Key Points

- ✅ Frontend NEVER knows about `localhost` or `127.0.0.1`
- ✅ All URLs use public IP/domain: `72.60.176.200`
- ✅ Backend binding `0.0.0.0:5001` allows external access if needed
- ✅ Nginx acts as single entry point for all traffic

---

## 🔧 Implementation Details

### Frontend Configuration

**File**: `frontend/src/lib/env.js`

```javascript
export function getApiBaseUrl() {
  // GitHub Pages: Use mock API
  if (window.location.hostname.includes('github.io')) {
    return 'MOCK_API';
  }
  
  // Explicit environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // VPS Production: Use public-facing URL
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  const port = window.location.port;
  
  if (hostname === '72.60.176.200' || hostname === 'optura.nl') {
    // Returns: http://72.60.176.200:8080/api
    return `${protocol}//${hostname}${port ? ':' + port : ''}/api`;
  }
  
  // Development fallback
  return '/api';
}
```

**Result**:
- Production: `http://72.60.176.200:8080/api`
- Development: `/api` (proxied by Vite dev server)

### Backend Configuration

**File**: `/etc/systemd/system/landscape-backend-dev.service`

```ini
[Service]
ExecStart=/var/www/landscape-architecture-tool-dev/venv/bin/gunicorn \
    --bind 0.0.0.0:5001 \
    --workers 4 \
    src.main:app
```

**Key**: `--bind 0.0.0.0:5001`
- Listens on ALL interfaces (not just localhost)
- Accessible from network if firewall allows
- Nginx can proxy to it

### Nginx Configuration

**File**: `/etc/nginx/sites-available/landscape-dev`

```nginx
server {
    listen 8080;
    server_name _;
    
    # Frontend - static files
    location / {
        root /var/www/landscape-architecture-tool-dev/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API - proxy to internal service
    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5001/health;
        access_log off;
    }
}
```

**Note**: Nginx uses `127.0.0.1:5001` internally, but this is HIDDEN from frontend.

---

## 🚫 What We Don't Want

### Bad Patterns (NEVER USE)

```javascript
// ❌ BAD: Hardcoded localhost
const API_URL = 'http://localhost:5001/api';

// ❌ BAD: Localhost in production
if (production) {
  API_URL = 'http://localhost:5001/api';
}

// ❌ BAD: Browser accessing backend directly
fetch('http://localhost:5001/api/suppliers');
```

### Why These Are Bad

1. **Doesn't work remotely**: Users can't access your `localhost`
2. **Security issues**: Exposes internal architecture
3. **Debugging nightmare**: "Works on my machine" syndrome
4. **Firewall problems**: Localhost not accessible through firewall
5. **Scalability**: Can't separate frontend/backend servers later

---

## ✅ Correct Patterns

### Good API Calls

```javascript
// ✅ GOOD: Relative URL (Nginx handles routing)
fetch('/api/suppliers');

// ✅ GOOD: Full public URL
fetch('http://72.60.176.200:8080/api/suppliers');

// ✅ GOOD: Using configured base URL
const BASE = getApiBaseUrl(); // Returns: http://72.60.176.200:8080/api
fetch(`${BASE}/suppliers`);
```

### Environment Variables

```bash
# .env.production
VITE_API_BASE_URL=http://72.60.176.200:8080/api

# .env.production (future with domain)
VITE_API_BASE_URL=https://optura.nl/api
```

---

## 🔒 Security Benefits

### Public API Design

1. **Firewall Friendly**: Single entry point (port 8080)
2. **HTTPS Ready**: Easy to add SSL certificate to Nginx
3. **Rate Limiting**: Nginx can limit API requests
4. **Authentication**: Backend validates all API requests
5. **CORS Control**: Backend controls allowed origins

### Internal Communication

- Nginx → Backend uses `127.0.0.1:5001` (internal only)
- Backend not exposed directly to internet
- Firewall only needs port 8080 open (+ 443 for HTTPS)

---

## 🎯 Production Checklist

### Deployment Verification

- [ ] Frontend uses `getApiBaseUrl()` for all API calls
- [ ] No `localhost` strings in frontend code
- [ ] Backend binds to `0.0.0.0:5001` (not `127.0.0.1:5001`)
- [ ] Nginx listens on `0.0.0.0:8080` (all interfaces)
- [ ] Nginx proxies `/api` to backend
- [ ] Firewall allows port 8080
- [ ] Test from external network: `curl http://72.60.176.200:8080/`
- [ ] Test API from external network: `curl http://72.60.176.200:8080/api/suppliers`

### Build Time

```bash
# Frontend build
cd frontend
npm run build
# Check: dist/assets/*.js should NOT contain "localhost"
grep -r "localhost" dist/ || echo "✅ No localhost references"
```

---

## 🚀 Future Enhancements

### Phase 1: Current (HTTP)
```
http://72.60.176.200:8080/
http://72.60.176.200:8080/api/*
```

### Phase 2: Domain + HTTPS
```
https://optura.nl/
https://optura.nl/api/*
```

### Phase 3: Separate Services (Optional)
```
Frontend: https://app.optura.nl/
API:      https://api.optura.nl/
```

---

## 📝 Testing Commands

### External Access Tests

```bash
# From ANY computer (not the VPS)

# Test frontend
curl http://72.60.176.200:8080/

# Test API
curl http://72.60.176.200:8080/api/suppliers

# Test health
curl http://72.60.176.200:8080/health

# Test with browser
# Open: http://72.60.176.200:8080
# Open DevTools → Network tab
# All API calls should go to: http://72.60.176.200:8080/api/*
```

### What You Should See

In browser DevTools Network tab:
```
✅ GET http://72.60.176.200:8080/ → 200 (HTML)
✅ GET http://72.60.176.200:8080/api/suppliers → 200 (JSON)
✅ POST http://72.60.176.200:8080/api/suppliers → 201 (JSON)

❌ NEVER: http://localhost:5001/...
❌ NEVER: http://127.0.0.1:5001/...
```

---

## 📚 Related Documentation

- **API Service**: `frontend/src/services/api.js`
- **Environment Config**: `frontend/src/lib/env.js`
- **Backend Main**: `src/main.py`
- **Deployment**: `.github/workflows/v1d-devdeploy.yml`

---

**Summary**: The application is designed as a **public API-first architecture** where all communication flows through externally accessible URLs. No internal `localhost` references should ever appear in frontend code or be visible to end users.
