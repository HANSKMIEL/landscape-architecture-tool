import { http, HttpResponse } from 'msw'
import {
  createMockPlants,
  createMockProjects,
  createMockClients,
  createMockSuppliers,
  createMockDashboardStats,
  createMockRecentActivity,
  createMockPlant,
  createMockProject,
  createMockClient,
  createMockSupplier,
  createApiResponse
} from '../utils/mockData'

const API_BASE = 'http://127.0.0.1:5000/api'

export const handlers = [
  // Dashboard endpoints
  http.get(`${API_BASE}/dashboard/stats`, () => {
    return HttpResponse.json(createMockDashboardStats())
  }),

  http.get(`${API_BASE}/dashboard/recent-activity`, () => {
    return HttpResponse.json(createMockRecentActivity())
  }),

  // Plants endpoints
  http.get(`${API_BASE}/plants`, ({ request }) => {
    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const limit = parseInt(url.searchParams.get('limit')) || 10
    
    let plants = createMockPlants(limit)
    
    if (search) {
      plants = plants.filter(plant => 
        plant.name.toLowerCase().includes(search.toLowerCase()) ||
        plant.common_name.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    // Return plants array directly, not wrapped
    return HttpResponse.json(plants)
  }),

  http.get(`${API_BASE}/plants/:id`, ({ params }) => {
    const plant = createMockPlant({ id: parseInt(params.id) })
    return HttpResponse.json(plant)
  }),

  http.post(`${API_BASE}/plants`, async ({ request }) => {
    const newPlant = await request.json()
    const plant = createMockPlant({ ...newPlant, id: Date.now() })
    return HttpResponse.json(plant, { status: 201 })
  }),

  http.put(`${API_BASE}/plants/:id`, async ({ params, request }) => {
    const updates = await request.json()
    const plant = createMockPlant({ ...updates, id: parseInt(params.id) })
    return HttpResponse.json(plant)
  }),

  http.delete(`${API_BASE}/plants/:id`, ({ params }) => {
    return HttpResponse.json({ message: 'Plant deleted successfully' })
  }),

  http.get(`${API_BASE}/plants/categories`, () => {
    return HttpResponse.json([
      'Tree', 'Shrub', 'Perennial', 'Annual', 'Grass', 'Fern', 'Vine'
    ])
  }),

  http.post(`${API_BASE}/plants/recommendations`, async ({ request }) => {
    const criteria = await request.json()
    const plants = createMockPlants(5)
    return HttpResponse.json(createApiResponse(plants))
  }),

  // Projects endpoints
  http.get(`${API_BASE}/projects`, ({ request }) => {
    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const status = url.searchParams.get('status')
    const limit = parseInt(url.searchParams.get('limit')) || 10
    
    let projects = createMockProjects(limit)
    
    if (search) {
      projects = projects.filter(project => 
        project.name.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    if (status) {
      projects = projects.filter(project => project.status === status)
    }
    
    // Return projects array directly, not wrapped
    return HttpResponse.json(projects)
  }),

  http.get(`${API_BASE}/projects/:id`, ({ params }) => {
    const project = createMockProject({ id: parseInt(params.id) })
    return HttpResponse.json(project)
  }),

  http.post(`${API_BASE}/projects`, async ({ request }) => {
    const newProject = await request.json()
    const project = createMockProject({ ...newProject, id: Date.now() })
    return HttpResponse.json(project, { status: 201 })
  }),

  http.put(`${API_BASE}/projects/:id`, async ({ params, request }) => {
    const updates = await request.json()
    const project = createMockProject({ ...updates, id: parseInt(params.id) })
    return HttpResponse.json(project)
  }),

  http.delete(`${API_BASE}/projects/:id`, ({ params }) => {
    return HttpResponse.json({ message: 'Project deleted successfully' })
  }),

  // Clients endpoints
  http.get(`${API_BASE}/clients`, ({ request }) => {
    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const limit = parseInt(url.searchParams.get('limit')) || 10
    
    let clients = createMockClients(limit)
    
    if (search) {
      clients = clients.filter(client => 
        client.name.toLowerCase().includes(search.toLowerCase()) ||
        client.email.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    // Return clients array directly, not wrapped
    return HttpResponse.json(clients)
  }),

  http.get(`${API_BASE}/clients/:id`, ({ params }) => {
    const client = createMockClient({ id: parseInt(params.id) })
    return HttpResponse.json(client)
  }),

  http.post(`${API_BASE}/clients`, async ({ request }) => {
    const newClient = await request.json()
    const client = createMockClient({ ...newClient, id: Date.now() })
    return HttpResponse.json(client, { status: 201 })
  }),

  http.put(`${API_BASE}/clients/:id`, async ({ params, request }) => {
    const updates = await request.json()
    const client = createMockClient({ ...updates, id: parseInt(params.id) })
    return HttpResponse.json(client)
  }),

  http.delete(`${API_BASE}/clients/:id`, ({ params }) => {
    return HttpResponse.json({ message: 'Client deleted successfully' })
  }),

  // Suppliers endpoints
  http.get(`${API_BASE}/suppliers`, ({ request }) => {
    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const limit = parseInt(url.searchParams.get('limit')) || 10
    
    let suppliers = createMockSuppliers(limit)
    
    if (search) {
      suppliers = suppliers.filter(supplier => 
        supplier.name.toLowerCase().includes(search.toLowerCase()) ||
        supplier.specialties.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    // Return suppliers array directly, not wrapped
    return HttpResponse.json(suppliers)
  }),

  http.get(`${API_BASE}/suppliers/:id`, ({ params }) => {
    const supplier = createMockSupplier({ id: parseInt(params.id) })
    return HttpResponse.json(supplier)
  }),

  http.post(`${API_BASE}/suppliers`, async ({ request }) => {
    const newSupplier = await request.json()
    const supplier = createMockSupplier({ ...newSupplier, id: Date.now() })
    return HttpResponse.json(supplier, { status: 201 })
  }),

  http.put(`${API_BASE}/suppliers/:id`, async ({ params, request }) => {
    const updates = await request.json()
    const supplier = createMockSupplier({ ...updates, id: parseInt(params.id) })
    return HttpResponse.json(supplier)
  }),

  http.delete(`${API_BASE}/suppliers/:id`, ({ params }) => {
    return HttpResponse.json({ message: 'Supplier deleted successfully' })
  }),

  // Error scenarios for testing
  http.get(`${API_BASE}/error/500`, () => {
    return HttpResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    )
  }),

  http.get(`${API_BASE}/error/404`, () => {
    return HttpResponse.json(
      { error: 'Not Found' },
      { status: 404 }
    )
  }),

  http.get(`${API_BASE}/error/timeout`, () => {
    return new Promise(() => {
      // Never resolves, simulates timeout
    })
  })
]