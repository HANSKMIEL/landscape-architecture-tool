# API Documentation

## Overview

The Landscape Architecture Tool API is a RESTful web service that provides programmatic access to manage suppliers, plants, products, projects, and clients. This document serves as the comprehensive reference for all available endpoints.

**Base URL**: 
- Development: `http://localhost:5000/api`
- Production: `https://optura.nl/api`
- DevDeploy: `http://72.60.176.200:8080/api`

**API Version**: v1 (implied in all endpoints)

## Table of Contents

1. [Authentication](#authentication)
2. [Common Patterns](#common-patterns)
3. [Suppliers API](#suppliers-api)
4. [Plants API](#plants-api)
5. [Products API](#products-api)
6. [Projects API](#projects-api)
7. [Clients API](#clients-api)
8. [Health Check](#health-check)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## Authentication

**Status**: Currently, the API does not require authentication for most operations. Future versions will implement token-based authentication.

**Planned Implementation**:
```http
Authorization: Bearer <token>
```

---

## Common Patterns

### Request Headers

All requests should include:
```http
Content-Type: application/json
Accept: application/json
```

### Response Format

All successful responses follow this structure:

```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2025-10-24T13:00:00Z"
  }
}
```

For list responses:
```json
{
  "status": "success",
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "timestamp": "2025-10-24T13:00:00Z"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server maintenance |

### Pagination

List endpoints support pagination:

**Query Parameters**:
- `page` (default: 1) - Page number
- `per_page` (default: 20, max: 100) - Items per page

**Example**:
```http
GET /api/suppliers?page=2&per_page=50
```

### Filtering and Search

Many list endpoints support filtering:

**Query Parameters**:
- `search` - Full-text search across relevant fields
- `sort` - Sort field (prefix with `-` for descending)
- `filter[field]` - Filter by specific field value

**Example**:
```http
GET /api/suppliers?search=tree&sort=-created_at&filter[country]=Netherlands
```

---

## Suppliers API

Manage landscape architecture suppliers.

### List All Suppliers

```http
GET /api/suppliers
```

**Query Parameters**:
- `page` (integer) - Page number
- `per_page` (integer) - Items per page
- `search` (string) - Search suppliers by name, specialty, or location
- `sort` (string) - Sort field (e.g., `name`, `-created_at`)

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Green Suppliers BV",
      "specialty": "Native Plants",
      "contact_person": "Jan de Vries",
      "email": "jan@greensuppliers.nl",
      "phone": "+31 20 1234567",
      "address": "Hoofdstraat 123",
      "city": "Amsterdam",
      "postal_code": "1012 AB",
      "country": "Netherlands",
      "website": "https://greensuppliers.nl",
      "notes": "Primary supplier for native species",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-03-20T14:45:00Z"
    }
  ],
  "meta": {
    "total": 45,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

### Get Supplier by ID

```http
GET /api/suppliers/{id}
```

**Path Parameters**:
- `id` (integer, required) - Supplier ID

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Green Suppliers BV",
    "specialty": "Native Plants",
    "contact_person": "Jan de Vries",
    "email": "jan@greensuppliers.nl",
    "phone": "+31 20 1234567",
    "address": "Hoofdstraat 123",
    "city": "Amsterdam",
    "postal_code": "1012 AB",
    "country": "Netherlands",
    "website": "https://greensuppliers.nl",
    "notes": "Primary supplier for native species",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-03-20T14:45:00Z"
  }
}
```

**Errors**:
- 404 Not Found - Supplier does not exist

### Create Supplier

```http
POST /api/suppliers
```

**Request Body**:
```json
{
  "name": "Green Suppliers BV",
  "specialty": "Native Plants",
  "contact_person": "Jan de Vries",
  "email": "jan@greensuppliers.nl",
  "phone": "+31 20 1234567",
  "address": "Hoofdstraat 123",
  "city": "Amsterdam",
  "postal_code": "1012 AB",
  "country": "Netherlands",
  "website": "https://greensuppliers.nl",
  "notes": "Primary supplier for native species"
}
```

**Required Fields**:
- `name` (string, max 200)
- `email` (valid email)

**Optional Fields**:
- `specialty` (string, max 200)
- `contact_person` (string, max 200)
- `phone` (string, max 50)
- `address` (string, max 500)
- `city` (string, max 100)
- `postal_code` (string, max 20)
- `country` (string, max 100)
- `website` (valid URL, max 500)
- `notes` (text)

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Green Suppliers BV",
    ...
  }
}
```

**Errors**:
- 400 Bad Request - Invalid input data
- 422 Unprocessable Entity - Validation failed

### Update Supplier

```http
PUT /api/suppliers/{id}
```

**Path Parameters**:
- `id` (integer, required) - Supplier ID

**Request Body**: Same as Create Supplier (all fields optional for PUT)

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Green Suppliers BV - Updated",
    ...
  }
}
```

**Errors**:
- 404 Not Found - Supplier does not exist
- 400 Bad Request - Invalid input data
- 422 Unprocessable Entity - Validation failed

### Delete Supplier

```http
DELETE /api/suppliers/{id}
```

**Path Parameters**:
- `id` (integer, required) - Supplier ID

**Response** (204 No Content)

**Errors**:
- 404 Not Found - Supplier does not exist

---

## Plants API

Manage plant catalog.

### List All Plants

```http
GET /api/plants
```

**Query Parameters**:
- `page` (integer) - Page number
- `per_page` (integer) - Items per page
- `search` (string) - Search by botanical or common name
- `filter[type]` (string) - Filter by plant type
- `filter[native]` (boolean) - Filter by native status
- `sort` (string) - Sort field

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "botanical_name": "Quercus robur",
      "common_name": "English Oak",
      "family": "Fagaceae",
      "type": "Tree",
      "native": true,
      "height_min": 20.0,
      "height_max": 40.0,
      "spread_min": 10.0,
      "spread_max": 20.0,
      "growth_rate": "Slow",
      "soil_type": "Clay, Loam",
      "soil_ph": "Neutral to slightly alkaline",
      "light_requirements": "Full sun to partial shade",
      "water_requirements": "Medium",
      "hardiness_zone": "4-8",
      "maintenance_level": "Low",
      "wildlife_value": "High",
      "seasonal_interest": "Spring flowers, autumn color",
      "notes": "Excellent native tree for large spaces",
      "supplier_id": 1,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-03-20T14:45:00Z"
    }
  ],
  "meta": {
    "total": 250,
    "page": 1,
    "per_page": 20,
    "total_pages": 13
  }
}
```

### Get Plant by ID

```http
GET /api/plants/{id}
```

**Response** (200 OK): Single plant object

### Create Plant

```http
POST /api/plants
```

**Required Fields**:
- `botanical_name` (string, max 200, unique)
- `type` (enum: Tree, Shrub, Perennial, Grass, Fern, Groundcover, Climber)

**Optional Fields**:
- `common_name` (string, max 200)
- `family` (string, max 100)
- `native` (boolean, default: false)
- `height_min` (float)
- `height_max` (float)
- `spread_min` (float)
- `spread_max` (float)
- `growth_rate` (enum: Slow, Medium, Fast)
- `soil_type` (string, max 200)
- `soil_ph` (string, max 100)
- `light_requirements` (string, max 200)
- `water_requirements` (enum: Low, Medium, High)
- `hardiness_zone` (string, max 50)
- `maintenance_level` (enum: Low, Medium, High)
- `wildlife_value` (enum: Low, Medium, High)
- `seasonal_interest` (string, max 500)
- `notes` (text)
- `supplier_id` (integer, foreign key)

**Response** (201 Created): Created plant object

### Update Plant

```http
PUT /api/plants/{id}
```

**Response** (200 OK): Updated plant object

### Delete Plant

```http
DELETE /api/plants/{id}
```

**Response** (204 No Content)

---

## Products API

Manage landscape products and materials.

### List All Products

```http
GET /api/products
```

**Query Parameters**:
- `page`, `per_page`, `search`, `sort` (standard pagination)
- `filter[category]` (string) - Filter by product category
- `filter[in_stock]` (boolean) - Filter by stock availability

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Premium Mulch",
      "category": "Soil Amendment",
      "description": "Organic bark mulch for garden beds",
      "sku": "MUL-001",
      "unit": "cubic meter",
      "price": 45.50,
      "currency": "EUR",
      "stock_quantity": 100,
      "minimum_order": 2,
      "supplier_id": 1,
      "supplier_name": "Green Suppliers BV",
      "specifications": {
        "coverage": "10 sqm per cubic meter",
        "depth": "5-10 cm recommended"
      },
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-03-20T14:45:00Z"
    }
  ],
  "meta": {
    "total": 180,
    "page": 1,
    "per_page": 20,
    "total_pages": 9
  }
}
```

### Get Product by ID

```http
GET /api/products/{id}
```

### Create Product

```http
POST /api/products
```

**Required Fields**:
- `name` (string, max 200)
- `category` (string, max 100)
- `price` (decimal)

**Optional Fields**:
- `description` (text)
- `sku` (string, max 100, unique)
- `unit` (string, max 50)
- `currency` (string, max 3, default: EUR)
- `stock_quantity` (integer)
- `minimum_order` (integer)
- `supplier_id` (integer, foreign key)
- `specifications` (JSON)

### Update Product

```http
PUT /api/products/{id}
```

### Delete Product

```http
DELETE /api/products/{id}
```

---

## Projects API

Manage landscape architecture projects.

### List All Projects

```http
GET /api/projects
```

**Query Parameters**:
- Standard pagination parameters
- `filter[status]` (enum: Planning, Active, Completed, On Hold, Cancelled)
- `filter[client_id]` (integer) - Filter by client

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Amstelpark Renovation",
      "description": "Complete renovation of public park gardens",
      "client_id": 1,
      "client_name": "City of Amsterdam",
      "location": "Amsterdam, Netherlands",
      "status": "Active",
      "start_date": "2025-04-01",
      "end_date": "2025-10-31",
      "budget": 500000.00,
      "currency": "EUR",
      "area_sqm": 15000.0,
      "project_type": "Public Park",
      "lead_designer": "Anna van der Berg",
      "notes": "Focus on native species and biodiversity",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-03-20T14:45:00Z"
    }
  ],
  "meta": {
    "total": 32,
    "page": 1,
    "per_page": 20,
    "total_pages": 2
  }
}
```

### Get Project by ID

```http
GET /api/projects/{id}
```

### Create Project

```http
POST /api/projects
```

**Required Fields**:
- `name` (string, max 200)
- `client_id` (integer, foreign key)

**Optional Fields**:
- `description` (text)
- `location` (string, max 500)
- `status` (enum: Planning, Active, Completed, On Hold, Cancelled)
- `start_date` (date)
- `end_date` (date)
- `budget` (decimal)
- `currency` (string, max 3, default: EUR)
- `area_sqm` (float)
- `project_type` (string, max 100)
- `lead_designer` (string, max 200)
- `notes` (text)

### Update Project

```http
PUT /api/projects/{id}
```

### Delete Project

```http
DELETE /api/projects/{id}
```

---

## Clients API

Manage landscape architecture clients.

### List All Clients

```http
GET /api/clients
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "City of Amsterdam",
      "type": "Public Sector",
      "contact_person": "Maria Jansen",
      "email": "m.jansen@amsterdam.nl",
      "phone": "+31 20 5551234",
      "address": "Amstel 1",
      "city": "Amsterdam",
      "postal_code": "1011 PN",
      "country": "Netherlands",
      "website": "https://amsterdam.nl",
      "notes": "Long-term client for public projects",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-03-20T14:45:00Z"
    }
  ],
  "meta": {
    "total": 25,
    "page": 1,
    "per_page": 20,
    "total_pages": 2
  }
}
```

### Get Client by ID

```http
GET /api/clients/{id}
```

### Create Client

```http
POST /api/clients
```

**Required Fields**:
- `name` (string, max 200)
- `email` (valid email)

**Optional Fields**:
- `type` (enum: Private, Commercial, Public Sector, Non-Profit)
- `contact_person` (string, max 200)
- `phone` (string, max 50)
- `address` (string, max 500)
- `city` (string, max 100)
- `postal_code` (string, max 20)
- `country` (string, max 100)
- `website` (valid URL, max 500)
- `notes` (text)

### Update Client

```http
PUT /api/clients/{id}
```

### Delete Client

```http
DELETE /api/clients/{id}
```

---

## Health Check

Check API availability and status.

### Health Endpoint

```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-24T13:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

**Response** (503 Service Unavailable) if unhealthy:
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2025-10-24T13:00:00Z",
  "services": {
    "database": "error",
    "redis": "disconnected"
  }
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed for one or more fields",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-10-24T13:00:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400, 422 | Input validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Validation Errors

Validation errors include specific field-level details:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "not-an-email"
      },
      {
        "field": "phone",
        "message": "Phone number is required",
        "value": null
      }
    ]
  }
}
```

---

## Rate Limiting

**Current Status**: Not implemented

**Planned Implementation**:
- 100 requests per minute per IP address
- 1000 requests per hour per authenticated user
- Headers included in responses:
  - `X-RateLimit-Limit` - Request limit
  - `X-RateLimit-Remaining` - Remaining requests
  - `X-RateLimit-Reset` - Reset time (Unix timestamp)

---

## OpenAPI/Swagger Specification

**Status**: Planned

A machine-readable OpenAPI 3.0 specification will be available at:
- `/api/openapi.json` - JSON format
- `/api/openapi.yaml` - YAML format
- `/api/docs` - Interactive Swagger UI

---

## Future Enhancements

### Planned Features

1. **Authentication & Authorization**
   - JWT token-based authentication
   - Role-based access control (RBAC)
   - API key management

2. **Webhooks**
   - Event notifications for resource changes
   - Configurable webhook endpoints

3. **Bulk Operations**
   - Batch create/update/delete operations
   - CSV import/export

4. **Advanced Search**
   - Full-text search across all resources
   - Complex filtering with AND/OR logic
   - Faceted search

5. **File Uploads**
   - Image uploads for plants/projects
   - Document attachments
   - Photo galleries

6. **Reporting API**
   - Custom report generation
   - Data export in multiple formats
   - Analytics endpoints

---

## Support

For API issues or questions:
- Create an issue on GitHub
- Check the [DEBUGGING_GUIDE.md](./DEBUGGING_GUIDE.md)
- Review [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)

---

## Versioning

The API follows semantic versioning (SemVer):
- **Major version** - Breaking changes
- **Minor version** - New features (backward compatible)
- **Patch version** - Bug fixes

Current version: **v1.0.0**

API version is included in all responses via the `X-API-Version` header.

---

## License

See [LICENSE](../LICENSE) file for details.
