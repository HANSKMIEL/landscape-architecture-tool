import React from 'react';
import { render, screen, waitFor } from '../../test/utils.jsx';
import { setupUser } from '../../test/utils/testHelpers';
import Plants from '../Plants';

// Mock window.confirm and window.alert
global.confirm = vi.fn();
global.alert = vi.fn();
global.fetch = vi.fn();

describe('Plants Component', () => {
  const user = setupUser();

  beforeEach(() => {
    vi.clearAllMocks();
    global.confirm.mockReturnValue(true);
    global.alert.mockImplementation(() => {});
    global.fetch.mockClear();
  });

  test('renders plants list page', async () => {
    // Mock API responses
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/plants')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      if (url.includes('/api/suppliers')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Plants />);
    
    expect(screen.getByRole('heading', { name: /Planten/i })).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText(/Plant toevoegen/i)).toBeInTheDocument();
    });
  });

  test('displays empty state when no plants exist', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/plants')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      if (url.includes('/api/suppliers')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText(/Nog geen planten toegevoegd/i)).toBeInTheDocument();
    });
  });

  test('loads and displays plants list', async () => {
    const mockPlants = [
      {
        id: 1,
        name: 'Rosa damascena',
        common_name: 'Damascener Roos',
        category: 'shrub',
        price: 15.99
      },
      {
        id: 2,
        name: 'Lavandula angustifolia',
        common_name: 'Echte Lavendel',
        category: 'perennial',
        price: 12.50
      }
    ];

    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/plants')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockPlants)
        });
      }
      if (url.includes('/api/suppliers')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText('Damascener Roos')).toBeInTheDocument();
      expect(screen.getByText('Echte Lavendel')).toBeInTheDocument();
    });
  });

  test('opens add plant modal when add button is clicked', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/plants')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      if (url.includes('/api/suppliers')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText(/Nog geen planten toegevoegd/i)).toBeInTheDocument();
    });

    // Use the first "Plant toevoegen" button (the one in the header)
    const addButtons = screen.getAllByText(/Plant toevoegen/i);
    await user.click(addButtons[0]);

    // Look for modal content and form fields
    expect(screen.getByPlaceholderText(/bijv. Acer platanoides/i)).toBeInTheDocument();
    expect(screen.getByText(/Wetenschappelijke naam/i)).toBeInTheDocument();
  });

  test('handles search functionality', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/api/plants')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      if (url.includes('/api/suppliers')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        });
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Zoek planten/i)).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Zoek planten/i);
    await user.type(searchInput, 'rosa');

    expect(searchInput).toHaveValue('rosa');
  });

  test('displays error message when API fails', async () => {
    global.fetch.mockRejectedValue(new Error('API Error'));

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText(/Fout bij laden van planten/i)).toBeInTheDocument();
    });
  });
});