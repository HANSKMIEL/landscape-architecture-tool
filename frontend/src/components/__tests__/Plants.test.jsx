// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { render } from '../../test/utils/render.jsx'
import { setupUser, waitForLoadingToFinish } from '../../test/utils/testHelpers'
import Plants from '../Plants'

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
      expect(screen.getByText('Plant toevoegen')).toBeInTheDocument()
    })

    it('displays plants list with data', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      // Should display plants from mock data
      expect(screen.getByText('Rose')).toBeInTheDocument()
      expect(screen.getByText('Garden Rose')).toBeInTheDocument()
      expect(screen.getByText('Tulip')).toBeInTheDocument()
      expect(screen.getByText('Spring Tulip')).toBeInTheDocument()
    })

    it('shows search input for filtering plants', async () => {
      render(<Plants />)
      
      await waitForLoadingToFinish()
      
      const searchInput = screen.getByPlaceholderText(/zoek planten/i)
      expect(searchInput).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('displays error message when plants fetch fails', async () => {
      // Override global fetch for this test
      const originalFetch = global.fetch
      global.fetch = jest.fn(() => 
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Server Error'
        })
      )

      render(<Plants />)
      
      await waitFor(() => {
        expect(screen.getByText(/fout bij laden van planten/i)).toBeInTheDocument()
      })

      // Restore original fetch
      global.fetch = originalFetch
    })
  })
})