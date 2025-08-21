// Framework-agnostic test utilities for Jest and Vitest compatibility

/**
 * Detect the current testing framework
 * @returns {'jest' | 'vitest' | 'unknown'}
 */
export function getTestFramework() {
  // Check for Vitest global
  if (typeof vi !== 'undefined') {
    return 'vitest';
  }
  
  // Check for Jest global
  if (typeof jest !== 'undefined') {
    return 'jest';
  }
  
  return 'unknown';
}

/**
 * Framework-agnostic mock function creator
 * @param {Function} implementation - Optional mock implementation
 * @returns {Function} Mock function
 */
export function createMockFn(implementation) {
  const framework = getTestFramework();
  
  switch (framework) {
    case 'vitest': {
      return implementation ? vi.fn(implementation) : vi.fn();
    }
    case 'jest': {
      return implementation ? jest.fn(implementation) : jest.fn();
    }
    default: {
      // Fallback for unknown frameworks - basic function that tracks calls
      const mockFn = implementation || (() => {});
      mockFn.mock = { calls: [], results: [] };
      mockFn.mockReturnValue = (value) => {
        mockFn._returnValue = value;
        return mockFn;
      };
      mockFn.mockResolvedValue = (value) => {
        mockFn._resolvedValue = value;
        return mockFn;
      };
      return mockFn;
    }
  }
}

/**
 * Framework-agnostic mock clear function
 */
export function clearAllMocks() {
  const framework = getTestFramework();
  
  switch (framework) {
    case 'vitest':
      vi.clearAllMocks();
      break;
    case 'jest':
      jest.clearAllMocks();
      break;
    default:
      // No-op for unknown frameworks
      break;
  }
}

/**
 * Framework-agnostic mock restore function
 */
export function restoreAllMocks() {
  const framework = getTestFramework();
  
  switch (framework) {
    case 'vitest':
      vi.restoreAllMocks();
      break;
    case 'jest':
      jest.restoreAllMocks();
      break;
    default:
      // No-op for unknown frameworks
      break;
  }
}

/**
 * Framework-agnostic timer mock functions
 */
export const timers = {
  useFakeTimers() {
    const framework = getTestFramework();
    switch (framework) {
      case 'vitest':
        vi.useFakeTimers();
        break;
      case 'jest':
        jest.useFakeTimers();
        break;
    }
  },

  useRealTimers() {
    const framework = getTestFramework();
    switch (framework) {
      case 'vitest':
        vi.useRealTimers();
        break;
      case 'jest':
        jest.useRealTimers();
        break;
    }
  },

  advanceTimersByTime(ms) {
    const framework = getTestFramework();
    switch (framework) {
      case 'vitest':
        vi.advanceTimersByTime(ms);
        break;
      case 'jest':
        jest.advanceTimersByTime(ms);
        break;
    }
  }
};

/**
 * Create a fetch mock that works with both frameworks
 * @param {Function} mockImplementation - Function that returns mock response based on URL
 * @returns {Function} Mocked fetch function
 */
export function createFetchMock(mockImplementation) {
  return createMockFn((url, options = {}) => {
    const mockResponse = mockImplementation(url, options);
    
    // Ensure the response has the fetch API structure
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve(mockResponse),
      text: () => Promise.resolve(JSON.stringify(mockResponse)),
      ...mockResponse.responseOverrides
    });
  });
}

/**
 * Framework-agnostic spy function creator
 * @param {Object} object - Object to spy on
 * @param {string} method - Method name to spy on
 * @returns {Function} Spy function
 */
export function createSpy(object, method) {
  const framework = getTestFramework();
  
  switch (framework) {
    case 'vitest': {
      return vi.spyOn(object, method);
    }
    case 'jest': {
      return jest.spyOn(object, method);
    }
    default: {
      // Basic spy implementation for unknown frameworks
      const originalMethod = object[method];
      const spy = (...args) => {
        spy.mock.calls.push(args);
        return originalMethod.apply(object, args);
      };
      spy.mock = { calls: [] };
      spy.mockRestore = () => {
        object[method] = originalMethod;
      };
      object[method] = spy;
      return spy;
    }
  }
}