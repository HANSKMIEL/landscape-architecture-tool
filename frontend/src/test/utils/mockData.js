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