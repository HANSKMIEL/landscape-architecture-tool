# External Integration Guide

**Landscape Architecture Tool API - Version 2.0.0**

This guide provides complete information for integrating external software with the Landscape Architecture Tool API.

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Code Examples](#code-examples)
5. [Rate Limiting](#rate-limiting)
6. [N8n Integration](#n8n-integration)
7. [Error Handling](#error-handling)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Base URLs

**Development**:

```
http://localhost:5000
```

**V1.00D DevDeploy**:

```
http://72.60.176.200:8080
```

**Production** (V1.00):

```
https://optura.nl
```

### Interactive API Documentation

Visit the Swagger UI for interactive API testing:

```
http://localhost:5000/api/docs
```

### Health Check

Test API connectivity:

```bash
curl http://localhost:5000/health
```

---

## 🔐 Authentication

### Current: Session-Based Authentication

The API currently uses session-based authentication for the web interface.

**Login**:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

**Response**:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user"
  },
  "message": "Login successful"
}
```

Session cookie will be set automatically.

### Coming Soon: API Key Authentication

API key authentication for external integrations will be available soon. This will allow:

- Separate authentication from user sessions
- Revocable access tokens
- Usage tracking per integration
- Programmatic access without user credentials

---

## 📡 API Endpoints

### Core Resources

#### Suppliers

- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Create new supplier
- `GET /api/suppliers/{id}` - Get supplier by ID
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Delete supplier

#### Plants

- `GET /api/plants` - List all plants
- `POST /api/plants` - Create new plant
- `GET /api/plants/{id}` - Get plant by ID
- `PUT /api/plants/{id}` - Update plant
- `DELETE /api/plants/{id}` - Delete plant

#### Products

- `GET /api/products` - List all products
- `POST /api/products` - Create new product
- `GET /api/products/{id}` - Get product by ID
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

#### Clients

- `GET /api/clients` - List all clients
- `POST /api/clients` - Create new client
- `GET /api/clients/{id}` - Get client by ID
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

#### Projects

- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project by ID
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Analytics & Insights

- `GET /api/analytics/summary` - Analytics summary
- `GET /api/analytics/plant-usage` - Plant usage statistics
- `GET /api/analytics/project-performance` - Project performance metrics
- `GET /api/analytics/client-insights` - Client insights
- `GET /api/analytics/financial` - Financial reporting

### Dashboard

- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/recent-activity` - Recent activity

### AI & Recommendations

- `GET /api/plant-recommendations` - Get plant recommendations
- `POST /api/plant-recommendations/evaluate` - Evaluate recommendations
- `GET /api/plant-recommendations/criteria-options` - Get criteria options

### Data Management

- `POST /api/excel/import` - Import data from Excel
- `GET /api/excel/template` - Download Excel template
- `POST /api/photos/upload` - Upload photos
- `GET /api/photos` - List photos

---

## 💻 Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Get all suppliers
response = requests.get(f"{BASE_URL}/api/suppliers")
suppliers = response.json()

print(f"Found {len(suppliers['suppliers'])} suppliers")
for supplier in suppliers['suppliers']:
    print(f"- {supplier['name']}: {supplier['email']}")

# Create new supplier
new_supplier = {
    "name": "Green Gardens BV",
    "contact_person": "Jane Smith",
    "email": "jane@greengardens.nl",
    "phone": "+31 20 123 4567",
    "address": "Garden Street 456",
    "city": "Amsterdam",
    "postal_code": "1012 CD",
    "country": "Netherlands"
}

response = requests.post(
    f"{BASE_URL}/api/suppliers",
    json=new_supplier
)

if response.status_code == 201:
    supplier = response.json()['supplier']
    print(f"Created supplier with ID: {supplier['id']}")
else:
    print(f"Error: {response.json()}")
```

### JavaScript (Node.js)

```javascript
const axios = require("axios");

const BASE_URL = "http://localhost:5000";

// Get all plants
async function getPlants() {
  try {
    const response = await axios.get(`${BASE_URL}/api/plants`);
    const plants = response.data.plants;

    console.log(`Found ${plants.length} plants`);
    plants.forEach((plant) => {
      console.log(`- ${plant.botanical_name} (${plant.common_name})`);
    });
  } catch (error) {
    console.error("Error:", error.response?.data || error.message);
  }
}

// Create new plant
async function createPlant() {
  try {
    const newPlant = {
      botanical_name: "Rosa 'Peace'",
      common_name: "Peace Rose",
      category: "Roses",
      height: "120-150 cm",
      spread: "90 cm",
      color: "Yellow with pink edges",
      bloom_time: "Summer",
      sun_requirements: "Full sun",
      water_requirements: "Moderate",
      soil_type: "Well-drained, fertile",
    };

    const response = await axios.post(`${BASE_URL}/api/plants`, newPlant);

    console.log("Created plant:", response.data.plant);
  } catch (error) {
    console.error("Error:", error.response?.data || error.message);
  }
}

getPlants();
```

### cURL

```bash
# Get health status
curl http://localhost:5000/health

# List all suppliers
curl http://localhost:5000/api/suppliers

# Get specific supplier
curl http://localhost:5000/api/suppliers/1

# Create new client
curl -X POST http://localhost:5000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+31 6 12345678",
    "address": "Example Street 123",
    "city": "Amsterdam"
  }'

# Update project
curl -X PUT http://localhost:5000/api/projects/5 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Garden Renovation Project - Updated",
    "status": "in_progress"
  }'

# Delete product
curl -X DELETE http://localhost:5000/api/products/10
```

---

## ⚡ Rate Limiting

The API implements rate limiting to ensure fair usage:

**Default Limits**:

- 100 requests per minute per IP address
- 1000 requests per hour per IP address

**Rate Limit Headers**:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1633036800
```

**429 Too Many Requests**:
When rate limit is exceeded:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

**Best Practices**:

- Cache responses when possible
- Implement exponential backoff on errors
- Respect rate limit headers
- Use batch endpoints when available

---

## 🔗 N8n Integration

The API includes built-in N8n webhook support for workflow automation.

### Available Webhooks

#### Client Onboarding

```
POST /webhooks/client-onboarding
```

Payload:

```json
{
  "client_id": 123,
  "client_name": "John Doe",
  "client_email": "john@example.com",
  "timestamp": "2025-10-01T10:00:00Z"
}
```

#### Project Milestone

```
POST /webhooks/project-milestone
```

Payload:

```json
{
  "project_id": 456,
  "project_name": "Garden Project",
  "milestone": "Design Complete",
  "percentage_complete": 30,
  "timestamp": "2025-10-01T10:00:00Z"
}
```

#### Inventory Alert

```
POST /webhooks/inventory-alert
```

Payload:

```json
{
  "product_id": 789,
  "product_name": "Terracotta Pot 30cm",
  "current_stock": 5,
  "threshold": 10,
  "alert_type": "low_stock",
  "timestamp": "2025-10-01T10:00:00Z"
}
```

### N8n Workflow Templates

Workflow templates are available in the repository:

```
n8n-workflows/
├── client-onboarding.json
├── project-milestone-tracking.json
└── inventory-management.json
```

Import these into your N8n instance to get started quickly.

---

## ❌ Error Handling

### Standard Error Response

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Resource deleted successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Validation Errors

```json
{
  "error": "Validation failed",
  "validation_errors": ["Email is required", "Phone number format is invalid"]
}
```

---

## 🔧 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to API

**Solutions**:

```bash
# 1. Check if service is running
curl http://localhost:5000/health

# 2. Verify correct URL
# Development: http://localhost:5000
# DevDeploy: http://72.60.176.200:8080

# 3. Check firewall/network settings
ping 72.60.176.200

# 4. Review logs
tail -f logs/app.log
```

### Authentication Issues

**Problem**: 401 Unauthorized

**Solutions**:

- Ensure you're logged in with valid credentials
- Check if session cookie is being sent
- Verify CORS settings if calling from browser

### Rate Limiting

**Problem**: 429 Too Many Requests

**Solutions**:

```python
import time
import requests

def api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code == 429:
            # Exponential backoff
            wait_time = 2 ** attempt
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

### Data Issues

**Problem**: Validation errors

**Solutions**:

- Check required fields are present
- Verify data types match schema
- Use API documentation for field formats
- Test with minimal payload first

---

## 📖 Additional Resources

- **API Documentation**: http://localhost:5000/api/docs (Swagger UI)
- **Repository**: https://github.com/HANSKMIEL/landscape-architecture-tool
- **OpenAPI Spec**: http://localhost:5000/api/openapi.json

---

## 🆘 Support

For issues or questions:

1. Check the [Swagger UI documentation](http://localhost:5000/api/docs)
2. Review [troubleshooting section](#troubleshooting)
3. Open an issue on GitHub

---

**Last Updated**: October 1, 2025  
**API Version**: 2.0.0  
**Branch**: V1.00D
