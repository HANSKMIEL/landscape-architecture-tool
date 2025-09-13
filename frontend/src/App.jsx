import { useState, useEffect, Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import ResponsiveSidebar from './components/ResponsiveSidebar'
import Header from './components/Header'
import Login from './components/Login'
import ErrorBoundary from './components/ErrorBoundary'
import authService from './services/authService'
import toast from 'react-hot-toast'
import { LanguageProvider, useLanguage } from './i18n/LanguageProvider'

// Dynamic imports for route components
const Dashboard = lazy(() => import('./components/Dashboard'))
const Suppliers = lazy(() => import('./components/Suppliers'))
const Plants = lazy(() => import('./components/Plants'))
const Products = lazy(() => import('./components/Products'))
const Clients = lazy(() => import('./components/Clients'))
const Projects = lazy(() => import('./components/Projects'))
const PlantRecommendations = lazy(() => import('./components/PlantRecommendations'))
const Reports = lazy(() => import('./components/Reports'))
const AIAssistant = lazy(() => import('./components/AIAssistant'))
const InvoiceQuoteManager = lazy(() => import('./components/InvoiceQuoteManager'))
const Photos = lazy(() => import('./components/Photos'))
const ProjectTimeline = lazy(() => import('./components/ProjectTimeline'))
const Settings = lazy(() => import('./components/Settings'))
const UserManagement = lazy(() => import('./components/UserManagement'))
const PasswordReset = lazy(() => import('./components/PasswordReset'))
import './unified-professional-styles.css'
import './enhanced_sidebar_styles.css'

// Main App component with authentication and routing
function AppContent() {
  const { t } = useLanguage()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [loginError, setLoginError] = useState('')

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const closeSidebar = () => setSidebarOpen(false)

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
      
      const welcomeMessage = t('auth.welcome', `Welcome back, ${response.user.username}!`)
        .replace('{username}', response.user.username)
      
      toast.success(welcomeMessage)
    } catch (_error) {
      const errorMessage = t('auth.loginFailed', 'Login failed. Please check your credentials.')
      
      setLoginError(errorMessage)
      toast.error(errorMessage)
    }
  }

  const handleLogout = async () => {
    try {
      await authService.logout()
      setUser(null)
      
      const logoutMessage = t('auth.logoutSuccess', 'Successfully logged out')
      
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

  return (
    <ErrorBoundary>
      <Router>
        <AuthenticatedApp 
          user={user}
          authLoading={authLoading}
          loginError={loginError}
          handleLogin={handleLogin}
          handleLogout={handleLogout}
          sidebarOpen={sidebarOpen}
          toggleSidebar={toggleSidebar}
          closeSidebar={closeSidebar}
        />
      </Router>
    </ErrorBoundary>
  )
}

// Component that handles authentication inside Router context
function AuthenticatedApp({ 
  user, 
  authLoading, 
  loginError, 
  handleLogin, 
  handleLogout, 
  sidebarOpen, 
  toggleSidebar, 
  closeSidebar 
}) {
  const { t } = useLanguage()

  // Show loading spinner while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {t('common.loading', 'Loading...')}
          </p>
        </div>
      </div>
    )
  }

  // Show login screen if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} error={loginError} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    )
  }

  return (
        <div className="min-h-screen bg-gray-50">
        {/* Responsive Sidebar */}
        <ResponsiveSidebar 
          isOpen={sidebarOpen} 
          onClose={closeSidebar}
          user={user}
        />
        
        {/* Main content area */}
        <div className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
          {/* Header */}
          <div className="header-container">
            <Header 
              onMenuClick={toggleSidebar}
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
                  {t('common.loading', 'Loading...')}
                </span>
              </div>
            }>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/login" element={<Login onLogin={handleLogin} error={loginError} />} />
                <Route path="/dashboard" element={<Dashboard user={user} />} />
                <Route path="/suppliers" element={<Suppliers user={user} />} />
                <Route path="/plants" element={<Plants user={user} />} />
                <Route path="/products" element={<Products user={user} />} />
                <Route path="/clients" element={<Clients user={user} />} />
                <Route path="/projects" element={<Projects user={user} />} />
                <Route path="/plant-recommendations" element={<PlantRecommendations user={user} />} />
                <Route path="/reports" element={<Reports user={user} />} />
                <Route path="/ai-assistant" element={<AIAssistant user={user} />} />
                <Route path="/invoices" element={<InvoiceQuoteManager user={user} />} />
                <Route path="/photos" element={<Photos user={user} />} />
                <Route path="/timeline" element={<ProjectTimeline user={user} />} />
                <Route path="/settings" element={<Settings user={user} />} />
                <Route path="/users" element={<UserManagement user={user} />} />
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
  )
}

// Main App wrapper with Language Provider
function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  )
}

export default App

