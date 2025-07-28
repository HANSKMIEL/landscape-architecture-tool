import React from 'react';
import { render, screen, waitFor } from '../../test/utils.jsx';
import { setupUser } from '../../test/utils/testHelpers';
import Projects from '../Projects';

global.fetch = vi.fn();

describe('Projects Component', () => {
  const user = setupUser();

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch.mockClear();
  });

  test('renders projects list page in English', async () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Keep loading

    render(<Projects language="en" />);
    expect(screen.getByRole('heading', { name: /Projects/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /New Project/i })).toBeInTheDocument();
  });

  test('renders projects list page in Dutch', async () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Keep loading

    render(<Projects language="nl" />);
    expect(screen.getByRole('heading', { name: /Projecten/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Nieuw Project/i })).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    global.fetch.mockImplementation(() => new Promise(() => {})); // Keep loading

    render(<Projects language="en" />);
    expect(screen.getByText(/Loading projects.../i)).toBeInTheDocument();
  });

  test('displays empty state when no projects exist', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([])
    });

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText(/No projects found/i)).toBeInTheDocument();
      expect(screen.getByText(/Create your first project to get started/i)).toBeInTheDocument();
    });
  });

  test('loads and displays projects list', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Garden Redesign',
        description: 'A beautiful garden project',
        status: 'active',
        client_name: 'John Doe',
        location: 'Amsterdam',
        budget: 50000,
        start_date: '2024-01-01'
      },
      {
        id: 2,
        name: 'Park Landscaping',
        description: 'Large park renovation',
        status: 'planning',
        client_name: 'Jane Smith',
        location: 'Rotterdam',
        budget: 100000,
        start_date: '2024-02-01'
      }
    ];

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockProjects)
    });

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Garden Redesign')).toBeInTheDocument();
      expect(screen.getByText('Park Landscaping')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  test('displays error message when API fails', async () => {
    global.fetch.mockRejectedValue(new Error('API Error'));

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Projects/i)).toBeInTheDocument();
    });
  });

  test('shows project details including status badges', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Active Project',
        description: 'Test project',
        status: 'in progress',
        client_name: 'Test Client',
        location: 'Test Location'
      }
    ];

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockProjects)
    });

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Active Project')).toBeInTheDocument();
      expect(screen.getByText('in progress')).toBeInTheDocument();
      expect(screen.getByText('Test Client')).toBeInTheDocument();
      expect(screen.getByText('Test Location')).toBeInTheDocument();
    });
  });

  test('can navigate to project detail view', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Test Project',
        description: 'Test description',
        status: 'active',
        client_name: 'Test Client'
      }
    ];

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockProjects)
    });

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });

    // Find and click the manage plants button
    const managePlantsButton = screen.getByRole('button', { name: /Manage Plants/i });
    await user.click(managePlantsButton);

    // Should navigate to project detail view
    await waitFor(() => {
      expect(screen.getByText(/Back to Projects/i)).toBeInTheDocument();
    });
  });

  test('can return to projects list from project detail', async () => {
    const mockProjects = [
      {
        id: 1,
        name: 'Test Project',
        description: 'Test description',
        status: 'active',
        client_name: 'Test Client'
      }
    ];

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockProjects)
    });

    render(<Projects language="en" />);

    // Navigate to project detail
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });

    const managePlantsButton = screen.getByRole('button', { name: /Manage Plants/i });
    await user.click(managePlantsButton);

    // Should show back button
    await waitFor(() => {
      expect(screen.getByText(/Back to Projects/i)).toBeInTheDocument();
    });

    // Click back button
    const backButton = screen.getByRole('button', { name: /Back to Projects/i });
    await user.click(backButton);

    // Should return to projects list
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /Projects/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /New Project/i })).toBeInTheDocument();
    });
  });
});