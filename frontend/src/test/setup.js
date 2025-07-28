import '@testing-library/jest-dom'

// Setup global mocks
global.fetch = vi.fn()

// Reset mocks before each test
beforeEach(() => {
  global.fetch.mockClear()
})