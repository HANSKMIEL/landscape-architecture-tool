import { setupServer } from 'msw/node'
import { handlers } from './handlers'

// Create server instance for Node.js environment (tests)
export const server = setupServer(...handlers)

// Establish API mocking before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

// Reset handlers between tests to ensure clean state
afterEach(() => {
  server.resetHandlers()
})

// Clean up after tests are finished
afterAll(() => {
  server.close()
})