// Environment configuration for API endpoints
// Handles both development and production environments

/**
 * Get the API base URL based on the current environment
 * @returns {string} The API base URL
 */
export function getApiBaseUrl() {
  // Check if we're in development mode (Vite sets this)
  if (import.meta.env.DEV) {
    // In development, use the proxy setup from vite.config.js
    // The proxy forwards /api requests to the backend
    return '/api';
  }
  
  // In production, construct the API URL
  // Check for environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Default to same origin with /api prefix for production
  return `${window.location.origin}/api`;
}

/**
 * Get environment-specific configuration
 * @returns {object} Environment configuration
 */
export function getConfig() {
  return {
    apiBaseUrl: getApiBaseUrl(),
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD,
    mode: import.meta.env.MODE,
  };
}