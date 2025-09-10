import React, { useState, useEffect, Suspense } from 'react';
import { LanguageProvider, useLanguage } from './i18n/LanguageProvider';
import authService from './services/authService';

// Import components
const Dashboard = React.lazy(() => import('./components/Dashboard'));
const Projects = React.lazy(() => import('./components/Projects'));
const Clients = React.lazy(() => import('./components/Clients'));
const Plants = React.lazy(() => import('./components/Plants'));
const Products = React.lazy(() => import('./components/Products'));
const Suppliers = React.lazy(() => import('./components/Suppliers'));
const Reports = React.lazy(() => import('./components/Reports'));
const Settings = React.lazy(() => import('./components/Settings'));

const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
  </div>
);

const LoginForm = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: 'admin', password: 'admin123' });
  const [loading, setLoading] = useState(false);
  const { t } = useLanguage();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await authService.login(credentials);
      if (response.success) {
        onLogin(response.user);
      } else {
        alert('Login failed: ' + response.error);
      }
    } catch (error) {
      alert('Login error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-green-800 mb-2">🌿 Landschapsarchitectuur Tool</h1>
          <p className="text-gray-600">Professional Garden Design Management</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('auth.username', 'Gebruikersnaam')}
            </label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('auth.password', 'Wachtwoord')}
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            {loading ? 'Inloggen...' : t('auth.login', 'Inloggen')}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-600">
          <p className="font-semibold mb-2">Demo Accounts:</p>
          <div className="space-y-1">
            <p><strong>Beheerder:</strong> admin / admin123</p>
            <p><strong>Medewerker:</strong> employee / employee123</p>
            <p><strong>Klant:</strong> client / client123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const MainApp = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const { t } = useLanguage();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const status = await authService.checkAuthStatus();
      if (status.authenticated) {
        setUser(status.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
      setActiveView('dashboard');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <LoginForm onLogin={setUser} />;
  }

  const renderContent = () => {
    switch (activeView) {
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

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-green-800">🌿 LA Tool</h1>
          <p className="text-sm text-gray-600">Welcome, {user.username}</p>
        </div>
        
        <nav className="mt-6">
          {[
            { key: 'dashboard', label: 'Dashboard', icon: '📊' },
            { key: 'projects', label: 'Projecten', icon: '🏗️' },
            { key: 'clients', label: 'Klanten', icon: '👥' },
            { key: 'plants', label: 'Planten', icon: '🌱' },
            { key: 'products', label: 'Producten', icon: '📦' },
            { key: 'suppliers', label: 'Leveranciers', icon: '🏪' },
            { key: 'reports', label: 'Rapporten', icon: '📈' },
            { key: 'settings', label: 'Instellingen', icon: '⚙️' }
          ].map((item) => (
            <button
              key={item.key}
              onClick={() => setActiveView(item.key)}
              className={`w-full text-left px-6 py-3 hover:bg-green-50 flex items-center space-x-3 ${
                activeView === item.key ? 'bg-green-100 border-r-4 border-green-500 text-green-700' : 'text-gray-700'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        
        <div className="absolute bottom-0 w-64 p-6 border-t">
          <button
            onClick={handleLogout}
            className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 flex items-center justify-center space-x-2"
          >
            <span>🚪</span>
            <span>Uitloggen</span>
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-semibold text-gray-800 capitalize">{activeView}</h2>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">{user.role}</span>
            </div>
          </div>
        </header>
        
        <main className="flex-1 p-6 overflow-auto">
          <Suspense fallback={<LoadingSpinner />}>
            {renderContent()}
          </Suspense>
        </main>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <LanguageProvider>
      <MainApp />
    </LanguageProvider>
  );
};

export default App;
