// Global DOM matchers and fetch polyfill
import '@testing-library/jest-dom';
import 'whatwg-fetch';
import { vi, beforeAll, afterEach, afterAll } from 'vitest';

// Set up TextEncoder/TextDecoder if missing
if (typeof globalThis.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = await import('node:util');
  globalThis.TextEncoder = TextEncoder;
  globalThis.TextDecoder = TextDecoder;
}

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Set up API mocking
let server;
let fetchMock;

try {
  const mod = await import('./mocks/server-vitest.js');
  server = mod.server;
  fetchMock = mod.fetchMock;
  
  // Set the global fetch to our mock
  global.fetch = fetchMock;
} catch {
  // Fallback to basic fetch mock if server module not available
  global.fetch = vi.fn();
}

// Establish API mocking before all tests
beforeAll(() => {
  if (server) {
    server.listen();
  }
});

// Reset handlers between tests to ensure clean state
afterEach(() => {
  if (server) {
    server.resetHandlers();
  }
  vi.clearAllMocks();
});

// Clean up after tests are finished
afterAll(() => {
  if (server) {
    server.close();
  }
});