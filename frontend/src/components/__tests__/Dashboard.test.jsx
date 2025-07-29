// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish, expectErrorMessage } from '../../test/utils/testHelpers'
import Dashboard from '../Dashboard'

expect.extend(toHaveNoViolations)

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

    it('displays dashboard data after loading', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      // Check for stats cards in Dutch
      expect(screen.getByText('Leveranciers')).toBeInTheDocument()
      expect(screen.getByText('Planten')).toBeInTheDocument()
      expect(screen.getByText('Actieve Projecten')).toBeInTheDocument()
      expect(screen.getByText('Totaal Budget')).toBeInTheDocument()
      
      // Check for stat values from mock data (updated to match mock response structure)
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
        expect(screen.getByText(/new project.*garden redesign.*created/i)).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('handles API error for dashboard stats', async () => {
      // Mock API error for stats endpoint only
      global.fetch.mockImplementation((url) => {
        if (url.includes('/api/dashboard/stats')) {
          return Promise.resolve({
            ok: false,
            status: 500,
            statusText: 'Server Error',
            json: () => Promise.resolve({ error: 'Server error' })
          });
        }
        if (url.includes('/api/dashboard/recent-activity')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([
              {
                id: 1,
                type: 'project_created',
                description: 'New project "Garden Redesign" created',
                timestamp: '2024-01-15T10:30:00Z',
                user: 'John Doe'
              }
            ])
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({})
        });
      });
      
      render(<Dashboard />)
      
      await waitFor(() => {
        expectErrorMessage('Fout bij laden van statistieken')
      })
    })

    it('shows quick action buttons', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Voeg Project Toe')).toBeInTheDocument()
      expect(screen.getByText('Voeg Plant Toe')).toBeInTheDocument()
      expect(screen.getByText('Bekijk Leveranciers')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})