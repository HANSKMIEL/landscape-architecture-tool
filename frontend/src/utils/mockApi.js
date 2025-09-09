// Mock API for GitHub Pages demo (when backend is not available)

const MOCK_DATA = {
  projects: [
    {
      id: 1,
      name: "Villa Botanica Garden Design",
      client: "Van der Berg Family",
      status: "In Progress",
      budget: 45000,
      startDate: "2024-03-15",
      description: "Complete garden redesign with sustainable plant selection"
    },
    {
      id: 2,
      name: "Corporate Headquarters Landscape",
      client: "TechCorp Netherlands",
      status: "Planning",
      budget: 120000,
      startDate: "2024-04-01",
      description: "Modern landscape design for corporate campus"
    },
    {
      id: 3,
      name: "Historic Park Restoration",
      client: "Municipality of Amsterdam",
      status: "Completed",
      budget: 85000,
      startDate: "2024-01-10",
      description: "Restoration of 19th century park with native species"
    }
  ],
  plants: [
    {
      id: 1,
      name: "Acer palmatum",
      commonName: "Japanese Maple",
      category: "Trees",
      price: 125.00,
      supplier: "Dutch Garden Center",
      description: "Beautiful ornamental tree with stunning fall colors"
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
  
  // Health check
  healthCheck: () => Promise.resolve({ 
    data: { 
      status: "healthy", 
      message: "Mock API running for GitHub Pages demo",
      timestamp: new Date().toISOString()
    } 
  })
}

// Check if we're running in a static environment (GitHub Pages)
export const isStaticDemo = () => {
  return window.location.hostname.includes('github.io') || 
         !window.location.hostname.includes('localhost')
}
