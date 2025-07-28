import '@testing-library/jest-dom'

// Setup global mocks
global.fetch = vi.fn()
global.ResizeObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn(),
}))

// Reset mocks before each test
beforeEach(() => {
  global.fetch.mockClear()
})