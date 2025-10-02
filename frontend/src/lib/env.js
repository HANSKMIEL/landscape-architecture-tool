// Environment configuration for API base URL
// Provides a consistent API base URL across dev/prod builds.
// ALWAYS uses public-facing URLs, never localhost
export function getApiBaseUrl() {
  // Force mock API for GitHub Pages (demo hosting only)
  if (typeof window !== 'undefined' && window.location.hostname.includes('github.io')) {
    console.log('GitHub Pages detected - forcing mock API mode');
    return 'MOCK_API'; // Special flag to trigger mock API
  }
  
  // Use Vite environment variables if explicitly provided
  if (import.meta.env.VITE_API_BASE_URL) {
    console.log('Using explicit API URL from env:', import.meta.env.VITE_API_BASE_URL);
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // VPS Production: Use public-facing URL through Nginx proxy
  // Frontend on port 8080 → Nginx proxies /api to backend on port 5001
  // This ensures everything goes through the public interface
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    const port = window.location.port;
    
    // VPS: Use the public URL with /api path (Nginx will proxy to backend)
    if (hostname === '72.60.176.200' || hostname === 'optura.nl') {
      const apiUrl = `${protocol}//${hostname}${port ? ':' + port : ''}/api`;
      console.log('Production VPS - API URL:', apiUrl);
      return apiUrl;
    }
    
    // Development: Use relative /api (handled by Vite dev server proxy)
    console.log('Development - using relative /api');
    return '/api';
  }
  
  // Fallback for SSR/build time
  return '/api';
}
