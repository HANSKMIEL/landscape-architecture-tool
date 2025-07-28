import '@testing-library/jest-dom';
import { server } from './mocks/server';
import { beforeAll, afterEach, afterAll, vi } from 'vitest';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Establish API mocking before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests
afterEach(() => {
  server.resetHandlers();
});

// Clean up after the tests are finished
afterAll(() => {
  server.close();
});