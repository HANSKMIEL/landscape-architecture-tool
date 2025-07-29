// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish } from '../../test/utils/testHelpers'
import Dashboard from '../Dashboard'

describe('Dashboard Component', () => {
  let user

  beforeEach(() => {
    user = setupUser()
  })

  describe('Rendering and Loading States', () => {
    it('renders dashboard title and subtitle', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText(/overzicht van uw landschapsarchitectuur projecten/i)).toBeInTheDocument()
    })

    it('shows loading state initially', () => {
      render(<Dashboard />)
      
      // Check for loading skeleton elements
      expect(document.querySelector('.animate-pulse')).toBeInTheDocument()
    })

    it('displays dashboard statistics after loading', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      // Check for stats cards in Dutch
      expect(screen.getByText('Leveranciers')).toBeInTheDocument()
      expect(screen.getByText('Planten')).toBeInTheDocument()
      expect(screen.getByText('Actieve Projecten')).toBeInTheDocument()
      expect(screen.getByText('Totaal Budget')).toBeInTheDocument()
      
      // Check for stat values from mock data
      expect(screen.getByText('5')).toBeInTheDocument()   // suppliers
      expect(screen.getByText('156')).toBeInTheDocument() // plants
      expect(screen.getByText('3')).toBeInTheDocument()   // active_projects
    })

    it('displays recent activity section', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Recente Activiteit')).toBeInTheDocument()
      
      // Look for activity items from mock data
      await waitFor(() => {
        expect(screen.getByText(/garden redesign.*created/i)).toBeInTheDocument()
      })
    })

    it('shows quick action buttons', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Leverancier toevoegen')).toBeInTheDocument()
      expect(screen.getByText('Plant toevoegen')).toBeInTheDocument()
      expect(screen.getByText('Klant toevoegen')).toBeInTheDocument()
      expect(screen.getByText('Project starten')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('handles API error for dashboard stats', async () => {
      // Override global fetch for this test
      const originalFetch = global.fetch
      global.fetch = jest.fn((url) => {
        if (url.includes('/api/dashboard/stats')) {
          return Promise.resolve({
            ok: false,
            status: 500,
            statusText: 'Server Error'
          });
        }
        if (url.includes('/api/dashboard/recent-activity')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([])
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({})
        });
      });
      
      render(<Dashboard />)
      
      await waitFor(() => {
        expect(screen.getByText(/verbinding met backend mislukt/i)).toBeInTheDocument()
      })

      // Restore original fetch
      global.fetch = originalFetch
    })
  })
})