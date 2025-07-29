// Mock API utilities for testing

// Mock an API endpoint with specific response
export const mockApiEndpoint = (method, url, response, status = 200) => {
  if (global.fetch && global.fetch.mockClear) {
    resetApiMocks()
  } else if (!global.fetch) {
    global.fetch = vi.fn()
  }
  
  global.fetch.mockImplementation((fetchUrl, options = {}) => {
    const fetchMethod = options.method || 'GET'
    
    // Check if the URL matches (handle full URLs with localhost)
    const urlMatches = fetchUrl.includes(url) || fetchUrl === url
    const methodMatches = fetchMethod.toUpperCase() === method.toUpperCase()
    
    if (urlMatches && methodMatches) {
      return Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        statusText: status >= 200 && status < 300 ? 'OK' : 'Error',
        json: () => Promise.resolve(response),
        text: () => Promise.resolve(JSON.stringify(response))
      })
    }
    
    // Return a default successful response for unmatched requests
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve({}),
      text: () => Promise.resolve('{}')
    })
  })
}

// Mock an API endpoint to return an error
export const mockApiError = (method, url, status, message) => {
  if (!global.fetch) {
    global.fetch = vi.fn()
  }
  
  global.fetch.mockImplementation((fetchUrl, options = {}) => {
    const fetchMethod = options.method || 'GET'
    
    // Check if the URL matches (handle full URLs with localhost)
    const urlMatches = fetchUrl.includes(url) || fetchUrl === url
    const methodMatches = fetchMethod.toUpperCase() === method.toUpperCase()
    
    if (urlMatches && methodMatches) {
      return Promise.resolve({
        ok: false,
        status,
        statusText: message,
        json: () => Promise.resolve({ error: message }),
        text: () => Promise.resolve(JSON.stringify({ error: message }))
      })
    }
    
    // Return a default successful response for unmatched requests
    return Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: () => Promise.resolve({}),
      text: () => Promise.resolve('{}')
    })
  })
}

// Reset all mocks
export const resetApiMocks = () => {
  if (global.fetch && global.fetch.mockClear) {
    global.fetch.mockClear()
  }
}