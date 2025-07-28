// Mock data generators for testing

// Create an array of mock items
export const createMockArray = (generator, count, options = {}) => {
  return Array.from({ length: count }, (_, index) => 
    generator({ ...options, index })
  )
}

// Mock plant data generator
export const createMockPlant = (overrides = {}) => {
  const { index = 0, name, ...rest } = overrides
  
  return {
    id: index + 1,
    name: name || overrides.names?.[index] || 'Mock Plant',
    common_name: `Common Plant ${index + 1}`,
    category: 'perennial',
    height_min: 30,
    height_max: 60,
    width_min: 20,
    width_max: 40,
    sun_requirements: 'full_sun',
    soil_type: 'well_drained',
    water_needs: 'moderate',
    hardiness_zone: '5-9',
    bloom_time: 'spring',
    bloom_color: 'white',
    foliage_color: 'green',
    native: false,
    supplier_id: 1,
    price: 15.99,
    availability: 'in_stock',
    planting_season: 'spring',
    maintenance: 'low',
    notes: 'Easy to grow plant',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...rest
  }
}

// Mock project data generator
export const createMockProject = (overrides = {}) => {
  const { index = 0, name, ...rest } = overrides
  
  return {
    id: index + 1,
    name: name || overrides.names?.[index] || 'Mock Project',
    description: `Description for project ${index + 1}`,
    status: 'active',
    client_id: 1,
    client_name: 'Test Client',
    location: 'Test Location',
    budget: 50000,
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...rest
  }
}

// Mock dashboard stats data
export const createMockDashboardStats = (overrides = {}) => {
  return {
    total_plants: 150,
    total_projects: 12,
    active_projects: 8,
    total_clients: 25,
    suppliers: 5,
    plants: 150,
    products: 200,
    clients: 25,
    projects: 12,
    total_budget: 250000,
    last_updated: '2024-01-01T12:00:00Z',
    recent_projects: [
      { id: 1, name: 'Garden Redesign', status: 'active' },
      { id: 2, name: 'Park Landscaping', status: 'planning' }
    ],
    ...overrides
  }
}

// Mock client data generator
export const createMockClient = (overrides = {}) => {
  const { index = 0, ...rest } = overrides
  
  return {
    id: index + 1,
    name: `Test Client ${index + 1}`,
    email: `client${index + 1}@example.com`,
    phone: '+1234567890',
    address: `Test Address ${index + 1}`,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...rest
  }
}