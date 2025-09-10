import React, { useState, useEffect } from 'react';
import { useLanguage } from '../i18n/LanguageProvider';

const Dashboard = () => {
  const { t } = useLanguage() || { t: (key, fallback) => fallback || key };
  const [stats, setStats] = useState({
    projects: 0,
    clients: 0,
    plants: 0,
    suppliers: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      
      // Fetch all stats in parallel
      const [projectsRes, clientsRes, plantsRes, suppliersRes] = await Promise.all([
        fetch('/api/projects', { credentials: 'include' }),
        fetch('/api/clients', { credentials: 'include' }),
        fetch('/api/plants', { credentials: 'include' }),
        fetch('/api/suppliers', { credentials: 'include' })
      ]);

      const [projects, clients, plants, suppliers] = await Promise.all([
        projectsRes.ok ? projectsRes.json() : { projects: [] },
        clientsRes.ok ? clientsRes.json() : { clients: [] },
        plantsRes.ok ? plantsRes.json() : { plants: [] },
        suppliersRes.ok ? suppliersRes.json() : { suppliers: [] }
      ]);

      setStats({
        projects: projects.projects?.length || 0,
        clients: clients.clients?.length || 0,
        plants: plants.plants?.length || 0,
        suppliers: suppliers.suppliers?.length || 0
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600">Welcome to your Landscape Architecture Management System</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-orange-500 mr-4">🏗️</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Total Projects</h3>
              <p className="text-3xl font-bold text-gray-900">{stats.projects}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-blue-500 mr-4">👥</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Total Clients</h3>
              <p className="text-3xl font-bold text-gray-900">{stats.clients}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-green-500 mr-4">🌱</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Plant Species</h3>
              <p className="text-3xl font-bold text-gray-900">{stats.plants}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="text-3xl text-red-500 mr-4">🏪</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Suppliers</h3>
              <p className="text-3xl font-bold text-gray-900">{stats.suppliers}</p>
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
              <span className="text-blue-600 font-semibold">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">New Clients This Month</span>
              <span className="text-green-600 font-semibold">{stats.clients}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active Projects</span>
              <span className="text-purple-600 font-semibold">0</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Financial Overview</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Project Budget</span>
              <span className="text-green-600 font-semibold">€0</span>
            </div>
          </div>
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-700">
              💡 Tip: Use the navigation menu to manage your projects, clients, and plant databases.
            </p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600 flex items-center justify-center">
            <span className="text-2xl mr-2">➕</span>
            Create New Project
          </button>
          <button className="bg-green-500 text-white p-4 rounded-lg hover:bg-green-600 flex items-center justify-center">
            <span className="text-2xl mr-2">👤</span>
            Add New Client
          </button>
          <button className="bg-purple-500 text-white p-4 rounded-lg hover:bg-purple-600 flex items-center justify-center">
            <span className="text-2xl mr-2">📊</span>
            View Reports
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
