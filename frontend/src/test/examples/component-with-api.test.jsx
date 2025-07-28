// Example of how to use MSW in component tests
// This demonstrates testing a component that makes API calls

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { useState, useEffect } from 'react';
import { mockApiEndpoint, mockApiError } from '../utils/mswUtils';
import apiService from '../../services/api';

// Example component that uses the API service
const PlantList = () => {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlants = async () => {
      try {
        setLoading(true);
        const data = await apiService.getPlants({ per_page: 3 });
        setPlants(data.plants);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPlants();
  }, []);

  if (loading) return <div data-testid="loading">Loading plants...</div>;
  if (error) return <div data-testid="error">Error: {error}</div>;

  return (
    <div data-testid="plant-list">
      <h2>Plant Collection</h2>
      {plants.length === 0 ? (
        <p>No plants found</p>
      ) : (
        <ul>
          {plants.map(plant => (
            <li key={plant.id} data-testid={`plant-item-${plant.id}`}>
              {plant.name} - {plant.scientific_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

describe('PlantList Component with MSW', () => {
  beforeEach(() => {
    // MSW automatically resets handlers after each test via setup.js
  });

  it('displays plants from API', async () => {
    render(<PlantList />);

    // Check loading state
    expect(screen.getByTestId('loading')).toBeInTheDocument();

    // Wait for plants to load
    await waitFor(() => {
      expect(screen.getByTestId('plant-list')).toBeInTheDocument();
    });

    // Check that plants are displayed
    expect(screen.getByText('Plant Collection')).toBeInTheDocument();
    expect(screen.getByTestId('plant-item-1')).toBeInTheDocument();
    expect(screen.getByText(/Mock Plant 1/)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    // Mock an API error for this specific test
    mockApiError('get', '/api/plants', 500, 'Server is down');

    render(<PlantList />);

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByTestId('error')).toBeInTheDocument();
    });

    expect(screen.getByText(/Error: HTTP error! status: 500/)).toBeInTheDocument();
  });

  it('handles empty plant list', async () => {
    // Mock an empty response for this test
    mockApiEndpoint('get', '/api/plants', {
      plants: [],
      total: 0,
      page: 1,
      per_page: 3
    });

    render(<PlantList />);

    await waitFor(() => {
      expect(screen.getByTestId('plant-list')).toBeInTheDocument();
    });

    expect(screen.getByText('No plants found')).toBeInTheDocument();
  });

  it('can test with custom plant data', async () => {
    // Mock custom plant data for this test
    const customPlants = [
      { id: 100, name: 'Custom Rose', scientific_name: 'Rosa testicus' },
      { id: 101, name: 'Test Lily', scientific_name: 'Lilium testicus' }
    ];

    mockApiEndpoint('get', '/api/plants', {
      plants: customPlants,
      total: 2,
      page: 1,
      per_page: 3
    });

    render(<PlantList />);

    await waitFor(() => {
      expect(screen.getByTestId('plant-list')).toBeInTheDocument();
    });

    expect(screen.getByTestId('plant-item-100')).toBeInTheDocument();
    expect(screen.getByText(/Custom Rose - Rosa testicus/)).toBeInTheDocument();
    expect(screen.getByTestId('plant-item-101')).toBeInTheDocument();
    expect(screen.getByText(/Test Lily - Lilium testicus/)).toBeInTheDocument();
  });
});