// Mock data factories for testing

// Plant mock data factory
export const createMockPlant = (overrides = {}) => ({
  id: 1,
  name: 'Rosa rugosa',
  common_name: 'Beach Rose',
  category: 'Shrub',
  height_min: 3,
  height_max: 6,
  width_min: 4,
  width_max: 6,
  sun_requirements: 'Full Sun',
  soil_type: 'Sandy',
  water_needs: 'Low',
  hardiness_zone: '2-7',
  bloom_time: 'Summer',
  bloom_color: 'Pink',
  foliage_color: 'Green',
  native: true,
  supplier_id: 1,
  supplier_name: 'Green Thumb Nursery',
  price: 25.99,
  availability: 'In Stock',
  planting_season: 'Spring/Fall',
  maintenance: 'Low',
  notes: 'Salt tolerant, good for coastal areas',
  ...overrides
})

// Project mock data factory
export const createMockProject = (overrides = {}) => ({
  id: 1,
  name: 'Residential Garden Redesign',
  description: 'Complete landscape renovation for residential property',
  client_id: 1,
  client_name: 'John Smith',
  location: '123 Main St, Garden City',
  budget: 15000,
  start_date: '2024-03-01',
  end_date: '2024-06-01',
  status: 'Planning',
  progress: 25,
  created_at: '2024-01-15',
  updated_at: '2024-01-20',
  ...overrides
})

// Client mock data factory
export const createMockClient = (overrides = {}) => ({
  id: 1,
  name: 'John Smith',
  email: 'john.smith@example.com',
  phone: '(555) 123-4567',
  address: '123 Main St, Garden City',
  company: 'Smith Enterprises',
  notes: 'Prefers native plants',
  created_at: '2024-01-01',
  updated_at: '2024-01-15',
  ...overrides
})

// Supplier mock data factory
export const createMockSupplier = (overrides = {}) => ({
  id: 1,
  name: 'Green Thumb Nursery',
  contact_person: 'Mary Johnson',
  email: 'mary@greenthumb.com',
  phone: '(555) 987-6543',
  address: '456 Plant Ave, Nursery Town',
  website: 'https://greenthumb.com',
  specialties: 'Native Plants, Perennials',
  notes: 'Reliable supplier with good pricing',
  rating: 4.8,
  created_at: '2024-01-01',
  updated_at: '2024-01-10',
  ...overrides
})

// Dashboard stats mock data factory
export const createMockDashboardStats = (overrides = {}) => ({
  suppliers: 5,
  plants: 156,
  products: 45,
  clients: 8,
  projects: 12,
  active_projects: 3,
  completed_projects: 7,
  pending_projects: 2,
  total_budget: 150000,
  plants_in_season: 45,
  low_stock_plants: 8,
  revenue_this_month: 25000,
  revenue_last_month: 18000,
  last_updated: '2024-01-20T10:30:00Z',
  ...overrides
})

// Recent activity mock data factory
export const createMockRecentActivity = (overrides = []) => [
  {
    id: 1,
    title: 'Project Created',
    description: 'New project "Garden Redesign" created',
    timestamp: '2024-01-20T10:30:00Z',
    user: 'Admin'
  },
  {
    id: 2,
    title: 'Plant Added',
    description: 'Added "Japanese Maple" to inventory',
    timestamp: '2024-01-19T14:15:00Z',
    user: 'Admin'
  },
  {
    id: 3,
    title: 'Client Contact',
    description: 'Called client about project timeline',
    timestamp: '2024-01-18T09:45:00Z',
    user: 'Admin'
  },
  ...overrides
]

// Array factories for collections
export const createMockPlants = (count = 3, overrides = []) => {
  const plants = []
  for (let i = 0; i < count; i++) {
    plants.push(createMockPlant({
      id: i + 1,
      name: `Plant ${i + 1}`,
      common_name: `Common Plant ${i + 1}`,
      ...overrides[i]
    }))
  }
  return plants
}

export const createMockProjects = (count = 3, overrides = []) => {
  const projects = []
  for (let i = 0; i < count; i++) {
    projects.push(createMockProject({
      id: i + 1,
      name: `Project ${i + 1}`,
      ...overrides[i]
    }))
  }
  return projects
}

export const createMockClients = (count = 3, overrides = []) => {
  const clients = []
  for (let i = 0; i < count; i++) {
    clients.push(createMockClient({
      id: i + 1,
      name: `Client ${i + 1}`,
      email: `client${i + 1}@example.com`,
      ...overrides[i]
    }))
  }
  return clients
}

export const createMockSuppliers = (count = 3, overrides = []) => {
  const suppliers = []
  for (let i = 0; i < count; i++) {
    suppliers.push(createMockSupplier({
      id: i + 1,
      name: `Supplier ${i + 1}`,
      email: `supplier${i + 1}@example.com`,
      ...overrides[i]
    }))
  }
  return suppliers
}

// API response wrappers
export const createApiResponse = (data, meta = {}) => ({
  ...data,
  total: meta.total || (Array.isArray(data) ? data.length : 1),
  pages: meta.pages || 1,
  current_page: meta.current_page || 1,
  per_page: meta.per_page || 10
})

export const createErrorResponse = (message = 'API Error', status = 500) => ({
  error: true,
  message,
  status
})