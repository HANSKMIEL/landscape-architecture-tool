// Simple component test to validate testing infrastructure without complex API calls
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Simple test component without complex dependencies
const SimpleTestComponent = ({ title = "Simple Test", message = "Testing infrastructure works!" }) => (
  <div>
    <h1>{title}</h1>
    <p>{message}</p>
    <button onClick={() => console.log('Button clicked')}>
      Test Button
    </button>
  </div>
)

describe('Simple Component Test', () => {
  describe('Basic Rendering', () => {
    it('renders simple component correctly', () => {
      render(<SimpleTestComponent />)
      
      expect(screen.getByText('Simple Test')).toBeInTheDocument()
      expect(screen.getByText('Testing infrastructure works!')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Test Button' })).toBeInTheDocument()
    })

    it('handles props correctly', () => {
      render(
        <SimpleTestComponent 
          title="Custom Title" 
          message="Custom message" 
        />
      )
      
      expect(screen.getByText('Custom Title')).toBeInTheDocument()
      expect(screen.getByText('Custom message')).toBeInTheDocument()
    })
  })

  describe('Router Integration', () => {
    it('works with React Router wrapper', () => {
      render(
        <BrowserRouter>
          <SimpleTestComponent title="Router Test" />
        </BrowserRouter>
      )
      
      expect(screen.getByText('Router Test')).toBeInTheDocument()
      expect(screen.getByText('Testing infrastructure works!')).toBeInTheDocument()
    })
  })

  describe('Event Handling', () => {
    it('button is clickable', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      
      render(<SimpleTestComponent />)
      
      const button = screen.getByRole('button', { name: 'Test Button' })
      button.click()
      
      // The component logs to console, so we can verify it was called
      expect(consoleSpy).toHaveBeenCalledWith('Button clicked')
      
      consoleSpy.mockRestore()
    })
  })
})