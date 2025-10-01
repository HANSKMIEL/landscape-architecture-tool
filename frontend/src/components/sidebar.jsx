import { Link, useLocation } from 'react-router-dom'
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
import { useLanguage } from '../i18n/LanguageProvider'

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation()
  const { t } = useLanguage()

  const navigation = [
    { name: t('nav.dashboard', 'Dashboard'), href: '/dashboard', icon: LayoutDashboard },
    { name: t('nav.suppliers', 'Suppliers'), href: '/suppliers', icon: Building2 },
    { name: t('nav.products', 'Products'), href: '/products', icon: Package },
    { name: t('nav.plants', 'Plants'), href: '/plants', icon: Leaf },
    { name: t('nav.clients', 'Clients'), href: '/clients', icon: Users },
    { name: t('nav.projects', 'Projects'), href: '/projects', icon: FolderOpen },
    { name: t('nav.plantRecommendations', 'Plant Recommendations'), href: '/plant-recommendations', icon: Lightbulb },
    { name: t('nav.reports', 'Reports'), href: '/reports', icon: FileText },
    { name: t('nav.settings', 'Settings'), href: '/settings', icon: Settings },
  ]

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-lg transform transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">{t('app.name', 'Landscape')}</h1>
              <p className="text-sm text-gray-500">{t('app.subtitle', 'Architecture Tool')}</p>
            </div>
          </div>
          
          {/* Close button - now visible on all screen sizes */}
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-gray-100 transition-colors"
            aria-label={t('common.close', 'Close')}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <ul className="space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    onClick={() => onClose()} // Always close sidebar when navigating
                    className={`
                      flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                      ${isActive 
                        ? 'bg-green-100 text-green-700 border-r-2 border-green-700' 
                        : 'text-gray-700 hover:bg-gray-100'
                      }
                    `}
                  >
                    <item.icon className={`mr-3 h-5 w-5 ${isActive ? 'text-green-700' : 'text-gray-500'}`} />
                    {item.name}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
      </div>
    </>
  )
}

export default Sidebar

