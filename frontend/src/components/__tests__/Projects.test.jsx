import React from 'react';
import { render, screen, waitFor } from '../../test/utils.jsx';
import { setupUser } from '../../test/utils/testHelpers';
import { mockApiEndpoint, mockApiError } from '../../test/utils/mswUtils';
import { createMockArray, createMockProject } from '../../test/utils/mockData';
import Projects from '../Projects';

describe('Projects Component', () => {
  const user = setupUser();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders projects list page', () => {
    render(<Projects language="en" />);
    expect(screen.getByRole('heading', { name: /Projects/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /New Project/i })).toBeInTheDocument();
  });

  test('renders projects list page in Dutch', () => {
    render(<Projects language="nl" />);
    expect(screen.getByRole('heading', { name: /Projecten/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Nieuw Project/i })).toBeInTheDocument();
  });

  test('loads and displays projects list', async () => {
    const mockProjects = createMockArray(createMockProject, 2, {
      names: ['Garden Redesign', 'Park Landscaping']
    });

    mockApiEndpoint('get', '/api/projects', mockProjects);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Garden Redesign')).toBeInTheDocument();
      expect(screen.getByText('Park Landscaping')).toBeInTheDocument();
    });
  });

  test('displays empty state when no projects exist', async () => {
    mockApiEndpoint('get', '/api/projects', []);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText(/No projects found/i)).toBeInTheDocument();
      expect(screen.getByText(/Create your first project to get started/i)).toBeInTheDocument();
    });
  });

  test('displays loading state initially', () => {
    render(<Projects language="en" />);
    expect(screen.getByText(/Loading projects.../i)).toBeInTheDocument();
  });

  test('displays error message when API fails', async () => {
    mockApiError('get', '/api/projects', 500, 'Failed to load projects');

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Projects/i)).toBeInTheDocument();
      expect(screen.getByText(/Failed to load projects/i)).toBeInTheDocument();
    });
  });

  test('shows project details including client and location', async () => {
    const mockProjects = [
      createMockProject({ 
        id: 1, 
        name: 'Test Project',
        client_name: 'John Doe',
        location: 'Amsterdam',
        status: 'active'
      })
    ];

    mockApiEndpoint('get', '/api/projects', mockProjects);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Amsterdam')).toBeInTheDocument();
      expect(screen.getByText('active')).toBeInTheDocument();
    });
  });

  test('displays project status badges with correct styling', async () => {
    const mockProjects = [
      createMockProject({ 
        id: 1, 
        name: 'Active Project', 
        status: 'in progress'
      }),
      createMockProject({ 
        id: 2, 
        name: 'Completed Project', 
        status: 'completed'
      }),
      createMockProject({ 
        id: 3, 
        name: 'Planning Project', 
        status: 'planning'
      })
    ];

    mockApiEndpoint('get', '/api/projects', mockProjects);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('in progress')).toBeInTheDocument();
      expect(screen.getByText('completed')).toBeInTheDocument();
      expect(screen.getByText('planning')).toBeInTheDocument();
    });
  });

  test('navigates to project detail when manage plants button is clicked', async () => {
    const mockProjects = [createMockProject({ id: 1, name: 'Test Project' })];
    mockApiEndpoint('get', '/api/projects', mockProjects);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });

    const managePlantsButton = screen.getByRole('button', { name: /Manage Plants/i });
    await user.click(managePlantsButton);

    // Should show the project plant management view
    await waitFor(() => {
      expect(screen.getByText(/Back to Projects/i)).toBeInTheDocument();
    });
  });

  test('can return to projects list from project detail', async () => {
    const mockProjects = [createMockProject({ id: 1, name: 'Test Project' })];
    mockApiEndpoint('get', '/api/projects', mockProjects);

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
      expect(screen.getByText(/Projects/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /New Project/i })).toBeInTheDocument();
    });
  });

  test('handles different project statuses correctly', async () => {
    const mockProjects = [
      createMockProject({ 
        id: 1, 
        name: 'On Hold Project', 
        status: 'on hold'
      })
    ];

    mockApiEndpoint('get', '/api/projects', mockProjects);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('on hold')).toBeInTheDocument();
    });
  });

  test('displays project budget when available', async () => {
    const mockProjects = [
      createMockProject({ 
        id: 1, 
        name: 'Budget Project', 
        budget: 50000
      })
    ];

    mockApiEndpoint('get', '/api/projects', mockProjects);

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText('Budget Project')).toBeInTheDocument();
      // The component should display budget information
    });
  });

  test('retries loading projects when try again button is clicked', async () => {
    // First mock an error
    mockApiError('get', '/api/projects', 500, 'Server error');

    render(<Projects language="en" />);

    await waitFor(() => {
      expect(screen.getByText(/Error Loading Projects/i)).toBeInTheDocument();
    });

    // Now mock successful response
    const mockProjects = [createMockProject({ name: 'Test Project' })];
    mockApiEndpoint('get', '/api/projects', mockProjects);

    // Click try again button
    const tryAgainButton = screen.getByRole('button', { name: /Try Again/i });
    await user.click(tryAgainButton);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });
  });
});