// Environment configuration for API base URL
export function getApiBaseUrl() {
  // Force mock API for GitHub Pages
  if (typeof window !== 'undefined' && window.location.hostname.includes('github.io')) {
    console.log('GitHub Pages detected - forcing mock API mode');
    return 'MOCK_API'; // Special flag to trigger mock API
  }
  
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