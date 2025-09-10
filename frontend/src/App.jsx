import React, { useState, useEffect } from 'react';
import { LanguageProvider } from './i18n/LanguageProvider';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Projects from './components/Projects';
import Clients from './components/Clients';
import Plants from './components/Plants';
import Products from './components/Products';
import Suppliers from './components/Suppliers';
import Reports from './components/Reports';
import Settings from './components/Settings';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/status', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.authenticated) {
          setIsAuthenticated(true);
          setUser(data.user);
        } else {
          setIsAuthenticated(false);
          setUser(null);
        }
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (credentials) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        setIsAuthenticated(true);
        setUser(data.user);
        setCurrentView('dashboard');
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const handleLogout = async () => {
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      
      // Always clear local state regardless of response
      setIsAuthenticated(false);
      setUser(null);
      setCurrentView('dashboard');
      
      // Force page reload to clear any cached data
      window.location.reload();
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state on error
      setIsAuthenticated(false);
      setUser(null);
      setCurrentView('dashboard');
      window.location.reload();
    }
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'projects':
        return <Projects />;
      case 'clients':
        return <Clients />;
      case 'plants':
        return <Plants />;
      case 'products':
        return <Products />;
      case 'suppliers':
        return <Suppliers />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <LanguageProvider>
        <Login onLogin={handleLogin} />
      </LanguageProvider>
    );
  }

  return (
    <LanguageProvider>
      <div className="min-h-screen bg-gray-100 flex">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-lg">
          {/* Logo */}
          <div className="p-6 border-b">
            <div className="flex items-center">
              <div className="text-2xl text-green-600 mr-2">🌿</div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">LA Tool</h1>
                <p className="text-sm text-gray-600">Welcome, {user?.username || 'admin'}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="mt-6">
            <div className="px-4 space-y-2">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'dashboard' 
                    ? 'bg-green-100 text-green-700 border-l-4 border-green-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">📊</span>
                Dashboard
              </button>

              <button
                onClick={() => setCurrentView('projects')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'projects' 
                    ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">🏗️</span>
                Projecten
              </button>

              <button
                onClick={() => setCurrentView('clients')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'clients' 
                    ? 'bg-yellow-100 text-yellow-700 border-l-4 border-yellow-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">👥</span>
                Klanten
              </button>

              <button
                onClick={() => setCurrentView('plants')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'plants' 
                    ? 'bg-purple-100 text-purple-700 border-l-4 border-purple-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">🌱</span>
                Planten
              </button>

              <button
                onClick={() => setCurrentView('products')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'products' 
                    ? 'bg-teal-100 text-teal-700 border-l-4 border-teal-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">📦</span>
                Producten
              </button>

              <button
                onClick={() => setCurrentView('suppliers')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'suppliers' 
                    ? 'bg-pink-100 text-pink-700 border-l-4 border-pink-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">🏪</span>
                Leveranciers
              </button>

              <button
                onClick={() => setCurrentView('reports')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'reports' 
                    ? 'bg-indigo-100 text-indigo-700 border-l-4 border-indigo-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">📈</span>
                Rapporten
              </button>

              <button
                onClick={() => setCurrentView('settings')}
                className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                  currentView === 'settings' 
                    ? 'bg-orange-100 text-orange-700 border-l-4 border-orange-500' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-xl mr-3">⚙️</span>
                Instellingen
              </button>
            </div>

            {/* Logout Button */}
            <div className="mt-8 px-4">
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-4 py-3 text-left rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors"
              >
                <span className="text-xl mr-3">🚪</span>
                Uitloggen
              </button>
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="bg-white shadow-sm border-b px-6 py-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-800 capitalize">{currentView}</h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">{user?.email || 'admin@landscape-tool.com'}</span>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  {user?.role || 'admin'}
                </span>
              </div>
            </div>
          </header>

          {/* Content */}
          <main className="flex-1 p-6">
            {renderCurrentView()}
          </main>
        </div>
      </div>
    </LanguageProvider>
  );
};

export default App;
