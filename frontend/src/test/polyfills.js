// Polyfills for MSW and modern web APIs
import 'whatwg-fetch';

// Add missing globals for modern web APIs that MSW needs
if (typeof global.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}

// Add TransformStream polyfill for MSW v2
if (typeof global.TransformStream === 'undefined') {
  // Simple TransformStream polyfill for testing
  global.TransformStream = class TransformStream {
    constructor(transformer = {}) {
      this.readable = new ReadableStream();
      this.writable = new WritableStream();
      this.transformer = transformer;
    }
  };
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