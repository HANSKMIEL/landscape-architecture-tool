import { Menu, LogOut, User, Settings, ChevronDown } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useLanguage, LanguageSelector } from '../i18n/LanguageProvider';

const Header = ({ 
  onMenuClick, 
  sidebarOpen, 
  user, 
  onLogout 
}) => {
  const { t } = useLanguage() || { t: (key, fallback) => fallback || key };
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef(null);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getRoleDisplay = (role) => {
    return t(`auth.roles.${role}`, role);
  };

  const getRoleColor = (role) => {
    const colors = {
      admin: 'bg-red-600',
      employee: 'bg-blue-600',
      client: 'bg-green-600'
    };
    return colors[role] || 'bg-gray-600';
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-4 shadow-sm">
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
            <h1 className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              {t('dashboard.title', 'Landscape Architecture Tool')}
            </h1>
          </div>
        </div>

        {/* Right side - Language selector and user menu */}
        <div className="flex items-center space-x-4">
          {/* Language Selector */}
          <LanguageSelector className="hidden sm:block" />
          
          {/* User Menu */}
          {user && (
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors"
                aria-expanded={showUserMenu}
              >
                {/* User Avatar */}
                <div className={`w-8 h-8 ${getRoleColor(user.role)} rounded-full flex items-center justify-center`}>
                  <span className="text-white text-sm font-bold">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                
                {/* User Info - Hidden on small screens */}
                <div className="hidden sm:block text-left">
                  <div className="font-medium text-gray-900">{user.username}</div>
                  <div className="text-xs text-gray-500">{getRoleDisplay(user.role)}</div>
                </div>
                
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </button>

              {/* User Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                  {/* User Info Header */}
                  <div className="px-4 py-3 border-b border-gray-100">
                    <div className="font-medium text-gray-900">{user.username}</div>
                    <div className="text-sm text-gray-500">{user.email}</div>
                    <div className="text-xs text-gray-400 mt-1">
                      {getRoleDisplay(user.role)}
                    </div>
                  </div>

                  {/* Menu Items */}
                  <div className="py-1">
                    <button className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                      <User className="w-4 h-4 mr-3" />
                      {t('common.profile', 'Profile')}
                    </button>
                    
                    <button className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors">
                      <Settings className="w-4 h-4 mr-3" />
                      {t('navigation.settings', 'Settings')}
                    </button>
                  </div>

                  {/* Logout */}
                  <div className="py-1 border-t border-gray-100">
                    <button
                      onClick={() => {
                        setShowUserMenu(false);
                        onLogout();
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <LogOut className="w-4 h-4 mr-3" />
                      {t('navigation.logout', 'Logout')}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Mobile title - shown when sidebar is closed */}
      <div className="sm:hidden mt-2">
        <h1 className="text-lg font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
          {t('dashboard.title', 'Landscape Architecture')}
        </h1>
      </div>
    </header>
  );
};

export default Header;
