import { Link, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import {
  LayoutDashboard,
  Building2,
  Package,
  Leaf,
  Users,
  FolderOpen,
  Lightbulb,
  FileText,
  Receipt,
  Upload,
  Settings,
  X,
  Shield,
  Eye
} from 'lucide-react'

const ResponsiveSidebar = ({ isOpen, onClose, language = 'nl', user }) => {
  const location = useLocation()

  const translations = {
    en: {
      dashboard: 'Dashboard',
      suppliers: 'Suppliers',
      products: 'Products',
      plants: 'Plants',
      clients: 'Clients',
      projects: 'Projects',
      recommendations: 'Plant Recommendations',
      reports: 'Reports',
      invoices: 'Invoices & Quotes',
      import: 'Excel Import',
      settings: 'Settings',
      closeSidebar: 'Close sidebar'
    },
    nl: {
      dashboard: 'Dashboard',
      suppliers: 'Leveranciers',
      products: 'Producten',
      plants: 'Planten',
      clients: 'Klanten',
      projects: 'Projecten',
      recommendations: 'Plant Aanbevelingen',
      reports: 'Rapporten',
      invoices: 'Offertes & Facturen',
      import: 'Excel Import',
      settings: 'Instellingen',
      closeSidebar: 'Sluit zijbalk'
    }
  }

  const t = translations[language]

  const navigation = [
    { 
      name: t.dashboard, 
      href: '/dashboard', 
      icon: LayoutDashboard,
      roles: ['admin', 'employee', 'client']
    },
    { 
      name: t.suppliers, 
      href: '/suppliers', 
      icon: Building2,
      roles: ['admin', 'employee']
    },
    { 
      name: t.products, 
      href: '/products', 
      icon: Package,
      roles: ['admin', 'employee']
    },
    { 
      name: t.plants, 
      href: '/plants', 
      icon: Leaf,
      roles: ['admin', 'employee']
    },
    { 
      name: t.clients, 
      href: '/clients', 
      icon: Users,
      roles: ['admin', 'employee']
    },
    { 
      name: t.projects, 
      href: '/projects', 
      icon: FolderOpen,
      roles: ['admin', 'employee', 'client']
    },
    { 
      name: t.recommendations, 
      href: '/plant-recommendations', 
      icon: Lightbulb,
      roles: ['admin', 'employee', 'client']
    },
    { 
      name: t.reports, 
      href: '/reports', 
      icon: FileText,
      roles: ['admin', 'employee']
    },
    { 
      name: t.invoices, 
      href: '/invoices', 
      icon: Receipt,
      roles: ['admin', 'employee']
    },
    { 
      name: t.import, 
      href: '/import', 
      icon: Upload,
      roles: ['admin', 'employee']
    },
    { 
      name: t.settings, 
      href: '/settings', 
      icon: Settings,
      roles: ['admin', 'employee', 'client']
    },
  ]

  // Filter navigation based on user role
  const getFilteredNavigation = () => {
    if (!user) return navigation
    
    return navigation.filter(item => {
      if (!item.roles) return true
      return item.roles.includes(user.role)
    })
  }

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return Shield
      case 'employee':
        return Users
      case 'client':
        return Eye
      default:
        return Users
    }
  }

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'text-red-600 bg-red-100'
      case 'employee':
        return 'text-blue-600 bg-blue-100'
      case 'client':
        return 'text-green-600 bg-green-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getRoleDisplay = (role) => {
    const roleNames = {
      en: { admin: 'Administrator', employee: 'Employee', client: 'Client' },
      nl: { admin: 'Beheerder', employee: 'Medewerker', client: 'Klant' }
    }
    return roleNames[language][role] || role
  }

  // Prevent body scroll when sidebar is open on mobile
  useEffect(() => {
    if (isOpen) {
      document.body.classList.add('sidebar-open')
    } else {
      document.body.classList.remove('sidebar-open')
    }

    return () => {
      document.body.classList.remove('sidebar-open')
    }
  }, [isOpen])

  // Close sidebar on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  return (
    <>
      {/* Backdrop - only visible on mobile when sidebar is open */}
      {isOpen && (
        <div
          className="sidebar-backdrop lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`sidebar-container ${isOpen ? 'open' : ''}`}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Logo and close button */}
        <div className="sidebar-logo">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                {language === 'nl' ? 'Landschap' : 'Landscape'}
              </h1>
              <p className="text-sm text-gray-500">
                {language === 'nl' ? 'Architectuur Tool' : 'Architecture Tool'}
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="sidebar-close-btn lg:hidden"
            aria-label={t.closeSidebar}
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* User Information */}
        {user && (
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 mx-4 rounded-lg mb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
                user.role === 'admin' ? 'bg-red-600' :
                user.role === 'employee' ? 'bg-blue-600' : 'bg-green-600'
              }`}>
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.username}
                </p>
                <div className="flex items-center space-x-1">
                  {(() => {
                    const RoleIcon = getRoleIcon(user.role)
                    return <RoleIcon className="w-3 h-3 text-gray-500" />
                  })()}
                  <p className="text-xs text-gray-500">
                    {getRoleDisplay(user.role)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="sidebar-navigation" aria-label="Main menu">
          <ul className="sidebar-nav-list">
            {getFilteredNavigation().map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name} className="sidebar-nav-item">
                  <Link
                    to={item.href}
                    onClick={onClose} // Always close sidebar when navigating on mobile
                    className={`sidebar-nav-link ${isActive ? 'active' : ''}`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <item.icon className={`sidebar-nav-icon ${isActive ? 'active' : ''}`} />
                    <span>{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* Sidebar Footer */}
        <div className="mt-auto p-4 border-t border-gray-200">
          <div className="text-center">
            <p className="text-xs text-gray-500">
              © 2025 {language === 'nl' ? 'Landschapsarchitectuur' : 'Landscape Architecture'}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              v1.0.0
            </p>
          </div>
        </div>
      </aside>
    </>
  )
}

export default ResponsiveSidebar

