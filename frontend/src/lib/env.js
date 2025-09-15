// Environment configuration for API base URL
// Provides a consistent API base URL across dev/prod builds.
// Vite will inline import.meta.env.* at build time.
export function getApiBaseUrl() {
  // Force mock API for GitHub Pages (kept as-is for demo hosting scenarios)
  if (typeof window !== 'undefined' && window.location.hostname.includes('github.io')) {
    console.log('GitHub Pages detected - forcing mock API mode');
    return 'MOCK_API'; // Special flag to trigger mock API
  }
  
  // Use Vite environment variables if explicitly provided
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Default to relative /api for all environments
  // This works with reverse proxy in production and development
  return '/api';
}
