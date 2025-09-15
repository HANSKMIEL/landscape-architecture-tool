// Environment configuration for API base URL
// Provides a consistent API base URL across dev/prod builds.
// Vite will inline import.meta.env.* at build time.
export function getApiBaseUrl() {
  // Highest priority: explicit environment variable
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  // Development fallback
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.DEV) {
    return 'http://localhost:5000/api';
  }

  // Production fallback (assume same origin, /api proxy)
  return '/api';
}
