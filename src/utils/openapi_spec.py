"""
OpenAPI 3.0 Specification Generator for Landscape Architecture Tool API
"""

from datetime import datetime


def generate_openapi_spec():
    """
    Generate OpenAPI 3.0 specification for the API
    """
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Landscape Architecture Tool API",
            "description": """
# Landscape Architecture Management System API

Professional API for managing landscape architecture projects, suppliers, plants, products, and clients.

## Features
- **19 API Endpoints** for complete landscape architecture management
- **N8n Integration** with webhook support
- **AI Assistant** for plant recommendations
- **Excel Import/Export** functionality
- **Photo Management** with cloud storage
- **Analytics & Reporting** capabilities

## Authentication
- Session-based authentication for web interface
- API key authentication for external integrations (coming soon)

## Rate Limiting
- Default: 100 requests/minute per IP
- Configurable per endpoint
            """,
            "version": "2.0.0",
            "contact": {
                "name": "Landscape Architecture Tool Support",
                "url": "https://github.com/HANSKMIEL/landscape-architecture-tool"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            },
            {
                "url": "http://72.60.176.200:8080",
                "description": "V1.00D DevDeploy server"
            },
            {
                "url": "https://optura.nl",
                "description": "Production server (V1.00)"
            }
        ],
        "tags": [
            {"name": "Health", "description": "System health and status endpoints"},
            {"name": "Authentication",
                "description": "User authentication and session management"},
            {"name": "Suppliers", "description": "Supplier management operations"},
            {"name": "Plants", "description": "Plant catalog and management"},
            {"name": "Products", "description": "Product catalog and inventory"},
            {"name": "Clients", "description": "Client management"},
            {"name": "Projects", "description": "Project management and tracking"},
            {"name": "Analytics", "description": "Analytics and statistics"},
            {"name": "Dashboard", "description": "Dashboard data and insights"},
            {"name": "Reports", "description": "Report generation"},
            {"name": "Invoices", "description": "Invoice and quote management"},
            {"name": "Photos", "description": "Photo upload and management"},
            {"name": "Plant Recommendations",
                "description": "AI-powered plant recommendations"},
            {"name": "Excel Import", "description": "Bulk data import from Excel"},
            {"name": "Settings", "description": "Application settings"},
            {"name": "N8n Webhooks", "description": "N8n integration webhooks"},
            {"name": "AI Assistant", "description": "AI-powered assistance"},
            {"name": "Performance", "description": "Performance monitoring"}
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Health check endpoint",
                    "description": "Returns system health status, version, and dependency information",
                    "operationId": "getHealth",
                    "responses": {
                        "200": {
                            "description": "System is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "timestamp": {"type": "string", "format": "date-time"},
                                            "version": {"type": "string", "example": "2.0.0"},
                                            "environment": {"type": "string", "example": "development"},
                                            "database_status": {"type": "string", "example": "connected"},
                                            "dependencies": {"type": "object"},
                                            "services": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "503": {
                            "description": "System is unhealthy - critical dependencies missing"
                        }
                    }
                }
            },
            "/api": {
                "get": {
                    "tags": ["Health"],
                    "summary": "API information and available routes",
                    "description": "Returns list of all available API endpoints",
                    "operationId": "getApiInfo",
                    "responses": {
                        "200": {
                            "description": "API information retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "version": {"type": "string"},
                                            "endpoints": {"type": "array", "items": {"type": "string"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/suppliers": {
                "get": {
                    "tags": ["Suppliers"],
                    "summary": "List all suppliers",
                    "description": "Returns a list of all suppliers in the system",
                    "operationId": "listSuppliers",
                    "responses": {
                        "200": {
                            "description": "Suppliers retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "suppliers": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Supplier"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Suppliers"],
                    "summary": "Create a new supplier",
                    "description": "Creates a new supplier in the system",
                    "operationId": "createSupplier",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SupplierCreate"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Supplier created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "supplier": {"$ref": "#/components/schemas/Supplier"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {"description": "Invalid input"}
                    }
                }
            },
            "/api/suppliers/{supplier_id}": {
                "get": {
                    "tags": ["Suppliers"],
                    "summary": "Get supplier by ID",
                    "description": "Returns a single supplier by ID",
                    "operationId": "getSupplier",
                    "parameters": [
                        {
                            "name": "supplier_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "description": "Supplier ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Supplier retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "supplier": {"$ref": "#/components/schemas/Supplier"}
                                        }
                                    }
                                }
                            }
                        },
                        "404": {"description": "Supplier not found"}
                    }
                },
                "put": {
                    "tags": ["Suppliers"],
                    "summary": "Update supplier",
                    "description": "Updates an existing supplier",
                    "operationId": "updateSupplier",
                    "parameters": [
                        {
                            "name": "supplier_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SupplierUpdate"}
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Supplier updated successfully"},
                        "404": {"description": "Supplier not found"}
                    }
                },
                "delete": {
                    "tags": ["Suppliers"],
                    "summary": "Delete supplier",
                    "description": "Deletes a supplier by ID",
                    "operationId": "deleteSupplier",
                    "parameters": [
                        {
                            "name": "supplier_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "204": {"description": "Supplier deleted successfully"},
                        "404": {"description": "Supplier not found"}
                    }
                }
            },
            "/api/analytics/summary": {
                "get": {
                    "tags": ["Analytics"],
                    "summary": "Get analytics summary",
                    "description": "Returns comprehensive analytics summary for dashboard",
                    "operationId": "getAnalyticsSummary",
                    "responses": {
                        "200": {
                            "description": "Analytics summary retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "suppliers": {"type": "object"},
                                            "plants": {"type": "object"},
                                            "products": {"type": "object"},
                                            "clients": {"type": "object"},
                                            "projects": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Supplier": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "name": {"type": "string", "example": "Green Supplies BV"},
                        "contact_person": {"type": "string", "example": "John Doe"},
                        "email": {"type": "string", "format": "email", "example": "john@greensupplies.nl"},
                        "phone": {"type": "string", "example": "+31 20 123 4567"},
                        "address": {"type": "string", "example": "Main Street 123"},
                        "city": {"type": "string", "example": "Amsterdam"},
                        "postal_code": {"type": "string", "example": "1012 AB"},
                        "country": {"type": "string", "example": "Netherlands"},
                        "notes": {"type": "string", "nullable": True},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                },
                "SupplierCreate": {
                    "type": "object",
                    "required": ["name", "email"],
                    "properties": {
                        "name": {"type": "string"},
                        "contact_person": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"},
                        "city": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "notes": {"type": "string"}
                    }
                },
                "SupplierUpdate": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "contact_person": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"},
                        "city": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "notes": {"type": "string"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "message": {"type": "string"}
                    }
                }
            },
            "securitySchemes": {
                "cookieAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "session",
                    "description": "Session-based authentication"
                },
                "apiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key authentication (coming in Phase 4)"
                }
            }
        }
    }

    return spec
