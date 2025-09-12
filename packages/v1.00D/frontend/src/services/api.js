// API service for landscape architecture application
import { getApiBaseUrl } from '../lib/env.js';
import { mockApi, isStaticDemo } from '../utils/mockApi.js';

const API_BASE_URL = getApiBaseUrl();

class ApiService {
  async request(endpoint, options = {}) {
    // Use mock API for static demo (GitHub Pages) or when explicitly flagged
    if (isStaticDemo() || API_BASE_URL === 'MOCK_API') {
      console.log('Using mock API - detected GitHub Pages or mock flag');
      return this.handleMockRequest(endpoint, options);
    }
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include session cookies for authentication
      ...options,
    };

    // Handle FormData - don't set Content-Type for FormData
    if (config.body instanceof FormData) {
      delete config.headers['Content-Type'];
    } else if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Mock request handler for static demo
  async handleMockRequest(endpoint, options = {}) {
    console.log('Using mock API for endpoint:', endpoint);
    
    // Handle authentication endpoints
    if (endpoint.includes('/auth/login')) {
      const credentials = JSON.parse(options.body || '{}');
      return mockApi.login(credentials);
    }
    
    if (endpoint.includes('/auth/status')) {
      return mockApi.checkAuthStatus();
    }
    
    if (endpoint.includes('/auth/logout')) {
      return mockApi.logout();
    }
    
    // Route to appropriate mock function
    if (endpoint.includes('/projects')) {
      if (endpoint.includes('/projects/') && !endpoint.endsWith('/projects/')) {
        const id = endpoint.split('/projects/')[1].split('/')[0];
        return mockApi.getProject(id);
      }
      return mockApi.getProjects();
    }
    
    if (endpoint.includes('/plants')) {
      if (endpoint.includes('/plants/') && !endpoint.endsWith('/plants/')) {
        const id = endpoint.split('/plants/')[1].split('/')[0];
        return mockApi.getPlant(id);
      }
      return mockApi.getPlants();
    }
    
    if (endpoint.includes('/clients')) {
      if (endpoint.includes('/clients/') && !endpoint.endsWith('/clients/')) {
        const id = endpoint.split('/clients/')[1].split('/')[0];
        return mockApi.getClient(id);
      }
      return mockApi.getClients();
    }
    
    if (endpoint.includes('/suppliers')) {
      if (endpoint.includes('/suppliers/') && !endpoint.endsWith('/suppliers/')) {
        const id = endpoint.split('/suppliers/')[1].split('/')[0];
        return mockApi.getSupplier(id);
      }
      return mockApi.getSuppliers();
    }
    
    if (endpoint.includes('/plant-recommendations')) {
      return mockApi.getPlantRecommendations();
    }
    
    if (endpoint.includes('/health')) {
      return mockApi.healthCheck();
    }
    
    // Default mock response
    return Promise.resolve({ 
      data: [], 
      message: 'Mock data for static demo',
      endpoint: endpoint 
    });
  }

  // Dashboard API
  async getDashboardStats() {
    return this.request('/dashboard/stats');
  }

  async getRecentActivity() {
    return this.request('/dashboard/recent-activity');
  }

  // Suppliers API
  async getSuppliers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/suppliers${queryString ? `?${queryString}` : ''}`);
  }

  async getSupplier(id) {
    return this.request(`/suppliers/${id}`);
  }

  async createSupplier(data) {
    return this.request('/suppliers', {
      method: 'POST',
      body: data,
    });
  }

  async updateSupplier(id, data) {
    return this.request(`/suppliers/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deleteSupplier(id) {
    return this.request(`/suppliers/${id}`, {
      method: 'DELETE',
    });
  }

  // Plants API
  async getPlants(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/plants${queryString ? `?${queryString}` : ''}`);
  }

  async getPlant(id) {
    return this.request(`/plants/${id}`);
  }

  async createPlant(data) {
    return this.request('/plants', {
      method: 'POST',
      body: data,
    });
  }

  async updatePlant(id, data) {
    return this.request(`/plants/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deletePlant(id) {
    return this.request(`/plants/${id}`, {
      method: 'DELETE',
    });
  }

  async getPlantRecommendations(criteria) {
    return this.request('/plants/recommendations', {
      method: 'POST',
      body: criteria,
    });
  }

  async getPlantCategories() {
    return this.request('/plants/categories');
  }

  // Products API
  async getProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/products${queryString ? `?${queryString}` : ''}`);
  }

  async getProduct(id) {
    return this.request(`/products/${id}`);
  }

  async createProduct(data) {
    return this.request('/products', {
      method: 'POST',
      body: data,
    });
  }

  async updateProduct(id, data) {
    return this.request(`/products/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deleteProduct(id) {
    return this.request(`/products/${id}`, {
      method: 'DELETE',
    });
  }

  // Clients API
  async getClients(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/clients${queryString ? `?${queryString}` : ''}`);
  }

  async getClient(id) {
    return this.request(`/clients/${id}`);
  }

  async createClient(data) {
    return this.request('/clients', {
      method: 'POST',
      body: data,
    });
  }

  async updateClient(id, data) {
    return this.request(`/clients/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deleteClient(id) {
    return this.request(`/clients/${id}`, {
      method: 'DELETE',
    });
  }

  // Projects API
  async getProjects(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/projects${queryString ? `?${queryString}` : ''}`);
  }

  async getProject(id) {
    return this.request(`/projects/${id}`);
  }

  async createProject(data) {
    return this.request('/projects', {
      method: 'POST',
      body: data,
    });
  }

  async updateProject(id, data) {
    return this.request(`/projects/${id}`, {
      method: 'PUT',
      body: data,
    });
  }

  async deleteProject(id) {
    return this.request(`/projects/${id}`, {
      method: 'DELETE',
    });
  }

  // Invoice and Quote API
  async getInvoiceableProjects() {
    return this.request('/invoices/projects');
  }

  async generateQuote(projectId, format = 'json') {
    return this.request(`/invoices/quote/${projectId}?format=${format}`);
  }

  async generateInvoice(projectId, data = {}) {
    return this.request(`/invoices/invoice/${projectId}`, {
      method: 'POST',
      body: data,
    });
  }

  // Excel Import API
  async getImportStatus() {
    return this.request('/import/status');
  }

  async validateImportFile(formData) {
    return this.request('/import/validate-file', {
      method: 'POST',
      body: formData,
    });
  }

  async processImport(formData) {
    return this.request('/import/process', {
      method: 'POST',
      body: formData,
    });
  }

  async downloadImportTemplate(importType) {
    return this.request(`/import/template/${importType}`);
  }
}

export default new ApiService();

