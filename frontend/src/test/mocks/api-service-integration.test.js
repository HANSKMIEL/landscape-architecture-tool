// Integration test showing MSW working with the actual API service
import { describe, it, expect } from 'vitest';
import apiService from '../../services/api';
import { mockApiEndpoint, mockApiError } from '../utils/mswUtils';

describe('MSW Integration with API Service', () => {
  it('should work with apiService.getPlants()', async () => {
    const plants = await apiService.getPlants({ page: 1, per_page: 3 });
    
    expect(plants).toHaveProperty('plants');
    expect(plants).toHaveProperty('total');
    expect(plants.plants).toHaveLength(3);
    expect(plants.plants[0]).toHaveProperty('name');
    expect(plants.plants[0].name).toContain('Mock Plant');
  });

  it('should work with apiService.getDashboardStats()', async () => {
    const stats = await apiService.getDashboardStats();
    
    expect(stats).toHaveProperty('total_plants', 150);
    expect(stats).toHaveProperty('total_projects', 12);
    expect(stats).toHaveProperty('active_projects', 8);
    expect(stats).toHaveProperty('total_clients', 25);
  });

  it('should work with apiService.getSuppliers()', async () => {
    const result = await apiService.getSuppliers({ page: 1 });
    
    expect(result).toHaveProperty('suppliers');
    expect(result.suppliers.length).toBeGreaterThan(0);
    expect(result.suppliers[0]).toHaveProperty('name');
    expect(result.suppliers[0]).toHaveProperty('contact_person');
  });

  it('should handle errors from API service', async () => {
    // Mock an error response for plants endpoint
    mockApiError('get', '/api/plants', 500, 'Database connection failed');
    
    await expect(apiService.getPlants()).rejects.toThrow('HTTP error! status: 500');
  });

  it('should work with custom overrides', async () => {
    // Override the dashboard stats with custom data
    const customStats = {
      total_plants: 999,
      total_projects: 888,
      active_projects: 777,
      total_clients: 666
    };
    
    mockApiEndpoint('get', '/api/dashboard/stats', customStats);
    
    const stats = await apiService.getDashboardStats();
    expect(stats).toEqual(customStats);
  });

  it('should work with plant recommendations', async () => {
    const criteria = {
      sun_requirements: 'Full Sun',
      water_requirements: 'Low'
    };
    
    const result = await apiService.getPlantRecommendations(criteria);
    
    expect(result).toHaveProperty('recommendations');
    expect(result).toHaveProperty('criteria', criteria);
    expect(result.recommendations).toHaveLength(3);
    expect(result.recommendations[0]).toHaveProperty('plant');
    expect(result.recommendations[0]).toHaveProperty('score');
  });

  it('should work with CRUD operations', async () => {
    // Test create
    const newPlant = { name: 'Test Plant', scientific_name: 'Testus plantus' };
    const created = await apiService.createPlant(newPlant);
    expect(created).toHaveProperty('id', 999);
    expect(created).toHaveProperty('name', newPlant.name);

    // Test get single
    const plant = await apiService.getPlant(5);
    expect(plant).toHaveProperty('id', 5);
    expect(plant).toHaveProperty('name', 'Mock Plant 5');

    // Test update
    const updated = await apiService.updateSupplier(3, { name: 'Updated Supplier' });
    expect(updated).toHaveProperty('id', 3);
    expect(updated).toHaveProperty('name', 'Updated Supplier');

    // Test delete
    const deleteResult = await apiService.deleteSupplier(7);
    expect(deleteResult).toHaveProperty('message');
    expect(deleteResult.message).toContain('Supplier 7 deleted successfully');
  });
});