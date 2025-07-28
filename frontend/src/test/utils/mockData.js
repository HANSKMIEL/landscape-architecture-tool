// Plant mock data factory
export const createMockPlant = (overrides = {}) => ({
  id: Math.floor(Math.random() * 1000),
  name: 'Mock Plant',
  common_name: 'Mock Common Name',
  scientific_name: 'Plantus mockus',
  category: 'shrub',
  height_min: 50,
  height_max: 150,
  width_min: 40,
  width_max: 100,
  sun_requirements: 'full_sun',
  soil_type: 'well_drained',
  water_needs: 'moderate',
  hardiness_zone: '5-9',
  bloom_time: 'spring',
  bloom_color: 'white',
  foliage_color: 'green',
  native: false,
  supplier_id: 1,
  price: '29.99',
  availability: 'available',
  planting_season: 'spring',
  maintenance: 'low',
  notes: 'Mock plant for testing',
  created_at: new Date().toISOString(),
  ...overrides
});

// Project mock data factory
export const createMockProject = (overrides = {}) => ({
  id: Math.floor(Math.random() * 1000),
  name: 'Mock Project',
  description: 'A test project for development',
  status: 'active',
  client_id: 1,
  client: {
    id: 1,
    name: 'Mock Client',
    email: 'client@example.com'
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides
});

// Client mock data factory
export const createMockClient = (overrides = {}) => ({
  id: Math.floor(Math.random() * 1000),
  name: 'Mock Client',
  email: 'client@example.com',
  phone: '+1234567890',
  address: '123 Mock Street',
  city: 'Mock City',
  state: 'Mock State',
  zip_code: '12345',
  created_at: new Date().toISOString(),
  ...overrides
});

// Supplier mock data factory
export const createMockSupplier = (overrides = {}) => ({
  id: Math.floor(Math.random() * 1000),
  name: 'Mock Supplier',
  contact_email: 'supplier@example.com',
  contact_phone: '+1234567890',
  address: '456 Supplier Ave',
  website: 'https://mocksupplier.com',
  specialty: 'plants',
  created_at: new Date().toISOString(),
  ...overrides
});

// Product mock data factory
export const createMockProduct = (overrides = {}) => ({
  id: Math.floor(Math.random() * 1000),
  name: 'Mock Product',
  description: 'A test product',
  price: 29.99,
  unit: 'each',
  supplier_id: 1,
  supplier: createMockSupplier(),
  category: 'plants',
  in_stock: true,
  stock_quantity: 100,
  ...overrides
});

// Plant recommendation mock data factory
export const createMockRecommendation = (overrides = {}) => ({
  id: Math.floor(Math.random() * 1000),
  plant: createMockPlant(),
  score: 0.85,
  reasons: ['Suitable for sun conditions', 'Appropriate height range'],
  criteria_match: {
    sun_requirements: true,
    height_range: true,
    soil_type: true,
    hardiness_zone: true
  },
  ...overrides
});

// Helper function to create arrays of mock data
export const createMockArray = (factory, count = 3, overrides = {}) => {
  return Array.from({ length: count }, (_, index) => 
    factory({ id: index + 1, ...overrides })
  );
};