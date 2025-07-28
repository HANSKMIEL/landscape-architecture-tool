import { http, HttpResponse } from 'msw';
import { 
  createMockArray, 
  createMockPlant, 
  createMockProject, 
  createMockClient, 
  createMockSupplier,
  createMockRecommendation,
  createMockDashboardStats,
  createMockActivity
} from '../utils/mockData';

// Helper function to create handlers for both relative and absolute URLs
const createHandler = (method, relativePath, handler) => [
  http[method](relativePath, handler),
  http[method](`http://localhost:5000${relativePath}`, handler),
];

export const handlers = [
  // Plant endpoints
  ...createHandler('get', '/api/plants', ({ request }) => {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');
    const search = url.searchParams.get('search') || '';
    
    let plants = createMockArray(createMockPlant, 15);
    
    // Filter by search if provided
    if (search) {
      plants = plants.filter(plant => 
        plant.name.toLowerCase().includes(search.toLowerCase()) ||
        plant.scientific_name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    // Paginate
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
  }),

  ...createHandler('get', '/api/plants/categories', () => {
    return HttpResponse.json({
      categories: [
        'Annual',
        'Perennial',
        'Shrub',
        'Tree',
        'Bulb',
        'Grass',
        'Fern',
        'Succulent'
      ]
    });
  }),

  ...createHandler('get', '/api/plants/:id', ({ params }) => {
    const id = parseInt(params.id);
    if (isNaN(id)) {
      return HttpResponse.json(
        { error: 'Invalid plant ID' },
        { status: 400 }
      );
    }
    return HttpResponse.json(createMockPlant({ id }));
  }),

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
    return HttpResponse.json(createMockProject({ id }));
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
    return HttpResponse.json(createMockClient({ id }));
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
    return HttpResponse.json(createMockSupplier({ id }));
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