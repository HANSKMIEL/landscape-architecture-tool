// Mock data generators for testing

// Helper function to create arrays of mock data
export const createMockArray = (createFn, count) => {
  return Array.from({ length: count }, (_, index) => createFn({ id: index + 1 }));
};

// Mock plant data generator
export const createMockPlant = (overrides = {}) => {
  const baseId = overrides.id || 1;
  return {
    id: baseId,
    name: `Mock Plant ${baseId}`,
    scientific_name: `Plantus mockensis ${baseId}`,
    description: `A mock plant for testing purposes. Plant number ${baseId}.`,
    category: 'Perennial',
    size: 'Medium',
    sun_requirements: 'Full Sun',
    water_requirements: 'Moderate',
    soil_type: 'Well-drained',
    bloom_time: 'Spring',
    color: 'Green',
    height_cm: 60 + (baseId * 5),
    spread_cm: 45 + (baseId * 3),
    hardiness_zone: '5-9',
    native: true,
    drought_tolerant: false,
    deer_resistant: true,
    image_url: `/images/plants/mock-plant-${baseId}.jpg`,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
};

// Mock project data generator
export const createMockProject = (overrides = {}) => {
  const baseId = overrides.id || 1;
  return {
    id: baseId,
    name: `Mock Project ${baseId}`,
    description: `A landscape architecture project for testing. Project ${baseId}.`,
    client_id: baseId,
    client_name: `Client ${baseId}`,
    status: 'Active',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    budget: 50000 + (baseId * 10000),
    location: `Test Location ${baseId}`,
    area_sqm: 1000 + (baseId * 100),
    project_type: 'Residential',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
};

// Mock client data generator
export const createMockClient = (overrides = {}) => {
  const baseId = overrides.id || 1;
  return {
    id: baseId,
    name: `Mock Client ${baseId}`,
    email: `client${baseId}@example.com`,
    phone: `555-010${baseId.toString().padStart(2, '0')}`,
    address: `${baseId}23 Test Street`,
    city: 'Test City',
    state: 'Test State',
    zip_code: `1234${baseId}`,
    company: baseId % 2 === 0 ? `Company ${baseId}` : null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
};

// Mock supplier data generator
export const createMockSupplier = (overrides = {}) => {
  const baseId = overrides.id || 1;
  return {
    id: baseId,
    name: `Mock Supplier ${baseId}`,
    contact_person: `Contact Person ${baseId}`,
    email: `supplier${baseId}@example.com`,
    phone: `555-020${baseId.toString().padStart(2, '0')}`,
    address: `${baseId}45 Supplier Lane`,
    city: 'Supplier City',
    state: 'Supplier State',
    zip_code: `5678${baseId}`,
    website: `https://supplier${baseId}.example.com`,
    specialty: 'Plants & Landscaping Materials',
    rating: Math.min(5, 3 + (baseId % 3)),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
};

// Mock recommendation data generator
export const createMockRecommendation = (overrides = {}) => {
  const baseId = overrides.id || 1;
  const plant = createMockPlant({ id: baseId });
  return {
    plant: plant,
    score: 0.8 + (baseId * 0.05),
    reasons: [
      'Matches sun requirements',
      'Suitable for soil type',
      'Appropriate size for space',
    ],
    compatibility: 'High',
    ...overrides,
  };
};

// Mock dashboard stats
export const createMockDashboardStats = (overrides = {}) => {
  return {
    total_plants: 150,
    total_projects: 12,
    active_projects: 8,
    total_clients: 25,
    total_suppliers: 15,
    recent_activities: 5,
    ...overrides,
  };
};

// Mock recent activity
export const createMockActivity = (overrides = {}) => {
  const baseId = overrides.id || 1;
  const activities = [
    'Plant added',
    'Project updated',
    'Client created',
    'Recommendation generated',
    'Supplier contacted',
  ];
  
  return {
    id: baseId,
    type: activities[baseId % activities.length],
    description: `Mock activity ${baseId}: ${activities[baseId % activities.length]}`,
    timestamp: new Date(Date.now() - (baseId * 3600000)).toISOString(), // Hours ago
    user: `User ${baseId}`,
    ...overrides,
  };
};

// === MAIN BRANCH COMPATIBILITY FUNCTIONS ===
// These functions provide compatibility with the main branch format

// Main branch plant factory
export const createMockPlants = (count = 10) => {
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    name: `Rosa rugosa ${index + 1}`,
    common_name: `Beach Rose ${index + 1}`,
    category: ['Shrub', 'Tree', 'Perennial', 'Annual'][index % 4],
    height_min: 2 + index,
    height_max: 5 + index,
    width_min: 2 + index,
    width_max: 4 + index,
    sun_requirements: ['Full Sun', 'Partial Sun', 'Shade'][index % 3],
    soil_type: ['Sandy', 'Clay', 'Loam'][index % 3],
    water_needs: ['Low', 'Medium', 'High'][index % 3],
    hardiness_zone: `${Math.floor(index % 8) + 1}-${Math.floor(index % 8) + 5}`,
    bloom_time: ['Spring', 'Summer', 'Fall'][index % 3],
    bloom_color: ['Pink', 'White', 'Red', 'Yellow'][index % 4],
    foliage_color: 'Green',
    native: index % 2 === 0,
    supplier_id: (index % 3) + 1,
    supplier_name: `Green Thumb Nursery ${(index % 3) + 1}`,
    price: 25.99 + (index * 5),
    availability: 'In Stock',
    planting_season: 'Spring/Fall',
    maintenance: ['Low', 'Medium', 'High'][index % 3],
    notes: `Plant notes for item ${index + 1}`
  }));
};

// Main branch project factory
export const createMockProjects = (count = 10) => {
  const statuses = ['Active', 'Planning', 'Completed', 'On Hold'];
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    name: `Garden Project ${index + 1}`,
    description: `Landscape project description ${index + 1}`,
    client_id: (index % 5) + 1,
    client_name: `Client ${(index % 5) + 1}`,
    location: `Location ${index + 1}`,
    budget: 50000 + (index * 10000),
    start_date: '2024-01-15',
    end_date: '2024-12-15',
    status: statuses[index % statuses.length],
    progress: Math.floor(Math.random() * 100),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }));
};

// Main branch client factory
export const createMockClients = (count = 10) => {
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    name: `Client ${index + 1}`,
    email: `client${index + 1}@example.com`,
    phone: `+1-555-${String(index + 1).padStart(4, '0')}`,
    address: `${100 + index} Main St, City ${index + 1}`,
    company: index % 2 === 0 ? `Company ${index + 1}` : null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }));
};

// Main branch supplier factory
export const createMockSuppliers = (count = 10) => {
  return Array.from({ length: count }, (_, index) => ({
    id: index + 1,
    name: `Supplier ${index + 1}`,
    email: `supplier${index + 1}@example.com`,
    phone: `+1-555-${String(index + 2000).padStart(4, '0')}`,
    address: `${200 + index} Industrial Dr, City ${index + 1}`,
    specialties: ['Plants', 'Tools', 'Materials', 'Services'][index % 4],
    rating: 3 + (index % 3),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }));
};

// Main branch dashboard stats (compatible format)
export const createMockDashboardStatsCompat = () => ({
  suppliers: 5,
  plants: 156,
  products: 45,
  clients: 8,
  projects: 12,
  active_projects: 3,
  total_budget: 150000
});

// Main branch recent activity
export const createMockRecentActivity = () => [
  {
    id: 1,
    type: 'project',
    action: 'created',
    description: 'New project "Garden Redesign" created',
    timestamp: new Date().toISOString()
  },
  {
    id: 2,
    type: 'plant',
    action: 'updated',
    description: 'Plant inventory updated',
    timestamp: new Date(Date.now() - 3600000).toISOString()
  }
];

// API response wrapper
export const createApiResponse = (data, meta = {}) => ({
  data,
  meta,
  success: true
});