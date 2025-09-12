// Test framework agnostic - works with Jest and Vitest
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { render } from '../../test/utils/render.jsx'
import { createMockPlants, createMockSuppliers } from '../../test/utils/mockData.js'
import { clearAllMocks, createMockFn } from '../../test/utils/test-helpers.js'
import Plants from '../Plants'

expect.extend(toHaveNoViolations)

describe('Plants Component', () => {
  let originalFetch

  beforeEach(() => {
    // Store original fetch
    originalFetch = global.fetch
    
    // Reset mocks before each test
    clearAllMocks()

    // Mock fetch for API calls using framework-agnostic helper
    global.fetch = createMockFn((url) => {
      if (url.includes('/api/plants')) {
        // Mock plants data with realistic plant information
        const mockPlants = createMockPlants(3, [
          {
            id: 1,
            name: 'Rosa rugosa',
            common_name: 'Garden Rose',
            category: 'Heester',
            height_min: 1.5,
            height_max: 2.0,
            sun_requirements: 'Volle zon',
            bloom_time: 'Juni-September',
            bloom_color: 'Roze',
            price: 15.99,
            availability: 'Voorradig',
            supplier_id: 1
          },
          {
            id: 2,
            name: 'Acer platanoides',
            common_name: 'Noorse esdoorn', 
            category: 'Boom',
            height_min: 15.0,
            height_max: 25.0,
            sun_requirements: 'Zon tot halfschaduw',
            bloom_time: 'April-Mei',
            bloom_color: 'Geel',
            price: 89.99,
            availability: 'Voorradig',
            supplier_id: 2
          },
          {
            id: 3,
            name: 'Lavandula angustifolia',
            common_name: 'Lavendel',
            category: 'Vaste plant',
            height_min: 0.3,
            height_max: 0.6,
            sun_requirements: 'Volle zon',
            bloom_time: 'Juli-Augustus',
            bloom_color: 'Paars',
            price: 8.99,
            availability: 'Voorradig',
            supplier_id: 1
          }
        ])
        
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (name) => name === 'content-type' ? 'application/json' : null
          },
          json: () => Promise.resolve({ plants: mockPlants })
        })
      }
      
      if (url.includes('/api/suppliers')) {
        // Mock suppliers data
        const mockSuppliers = createMockSuppliers(2, [
          {
            id: 1,
            name: 'Groene Vingers Kwekerij',
            contact_person: 'Jan de Boer',
            email: 'jan@groenevingers.nl'
          },
          {
            id: 2,
            name: 'Boom & Plant Specialist',
            contact_person: 'Maria van den Berg', 
            email: 'maria@boomspecialist.nl'
          }
        ])
        
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (name) => name === 'content-type' ? 'application/json' : null
          },
          json: () => Promise.resolve({ suppliers: mockSuppliers })
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
    it('renders plants page', async () => {
      render(<Plants />)
      
      // Check for loading state first
      expect(document.querySelector('.animate-spin')).toBeInTheDocument()
      
      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('Planten')).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('displays plants data after loading', async () => {
      render(<Plants />)
      
      await waitFor(() => {
        // Look for plant names from mock data - check for common_name from mock
        expect(screen.getByText(/Garden Rose/i)).toBeInTheDocument()
      }, { timeout: 10000 })
      
      // Verify other mock plants are displayed
      await waitFor(() => {
        expect(screen.getByText(/Noorse esdoorn/i)).toBeInTheDocument()
        expect(screen.getByText(/Lavendel/i)).toBeInTheDocument()
      })
    })
  })

  describe('Search Functionality', () => {
    it('allows searching for plants', async () => {
      render(<Plants />)
      
      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText(/zoek planten/i)
        expect(searchInput).toBeInTheDocument()
      }, { timeout: 5000 })
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<Plants />)
      
      await waitFor(() => {
        expect(document.querySelector('.animate-spin')).not.toBeInTheDocument()
      }, { timeout: 5000 })
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})