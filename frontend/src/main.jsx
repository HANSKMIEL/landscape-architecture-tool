import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'  // Tailwind CSS with landscape design system
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

