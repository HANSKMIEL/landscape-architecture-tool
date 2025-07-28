// Simple test to verify our API endpoints are working
import { describe, it, expect } from 'vitest';

describe('MSW Direct API Tests', () => {
  it('should mock plants API with pagination', async () => {
    const response = await fetch('/api/plants?page=1&per_page=5');
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data).toHaveProperty('plants');
    expect(data).toHaveProperty('total');
    expect(data).toHaveProperty('page', 1);
    expect(data).toHaveProperty('per_page', 5);
    expect(data.plants).toHaveLength(5);
    expect(data.plants[0]).toHaveProperty('name');
    expect(data.plants[0]).toHaveProperty('scientific_name');
  });

  it('should mock single plant API', async () => {
    const response = await fetch('/api/plants/123');
    expect(response.ok).toBe(true);
    
    const plant = await response.json();
    expect(plant).toHaveProperty('id', 123);
    expect(plant).toHaveProperty('name', 'Mock Plant 123');
    expect(plant).toHaveProperty('scientific_name');
  });

  it('should mock dashboard stats', async () => {
    const response = await fetch('/api/dashboard/stats');
    expect(response.ok).toBe(true);
    
    const stats = await response.json();
    expect(stats).toHaveProperty('total_plants', 150);
    expect(stats).toHaveProperty('total_projects', 12);
    expect(stats).toHaveProperty('active_projects', 8);
    expect(stats).toHaveProperty('total_clients', 25);
  });

  it('should mock plant recommendations', async () => {
    const criteria = {
      sun_requirements: 'Full Sun',
      water_requirements: 'Low',
      soil_type: 'Sandy'
    };
    
    const response = await fetch('/api/plants/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(criteria)
    });
    
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data).toHaveProperty('recommendations');
    expect(data).toHaveProperty('criteria', criteria);
    expect(data.recommendations).toHaveLength(3);
    expect(data.recommendations[0]).toHaveProperty('plant');
    expect(data.recommendations[0]).toHaveProperty('score');
  });

  it('should mock suppliers API', async () => {
    const response = await fetch('/api/suppliers');
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data).toHaveProperty('suppliers');
    expect(data.suppliers.length).toBeGreaterThan(0);
    expect(data.suppliers[0]).toHaveProperty('name');
    expect(data.suppliers[0]).toHaveProperty('contact_person');
  });

  it('should handle search parameters', async () => {
    const response = await fetch('/api/plants?search=Mock');
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data).toHaveProperty('plants');
    // All mock plants should contain "Mock" in the name
    data.plants.forEach(plant => {
      expect(plant.name.toLowerCase()).toContain('mock');
    });
  });
});