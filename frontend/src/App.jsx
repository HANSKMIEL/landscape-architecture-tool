import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import ResponsiveSidebar from './components/ResponsiveSidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import Suppliers from './components/Suppliers'
import Plants from './components/Plants'
import Products from './components/Products'
import Clients from './components/Clients'
import Projects from './components/Projects'
import PlantRecommendations from './components/PlantRecommendations'
import Reports from './components/Reports'
import Settings from './components/Settings'
import './unified-professional-styles.css'
import './enhanced_sidebar_styles.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [language, setLanguage] = useState('en')

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const closeSidebar = () => setSidebarOpen(false)
  const toggleLanguage = () => setLanguage(language === 'en' ? 'nl' : 'en')

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      // Close sidebar on mobile when resizing to desktop
      if (window.innerWidth >= 1024 && sidebarOpen) {
        // On desktop, we can keep it open or closed based on user preference
        // For now, let's keep the current state
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [sidebarOpen])

  // Close sidebar when route changes on mobile
  useEffect(() => {
    const handleRouteChange = () => {
      if (window.innerWidth < 1024) {
        closeSidebar()
      }
    }

    // Listen for route changes
    window.addEventListener('popstate', handleRouteChange)
    return () => window.removeEventListener('popstate', handleRouteChange)
  }, [])

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Responsive Sidebar */}
        <ResponsiveSidebar 
          isOpen={sidebarOpen} 
          onClose={closeSidebar} 
        />
        
        {/* Main content area */}
        <div className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
          {/* Header */}
          <div className="header-container">
            <Header 
              onMenuClick={toggleSidebar}
              language={language}
              onLanguageToggle={toggleLanguage}
              sidebarOpen={sidebarOpen}
            />
          </div>
          
          {/* Main content */}
          <main className="p-4 sm:p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard language={language} />} />
              <Route path="/suppliers" element={<Suppliers language={language} />} />
              <Route path="/plants" element={<Plants language={language} />} />
              <Route path="/products" element={<Products language={language} />} />
              <Route path="/clients" element={<Clients language={language} />} />
              <Route path="/projects" element={<Projects language={language} />} />
              <Route path="/plant-recommendations" element={<PlantRecommendations language={language} />} />
              <Route path="/reports" element={<Reports language={language} />} />
              <Route path="/settings" element={<Settings language={language} />} />
            </Routes>
          </main>
        </div>
        
        {/* Toast notifications */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              theme: {
                primary: '#059669',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              theme: {
                primary: '#dc2626',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App

