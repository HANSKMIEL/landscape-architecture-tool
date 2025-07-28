// API service for landscape architecture application
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
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

  async getPlantRecommendations(criteria) {
    return this.request('/plants/recommendations', {
      method: 'POST',
      body: criteria,
    });
  }

  async getPlantCategories() {
    return this.request('/plants/categories');
  }

  // Products API (placeholder for future implementation)
  async getProducts() {
    // For now, return mock data
    return {
      products: [],
      total: 0,
      pages: 0,
      current_page: 1
    };
  }

  // Clients API (placeholder for future implementation)
  async getClients() {
    // For now, return mock data
    return {
      clients: [],
      total: 0,
      pages: 0,
      current_page: 1
    };
  }

  // Projects API (placeholder for future implementation)
  async getProjects() {
    // For now, return mock data
    return {
      projects: [],
      total: 0,
      pages: 0,
      current_page: 1
    };
  }
}

export default new ApiService();

