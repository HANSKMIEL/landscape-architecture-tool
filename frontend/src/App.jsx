import { useState, useEffect, Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import ResponsiveSidebar from './components/ResponsiveSidebar'
import Header from './components/Header'
import Login from './components/Login'
import authService from './services/authService'
import toast from 'react-hot-toast'

// Dynamic imports for route components
const Dashboard = lazy(() => import('./components/Dashboard'))
const Suppliers = lazy(() => import('./components/Suppliers'))
const Plants = lazy(() => import('./components/Plants'))
const Products = lazy(() => import('./components/Products'))
const Clients = lazy(() => import('./components/Clients'))
const Projects = lazy(() => import('./components/Projects'))
const PlantRecommendations = lazy(() => import('./components/PlantRecommendations'))
const Reports = lazy(() => import('./components/Reports'))
const InvoiceQuoteManager = lazy(() => import('./components/InvoiceQuoteManager'))
const Settings = lazy(() => import('./components/Settings'))
import './unified-professional-styles.css'
import './enhanced_sidebar_styles.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [language, setLanguage] = useState('nl') // Default to Dutch
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [loginError, setLoginError] = useState('')

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const closeSidebar = () => setSidebarOpen(false)
  const toggleLanguage = () => setLanguage(language === 'en' ? 'nl' : 'en')

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const authStatus = await authService.checkAuthStatus()
      if (authStatus.authenticated) {
        setUser(authStatus.user)
      }
    } catch (error) {
      console.error('Auth status check failed:', error)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogin = async (credentials) => {
    try {
      setLoginError('')
      const response = await authService.login(credentials)
      setUser(response.user)
      
      const welcomeMessage = language === 'nl' 
        ? `Welkom terug, ${response.user.username}!`
        : `Welcome back, ${response.user.username}!`
      
      toast.success(welcomeMessage)
    } catch (error) {
      const errorMessage = language === 'nl'
        ? 'Inloggen mislukt. Controleer uw gegevens.'
        : 'Login failed. Please check your credentials.'
      
      setLoginError(errorMessage)
      toast.error(errorMessage)
    }
  }

  const handleLogout = async () => {
    try {
      await authService.logout()
      setUser(null)
      
      const logoutMessage = language === 'nl'
        ? 'U bent succesvol uitgelogd'
        : 'Successfully logged out'
      
      toast.success(logoutMessage)
    } catch (error) {
      console.error('Logout error:', error)
      // Force logout on client side even if server request fails
      setUser(null)
    }
  }

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

  // Show loading spinner while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {language === 'nl' ? 'Laden...' : 'Loading...'}
          </p>
        </div>
      </div>
    )
  }

  // Show login screen if not authenticated
  if (!user) {
    return <Login onLogin={handleLogin} error={loginError} />
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Responsive Sidebar */}
        <ResponsiveSidebar 
          isOpen={sidebarOpen} 
          onClose={closeSidebar}
          language={language}
          user={user}
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
              user={user}
              onLogout={handleLogout}
            />
          </div>
          
          {/* Main content */}
          <main className="p-4 sm:p-6">
            <Suspense fallback={
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
                <span className="ml-3 text-gray-600">
                  {language === 'nl' ? 'Laden...' : 'Loading...'}
                </span>
              </div>
            }>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard language={language} user={user} />} />
                <Route path="/suppliers" element={<Suppliers language={language} user={user} />} />
                <Route path="/plants" element={<Plants language={language} user={user} />} />
                <Route path="/products" element={<Products language={language} user={user} />} />
                <Route path="/clients" element={<Clients language={language} user={user} />} />
                <Route path="/projects" element={<Projects language={language} user={user} />} />
                <Route path="/plant-recommendations" element={<PlantRecommendations language={language} user={user} />} />
                <Route path="/reports" element={<Reports language={language} user={user} />} />
                <Route path="/invoices" element={<InvoiceQuoteManager language={language} user={user} />} />
                <Route path="/settings" element={<Settings language={language} user={user} />} />
              </Routes>
            </Suspense>
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

