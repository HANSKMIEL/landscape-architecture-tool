import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { useState, useEffect } from 'react';
import { mockApiEndpoint, mockApiError } from '../utils/mswUtils';

// Mock component that makes API call
const TestApiComponent = ({ endpoint = '/api/plants' }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(endpoint);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;
  
  return (
    <div>
      <h2>API Response</h2>
      {data.plants && (
        <ul>
          {data.plants.map(plant => (
            <div key={plant.id} data-testid={`plant-${plant.id}`}>
              {plant.name}
            </div>
          ))}
        </ul>
      )}
      {data.projects && (
        <ul>
          {data.projects.map(project => (
            <div key={project.id} data-testid={`project-${project.id}`}>
              {project.name}
            </div>
          ))}
        </ul>
      )}
      {data.total_plants && (
        <div data-testid="dashboard-stats">
          Total Plants: {data.total_plants}
        </div>
      )}
    </div>
  );
};

describe('MSW API Mocking', () => {
  beforeEach(() => {
    // Reset any custom handlers before each test
    // This is automatically done by the afterEach in setup.js
  });

  it('intercepts and mocks GET /api/plants', async () => {
    render(<TestApiComponent endpoint="/api/plants" />);
    
    // Should show loading initially
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    // Wait for API response and check mock data
    await waitFor(() => {
      expect(screen.getByText('API Response')).toBeInTheDocument();
    });
    
    // Check that mock plant data is displayed
    expect(screen.getByText('Mock Plant 1')).toBeInTheDocument();
    expect(screen.getByTestId('plant-1')).toBeInTheDocument();
  });

  it('intercepts and mocks GET /api/projects', async () => {
    render(<TestApiComponent endpoint="/api/projects" />);
    
    await waitFor(() => {
      expect(screen.getByText('API Response')).toBeInTheDocument();
    });
    
    // Check that mock project data is displayed
    expect(screen.getByText('Mock Project 1')).toBeInTheDocument();
    expect(screen.getByTestId('project-1')).toBeInTheDocument();
  });

  it('intercepts and mocks GET /api/dashboard/stats', async () => {
    render(<TestApiComponent endpoint="/api/dashboard/stats" />);
    
    await waitFor(() => {
      expect(screen.getByText('API Response')).toBeInTheDocument();
    });
    
    // Check dashboard stats
    expect(screen.getByTestId('dashboard-stats')).toBeInTheDocument();
    expect(screen.getByText('Total Plants: 150')).toBeInTheDocument();
  });

  it('can override endpoints for custom responses', async () => {
    // Override the plants endpoint with custom data
    mockApiEndpoint('get', '/api/plants', {
      plants: [
        { id: 999, name: 'Custom Test Plant' }
      ],
      total: 1
    });

    render(<TestApiComponent endpoint="/api/plants" />);
    
    await waitFor(() => {
      expect(screen.getByText('Custom Test Plant')).toBeInTheDocument();
    });
    
    expect(screen.getByTestId('plant-999')).toBeInTheDocument();
  });

  it('can mock API errors', async () => {
    // Mock an error response
    mockApiError('get', '/api/plants', 500, 'Test server error');

    render(<TestApiComponent endpoint="/api/plants" />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/HTTP error! status: 500/)).toBeInTheDocument();
  });

  it('handles 404 errors correctly', async () => {
    mockApiError('get', '/api/plants/999', 404, 'Plant not found');

    render(<TestApiComponent endpoint="/api/plants/999" />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/HTTP error! status: 404/)).toBeInTheDocument();
  });

  it('works with POST requests', async () => {
    // Test that MSW intercepts POST requests
    const testData = { name: 'New Test Plant', scientific_name: 'Testus plantus' };
    
    const result = await fetch('/api/plants', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testData)
    });
    
    expect(result.status).toBe(201);
    const responseData = await result.json();
    expect(responseData.id).toBe(999); // Mock ID from handler
    expect(responseData.name).toBe(testData.name);
  });

  it('works with PUT requests', async () => {
    const updateData = { name: 'Updated Plant Name' };
    
    const result = await fetch('/api/plants/5', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    
    expect(result.ok).toBe(true);
    const responseData = await result.json();
    expect(responseData.id).toBe(5);
    expect(responseData.name).toBe(updateData.name);
  });

  it('works with DELETE requests', async () => {
    const result = await fetch('/api/plants/3', {
      method: 'DELETE'
    });
    
    expect(result.ok).toBe(true);
    const responseData = await result.json();
    expect(responseData.message).toContain('Plant 3 deleted successfully');
  });
});