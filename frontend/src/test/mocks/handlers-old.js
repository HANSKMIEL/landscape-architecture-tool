import { http, HttpResponse } from 'msw';
import { 
  createMockArray, 
  createMockPlant, 
  createMockProject, 
  createMockClient, 
  createMockSupplier,
  createMockRecommendation,
  createMockDashboardStats,
  createMockActivity,
  // Import additional mock data from main branch
  createMockPlants,
  createMockProjects,
  createMockClients,
  createMockSuppliers,
  createMockRecentActivity,
  createApiResponse
} from '../utils/mockData';

// Helper function to create handlers for both relative and absolute URLs
const createHandler = (method, relativePath, handler) => [
  http[method](relativePath, handler),
  http[method](`http://localhost:5000${relativePath}`, handler),
  http[method](`http://127.0.0.1:5000${relativePath}`, handler), // Add support for main branch API base
];

export const handlers = [
  // Dashboard endpoints (enhanced from main branch)
  ...createHandler('get', '/api/dashboard/stats', () => {
    return HttpResponse.json(createMockDashboardStats());
  }),

  ...createHandler('get', '/api/dashboard/recent-activity', () => {
    return HttpResponse.json(createMockRecentActivity());
  }),

  // Plant endpoints (merged from both implementations)
  ...createHandler('get', '/api/plants', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');
    const limit = parseInt(url.searchParams.get('limit') || perPage);
    const search = url.searchParams.get('search') || '';
    
    // Use main branch approach for compatibility
    let plants = createMockPlants ? createMockPlants(limit) : createMockArray(createMockPlant, limit);
    
    // Filter by search if provided
    if (search) {
      plants = plants.filter(plant => 
        plant.name.toLowerCase().includes(search.toLowerCase()) ||
        (plant.scientific_name && plant.scientific_name.toLowerCase().includes(search.toLowerCase())) ||
        (plant.common_name && plant.common_name.toLowerCase().includes(search.toLowerCase()))
      );
    }
    
    // Support both response formats - main branch returns array directly
    if (page > 1 || url.searchParams.has('page')) {
      // Paginated response (my format)
      const total = plants.length;
      const startIndex = (page - 1) * perPage;
      const endIndex = startIndex + perPage;
      const paginatedPlants = plants.slice(startIndex, endIndex);
      
      return HttpResponse.json({
        plants: paginatedPlants,
        total: total,
        page: page,
        per_page: perPage,
        pages: Math.ceil(total / perPage)
      });
    } else {
      // Simple array response (main branch format)
      return HttpResponse.json(plants.slice(0, limit));
    }
  }),

  ...createHandler('get', '/api/plants/categories', () => {
    // Main branch format
    return HttpResponse.json([
      'Tree', 'Shrub', 'Perennial', 'Annual', 'Grass', 'Fern', 'Vine'
    ]);
  }),

  ...createHandler('post', '/api/plants/recommendations', async ({ request }) => {
    const _criteria = await request.json();
    const plants = createMockPlants ? createMockPlants(5) : createMockArray(createMockPlant, 5);
    return HttpResponse.json(createApiResponse ? createApiResponse(plants) : plants);
  }),

  ...createHandler('get', '/api/plants/:id', ({ params }) => {
    const id = parseInt(params.id);
    if (isNaN(id)) {
      return HttpResponse.json(
        { error: 'Invalid plant ID' },
        { status: 400 }
      );
    }
    const plant = createMockPlant ? createMockPlant({ id }) : createMockPlants(1)[0];
    return HttpResponse.json(plant);
  }),

  ...createHandler('post', '/api/plants', async ({ request }) => {
    const newPlant = await request.json();
    const plant = createMockPlant ? createMockPlant({ id: Date.now(), ...newPlant }) : createMockPlants(1)[0];
    return HttpResponse.json(plant, { status: 201 });
  }),

  ...createHandler('put', '/api/plants/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    const plant = createMockPlant ? createMockPlant({ id, ...updates }) : createMockPlants(1)[0];
    return HttpResponse.json(plant);
  }),

  ...createHandler('delete', '/api/plants/:id', ({ params }) => {
    const id = parseInt(params.id);
    return HttpResponse.json({ 
      message: `Plant deleted successfully` 
    });
  }),

  // Projects endpoints (merged from both implementations)
  ...createHandler('get', '/api/projects', ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get('search');
    const status = url.searchParams.get('status');
    const limit = parseInt(url.searchParams.get('limit')) || 10;
    
    let projects = createMockProjects ? createMockProjects(limit) : createMockArray(createMockProject, limit);
    
    if (search) {
      projects = projects.filter(project => 
        project.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (status) {
      projects = projects.filter(project => project.status === status);
    }
    
    // Return projects array directly (main branch format)
    return HttpResponse.json(projects);
  }),

  ...createHandler('get', '/api/projects/:id', ({ params }) => {
    const id = parseInt(params.id);
    const project = createMockProject ? createMockProject({ id }) : createMockProjects(1)[0];
    return HttpResponse.json(project);
  }),

  ...createHandler('post', '/api/projects', async ({ request }) => {
    const newProject = await request.json();
    const project = createMockProject ? createMockProject({ id: Date.now(), ...newProject }) : createMockProjects(1)[0];
    return HttpResponse.json(project, { status: 201 });
  }),

  ...createHandler('put', '/api/projects/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    const project = createMockProject ? createMockProject({ id, ...updates }) : createMockProjects(1)[0];
    return HttpResponse.json(project);
  }),

  ...createHandler('delete', '/api/projects/:id', () => {
    return HttpResponse.json({ message: 'Project deleted successfully' });
  }),

  // Clients endpoints
  ...createHandler('get', '/api/clients', ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get('search');
    const limit = parseInt(url.searchParams.get('limit')) || 10;
    
    let clients = createMockClients ? createMockClients(limit) : createMockArray(createMockClient, limit);
    
    if (search) {
      clients = clients.filter(client => 
        client.name.toLowerCase().includes(search.toLowerCase()) ||
        client.email.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    return HttpResponse.json(clients);
  }),

  ...createHandler('get', '/api/clients/:id', ({ params }) => {
    const id = parseInt(params.id);
    const client = createMockClient ? createMockClient({ id }) : createMockClients(1)[0];
    return HttpResponse.json(client);
  }),

  ...createHandler('post', '/api/clients', async ({ request }) => {
    const newClient = await request.json();
    const client = createMockClient ? createMockClient({ id: Date.now(), ...newClient }) : createMockClients(1)[0];
    return HttpResponse.json(client, { status: 201 });
  }),

  ...createHandler('put', '/api/clients/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    const client = createMockClient ? createMockClient({ id, ...updates }) : createMockClients(1)[0];
    return HttpResponse.json(client);
  }),

  ...createHandler('delete', '/api/clients/:id', () => {
    return HttpResponse.json({ message: 'Client deleted successfully' });
  }),

  // Suppliers endpoints
  ...createHandler('get', '/api/suppliers', ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get('search');
    const limit = parseInt(url.searchParams.get('limit')) || 10;
    
    let suppliers = createMockSuppliers ? createMockSuppliers(limit) : createMockArray(createMockSupplier, limit);
    
    if (search) {
      suppliers = suppliers.filter(supplier => 
        supplier.name.toLowerCase().includes(search.toLowerCase()) ||
        (supplier.specialties && supplier.specialties.toLowerCase().includes(search.toLowerCase()))
      );
    }
    
    return HttpResponse.json(suppliers);
  }),

  ...createHandler('get', '/api/suppliers/:id', ({ params }) => {
    const id = parseInt(params.id);
    const supplier = createMockSupplier ? createMockSupplier({ id }) : createMockSuppliers(1)[0];
    return HttpResponse.json(supplier);
  }),

  ...createHandler('post', '/api/suppliers', async ({ request }) => {
    const newSupplier = await request.json();
    const supplier = createMockSupplier ? createMockSupplier({ id: Date.now(), ...newSupplier }) : createMockSuppliers(1)[0];
    return HttpResponse.json(supplier, { status: 201 });
  }),

  ...createHandler('put', '/api/suppliers/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    const supplier = createMockSupplier ? createMockSupplier({ id, ...updates }) : createMockSuppliers(1)[0];
    return HttpResponse.json(supplier);
  }),

  ...createHandler('delete', '/api/suppliers/:id', () => {
    return HttpResponse.json({ message: 'Supplier deleted successfully' });
  }),

  // Error scenarios for testing (from main branch)
  ...createHandler('get', '/api/error/500', () => {
    return HttpResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }),

  ...createHandler('get', '/api/error/404', () => {
    return HttpResponse.json(
      { error: 'Not Found' },
      { status: 404 }
    );
  }),

  ...createHandler('get', '/api/error/timeout', () => {
    return new Promise(() => {
      // Never resolves, simulates timeout
    });
  })
];

  ...createHandler('post', '/api/plants', async ({ request }) => {
    const newPlant = await request.json();
    return HttpResponse.json(
      createMockPlant({ id: 999, ...newPlant }), 
      { status: 201 }
    );
  }),

  ...createHandler('put', '/api/plants/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    return HttpResponse.json(
      createMockPlant({ id, ...updates })
    );
  }),

  ...createHandler('delete', '/api/plants/:id', ({ params }) => {
    const id = parseInt(params.id);
    return HttpResponse.json({ 
      message: `Plant ${id} deleted successfully` 
    });
  }),

  // Plant recommendations endpoint
  ...createHandler('post', '/api/plants/recommendations', async ({ request }) => {
    const criteria = await request.json();
    return HttpResponse.json({
      recommendations: createMockArray(createMockRecommendation, 3),
      criteria: criteria,
      total: 3
    });
  }),

  // Project endpoints
  ...createHandler('get', '/api/projects', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');
    
    const projects = createMockArray(createMockProject, 8);
    const total = projects.length;
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    const paginatedProjects = projects.slice(startIndex, endIndex);
    
    return HttpResponse.json({
      projects: paginatedProjects,
      total: total,
      page: page,
      per_page: perPage,
      pages: Math.ceil(total / perPage)
    });
  }),

  ...createHandler('get', '/api/projects/:id', ({ params }) => {
    const id = parseInt(params.id);
    const projects = createMockArray(createMockProject, 8);
    const project = projects.find(p => p.id === id);
    if (!project) {
      return HttpResponse.json(
        { error: "Project not found" },
        { status: 404 }
      );
    }
    return HttpResponse.json(project);
  }),

  ...createHandler('post', '/api/projects', async ({ request }) => {
    const newProject = await request.json();
    return HttpResponse.json(
      createMockProject({ id: 999, ...newProject }), 
      { status: 201 }
    );
  }),

  ...createHandler('put', '/api/projects/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    return HttpResponse.json(
      createMockProject({ id, ...updates })
    );
  }),

  ...createHandler('delete', '/api/projects/:id', ({ params }) => {
    const id = parseInt(params.id);
    return HttpResponse.json({ 
      message: `Project ${id} deleted successfully` 
    });
  }),

  // Client endpoints
  ...createHandler('get', '/api/clients', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');
    
    const clients = createMockArray(createMockClient, 12);
    const total = clients.length;
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    const paginatedClients = clients.slice(startIndex, endIndex);
    
    return HttpResponse.json({
      clients: paginatedClients,
      total: total,
      page: page,
      per_page: perPage,
      pages: Math.ceil(total / perPage)
    });
  }),

  ...createHandler('get', '/api/clients/:id', ({ params }) => {
    const id = parseInt(params.id);
    const clients = createMockArray(createMockClient, 12); // Mock list of clients
    const client = clients.find(client => client.id === id);
    
    if (!client) {
      return HttpResponse.json(
        { error: "Client not found" },
        { status: 404 }
      );
    }
    
    return HttpResponse.json(client);
  }),

  ...createHandler('post', '/api/clients', async ({ request }) => {
    const newClient = await request.json();
    return HttpResponse.json(
      createMockClient({ id: 999, ...newClient }), 
      { status: 201 }
    );
  }),

  // Supplier endpoints
  ...createHandler('get', '/api/suppliers', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');
    
    const suppliers = createMockArray(createMockSupplier, 10);
    const total = suppliers.length;
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    const paginatedSuppliers = suppliers.slice(startIndex, endIndex);
    
    return HttpResponse.json({
      suppliers: paginatedSuppliers,
      total: total,
      page: page,
      per_page: perPage,
      pages: Math.ceil(total / perPage)
    });
  }),

  ...createHandler('get', '/api/suppliers/:id', ({ params }) => {
    const id = parseInt(params.id);
    const suppliers = createMockArray(createMockSupplier, 10); // Mock list of suppliers
    const supplier = suppliers.find(s => s.id === id);
    if (!supplier) {
      return HttpResponse.json({ error: 'Supplier not found' }, { status: 404 });
    }
    return HttpResponse.json(supplier);
  }),

  ...createHandler('post', '/api/suppliers', async ({ request }) => {
    const newSupplier = await request.json();
    return HttpResponse.json(
      createMockSupplier({ id: 999, ...newSupplier }), 
      { status: 201 }
    );
  }),

  ...createHandler('put', '/api/suppliers/:id', async ({ params, request }) => {
    const updates = await request.json();
    const id = parseInt(params.id);
    return HttpResponse.json(
      createMockSupplier({ id, ...updates })
    );
  }),

  ...createHandler('delete', '/api/suppliers/:id', ({ params }) => {
    const id = parseInt(params.id);
    return HttpResponse.json({ 
      message: `Supplier ${id} deleted successfully` 
    });
  }),

  // Dashboard endpoints
  ...createHandler('get', '/api/dashboard/stats', () => {
    return HttpResponse.json(createMockDashboardStats());
  }),

  ...createHandler('get', '/api/dashboard/recent-activity', () => {
    const activities = createMockArray(createMockActivity, 8);
    return HttpResponse.json({
      activities: activities,
      total: activities.length
    });
  }),

  // Products endpoint (placeholder implementation)
  ...createHandler('get', '/api/products', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');
    
    return HttpResponse.json({
      products: [], // Empty for now as per API service
      total: 0,
      page: page,
      per_page: perPage,
      pages: 0
    });
  }),

  // Error scenarios for testing
  ...createHandler('get', '/api/plants/error', () => {
    return HttpResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }),

  ...createHandler('get', '/api/plants/not-found', () => {
    return HttpResponse.json(
      { error: 'Plant not found' },
      { status: 404 }
    );
  }),

  ...createHandler('get', '/api/projects/error', () => {
    return HttpResponse.json(
      { error: 'Failed to fetch projects' },
      { status: 500 }
    );
  }),

  ...createHandler('get', '/api/suppliers/error', () => {
    return HttpResponse.json(
      { error: 'Supplier service unavailable' },
      { status: 503 }
    );
  })
];