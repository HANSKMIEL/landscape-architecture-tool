import { Menu, Globe } from 'lucide-react'

const Header = ({ onMenuClick, language, onLanguageToggle, sidebarOpen }) => {
  return (
    <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Menu button and title */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="mobile-menu-btn p-2 rounded-md text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors"
            aria-label={sidebarOpen ? "Close menu" : "Open menu"}
            aria-expanded={sidebarOpen}
          >
            <Menu className="w-6 h-6" />
          </button>
          
          <div className="hidden sm:block">
            <h1 className="text-xl font-semibold text-gray-900">
              Landscape Architecture Tool
            </h1>
          </div>
        </div>

        {/* Right side - Language toggle and other controls */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onLanguageToggle}
            className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors"
            aria-label={`Switch to ${language === 'en' ? 'Dutch' : 'English'}`}
          >
            <Globe className="w-4 h-4" />
            <span className="hidden sm:inline">
              {language === 'en' ? 'EN' : 'NL'}
            </span>
          </button>
          
          {/* User profile or additional controls can go here */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">LA</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile title - shown when sidebar is closed */}
      <div className="sm:hidden mt-2">
        <h1 className="text-lg font-semibold text-gray-900">
          Landscape Architecture
        </h1>
      </div>
    </header>
  )
}

export default Header

