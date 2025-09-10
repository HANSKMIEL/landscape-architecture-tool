// Mock API implementation for static demos and development
// Mock data for static demo
const MOCK_DATA = {
  projects: [
    {
      id: 1,
      name: "Amsterdam City Park Renovation",
      client: "Amsterdam Municipality",
      status: "In Progress",
      budget: 125000,
      startDate: "2025-03-15",
      endDate: "2025-08-30"
    },
    {
      id: 2,
      name: "Corporate Headquarters Landscaping",
      client: "TechCorp Netherlands",
      status: "Planning",
      budget: 75000,
      startDate: "2025-10-01",
      endDate: "2025-12-15"
    }
  ],
  plants: [
    {
      id: 1,
      name: "Quercus robur",
      commonName: "English Oak",
      category: "Trees",
      price: 85.50,
      supplier: "Dutch Garden Center",
      description: "Majestic deciduous tree with broad, rounded crown"
    },
    {
      id: 2,
      name: "Lavandula angustifolia",
      commonName: "English Lavender",
      category: "Perennials",
      price: 8.50,
      supplier: "Herb Specialists BV",
      description: "Fragrant perennial perfect for borders and bee gardens"
    },
    {
      id: 3,
      name: "Buxus sempervirens",
      commonName: "Common Boxwood",
      category: "Shrubs",
      price: 15.75,
      supplier: "Evergreen Nursery",
      description: "Classic evergreen shrub ideal for hedging and topiary"
    }
  ],
  clients: [
    {
      id: 1,
      name: "Van der Berg Family",
      email: "info@vanderberg.nl",
      phone: "+31 20 123 4567",
      address: "Prinsengracht 123, Amsterdam"
    },
    {
      id: 2,
      name: "TechCorp Netherlands",
      email: "facilities@techcorp.nl",
      phone: "+31 30 987 6543",
      address: "Science Park 904, Amsterdam"
    }
  ],
  suppliers: [
    {
      id: 1,
      name: "Dutch Garden Center",
      contact: "Jan Jansen",
      email: "orders@dutchgarden.nl",
      phone: "+31 172 123 456",
      specialty: "Trees and Shrubs"
    },
    {
      id: 2,
      name: "Herb Specialists BV",
      contact: "Maria Smit",
      email: "info@herbspecialists.nl",
      phone: "+31 174 789 012",
      specialty: "Herbs and Perennials"
    }
  ]
}

// Mock API functions
export const mockApi = {
  // Projects
  getProjects: () => Promise.resolve({ data: MOCK_DATA.projects }),
  getProject: (id) => Promise.resolve({ 
    data: MOCK_DATA.projects.find(p => p.id === parseInt(id)) 
  }),
  
  // Plants
  getPlants: () => Promise.resolve({ data: MOCK_DATA.plants }),
  getPlant: (id) => Promise.resolve({ 
    data: MOCK_DATA.plants.find(p => p.id === parseInt(id)) 
  }),
  
  // Clients
  getClients: () => Promise.resolve({ data: MOCK_DATA.clients }),
  getClient: (id) => Promise.resolve({ 
    data: MOCK_DATA.clients.find(c => c.id === parseInt(id)) 
  }),
  
  // Suppliers
  getSuppliers: () => Promise.resolve({ data: MOCK_DATA.suppliers }),
  getSupplier: (id) => Promise.resolve({ 
    data: MOCK_DATA.suppliers.find(s => s.id === parseInt(id)) 
  }),
  
  // Plant Recommendations
  getPlantRecommendations: (criteria) => Promise.resolve({
    data: MOCK_DATA.plants.slice(0, 2).map(plant => ({
      ...plant,
      matchScore: Math.floor(Math.random() * 30) + 70,
      reasons: [
        "Suitable for local climate",
        "Low maintenance requirements",
        "Attractive seasonal interest"
      ]
    }))
  }),
  
  // Authentication
  login: (credentials) => {
    const { username, password } = credentials;
    // Demo credentials
    const validCredentials = [
      { username: 'admin', password: 'admin123', role: 'admin' },
      { username: 'employee', password: 'employee123', role: 'employee' },
      { username: 'client', password: 'client123', role: 'client' }
    ];
    
    const user = validCredentials.find(u => u.username === username && u.password === password);
    
    if (user) {
      // Store mock session
      localStorage.setItem('mockUser', JSON.stringify(user));
      return Promise.resolve({
        data: {
          success: true,
          user: { username: user.username, role: user.role },
          token: 'mock-jwt-token'
        }
      });
    } else {
      return Promise.reject(new Error('Invalid credentials'));
    }
  },
  
  checkAuthStatus: () => {
    const mockUser = localStorage.getItem('mockUser');
    if (mockUser) {
      const user = JSON.parse(mockUser);
      return Promise.resolve({
        data: {
          authenticated: true,
          user: { username: user.username, role: user.role }
        }
      });
    } else {
      return Promise.resolve({
        data: { authenticated: false }
      });
    }
  },
  
  logout: () => {
    localStorage.removeItem('mockUser');
    return Promise.resolve({
      data: { success: true }
    });
  },
  
  // Health check
  healthCheck: () => Promise.resolve({ 
    data: { 
      status: "healthy", 
      message: "Mock API running for GitHub Pages demo",
      timestamp: new Date().toISOString()
    } 
  })
}

// Get production domains from environment or use default
const PRODUCTION_DOMAINS = (import.meta.env.VITE_PRODUCTION_DOMAINS || '').split(',').filter(Boolean);

// Check if we're running in a static environment (GitHub Pages) or need to use mock API
export const isStaticDemo = () => {
  // Check for GitHub Pages
  const isGitHubPages = window.location.hostname.includes('github.io');
  console.log('GitHub Pages check:', isGitHubPages);
  
  // Check for file protocol
  const isFileProtocol = window.location.protocol === 'file:';
  console.log('File protocol check:', isFileProtocol);
  
  // Check for non-development environment
  const isNonDevEnvironment = 
    window.location.hostname !== 'localhost' && 
    window.location.hostname !== '127.0.0.1' && 
    !window.location.hostname.includes('manusvm.computer') &&
    // Allow production domains to use real API
    !PRODUCTION_DOMAINS.includes(window.location.hostname);
  
  console.log('Non-dev environment check:', isNonDevEnvironment);
  
  // Use mock API if any condition is true
  const shouldUseMockApi = isGitHubPages || isFileProtocol || isNonDevEnvironment;
  console.log('Should use mock API:', shouldUseMockApi);
  
  return shouldUseMockApi;
}
