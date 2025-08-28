// Environment configuration for API base URL
export function getApiBaseUrl() {
  // Use Vite environment variables with fallback
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Development fallback
  if (import.meta.env.DEV) {
    return 'http://localhost:5000/api';
  }
  
  // Production fallback
  return '/api';
}