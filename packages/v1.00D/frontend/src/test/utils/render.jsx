import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Mock providers for testing
const MockProviders = ({ children }) => {
  return (
    <BrowserRouter>
      {children}
      <Toaster />
    </BrowserRouter>
  )
}

// Custom render function with providers
const customRender = (ui, options = {}) => {
  const {
    initialEntries = ['/'],
    ...renderOptions
  } = options

  const Wrapper = ({ children }) => (
    <MockProviders initialEntries={initialEntries}>
      {children}
    </MockProviders>
  )

  return render(ui, {
    wrapper: Wrapper,
    ...renderOptions
  })
}

// Enhanced render with specific route
export const renderWithRouter = (ui, { route = '/', ...options } = {}) => {
  window.history.pushState({}, 'Test page', route)
  return customRender(ui, options)
}

// Render with language context
export const renderWithLanguage = (ui, { language = 'en', ...options } = {}) => {
  const LanguageWrapper = ({ children }) => (
    <MockProviders>
      <div data-testid="language-context" data->
        {React.cloneElement(children, { language })}
      </div>
    </MockProviders>
  )

  return render(ui, {
    wrapper: LanguageWrapper,
    ...options
  })
}

// Re-export everything from RTL
export * from '@testing-library/react'

// Override render method
export { customRender as render }