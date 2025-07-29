// Simple mock server for Vitest testing
// MSW integration will be implemented in a future update
import { vi } from 'vitest'

// Create a mock server object for compatibility
const server = {
  listen: vi.fn(),
  resetHandlers: vi.fn(),
  close: vi.fn(),
  use: vi.fn()
};

// Mock the global fetch for basic API mocking
global.fetch = vi.fn((url) => {
  // Simple mock responses for dashboard endpoints
  if (url.includes('/api/dashboard/stats')) {
    return Promise.resolve({
      ok: true,
      status: 200,
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
      json: () => Promise.resolve([
        { id: 1, name: 'Rose', common_name: 'Garden Rose' },
        { id: 2, name: 'Tulip', common_name: 'Spring Tulip' }
      ])
    });
  }

  // Default response for other endpoints
  return Promise.resolve({
    ok: true,
    status: 200,
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
  vi.clearAllMocks();
});

// Clean up after tests are finished
afterAll(() => {
  server.close();
});

// Export for Vitest compatibility
export { server };