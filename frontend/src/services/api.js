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
}

export default new ApiService();

