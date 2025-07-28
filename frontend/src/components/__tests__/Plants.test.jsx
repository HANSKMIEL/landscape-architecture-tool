import React from 'react';
import { render, screen, waitFor, within } from '../../test/utils.jsx';
import { setupUser } from '../../test/utils/testHelpers';
import { mockApiEndpoint, mockApiError } from '../../test/utils/mswUtils';
import { createMockArray, createMockPlant } from '../../test/utils/mockData';
import Plants from '../Plants';

// Mock window.confirm and window.alert
global.confirm = vi.fn();
global.alert = vi.fn();

describe('Plants Component', () => {
  const user = setupUser();

  beforeEach(() => {
    vi.clearAllMocks();
    global.confirm.mockReturnValue(true);
    global.alert.mockImplementation(() => {});
  });

  test('renders plants list page', () => {
    render(<Plants />);
    expect(screen.getByRole('heading', { name: /Planten/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Plant toevoegen/i })).toBeInTheDocument();
  });

  test('loads and displays plants list', async () => {
    const mockPlants = createMockArray(createMockPlant, 3, {
      names: ['Rosa damascena', 'Lavandula angustifolia', 'Buxus sempervirens']
    });

    mockApiEndpoint('get', '/api/plants', mockPlants);
    mockApiEndpoint('get', '/api/suppliers', []);

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText('Rosa damascena')).toBeInTheDocument();
      expect(screen.getByText('Lavandula angustifolia')).toBeInTheDocument();
      expect(screen.getByText('Buxus sempervirens')).toBeInTheDocument();
    });
  });

  test('displays empty state when no plants exist', async () => {
    mockApiEndpoint('get', '/api/plants', []);
    mockApiEndpoint('get', '/api/suppliers', []);

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText(/Nog geen planten toegevoegd/i)).toBeInTheDocument();
    });
  });

  test('filters plants by search term', async () => {
    const mockPlants = createMockArray(createMockPlant, 3);
    mockApiEndpoint('get', '/api/plants', mockPlants);
    mockApiEndpoint('get', '/api/suppliers', []);

    render(<Plants />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Mock Plant')).toBeInTheDocument();
    });

    // Search for specific plant - this should trigger a new API call
    const searchInput = screen.getByPlaceholderText(/Zoek planten/i);
    await user.type(searchInput, 'rosa');

    // Mock filtered results for search
    const filteredPlants = [createMockPlant({ name: 'Rosa damascena' })];
    mockApiEndpoint('get', '/api/plants?search=rosa', filteredPlants);

    await waitFor(() => {
      // The component should make a new API call with the search term
      expect(searchInput).toHaveValue('rosa');
    });
  });

  test('opens add plant modal when add button is clicked', async () => {
    mockApiEndpoint('get', '/api/plants', []);
    mockApiEndpoint('get', '/api/suppliers', []);

    render(<Plants />);

    const addButton = screen.getByRole('button', { name: /Plant toevoegen/i });
    await user.click(addButton);

    expect(screen.getByText(/Plant toevoegen/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Wetenschappelijke naam/i)).toBeInTheDocument();
  });

  test('creates new plant successfully', async () => {
    const newPlant = createMockPlant({ name: 'Rosa newicus' });
    mockApiEndpoint('get', '/api/plants', []);
    mockApiEndpoint('get', '/api/suppliers', []);
    mockApiEndpoint('post', '/api/plants', newPlant, 201);

    render(<Plants />);

    // Open add modal
    const addButton = screen.getByRole('button', { name: /Plant toevoegen/i });
    await user.click(addButton);

    // Fill form
    await user.type(screen.getByLabelText(/Wetenschappelijke naam/i), 'Rosa newicus');
    await user.type(screen.getByLabelText(/Nederlandse naam/i), 'Nieuwe roos');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /toevoegen/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith('Plant succesvol toegevoegd!');
    });
  });

  test('displays error when plant creation fails', async () => {
    mockApiEndpoint('get', '/api/plants', []);
    mockApiEndpoint('get', '/api/suppliers', []);
    mockApiError('post', '/api/plants', 400, 'Validation error');

    render(<Plants />);

    // Open add modal and submit invalid form
    const addButton = screen.getByRole('button', { name: /Plant toevoegen/i });
    await user.click(addButton);

    const submitButton = screen.getByRole('button', { name: /toevoegen/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Fout bij toevoegen plant'));
    });
  });

  test('deletes plant when delete button is clicked', async () => {
    const mockPlants = [createMockPlant({ id: 1, name: 'Test Plant', common_name: 'Test Plant Common' })];
    mockApiEndpoint('get', '/api/plants', mockPlants);
    mockApiEndpoint('get', '/api/suppliers', []);
    mockApiEndpoint('delete', '/api/plants/1', { message: 'Plant deleted' });

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText('Test Plant')).toBeInTheDocument();
    });

    // Find and click delete button
    const deleteButtons = screen.getAllByText(/Verwijderen/i);
    await user.click(deleteButtons[0]);

    await waitFor(() => {
      expect(global.confirm).toHaveBeenCalledWith(expect.stringContaining('Test Plant Common'));
      expect(global.alert).toHaveBeenCalledWith('Plant succesvol verwijderd!');
    });
  });

  test('handles API error when loading plants', async () => {
    mockApiError('get', '/api/plants', 500, 'Server error');
    mockApiEndpoint('get', '/api/suppliers', []);

    render(<Plants />);

    await waitFor(() => {
      expect(screen.getByText(/Fout bij laden van planten/i)).toBeInTheDocument();
    });
  });

  test('displays loading spinner initially', () => {
    render(<Plants />);
    
    // Look for loading spinner or animation
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  test('shows empty state message when search yields no results', async () => {
    mockApiEndpoint('get', '/api/plants', []);
    mockApiEndpoint('get', '/api/suppliers', []);

    render(<Plants />);

    // Type in search box
    const searchInput = screen.getByPlaceholderText(/Zoek planten/i);
    await user.type(searchInput, 'nonexistent');

    await waitFor(() => {
      expect(screen.getByText(/Geen planten gevonden/i)).toBeInTheDocument();
    });
  });
});