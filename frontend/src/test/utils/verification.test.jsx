import { describe, it, expect } from 'vitest';
import { render, screen } from '../utils';
import { createMockPlant, createMockArray } from '../utils';

// Simple test component for verification
const TestComponent = ({ plant }) => (
  <div>
    <h1>Test Plant: {plant.name}</h1>
    <p>Category: {plant.category}</p>
  </div>
);

describe('Test utilities verification', () => {
  it('custom render function works with React Router', () => {
    const mockPlant = createMockPlant({ name: 'Test Plant' });
    render(<TestComponent plant={mockPlant} />);
    
    expect(screen.getByText('Test Plant: Test Plant')).toBeInTheDocument();
    expect(screen.getByText('Category: shrub')).toBeInTheDocument();
  });

  it('mock data factories create realistic data', () => {
    const mockPlant = createMockPlant({ name: 'Test Plant' });
    expect(mockPlant.name).toBe('Test Plant');
    expect(mockPlant.category).toBe('shrub');
    expect(mockPlant.sun_requirements).toBe('full_sun');
    expect(mockPlant.id).toBeTypeOf('number');
  });

  it('createMockArray helper works correctly', () => {
    const mockPlants = createMockArray(createMockPlant, 3);
    expect(mockPlants).toHaveLength(3);
    expect(mockPlants[0].id).toBe(1);
    expect(mockPlants[1].id).toBe(2);
    expect(mockPlants[2].id).toBe(3);
  });
});