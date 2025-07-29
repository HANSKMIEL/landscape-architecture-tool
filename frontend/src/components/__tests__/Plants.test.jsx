// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish, fillInput, expectErrorMessage, openModal } from '../../test/utils/testHelpers'
import Plants from '../Plants'

expect.extend(toHaveNoViolations)

describe('Plants Component', () => {
  let user

  beforeEach(() => {
    user = setupUser()
  })

  describe('Rendering and Loading States', () => {
    it('renders plants page with title and navigation', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Planten')).toBeInTheDocument()
      expect(screen.getByText('Plant Toevoegen')).toBeInTheDocument()
    })

    it('displays empty state when no plants', async () => {
      // Mock empty response
      global.fetch.mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        })
      )

      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText(/geen planten gevonden/i)).toBeInTheDocument()
    })

    it('displays plants list with data', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      // Should display plants from mock data
      expect(screen.getByText('Lavandula angustifolia')).toBeInTheDocument()
      expect(screen.getByText('Common Lavender')).toBeInTheDocument()
      expect(screen.getByText('Echinacea purpurea')).toBeInTheDocument()
      expect(screen.getByText('Purple Coneflower')).toBeInTheDocument()
    })
  })

  describe('User Interactions', () => {
    it('opens add plant modal when button clicked', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      const addButton = screen.getByText('Plant Toevoegen')
      await user.click(addButton)
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
        expect(screen.getByText('Plant Toevoegen')).toBeInTheDocument()
      })
    })

    it('allows searching through plants', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      const searchInput = screen.getByPlaceholderText(/zoek planten/i)
      await fillInput(user, searchInput, 'Lavender')
      
      // Should filter results
      await waitFor(() => {
        expect(screen.getByText('Lavandula angustifolia')).toBeInTheDocument()
        expect(screen.queryByText('Echinacea purpurea')).not.toBeInTheDocument()
      })
    })

    it('handles plant form submission', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      // Open modal
      const addButton = screen.getByText('Plant Toevoegen')
      await user.click(addButton)
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
      
      // Fill form
      const nameInput = screen.getByLabelText(/wetenschappelijke naam/i)
      await fillInput(user, nameInput, 'Test Plant')
      
      const commonNameInput = screen.getByLabelText(/gewone naam/i)
      await fillInput(user, commonNameInput, 'Common Test Plant')
      
      // Submit form
      const submitButton = screen.getByText('Plant Opslaan')
      await user.click(submitButton)
      
      // Check for success message or modal close
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message when plants fetch fails', async () => {
      global.fetch.mockImplementation(() => 
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Server Error'
        })
      )

      render(<Plants />)
      
      await waitFor(() => {
        expectErrorMessage('Fout bij laden van planten')
      })
    })

    it('handles form validation errors', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      // Open modal
      const addButton = screen.getByText('Plant Toevoegen')
      await user.click(addButton)
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
      
      // Try to submit without required fields
      const submitButton = screen.getByText('Plant Opslaan')
      await user.click(submitButton)
      
      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/wetenschappelijke naam is verplicht/i)).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<Plants />)
      
      await waitForLoadingToFinish()
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})