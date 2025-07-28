import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Custom render function that wraps components with necessary providers
const customRender = (ui, options = {}) => {
  const Wrapper = ({ children }) => {
    return <BrowserRouter>{children}</BrowserRouter>
  }

  return render(ui, { wrapper: Wrapper, ...options })
}

// Re-export everything from @testing-library/react
export * from '@testing-library/react'

// Override render method
export { customRender as render }