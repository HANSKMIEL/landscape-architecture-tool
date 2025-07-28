import { vi } from 'vitest';
import { createMockPlant, createMockProject, createMockRecommendation } from './mockData';

// Mock API responses for common endpoints
export const mockApiResponses = {
  plants: {
    getAll: {
      plants: [
        createMockPlant({ id: 1, name: 'Rose' }),
        createMockPlant({ id: 2, name: 'Lavender' }),
        createMockPlant({ id: 3, name: 'Boxwood' })
      ],
      total: 3,
      page: 1,
      per_page: 10
    },
    getById: (id) => createMockPlant({ id }),
    create: (data) => createMockPlant({ id: 999, ...data }),
    update: (id, data) => createMockPlant({ id, ...data }),
    delete: { message: 'Plant deleted successfully' }
  },
  
  projects: {
    getAll: {
      projects: [
        createMockProject({ id: 1, name: 'Garden Redesign' }),
        createMockProject({ id: 2, name: 'Park Landscaping' })
      ],
      total: 2
    },
    getById: (id) => createMockProject({ id }),
    create: (data) => createMockProject({ id: 999, ...data }),
    update: (id, data) => createMockProject({ id, ...data })
  },
  
  recommendations: {
    get: {
      recommendations: [
        createMockRecommendation({ score: 0.95 }),
        createMockRecommendation({ score: 0.87 }),
        createMockRecommendation({ score: 0.82 })
      ],
      criteria: {
        sun_requirements: 'full_sun',
        height_range: [50, 200],
        soil_type: 'well_drained'
      }
    }
  }
};

// Helper to create fetch mock responses
export const createFetchMock = (response, status = 200) => {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(response)
  });
};

// Helper to mock API calls
export const mockApiCall = (endpoint, response, status = 200) => {
  globalThis.fetch = createFetchMock(response, status);
};