import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// User event setup for each test
export const setupUser = () => userEvent.setup()

// Common test utilities
export const getByTestId = (testId) => screen.getByTestId(testId)
export const queryByTestId = (testId) => screen.queryByTestId(testId)
export const findByTestId = (testId) => screen.findByTestId(testId)

// Form interaction helpers
export const fillInput = async (user, input, value) => {
  await user.clear(input)
  await user.type(input, value)
}

export const selectOption = async (user, select, option) => {
  await user.click(select)
  await user.click(screen.getByRole('option', { name: option }))
}

export const submitForm = async (user, form) => {
  const submitButton = form.querySelector('button[type="submit"]') || 
                      form.querySelector('input[type="submit"]')
  if (submitButton) {
    await user.click(submitButton)
  }
}

// Loading state helpers
export const waitForLoadingToFinish = async () => {
  await waitFor(() => {
    // Check for various loading indicators
    const loadingSpinner = document.querySelector('.animate-pulse')
    const loadingText = document.querySelector('[data-testid="loading"]')
    expect(loadingSpinner).not.toBeInTheDocument()
    if (loadingText) {
      expect(loadingText).not.toBeInTheDocument()
    }
  }, { timeout: 5000 })
}

export const expectLoadingState = () => {
  expect(screen.getByText(/loading/i)).toBeInTheDocument()
}

// Error state helpers
export const expectErrorMessage = (message) => {
  expect(screen.getByText(message)).toBeInTheDocument()
}

export const expectNoErrorMessage = (message) => {
  expect(screen.queryByText(message)).not.toBeInTheDocument()
}

// Modal/Dialog helpers
export const openModal = async (user, triggerButton) => {
  await user.click(triggerButton)
  await waitFor(() => {
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })
}

export const closeModal = async (user) => {
  const closeButton = screen.getByRole('button', { name: /close/i }) ||
                     screen.getByLabelText(/close/i)
  await user.click(closeButton)
  await waitFor(() => {
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
}

// Table helpers
export const getTableRows = () => screen.getAllByRole('row')
export const getTableCells = (row) => row.querySelectorAll('td')
export const findTableCell = (rowIndex, cellIndex) => {
  const rows = getTableRows()
  const cells = getTableCells(rows[rowIndex])
  return cells[cellIndex]
}

// Search helpers
export const performSearch = async (user, searchInput, searchTerm) => {
  await fillInput(user, searchInput, searchTerm)
  // Usually search happens on input change or Enter
  await user.keyboard('{Enter}')
}

// Navigation helpers
export const expectCurrentPath = (path) => {
  expect(window.location.pathname).toBe(path)
}

export const navigateToPath = (path) => {
  window.history.pushState({}, '', path)
}

// Accessibility helpers
export const expectFocusedElement = (element) => {
  expect(element).toHaveFocus()
}

export const expectAriaLabel = (element, label) => {
  expect(element).toHaveAttribute('aria-label', label)
}

export const expectAriaExpanded = (element, expanded) => {
  expect(element).toHaveAttribute('aria-expanded', expanded.toString())
}

// Data attribute helpers
export const expectDataAttribute = (element, attribute, value) => {
  expect(element).toHaveAttribute(`data-${attribute}`, value)
}

// Async operation helpers
export const waitForApiCall = async (mockFn) => {
  await waitFor(() => {
    expect(mockFn).toHaveBeenCalled()
  })
}

export const waitForApiCallWith = async (mockFn, expectedArgs) => {
  await waitFor(() => {
    expect(mockFn).toHaveBeenCalledWith(...expectedArgs)
  })
}

// Component state helpers
export const expectComponentToRender = async (getComponent) => {
  await waitFor(() => {
    expect(getComponent()).toBeInTheDocument()
  })
}

export const expectComponentNotToRender = async (getComponent) => {
  await waitFor(() => {
    expect(getComponent()).not.toBeInTheDocument()
  })
}

// Language/i18n helpers
export const expectTranslatedText = (key, language = 'en') => {
  const element = screen.getByTestId('language-context')
  expect(element).toHaveAttribute('data-language', language)
}

// Debugging helpers for development
export const debugElement = (element) => {
  console.log('Element HTML:', element.outerHTML)
  console.log('Element attributes:', [...element.attributes].map(attr => `${attr.name}="${attr.value}"`))
}

export const debugScreen = () => {
  screen.debug()
}

// Performance helpers
export const measureRenderTime = (renderFn) => {
  const start = performance.now()
  const result = renderFn()
  const end = performance.now()
  console.log(`Render time: ${end - start}ms`)
  return result
}