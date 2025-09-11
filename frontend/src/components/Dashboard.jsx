import React, { useState, useEffect } from 'react';
import { DashboardStatsChart } from './Charts/LandscapeCharts';
import { useLanguage } from '../i18n/LanguageProvider';

const Dashboard = () => {
  const { t } = useLanguage();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch dashboard stats
      const statsResponse = await fetch('/api/dashboard/stats');
      if (!statsResponse.ok) {
        throw new Error(`Stats API error: ${statsResponse.status} ${statsResponse.statusText}`);
      }
      const statsData = await statsResponse.json();

      // Fetch recent activity
      const activityResponse = await fetch('/api/dashboard/recent-activity');
      if (!activityResponse.ok) {
        throw new Error(`Activity API error: ${activityResponse.status} ${activityResponse.statusText}`);
      }
      const activityData = await activityResponse.json();

      setStats(statsData);
      setRecentActivity(activityData);
      setRetryCount(0); // Reset retry count on success
    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    fetchDashboardData();
  };

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Error component
  const ErrorDisplay = () => (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Verbinding met backend mislukt
        </h3>
        <p className="text-gray-600 mb-6">
          {error.includes('Failed to fetch') 
            ? 'Controleer of de backend server draait op http://127.0.0.1:5000'
            : error
          }
        </p>
        <button
          onClick={handleRetry}
          className="w-full bg-landscape-primary hover:bg-landscape-primary-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        >
          {retryCount > 0 ? `Opnieuw proberen (${retryCount + 1})` : 'Opnieuw proberen'}
        </button>
        <div className="mt-4 text-sm text-gray-500">
          <p>Zorg ervoor dat:</p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>De backend server draait</li>
            <li>Port 5000 beschikbaar is</li>
            <li>CORS correct is geconfigureerd</li>
          </ul>
        </div>
      </div>
    </div>
  );

  // Empty state component
  const EmptyState = () => (
    <div className="text-center py-12">
      <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
        <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Geen gegevens beschikbaar
      </h3>
      <p className="text-gray-600 mb-6">
        De database lijkt leeg te zijn. Voeg eerst wat gegevens toe om het dashboard te vullen.
      </p>
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => window.location.href = '/suppliers'}
          className="bg-landscape-primary hover:bg-landscape-primary-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Leveranciers toevoegen
        </button>
        <button
          onClick={() => window.location.href = '/plants'}
          className="bg-landscape-secondary hover:bg-landscape-secondary-dark text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Planten toevoegen
        </button>
      </div>
    </div>
  );

  // Show error if there's an error
  if (error && !loading) {
    return <ErrorDisplay />;
  }

  // Show loading skeleton while loading
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <div className="h-8 bg-gray-200 rounded w-64 mb-2 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
          </div>
          <LoadingSkeleton />
        </div>
      </div>
    );
  }

  // Show empty state if no data
  if (stats && Object.values(stats).every(val => val === 0 || val === '0')) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-2">Overzicht van uw landschapsarchitectuur projecten</p>
          </div>
          <EmptyState />
        </div>
      </div>
    );
  }

  // Format currency for display
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  // Format date for display
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('nl-NL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Overzicht van uw landschapsarchitectuur projecten
          </p>
          {stats?.last_updated && (
            <p className="text-sm text-gray-500 mt-1">
              Laatst bijgewerkt: {formatDate(stats.last_updated)}
            </p>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Leveranciers</p>
                <p className="text-2xl font-bold text-landscape-primary">{stats?.suppliers || 0}</p>
              </div>
              <div className="w-12 h-12 bg-landscape-primary/10 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-landscape-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Planten</p>
                <p className="text-2xl font-bold text-landscape-secondary">{stats?.plants || 0}</p>
              </div>
              <div className="w-12 h-12 bg-landscape-secondary/10 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-landscape-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Actieve Projecten</p>
                <p className="text-2xl font-bold text-landscape-accent">{stats?.active_projects || 0}</p>
              </div>
              <div className="w-12 h-12 bg-landscape-accent/10 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-landscape-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Totaal Budget</p>
                <p className="text-2xl font-bold text-landscape-primary">
                  {formatCurrency(stats?.total_budget || 0)}
                </p>
              </div>
              <div className="w-12 h-12 bg-landscape-primary/10 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-landscape-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Charts and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Charts */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Projectoverzicht</h2>
            {stats && (
              <DashboardStatsChart 
                data={{
                  suppliers: stats.suppliers,
                  plants: stats.plants,
                  products: stats.products,
                  clients: stats.clients,
                  projects: stats.projects
                }}
              />
            )}
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recente Activiteit</h2>
            {recentActivity.length > 0 ? (
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-landscape-primary/10 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-landscape-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                      <p className="text-sm text-gray-600">{activity.description}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(activity.timestamp)} • {activity.user}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-gray-600">Geen recente activiteit</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Snelle Acties</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => window.location.href = '/suppliers'}
              className="flex items-center justify-center space-x-2 bg-landscape-primary hover:bg-landscape-primary-dark text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Leverancier toevoegen</span>
            </button>
            
            <button
              onClick={() => window.location.href = '/plants'}
              className="flex items-center justify-center space-x-2 bg-landscape-secondary hover:bg-landscape-secondary-dark text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Plant toevoegen</span>
            </button>
            
            <button
              onClick={() => window.location.href = '/clients'}
              className="flex items-center justify-center space-x-2 bg-landscape-accent hover:bg-landscape-accent-dark text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Klant toevoegen</span>
            </button>
            
            <button
              onClick={() => window.location.href = '/projects'}
              className="flex items-center justify-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <span>Project starten</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

