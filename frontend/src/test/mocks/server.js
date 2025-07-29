// Enhanced mock server for Jest testing
// Provides realistic API mocking with improved data and error scenarios

// Create a mock server object for compatibility
const server = {
  listen: jest.fn(),
  resetHandlers: jest.fn(),
  close: jest.fn(),
  use: jest.fn()
};

// Enhanced mock data factories
const createMockDashboardStats = () => ({
  suppliers: 5,
  plants: 156,
  products: 45,
  clients: 8,
  projects: 12,
  active_projects: 3,
  total_budget: 150000
});

const createMockRecentActivity = () => [
  {
    id: 1,
    type: 'project',
    action: 'created',
    description: 'New project "Garden Redesign" created',
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

const createMockPlants = (count = 5) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Plant ${i + 1}`,
    common_name: `Common Plant ${i + 1}`,
    category: 'Shrub',
    sun_requirements: 'Full Sun',
    water_needs: 'Low',
    hardiness_zone: '2-7',
    price: 25.99 + i * 5,
    supplier_id: 1
  }));
};

const createMockProjects = (count = 3) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Project ${i + 1}`,
    client: `Client ${i + 1}`,
    location: `Location ${i + 1}`,
    budget: 50000 + i * 25000,
    start_date: '2024-01-15',
    status: i % 2 === 0 ? 'active' : 'planning'
  }));
};

// Enhanced fetch mock with search and filtering support
global.fetch = jest.fn((url, options = {}) => {
  const urlObj = new URL(url);
  const search = urlObj.searchParams.get('search');
  const status = urlObj.searchParams.get('status');
  const limit = parseInt(urlObj.searchParams.get('limit')) || 10;

  // Dashboard endpoints
  if (url.includes('/api/dashboard/stats')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve(createMockDashboardStats())
    });
  }

  if (url.includes('/api/dashboard/recent-activity')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve(createMockRecentActivity())
    });
  }

  // Plants endpoints with search and filtering
  if (url.includes('/api/plants')) {
    let plants = createMockPlants(limit);
    
    if (search) {
      plants = plants.filter(plant => 
        plant.name.toLowerCase().includes(search.toLowerCase()) ||
        plant.common_name.toLowerCase().includes(search.toLowerCase())
      );
    }

    // POST request for creating plants
    if (options.method === 'POST') {
      return Promise.resolve({
        ok: true,
        status: 201,
        statusText: 'Created',
        json: () => Promise.resolve({ 
          id: Date.now(), 
          ...JSON.parse(options.body || '{}')
        })
      });
    }

    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve(plants)
    });
  }

  // Projects endpoints with search and filtering
  if (url.includes('/api/projects')) {
    let projects = createMockProjects(limit);
    
    if (search) {
      projects = projects.filter(project => 
        project.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (status) {
      projects = projects.filter(project => project.status === status);
    }

    // POST request for creating projects
    if (options.method === 'POST') {
      return Promise.resolve({
        ok: true,
        status: 201,
        statusText: 'Created',
        json: () => Promise.resolve({ 
          id: Date.now(), 
          ...JSON.parse(options.body || '{}')
        })
      });
    }

    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve(projects)
    });
  }

  // Error simulation endpoints
  if (url.includes('/error/500')) {
    return Promise.resolve({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.resolve({ error: 'Internal Server Error' })
    });
  }

  if (url.includes('/error/404')) {
    return Promise.resolve({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({ error: 'Not Found' })
    });
  }

  // Default response for other endpoints
  return Promise.resolve({
    ok: true,
    status: 200,
    statusText: 'OK',
    json: () => Promise.resolve({ success: true })
  });
});

// Utility functions for test scenarios
const mockApiError = (method, endpoint, status = 500, message = 'Server Error') => {
  const originalFetch = global.fetch;
  global.fetch = jest.fn((url, options = {}) => {
    if (url.includes(endpoint) && (options.method || 'GET').toLowerCase() === method.toLowerCase()) {
      return Promise.resolve({
        ok: false,
        status,
        statusText: message,
        json: () => Promise.resolve({ error: message })
      });
    }
    return originalFetch(url, options);
  });
};

const mockApiEndpoint = (method, endpoint, response, status = 200) => {
  const originalFetch = global.fetch;
  global.fetch = jest.fn((url, options = {}) => {
    if (url.includes(endpoint) && (options.method || 'GET').toLowerCase() === method.toLowerCase()) {
      return Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        statusText: 'OK',
        json: () => Promise.resolve(response)
      });
    }
    return originalFetch(url, options);
  });
};

// Establish API mocking before all tests
beforeAll(() => {
  server.listen();
});

// Reset handlers between tests to ensure clean state
afterEach(() => {
  server.resetHandlers();
  jest.clearAllMocks();
});

// Clean up after tests are finished
afterAll(() => {
  server.close();
});

// Export using CommonJS for Jest compatibility
module.exports = { 
  server,
  mockApiError,
  mockApiEndpoint
};