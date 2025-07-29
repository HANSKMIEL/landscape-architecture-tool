import { describe, it, expect, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { render } from '../../test/utils/render.jsx'
import Plants from '../Plants'

expect.extend(toHaveNoViolations)

describe('Plants Component', () => {
  beforeEach(() => {
    // Setup for each test
  })

  describe('Basic Rendering', () => {
    it('renders plants page', async () => {
      render(<Plants />)
      
      // Check for loading state first
      expect(screen.getByRole('progressbar')).toBeInTheDocument()
      
      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('Planten')).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('displays plants data after loading', async () => {
      render(<Plants />)
      
      await waitFor(() => {
        // Look for plant names from mock data
        expect(screen.getByText(/Plant 1/i)).toBeInTheDocument()
      }, { timeout: 5000 })
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
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
      }, { timeout: 5000 })
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})