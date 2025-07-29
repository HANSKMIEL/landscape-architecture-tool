// Simple mock server for Jest testing
// MSW integration will be implemented in a future update

// Create a mock server object for compatibility
const server = {
  listen: jest.fn(),
  resetHandlers: jest.fn(),
  close: jest.fn(),
  use: jest.fn()
};

// Mock the global fetch for basic API mocking
const originalFetch = global.fetch;

global.fetch = jest.fn((url, options) => {
  // Simple mock responses for dashboard endpoints
  if (url.includes('/api/dashboard/stats')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve({
        suppliers: 5,
        plants: 156,
        products: 45,
        clients: 8,
        projects: 12,
        active_projects: 3,
        total_budget: 150000
      })
    });
  }

  if (url.includes('/api/dashboard/recent-activity')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve([
        {
          id: 1,
          type: 'project',
          action: 'created',
          description: 'New project "Garden Redesign" created',
          timestamp: new Date().toISOString()
        }
      ])
    });
  }

  if (url.includes('/api/plants')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve([
        { id: 1, name: 'Rose', common_name: 'Garden Rose' },
        { id: 2, name: 'Tulip', common_name: 'Spring Tulip' }
      ])
    });
  }

  if (url.includes('/api/projects')) {
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve([
        {
          id: 1,
          name: 'Garden Redesign Project',
          client: 'Green Spaces Inc.',
          location: 'Amsterdam',
          budget: 50000,
          start_date: '2024-01-15',
          status: 'active'
        },
        {
          id: 2,
          name: 'Park Renovation',
          client: 'City Council',
          location: 'Utrecht',
          budget: 125000,
          start_date: '2024-02-01',
          status: 'planning'
        }
      ])
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
module.exports = { server };