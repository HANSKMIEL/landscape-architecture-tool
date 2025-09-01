// Test framework agnostic - works with Jest and Vitest
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { renderWithLanguage } from '../../test/utils/render.jsx'
import { createMockProjects, createApiResponse } from '../../test/utils/mockData.js'
import { clearAllMocks, createMockFn } from '../../test/utils/test-helpers.js'
import Projects from '../Projects'

expect.extend(toHaveNoViolations)

describe('Projects Component', () => {
  let originalFetch

  beforeEach(() => {
    // Store original fetch
    originalFetch = global.fetch
    
    // Reset mocks before each test
    clearAllMocks()

    // Mock fetch for API calls using framework-agnostic helper
    global.fetch = createMockFn((url) => {
      if (url.includes('/projects')) {
        // Mock projects data with realistic project information
        const mockProjects = createMockProjects(3, [
          {
            id: 1,
            name: 'Garden Redesign Project',
            description: 'Complete residential garden transformation with native plants',
            client_name: 'Family Johnson',
            location: 'Amsterdam, Netherlands',
            budget: 25000,
            start_date: '2024-03-01',
            status: 'Planning'
          },
          {
            id: 2, 
            name: 'Park Renovation',
            description: 'Urban park landscape renovation with sustainable features',
            client_name: 'City Council',
            location: 'Utrecht, Netherlands',
            budget: 150000,
            start_date: '2024-04-15',
            status: 'In Progress'
          },
          {
            id: 3,
            name: 'Corporate Landscape',
            description: 'Office building exterior landscaping design',
            client_name: 'TechCorp BV',
            location: 'Rotterdam, Netherlands', 
            budget: 75000,
            start_date: '2024-02-01',
            status: 'Completed'
          }
        ])
        
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (name) => name === 'content-type' ? 'application/json' : null
          },
          json: () => Promise.resolve({ projects: mockProjects })
        })
      }
      
      // Default fallback for unhandled URLs
      return Promise.reject(new Error(`Unhandled URL in mock: ${url}`))
    })
  })

  afterEach(() => {
    // Restore original fetch
    global.fetch = originalFetch
  })

  describe('Basic Rendering', () => {
    it('renders projects page with English language', async () => {
      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('renders projects page with Dutch language', async () => {
      renderWithLanguage(<Projects language="nl" />, { language: 'nl' })
      
      await waitFor(() => {
        expect(screen.getByText('Projecten')).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('displays projects data after loading', async () => {
      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      // Wait for initial page load
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 5000 })
      
      // Wait for projects data to load (increased timeout for CI reliability)
      await waitFor(() => {
        // Look for project names from mock data
        expect(screen.getByText(/Garden Redesign Project/i)).toBeInTheDocument()
      }, { timeout: 15000 })
      
      // Verify other mock projects are displayed
      await waitFor(() => {
        expect(screen.getByText(/Park Renovation/i)).toBeInTheDocument()
        expect(screen.getByText(/Corporate Landscape/i)).toBeInTheDocument()
      }, { timeout: 5000 })
    })
  })

  describe('Language Support', () => {
    it('displays correct translations for English', async () => {
      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
        expect(screen.getByText(/manage your landscape architecture projects/i)).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('displays correct translations for Dutch', async () => {
      renderWithLanguage(<Projects language="nl" />, { language: 'nl' })
      
      await waitFor(() => {
        expect(screen.getByText('Projecten')).toBeInTheDocument()
        expect(screen.getByText(/beheer uw landschapsarchitectuur projecten/i)).toBeInTheDocument()
      }, { timeout: 5000 })
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 5000 })
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})