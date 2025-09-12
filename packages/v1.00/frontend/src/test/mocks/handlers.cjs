// MSW handlers for Jest testing (CommonJS format)
const { http, HttpResponse } = require('msw');
const { URL } = require('url');

// Mock data factories (inline to avoid import issues in Jest)
const createMockDashboardStats = () => ({
  suppliers: 8,
  plants: 234,
  products: 67,
  clients: 12,
  projects: 15,
  active_projects: 4,
  total_budget: 280000
});

const createMockRecentActivity = () => [
  {
    id: 1,
    type: 'project',
    action: 'created',
    description: 'New project "Urban Park Design" created',
    timestamp: new Date().toISOString()
  },
  {
    id: 2,
    type: 'plant',
    action: 'added',
    description: 'Added "Japanese Maple" to inventory',
    timestamp: new Date().toISOString()
  }
];

const createMockPlant = (overrides = {}) => ({
  id: 1,
  name: 'Rosa rugosa',
  common_name: 'Beach Rose',
  category: 'Shrub',
  sun_requirements: 'Full Sun',
  water_needs: 'Low',
  hardiness_zone: '2-7',
  price: 25.99,
  supplier_id: 1,
  ...overrides
});

const createMockPlants = (count = 5) => {
  return Array.from({ length: count }, (_, i) => createMockPlant({
    id: i + 1,
    name: `Plant ${i + 1}`,
    common_name: `Common Plant ${i + 1}`
  }));
};

const createMockProject = (overrides = {}) => ({
  id: 1,
  name: 'Garden Redesign Project',
  client: 'Green Spaces Inc.',
  location: 'Amsterdam',
  budget: 50000,
  start_date: '2024-01-15',
  status: 'active',
  ...overrides
});

const createMockProjects = (count = 3) => {
  return Array.from({ length: count }, (_, i) => createMockProject({
    id: i + 1,
    name: `Project ${i + 1}`,
    status: i % 2 === 0 ? 'active' : 'planning'
  }));
};

const API_BASE = 'http://127.0.0.1:5000/api';

const handlers = [
  // Dashboard endpoints
  http.get(`${API_BASE}/dashboard/stats`, () => {
    return HttpResponse.json(createMockDashboardStats());
  }),

  http.get(`${API_BASE}/dashboard/recent-activity`, () => {
    return HttpResponse.json(createMockRecentActivity());
  }),

  // Plants endpoints
  http.get(`${API_BASE}/plants`, ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get('search');
    const limit = parseInt(url.searchParams.get('limit')) || 10;
    
    let plants = createMockPlants(limit);
    
    if (search) {
      plants = plants.filter(plant => 
        plant.name.toLowerCase().includes(search.toLowerCase()) ||
        plant.common_name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    return HttpResponse.json(plants);
  }),

  http.get(`${API_BASE}/plants/:id`, ({ params }) => {
    const plant = createMockPlant({ id: parseInt(params.id) });
    return HttpResponse.json(plant);
  }),

  http.post(`${API_BASE}/plants`, async ({ request }) => {
    const newPlant = await request.json();
    const plant = createMockPlant({ ...newPlant, id: Date.now() });
    return HttpResponse.json(plant, { status: 201 });
  }),

  // Projects endpoints
  http.get(`${API_BASE}/projects`, ({ request }) => {
    const url = new URL(request.url);
    const search = url.searchParams.get('search');
    const status = url.searchParams.get('status');
    const limit = parseInt(url.searchParams.get('limit')) || 10;
    
    let projects = createMockProjects(limit);
    
    if (search) {
      projects = projects.filter(project => 
        project.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (status) {
      projects = projects.filter(project => project.status === status);
    }
    
    return HttpResponse.json(projects);
  }),

  http.get(`${API_BASE}/projects/:id`, ({ params }) => {
    const project = createMockProject({ id: parseInt(params.id) });
    return HttpResponse.json(project);
  }),

  // Error scenarios for testing
  http.get(`${API_BASE}/error/500`, () => {
    return HttpResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }),

  http.get(`${API_BASE}/error/404`, () => {
    return HttpResponse.json(
      { error: 'Not Found' },
      { status: 404 }
    );
  })
];

module.exports = { handlers };