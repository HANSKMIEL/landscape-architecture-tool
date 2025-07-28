import React from 'react';
import { render, screen, waitFor } from '../../test/utils.jsx';
import { setupUser } from '../../test/utils/testHelpers';
import { mockApiEndpoint, mockApiError } from '../../test/utils/mswUtils';
import Dashboard from '../Dashboard';

describe('Dashboard Component', () => {
  const user = setupUser();
  beforeEach(() => {
    // Reset any custom API mocks before each test
    vi.clearAllMocks();
  });

  test('renders dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('loads and displays dashboard statistics', async () => {
    const mockStats = {
      total_plants: 150,
      total_projects: 12,
      active_projects: 8,
      total_clients: 25,
      suppliers: 5,
      plants: 150,
      products: 200,
      clients: 25,
      projects: 12,
      total_budget: 250000
    };

    mockApiEndpoint('get', '/api/dashboard/stats', mockStats);
    mockApiEndpoint('get', '/api/dashboard/recent-activity', []);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument(); // total plants
      expect(screen.getByText('12')).toBeInTheDocument();  // total projects
      expect(screen.getByText('8')).toBeInTheDocument();   // active projects
      expect(screen.getByText('25')).toBeInTheDocument();  // total clients
    });

    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

  test('displays error message when API fails', async () => {
    mockApiError('get', '/api/dashboard/stats', 500, 'Failed to load dashboard data');

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Verbinding met backend mislukt/i)).toBeInTheDocument();
    });

    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

  test('displays recent projects section', async () => {
    const mockStats = {
      total_plants: 150,
      total_projects: 12,
      active_projects: 8,
      total_clients: 25,
      suppliers: 5,
      plants: 150,
      products: 200,
      clients: 25,
      projects: 12,
      total_budget: 250000
    };

    const mockActivity = [
      { 
        id: 1, 
        title: 'Garden Redesign', 
        description: 'New project started',
        timestamp: '2024-01-01T12:00:00Z',
        user: 'Test User'
      },
      { 
        id: 2, 
        title: 'Park Landscaping', 
        description: 'Project in planning',
        timestamp: '2024-01-01T12:00:00Z',
        user: 'Test User'
      }
    ];

    mockApiEndpoint('get', '/api/dashboard/stats', mockStats);
    mockApiEndpoint('get', '/api/dashboard/recent-activity', mockActivity);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Garden Redesign')).toBeInTheDocument();
      expect(screen.getByText('Park Landscaping')).toBeInTheDocument();
    });
  });

  test('displays empty state when no data exists', async () => {
    const emptyStats = {
      total_plants: 0,
      total_projects: 0,
      active_projects: 0,
      total_clients: 0,
      suppliers: 0,
      plants: 0,
      products: 0,
      clients: 0,
      projects: 0,
      total_budget: 0
    };

    mockApiEndpoint('get', '/api/dashboard/stats', emptyStats);
    mockApiEndpoint('get', '/api/dashboard/recent-activity', []);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Geen gegevens beschikbaar/i)).toBeInTheDocument();
    });
  });

  test('refreshes data when retry button is clicked', async () => {
    // First, mock an error response
    mockApiError('get', '/api/dashboard/stats', 500, 'Server error');

    render(<Dashboard />);

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(/Verbinding met backend mislukt/i)).toBeInTheDocument();
    });

    // Now mock a successful response for retry
    const mockStats = {
      total_plants: 150,
      total_projects: 12,
      active_projects: 8,
      total_clients: 25,
      suppliers: 5,
      plants: 150,
      products: 200,
      clients: 25,
      projects: 12,
      total_budget: 250000
    };

    mockApiEndpoint('get', '/api/dashboard/stats', mockStats);
    mockApiEndpoint('get', '/api/dashboard/recent-activity', []);

    // Click retry button
    const retryButton = screen.getByRole('button', { name: /Opnieuw proberen/i });
    await userEvent.click(retryButton);

    // Should show loading state again
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();

    // Should load data successfully
    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument();
    });
  });
});