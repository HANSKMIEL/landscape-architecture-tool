// Polyfills for MSW and modern web APIs
import 'whatwg-fetch';

// Add missing globals for modern web APIs that MSW needs
if (typeof global.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}

// Ensure fetch APIs are available globally before MSW loads
if (typeof global.fetch === 'undefined') {
  global.fetch = require('whatwg-fetch').fetch;
}
if (typeof global.Response === 'undefined') {
  global.Response = require('whatwg-fetch').Response;  
}
if (typeof global.Request === 'undefined') {
  global.Request = require('whatwg-fetch').Request;
}
if (typeof global.Headers === 'undefined') {
  global.Headers = require('whatwg-fetch').Headers;
}

// Add other global APIs that might be needed
if (typeof global.URL === 'undefined') {
  global.URL = require('url').URL;
}
if (typeof global.URLSearchParams === 'undefined') {
  global.URLSearchParams = require('url').URLSearchParams;
}

// Mock BroadcastChannel for MSW
if (typeof global.BroadcastChannel === 'undefined') {
  global.BroadcastChannel = class BroadcastChannel {
    constructor(name) {
      this.name = name;
    }
    postMessage() {}
    close() {}
    addEventListener() {}
    removeEventListener() {}
  };
}

// Polyfill for TransformStream (required by MSW v2)
if (typeof global.TransformStream === 'undefined') {
  global.TransformStream = class TransformStream {
    readable = {
      pipeThrough: jest.fn ? jest.fn().mockReturnThis() : () => this.readable,
      pipeTo: jest.fn ? jest.fn() : () => {},
      getReader: jest.fn ? jest.fn() : () => ({ read: () => ({}) })
    };
    writable = {
      getWriter: jest.fn ? jest.fn() : () => ({ write: () => {} })
    };
    
    constructor() {}
  };
}

// Mock ReadableStream
if (typeof global.ReadableStream === 'undefined') {
  global.ReadableStream = class ReadableStream {
    constructor() {}
    getReader() { return { read: jest.fn ? jest.fn() : () => ({}) }; }
  };
}

// Mock WritableStream  
if (typeof global.WritableStream === 'undefined') {
  global.WritableStream = class WritableStream {
    constructor() {}
    getWriter() { return { write: jest.fn ? jest.fn() : () => {} }; }
  };
}