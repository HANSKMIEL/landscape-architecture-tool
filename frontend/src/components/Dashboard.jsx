import React, { useState, useEffect } from 'react';
import { useLanguage } from '../i18n/LanguageProvider';

const Dashboard = () => {
  const { t } = useLanguage() || { t: (key, fallback) => fallback || key };
  const [dashboardData, setDashboardData] = useState({
    totals: {
      projects: 0,
      clients: 0,
      plants: 0,
      suppliers: 0,
      active_projects: 0
    },
    recent_activity: {
      new_projects: 0,
      new_clients: 0
    },
    financial: {
      total_budget: 0
    },
    projects_by_status: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/dashboard/stats', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else if (response.status === 401) {
        setError('Authentication required');
      } else {
        setError('Failed to load dashboard data');
      }
    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      setError('Connection to backend failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <div className="text-red-600 text-6xl mb-4">⚠️</div>
        <h3 className="text-lg font-semibold text-red-800 mb-2">Dashboard Loading Error</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Retry Loading
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          {t('dashboard.title', 'Dashboard Overview')}
        </h1>
        <p className="text-gray-600">
          {t('dashboard.subtitle', 'Welcome to your Landscape Architecture Management System')}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-blue-500 mr-4">🏗️</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Projects</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.totals.projects}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-green-500 mr-4">👥</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Clients</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.totals.clients}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-purple-500 mr-4">🌱</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Plant Species</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.totals.plants}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-orange-500 mr-4">🏪</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Suppliers</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.totals.suppliers}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">New Projects This Month</span>
              <span className="font-semibold text-blue-600">{dashboardData.recent_activity.new_projects}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">New Clients This Month</span>
              <span className="font-semibold text-green-600">{dashboardData.recent_activity.new_clients}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active Projects</span>
              <span className="font-semibold text-purple-600">{dashboardData.totals.active_projects}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Financial Overview</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Project Budget</span>
              <span className="font-semibold text-green-600">
                €{dashboardData.financial.total_budget.toLocaleString()}
              </span>
            </div>
            <div className="text-sm text-gray-500 mt-4">
              💡 Tip: Use the navigation menu to manage your projects, clients, and plant databases.
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600 transition-colors">
            <div className="text-2xl mb-2">➕</div>
            <div>Create New Project</div>
          </button>
          <button className="bg-green-500 text-white p-4 rounded-lg hover:bg-green-600 transition-colors">
            <div className="text-2xl mb-2">👤</div>
            <div>Add New Client</div>
          </button>
          <button className="bg-purple-500 text-white p-4 rounded-lg hover:bg-purple-600 transition-colors">
            <div className="text-2xl mb-2">📊</div>
            <div>View Reports</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
