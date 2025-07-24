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
  Settings,
  X
} from 'lucide-react'

const ResponsiveSidebar = ({ isOpen, onClose }) => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Suppliers', href: '/suppliers', icon: Building2 },
    { name: 'Products', href: '/products', icon: Package },
    { name: 'Plants', href: '/plants', icon: Leaf },
    { name: 'Clients', href: '/clients', icon: Users },
    { name: 'Projects', href: '/projects', icon: FolderOpen },
    { name: 'Plant Recommendations', href: '/plant-recommendations', icon: Lightbulb },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

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
            <div className="sidebar-logo-icon">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Landscape</h1>
              <p className="text-sm text-gray-500">Architecture Tool</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="sidebar-close-btn"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="sidebar-navigation" aria-label="Main menu">
          <ul className="sidebar-nav-list">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name} className="sidebar-nav-item">
                  <Link
                    to={item.href}
                    onClick={onClose} // Always close sidebar when navigating
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
      </aside>
    </>
  )
}

export default ResponsiveSidebar

