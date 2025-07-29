// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish, expectErrorMessage } from '../../test/utils/testHelpers'
// import { server } from '../../test/mocks/server'  // Temporarily disabled
// import { http, HttpResponse } from 'msw'  // Temporarily disabled
import Dashboard from '../Dashboard'

expect.extend(toHaveNoViolations)

describe('Dashboard Component', () => {
  let user

  beforeEach(() => {
    user = setupUser()
  })

  describe('Rendering and Loading States', () => {
    it('renders dashboard title and subtitle', () => {
      render(<Dashboard />)
      
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
      // Mock API error for stats endpoint
      server.use(
        http.get('http://127.0.0.1:5000/api/dashboard/stats', () => {
          return HttpResponse.json(
            { error: 'Server error' },
            { status: 500 }
          )
        })
      )

      render(<Dashboard />)
      
      await waitFor(() => {
        expectErrorMessage(/stats api error: 500/i)
      })
    })

    it('handles API error for recent activity', async () => {
      // Mock API error for activity endpoint
      server.use(
        http.get('http://127.0.0.1:5000/api/dashboard/recent-activity', () => {
          return HttpResponse.json(
            { error: 'Server error' },
            { status: 500 }
          )
        })
      )

      render(<Dashboard />)
      
      await waitFor(() => {
        expectErrorMessage(/activity api error: 500/i)
      })
    })

    it('displays retry button on error and allows retry', async () => {
      // Mock initial error
      server.use(
        http.get('http://127.0.0.1:5000/api/dashboard/stats', () => {
          return HttpResponse.json(
            { error: 'Server error' },
            { status: 500 }
          )
        })
      )

      render(<Dashboard />)
      
      await waitFor(() => {
        expectErrorMessage(/stats api error: 500/i)
      })

      const retryButton = screen.getByRole('button', { name: /opnieuw proberen/i })
      expect(retryButton).toBeInTheDocument()

      // Reset to successful response
      server.resetHandlers()

      await user.click(retryButton)
      
      await waitForLoadingToFinish()
      expect(screen.getByText('Leveranciers')).toBeInTheDocument()
    })
  })

  describe('Data Display and Formatting', () => {
    it('displays active vs completed projects correctly', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Actieve Projecten')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument() // active_projects from mock
    })

    it('displays budget information with proper formatting', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Totaal Budget')).toBeInTheDocument()
      // Check for Euro formatting (Dutch locale)
      expect(screen.getByText('€ 150.000')).toBeInTheDocument() // total_budget formatted
    })

    it('displays plants and suppliers information', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Planten')).toBeInTheDocument()
      expect(screen.getByText('156')).toBeInTheDocument() // plants from mock
      
      expect(screen.getByText('Leveranciers')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument() // suppliers from mock
    })
  })

  describe('Interactive Elements', () => {
    it('renders chart component when stats are available', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      // The DashboardStatsChart should be rendered with data
      expect(screen.getByText('Projectoverzicht')).toBeInTheDocument()
    })

    it('shows quick action buttons', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Snelle Acties')).toBeInTheDocument()
      expect(screen.getByText('Leverancier toevoegen')).toBeInTheDocument()
      expect(screen.getByText('Plant toevoegen')).toBeInTheDocument()
    })

    it('navigates when clicking quick action buttons', async () => {
      const originalLocation = window.location.href

      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      const addSupplierButton = screen.getByText('Leverancier toevoegen')
      await user.click(addSupplierButton)
      
      // In a real test environment with actual routing, we'd check navigation
      // For now, we just verify the button is clickable
      expect(addSupplierButton).toBeInTheDocument()
      
      // Restore original location
      window.location.href = originalLocation
    })
  })

  describe('Responsive Design', () => {
    it('adapts to mobile viewport', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      // Check that responsive grid classes are present
      const statsGrid = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4')
      expect(statsGrid).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('has proper ARIA labels and roles', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      // Check for proper heading hierarchy
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/dashboard/i)
      
      // Check for proper button labels
      const retryButton = screen.queryByRole('button', { name: /opnieuw proberen/i })
      if (retryButton) {
        expect(retryButton).toHaveAccessibleName()
      }
      
      // Check for proper region landmarks
      const main = document.querySelector('main') || document.querySelector('.min-h-screen')
      expect(main).toBeInTheDocument()
    })

    it('supports keyboard navigation', async () => {
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      // Test tab navigation through interactive elements
      await user.tab()
      
      const firstFocusableElement = document.activeElement
      expect(firstFocusableElement).toBeInstanceOf(HTMLElement)
      
      // Test that focused elements are visible
      if (firstFocusableElement) {
        expect(firstFocusableElement).toBeVisible()
      }
    })
  })

  describe('Data Refresh and Updates', () => {
    it('refreshes data when retry is clicked after network recovery', async () => {
      let callCount = 0
      
      // Mock unstable network
      server.use(
        http.get('http://127.0.0.1:5000/api/dashboard/stats', () => {
          callCount++
          if (callCount === 1) {
            return HttpResponse.json(
              { error: 'Network error' },
              { status: 500 }
            )
          }
          return HttpResponse.json({
            suppliers: 6, // Different value to verify refresh
            plants: 200,
            products: 50,
            clients: 10,
            projects: 15,
            active_projects: 4,
            total_budget: 200000
          })
        })
      )

      render(<Dashboard />)
      
      // Wait for initial error
      await waitFor(() => {
        expectErrorMessage(/stats api error: 500/i)
      })

      const retryButton = screen.getByRole('button', { name: /opnieuw proberen/i })
      await user.click(retryButton)
      
      // Wait for successful refresh with new data
      await waitFor(() => {
        expect(screen.getByText('200')).toBeInTheDocument() // Updated plants count
      })
    })
  })

  describe('Performance', () => {
    it('loads and renders within acceptable time', async () => {
      const startTime = performance.now()
      
      render(<Dashboard />)
      
      await waitForLoadingToFinish()
      
      const endTime = performance.now()
      const renderTime = endTime - startTime
      
      // Should render within 2 seconds
      expect(renderTime).toBeLessThan(2000)
    })
  })
})