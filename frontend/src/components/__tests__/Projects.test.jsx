// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish } from '../../test/utils/testHelpers'
import Projects from '../Projects'

describe('Projects Component', () => {
  let user

  beforeEach(() => {
    user = setupUser()
  })

  describe('Rendering and Loading States', () => {
    it('renders projects page with title and navigation', async () => {
      render(<Projects language="nl" />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Projecten')).toBeInTheDocument()
      expect(screen.getByText('Nieuw Project')).toBeInTheDocument()
    })

    it('supports both English and Dutch rendering', async () => {
      // Test English
      render(<Projects language="en" />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Projects')).toBeInTheDocument()
      expect(screen.getByText('New Project')).toBeInTheDocument()
    })

    it('displays projects list with data', async () => {
      render(<Projects language="en" />)
      
      await waitForLoadingToFinish()
      
      // Should display projects from mock data
      expect(screen.getByText('Garden Redesign Project')).toBeInTheDocument()
      expect(screen.getByText('Park Renovation')).toBeInTheDocument()
    })

    it('displays project status information', async () => {
      render(<Projects language="en" />)
      
      await waitForLoadingToFinish()
      
      // Check for status indicators
      expect(screen.getByText('active')).toBeInTheDocument()
      expect(screen.getByText('planning')).toBeInTheDocument()
    })

    it('shows project locations and budgets', async () => {
      render(<Projects language="en" />)
      
      await waitForLoadingToFinish()
      
      // Look for project details from mock data
      expect(screen.getByText('Amsterdam')).toBeInTheDocument()
      expect(screen.getByText('Utrecht')).toBeInTheDocument()
    })
  })

  describe('User Interactions', () => {
    it('allows clicking on new project button', async () => {
      render(<Projects language="nl" />)
      
      await waitForLoadingToFinish()
      
      const newProjectButton = screen.getByText('Nieuw Project')
      expect(newProjectButton).toBeInTheDocument()
      await user.click(newProjectButton)
      
      // Button should be clickable (no error thrown)
    })
  })

  describe('Error Handling', () => {
    it('displays error message when projects fetch fails', async () => {
      // Override global fetch for this test
      const originalFetch = global.fetch
      global.fetch = jest.fn(() => 
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Server Error'
        })
      )

      render(<Projects language="en" />)
      
      await waitFor(() => {
        expect(screen.getByText(/error loading projects/i)).toBeInTheDocument()
      })

      // Restore original fetch
      global.fetch = originalFetch
    })
  })
})