// Use dynamic import for MSW to handle ES module issues
let setupServer;

const initializeMSW = async () => {
  try {
    const msw = await import('msw/node');
    setupServer = msw.setupServer;
    return true;
  } catch (error) {
    console.warn('MSW not available:', error.message);
    return false;
  }
};

// Mock handlers - simplified for Jest compatibility
const mockHandlers = [];

let server;

// Initialize MSW conditionally
const setupMockServer = async () => {
  const mswAvailable = await initializeMSW();
  if (mswAvailable && setupServer) {
    const { handlers } = await import('./handlers');
    server = setupServer(...handlers);
    
    // Establish API mocking before all tests
    beforeAll(() => {
      server.listen({ onUnhandledRequest: 'error' });
    });

    // Reset handlers between tests to ensure clean state  
    afterEach(() => {
      server.resetHandlers();
    });

    // Clean up after tests are finished
    afterAll(() => {
      server.close();
    });
  }
};

// Try to setup MSW, but don't fail if it's not available
setupMockServer().catch(error => {
  console.warn('MSW setup failed, tests will run without mocking:', error.message);
});

export { server };