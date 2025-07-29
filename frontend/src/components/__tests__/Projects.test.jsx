// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish, fillInput, expectErrorMessage } from '../../test/utils/testHelpers'
import Projects from '../Projects'

expect.extend(toHaveNoViolations)

describe('Projects Component', () => {
  let user

  beforeEach(() => {
    user = setupUser()
  })

  describe('Rendering and Loading States', () => {
    it('renders projects page with title and navigation', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Projecten')).toBeInTheDocument()
      expect(screen.getByText('Project Toevoegen')).toBeInTheDocument()
    })

    it('supports both English and Dutch rendering', async () => {
      // Test English
      render(<Projects />, { language: 'en' })
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText('Projects')).toBeInTheDocument()
      expect(screen.getByText('Add Project')).toBeInTheDocument()
    })

    it('displays empty state when no projects', async () => {
      global.fetch.mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve([])
        })
      )

      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      expect(screen.getByText(/geen projecten gevonden/i)).toBeInTheDocument()
    })

    it('displays projects list with data', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Should display projects from mock data
      expect(screen.getByText('Garden Redesign')).toBeInTheDocument()
      expect(screen.getByText('Park Landscaping')).toBeInTheDocument()
      expect(screen.getByText('Rooftop Garden')).toBeInTheDocument()
    })
  })

  describe('Project Status and Management', () => {
    it('displays project status badges correctly', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Check for status badges
      expect(screen.getByText('Actief')).toBeInTheDocument()
      expect(screen.getByText('Planning')).toBeInTheDocument()
      expect(screen.getByText('Voltooid')).toBeInTheDocument()
    })

    it('shows client information for projects', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Look for client names from mock data
      expect(screen.getByText('Doe Corporation')).toBeInTheDocument()
      expect(screen.getByText('Green Spaces Inc')).toBeInTheDocument()
      expect(screen.getByText('Urban Development Co')).toBeInTheDocument()
    })

    it('handles different project statuses', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Test filtering by status
      const statusFilter = screen.getByLabelText(/filter op status/i)
      await user.click(statusFilter)
      
      const activeOption = screen.getByText('Actief')
      await user.click(activeOption)
      
      await waitFor(() => {
        expect(screen.getByText('Garden Redesign')).toBeInTheDocument()
        expect(screen.queryByText('Rooftop Garden')).not.toBeInTheDocument()
      })
    })
  })

  describe('User Interactions', () => {
    it('enables navigation between project list and detail views', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Click on a project to view details
      const projectLink = screen.getByText('Garden Redesign')
      await user.click(projectLink)
      
      await waitFor(() => {
        expect(window.location.pathname).toContain('/projects/')
      })
    })

    it('opens add project modal when button clicked', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      const addButton = screen.getByText('Project Toevoegen')
      await user.click(addButton)
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
        expect(screen.getByText('Project Toevoegen')).toBeInTheDocument()
      })
    })

    it('allows searching through projects', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      const searchInput = screen.getByPlaceholderText(/zoek projecten/i)
      await fillInput(user, searchInput, 'Garden')
      
      await waitFor(() => {
        expect(screen.getByText('Garden Redesign')).toBeInTheDocument()
        expect(screen.getByText('Rooftop Garden')).toBeInTheDocument()
        expect(screen.queryByText('Park Landscaping')).not.toBeInTheDocument()
      })
    })

    it('handles project form submission', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Open modal
      const addButton = screen.getByText('Project Toevoegen')
      await user.click(addButton)
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
      
      // Fill form
      const nameInput = screen.getByLabelText(/project naam/i)
      await fillInput(user, nameInput, 'Test Project')
      
      const descriptionInput = screen.getByLabelText(/beschrijving/i)
      await fillInput(user, descriptionInput, 'Test project description')
      
      // Submit form
      const submitButton = screen.getByText('Project Opslaan')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message when projects fetch fails', async () => {
      global.fetch.mockImplementation(() => 
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Server Error'
        })
      )

      render(<Projects />)
      
      await waitFor(() => {
        expectErrorMessage('Fout bij laden van projecten')
      })
    })

    it('handles form validation errors', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Open modal
      const addButton = screen.getByText('Project Toevoegen')
      await user.click(addButton)
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
      
      // Try to submit without required fields
      const submitButton = screen.getByText('Project Opslaan')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/project naam is verplicht/i)).toBeInTheDocument()
      })
    })
  })

  describe('Project Workflows', () => {
    it('supports project status updates', async () => {
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      // Find a project with status dropdown
      const statusDropdown = screen.getAllByLabelText(/wijzig status/i)[0]
      await user.click(statusDropdown)
      
      const completedOption = screen.getByText('Voltooid')
      await user.click(completedOption)
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/projects/'),
          expect.objectContaining({
            method: 'PATCH',
            body: expect.stringContaining('status')
          })
        )
      })
    })

    it('allows project deletion with confirmation', async () => {
      // Mock window.confirm
      window.confirm = jest.fn(() => true)
      
      render(<Projects />)
      
      await waitForLoadingToFinish()
      
      const deleteButton = screen.getAllByLabelText(/verwijder project/i)[0]
      await user.click(deleteButton)
      
      expect(window.confirm).toHaveBeenCalledWith(
        expect.stringContaining('Weet je zeker dat je dit project wilt verwijderen')
      )
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/projects/'),
          expect.objectContaining({
            method: 'DELETE'
          })
        )
      })
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = render(<Projects />)
      
      await waitForLoadingToFinish()
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})