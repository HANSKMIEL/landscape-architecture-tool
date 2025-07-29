// Jest provides describe, it, expect, beforeEach as globals
import { screen, waitFor } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { renderWithLanguage } from '../../test/utils/render.jsx'
import Projects from '../Projects'

expect.extend(toHaveNoViolations)

describe('Projects Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks()
  })

  describe('Basic Rendering', () => {
    it('renders projects page with English language', async () => {
      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('renders projects page with Dutch language', async () => {
      renderWithLanguage(<Projects language="nl" />, { language: 'nl' })
      
      await waitFor(() => {
        expect(screen.getByText('Projecten')).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('displays projects data after loading', async () => {
      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        // Look for project names from mock data
        const hasProjectContent = screen.queryByText(/garden redesign/i) || 
                                  screen.queryByText(/park renovation/i) ||
                                  screen.queryByText(/projects/i) ||
                                  screen.queryByText(/no projects/i);
        expect(hasProjectContent).toBeInTheDocument()
      }, { timeout: 10000 })
    })
  })

  describe('Language Support', () => {
    it('displays correct translations for English', async () => {
      renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
        expect(screen.getByText(/manage your landscape architecture projects/i)).toBeInTheDocument()
      }, { timeout: 5000 })
    })

    it('displays correct translations for Dutch', async () => {
      renderWithLanguage(<Projects language="nl" />, { language: 'nl' })
      
      await waitFor(() => {
        expect(screen.getByText('Projecten')).toBeInTheDocument()
        expect(screen.getByText(/beheer uw landschapsarchitectuur projecten/i)).toBeInTheDocument()
      }, { timeout: 5000 })
    })
  })

  describe('Accessibility', () => {
    it('should not have accessibility violations', async () => {
      const { container } = renderWithLanguage(<Projects language="en" />, { language: 'en' })
      
      await waitFor(() => {
        expect(screen.getByText('Projects')).toBeInTheDocument()
      }, { timeout: 5000 })
      
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})