// Test framework agnostic - works with Jest and Vitest
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { renderWithLanguage } from '../../test/utils/render.jsx'
import { createMockProjects } from '../../test/utils/mockData.js'
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
      
      if (url.includes('/clients')) {
        // Mock clients data for dropdown
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (name) => name === 'content-type' ? 'application/json' : null
          },
          json: () => Promise.resolve({ 
            clients: [
              { id: 1, name: 'Family Johnson', email: 'johnson@example.com' },
              { id: 2, name: 'City Council', email: 'council@city.gov' },
              { id: 3, name: 'TechCorp BV', email: 'contact@techcorp.nl' }
            ]
          })
        })
      }
      
      // Default fallback for unhandled URLs
      return Promise.resolve({
        ok: true,
        status: 200,
        headers: {
          get: (name) => name === 'content-type' ? 'application/json' : null
        },
        json: () => Promise.resolve({})
      })
    })
  })

  afterEach(() => {
    // Restore original fetch
    global.fetch = originalFetch
  })

  describe('Basic Rendering', () => {
    it('renders projects page with English language', async () => {
      // Mock localStorage to prevent infinite loading
      const mockLocalStorage = {
        getItem: createMockFn(() => null),
        setItem: createMockFn(),
        removeItem: createMockFn(),
        clear: createMockFn()
      }
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      })

      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 10000 })
    })

    it('renders projects page with Dutch language', async () => {
      // Mock localStorage to prevent infinite loading
      const mockLocalStorage = {
        getItem: createMockFn(() => null),
        setItem: createMockFn(),
        removeItem: createMockFn(),
        clear: createMockFn()
      }
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      })

      renderWithLanguage(<Projects language="nl" />, { language: 'nl' })
      
      await waitFor(() => {
        expect(screen.getByText('Projecten')).toBeInTheDocument()
      }, { timeout: 10000 })
    })

    it('displays projects data after loading', async () => {
      // Mock localStorage to prevent infinite loading
      const mockLocalStorage = {
        getItem: createMockFn(() => null),
        setItem: createMockFn(),
        removeItem: createMockFn(),
        clear: createMockFn()
      }
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      })

      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      // Wait for initial page load
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 10000 })
      
      // Wait for projects data to load (increased timeout for CI reliability)
      await waitFor(() => {
        // Look for project names from mock data
        expect(screen.getByText(/Garden Redesign Project/i)).toBeInTheDocument()
      }, { timeout: 20000 })
      
      // Verify other mock projects are displayed
      await waitFor(() => {
        expect(screen.getByText(/Park Renovation/i)).toBeInTheDocument()
        expect(screen.getByText(/Corporate Landscape/i)).toBeInTheDocument()
      }, { timeout: 10000 })
    })
  })

  describe('Language Support', () => {
    it('displays correct translations for English', async () => {
      // Mock localStorage to prevent infinite loading
      const mockLocalStorage = {
        getItem: createMockFn(() => null),
        setItem: createMockFn(),
        removeItem: createMockFn(),
        clear: createMockFn()
      }
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      })

      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
        expect(screen.getByText(/manage your landscape architecture projects/i)).toBeInTheDocument()
      }, { timeout: 10000 })
    })

    it('displays correct translations for Dutch', async () => {
      // Mock localStorage to prevent infinite loading
      const mockLocalStorage = {
        getItem: createMockFn(() => null),
        setItem: createMockFn(),
        removeItem: createMockFn(),
        clear: createMockFn()
      }
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      })

      renderWithLanguage(<Projects language="nl" />, { language: 'nl' })
      
      await waitFor(() => {
        expect(screen.getByText('Projecten')).toBeInTheDocument()
        expect(screen.getByText(/beheer uw landschapsarchitectuur projecten/i)).toBeInTheDocument()
      }, { timeout: 10000 })
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      // Mock localStorage to prevent infinite loading
      const mockLocalStorage = {
        getItem: createMockFn(() => null),
        setItem: createMockFn(),
        removeItem: createMockFn(),
        clear: createMockFn()
      }
      Object.defineProperty(window, 'localStorage', {
        value: mockLocalStorage,
        writable: true
      })

      const { container } = renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 10000 })
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})