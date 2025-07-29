// Mock API utilities for testing

// Mock an API endpoint with specific response
export const mockApiEndpoint = (method, url, response, status = 200) => {
  if (global.fetch && global.fetch.mockClear) {
    resetApiMocks()
  } else if (!global.fetch) {
    global.fetch = vi.fn((fetchUrl, options = {}) => {
      const fetchMethod = options.method || 'GET'
      for (const handler of mockHandlers) {
        if (handler.method === fetchMethod.toUpperCase() && (fetchUrl.includes(handler.url) || fetchUrl === handler.url)) {
         return handler.response()
        }
      }
      // Default response for unmatched requests
      return Promise.resolve({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: () => Promise.resolve({}),
        text: () => Promise.resolve('{}')
      })
    })
  }
  
  mockHandlers.push({
    method: method.toUpperCase(),
    url,
    response: () => Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      statusText: status >= 200 && status < 300 ? 'OK' : 'Error',
      json: () => Promise.resolve(response),
      text: () => Promise.resolve(JSON.stringify(response))
    })
  })
}

// Mock an API endpoint to return an error
const mockHandlers = []

export const mockApiError = (method, url, status, message) => {
  if (!global.fetch) {
    global.fetch = vi.fn((fetchUrl, options = {}) => {
      const fetchMethod = options.method || 'GET'
      for (const handler of mockHandlers) {
        if (handler.method === fetchMethod.toUpperCase() && (fetchUrl.includes(handler.url) || fetchUrl === handler.url)) {
          return handler.response()
        }
      }
      // Default response for unmatched requests
      return Promise.resolve({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: () => Promise.resolve({}),
        text: () => Promise.resolve('{}')
      })
    })
  }
  
  mockHandlers.push({
    method: method.toUpperCase(),
    url,
    response: () => Promise.resolve({
      ok: false,
      status,
      statusText: message,
      json: () => Promise.resolve({ error: message }),
      text: () => Promise.resolve(JSON.stringify({ error: message }))
    })
  })
}

// Reset all mocks
export const resetApiMocks = () => {
  if (global.fetch && global.fetch.mockReset) {
    global.fetch.mockReset()
  }
}