import React from 'react';
import { render, screen, waitFor } from '../../test/utils.jsx';
import { setupUser } from '../../test/utils/testHelpers';
import Dashboard from '../Dashboard';

describe('Dashboard Component', () => {
  const user = setupUser();

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch.mockClear();
  });

  test('renders dashboard content', async () => {
    // Mock successful but empty API responses 
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/dashboard/stats')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            suppliers: 0,
            plants: 0,
            active_projects: 0,
            total_budget: 0
          })
        });
      }
      if (url.includes('/api/dashboard/recent-activity')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Dashboard />);
    
    // Wait for the component to load and check for dashboard-specific content
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  test('shows loading state initially', () => {
    // Mock pending promises to keep loading state
    global.fetch.mockImplementation(() => new Promise(() => {}));

    render(<Dashboard />);
    
    // Check for loading skeleton elements
    const skeletonElements = document.querySelectorAll('.animate-pulse');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  test('displays empty state when no data exists', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/dashboard/stats')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            suppliers: 0,
            plants: 0,
            active_projects: 0,
            total_budget: 0
          })
        });
      }
      if (url.includes('/api/dashboard/recent-activity')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Geen gegevens beschikbaar/i)).toBeInTheDocument();
    });
  });

  test('displays error state when API fails', async () => {
    global.fetch.mockRejectedValue(new Error('API Error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Verbinding met backend mislukt/i)).toBeInTheDocument();
    });
  });

  test('displays statistics when data is available', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/dashboard/stats')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            suppliers: 5,
            plants: 150,
            active_projects: 8,
            total_budget: 250000
          })
        });
      }
      if (url.includes('/api/dashboard/recent-activity')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument(); // plants
      expect(screen.getByText('5')).toBeInTheDocument();   // suppliers  
      expect(screen.getByText('8')).toBeInTheDocument();   // active projects
    });
  });

  test('renders quick action buttons', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/dashboard/stats')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            suppliers: 5,
            plants: 150,
            active_projects: 8,
            total_budget: 250000
          })
        });
      }
      if (url.includes('/api/dashboard/recent-activity')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Leverancier toevoegen/i)).toBeInTheDocument();
      expect(screen.getByText(/Plant toevoegen/i)).toBeInTheDocument();
      expect(screen.getByText(/Klant toevoegen/i)).toBeInTheDocument();
      expect(screen.getByText(/Project starten/i)).toBeInTheDocument();
    });
  });
});