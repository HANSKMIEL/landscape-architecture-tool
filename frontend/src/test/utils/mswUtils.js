import { http, HttpResponse } from 'msw';
import { server } from '../mocks/server';

// Utility to override specific endpoints in tests
export const mockApiEndpoint = (method, url, response, status = 200) => {
  // Support both relative and absolute URLs
  const handlers = [
    http[method](url, () => {
      return HttpResponse.json(response, { status });
    })
  ];
  
  // If it's a relative URL, also add the absolute version
  if (url.startsWith('/api/')) {
    handlers.push(
      http[method](`http://localhost:5000${url}`, () => {
        return HttpResponse.json(response, { status });
      })
    );
  }
  
  server.use(...handlers);
};

// Utility to mock API errors
export const mockApiError = (method, url, status = 500, message = 'Server Error') => {
  // Support both relative and absolute URLs
  const handlers = [
    http[method](url, () => {
      return HttpResponse.json({ error: message }, { status });
    })
  ];
  
  // If it's a relative URL, also add the absolute version
  if (url.startsWith('/api/')) {
    handlers.push(
      http[method](`http://localhost:5000${url}`, () => {
        return HttpResponse.json({ error: message }, { status });
      })
    );
  }
  
  server.use(...handlers);
};

// Utility to mock loading delays
export const mockApiDelay = (method, url, response, delay = 1000) => {
  // Support both relative and absolute URLs
  const handlers = [
    http[method](url, async () => {
      await new Promise(resolve => setTimeout(resolve, delay));
      return HttpResponse.json(response);
    })
  ];
  
  // If it's a relative URL, also add the absolute version
  if (url.startsWith('/api/')) {
    handlers.push(
      http[method](`http://localhost:5000${url}`, async () => {
        await new Promise(resolve => setTimeout(resolve, delay));
        return HttpResponse.json(response);
      })
    );
  }
  
  server.use(...handlers);
};

// Utility to mock network failures
export const mockApiNetworkError = (method, url) => {
  // Support both relative and absolute URLs
  const handlers = [
    http[method](url, () => {
      return HttpResponse.error();
    })
  ];
  
  // If it's a relative URL, also add the absolute version
  if (url.startsWith('/api/')) {
    handlers.push(
      http[method](`http://localhost:5000${url}`, () => {
        return HttpResponse.error();
      })
    );
  }
  
  server.use(...handlers);
};

// Utility to reset specific handlers
export const resetApiMocks = () => {
  server.resetHandlers();
};

// Utility to create a custom handler for testing
export const createMockHandler = (method, url, responseFunction) => {
  return http[method](url, responseFunction);
};

// Utility to temporarily override multiple endpoints
export const withMockEndpoints = (handlers, testFn) => {
  return async () => {
    server.use(...handlers);
    try {
      await testFn();
    } finally {
      server.resetHandlers();
    }
  };
};