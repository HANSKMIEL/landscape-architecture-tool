# MSW (Mock Service Worker) Setup

This project uses Mock Service Worker (MSW) to intercept and mock API calls during testing, providing realistic API responses without requiring a running backend.

## Overview

MSW is configured to handle all API endpoints used by the frontend application with realistic mock responses. It works seamlessly with our existing Vitest + Testing Library setup.

## Files Structure

```
src/test/
├── mocks/
│   ├── handlers.js          # MSW request handlers for all API endpoints
│   ├── server.js            # MSW server setup for Node.js tests
│   ├── browser.js           # MSW worker setup for browser/development
│   └── msw.test.jsx         # MSW verification tests
├── utils/
│   ├── mockData.js          # Mock data generators for all entities
│   └── mswUtils.js          # Utility functions for MSW testing
├── examples/
│   └── component-with-api.test.jsx  # Example component test using MSW
└── setup.js                 # Test setup with MSW configuration
```

## API Endpoints Covered

MSW handles all the following API endpoints:

### Plants API
- `GET /api/plants` - List plants with pagination and search
- `GET /api/plants/:id` - Get single plant
- `POST /api/plants` - Create new plant
- `PUT /api/plants/:id` - Update plant
- `DELETE /api/plants/:id` - Delete plant
- `GET /api/plants/categories` - Get plant categories
- `POST /api/plants/recommendations` - Get plant recommendations

### Projects API
- `GET /api/projects` - List projects with pagination
- `GET /api/projects/:id` - Get single project
- `POST /api/projects` - Create new project
- `PUT /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project

### Clients API
- `GET /api/clients` - List clients with pagination
- `GET /api/clients/:id` - Get single client
- `POST /api/clients` - Create new client

### Suppliers API
- `GET /api/suppliers` - List suppliers with pagination
- `GET /api/suppliers/:id` - Get single supplier
- `POST /api/suppliers` - Create new supplier
- `PUT /api/suppliers/:id` - Update supplier
- `DELETE /api/suppliers/:id` - Delete supplier

### Dashboard API
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activities

### Error Testing Endpoints
- `GET /api/plants/error` - Mock 500 error
- `GET /api/plants/not-found` - Mock 404 error
- `GET /api/projects/error` - Mock 500 error
- `GET /api/suppliers/error` - Mock 503 error

## How to Use MSW in Tests

### Basic Usage

MSW works automatically in all tests. Just use your API service or fetch directly:

```javascript
import { describe, it, expect } from 'vitest';
import apiService from '../../services/api';

describe('My Component', () => {
  it('fetches plants from API', async () => {
    const plants = await apiService.getPlants();
    expect(plants.plants).toHaveLength(10); // Default pagination
  });
});
```

### Custom Mock Responses

Use MSW utilities to override specific endpoints:

```javascript
import { mockApiEndpoint, mockApiError } from '../utils/mswUtils';

describe('Error Handling', () => {
  it('handles API errors', async () => {
    // Mock an error response
    mockApiError('get', '/api/plants', 500, 'Server Error');
    
    // Your test code here
    await expect(apiService.getPlants()).rejects.toThrow('HTTP error! status: 500');
  });

  it('works with custom data', async () => {
    // Mock custom response
    mockApiEndpoint('get', '/api/plants', {
      plants: [{ id: 1, name: 'Test Plant' }],
      total: 1
    });
    
    const result = await apiService.getPlants();
    expect(result.plants[0].name).toBe('Test Plant');
  });
});
```

### Component Testing Example

```javascript
import { render, screen, waitFor } from '@testing-library/react';
import { mockApiEndpoint } from '../utils/mswUtils';

const MyComponent = () => {
  // Component that uses API
};

describe('MyComponent', () => {
  it('displays data from API', async () => {
    render(<MyComponent />);
    
    await waitFor(() => {
      expect(screen.getByText('Mock Plant 1')).toBeInTheDocument();
    });
  });
  
  it('handles loading states', async () => {
    // Mock slow response
    mockApiDelay('get', '/api/plants', { plants: [] }, 2000);
    
    render(<MyComponent />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
```

## MSW Utility Functions

### `mockApiEndpoint(method, url, response, status)`
Override any endpoint with custom response data.

```javascript
mockApiEndpoint('get', '/api/plants', { plants: [] }, 200);
```

### `mockApiError(method, url, status, message)`
Mock API error responses.

```javascript
mockApiError('get', '/api/plants', 404, 'Not found');
```

### `mockApiDelay(method, url, response, delay)`
Add artificial delays to responses for testing loading states.

```javascript
mockApiDelay('get', '/api/plants', { plants: [] }, 1000);
```

### `mockApiNetworkError(method, url)`
Mock network failures.

```javascript
mockApiNetworkError('get', '/api/plants');
```

### `resetApiMocks()`
Reset all custom handlers back to defaults.

```javascript
resetApiMocks();
```

## Mock Data Generators

The following functions generate realistic mock data:

- `createMockPlant(overrides)` - Generate plant data
- `createMockProject(overrides)` - Generate project data
- `createMockClient(overrides)` - Generate client data
- `createMockSupplier(overrides)` - Generate supplier data
- `createMockRecommendation(overrides)` - Generate recommendation data
- `createMockDashboardStats(overrides)` - Generate dashboard stats
- `createMockActivity(overrides)` - Generate activity data
- `createMockArray(createFn, count)` - Generate arrays of mock data

Example:

```javascript
import { createMockPlant, createMockArray } from '../utils/mockData';

// Single plant
const plant = createMockPlant({ name: 'Custom Plant' });

// Array of plants
const plants = createMockArray(createMockPlant, 5);
```

## Configuration

MSW is automatically configured in the test setup (`src/test/setup.js`). No additional configuration is needed for basic usage.

### Development Usage

For development/manual testing, you can enable MSW in the browser:

```javascript
// In your main.jsx or development environment
import { worker } from './test/mocks/browser';

if (import.meta.env.DEV) {
  worker.start();
}
```

## Best Practices

1. **Use realistic mock data**: The default handlers provide realistic data structures
2. **Test error scenarios**: Use `mockApiError` to test error handling
3. **Reset between tests**: MSW automatically resets handlers after each test
4. **Test loading states**: Use `mockApiDelay` to test loading indicators
5. **Isolate tests**: Each test should be independent and not rely on previous test state

## Debugging

If MSW isn't working as expected:

1. Check that the URL matches exactly (including query parameters)
2. Verify the HTTP method matches (GET, POST, etc.)
3. Use the browser dev tools to see network requests
4. Check the console for MSW warning/error messages
5. Use `resetApiMocks()` to clear any custom handlers

## Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test src/test/mocks/msw.test.jsx

# Run tests in watch mode
npm test -- --watch
```

All tests should pass without making real API calls, and MSW will handle all the mocking automatically.