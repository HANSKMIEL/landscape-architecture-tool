import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Building2,
  Package,
  Leaf,
  Users,
  FolderOpen,
  TrendingUp,
  Plus,
  Activity
} from 'lucide-react'
import { toast } from 'sonner'
import apiService from '../services/api'
import { DashboardStatsChart } from './charts/LandscapeCharts'

const Dashboard = ({ language }) => {
  const [stats, setStats] = useState(null)
  const [recentActivity, setRecentActivity] = useState([])
  const [loading, setLoading] = useState(true)

  const translations = {
    en: {
      title: 'Dashboard',
      subtitle: 'Overview of your landscape architecture business',
      suppliers: 'Suppliers',
      products: 'Products',
      plants: 'Plants',
      clients: 'Clients',
      projects: 'Projects',
      activeProjects: 'Active Projects',
      monthlyRevenue: 'Monthly Revenue',
      quickActions: 'Quick Actions',
      addSupplier: 'Add Supplier',
      addClient: 'Add Client',
      newProject: 'New Project',
      generateReport: 'Generate Report',
      recentActivity: 'Recent Activity',
      projectStatus: 'Project Status Distribution',
      productCategories: 'Product Categories',
      loading: 'Loading dashboard data...',
      error: 'Error loading data'
    },
    nl: {
      title: 'Dashboard',
      subtitle: 'Overzicht van uw landschapsarchitectuur bedrijf',
      suppliers: 'Leveranciers',
      products: 'Producten',
      plants: 'Planten',
      clients: 'Klanten',
      projects: 'Projecten',
      activeProjects: 'Actieve Projecten',
      monthlyRevenue: 'Maandelijkse Omzet',
      quickActions: 'Snelle Acties',
      addSupplier: 'Klant Toevoegen',
      addClient: 'Klant Toevoegen',
      newProject: 'Nieuw Project',
      generateReport: 'Rapport Genereren',
      recentActivity: 'Recente Activiteit',
      projectStatus: 'Project Status Verdeling',
      productCategories: 'Product Categorieën',
      loading: 'Dashboard gegevens laden...',
      error: 'Fout bij laden van gegevens'
    }
  }

  const t = translations[language]

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [statsData, activityData] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getRecentActivity()
      ])
      setStats(statsData)
      setRecentActivity(activityData)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      toast.error(`${t.error}: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p className="ml-2 text-gray-600">{t.loading}</p>
        </div>
      </div>
    )
  }

  const statCards = [
    { 
      title: t.suppliers, 
      value: stats?.suppliers || 0, 
      icon: Building2, 
      color: 'bg-green-500',
      trend: '+12%'
    },
    { 
      title: t.products, 
      value: stats?.products || 0, 
      icon: Package, 
      color: 'bg-blue-500',
      trend: '+8%'
    },
    { 
      title: t.plants, 
      value: stats?.plants || 0, 
      icon: Leaf, 
      color: 'bg-emerald-500',
      trend: '+15%'
    },
    { 
      title: t.clients, 
      value: stats?.clients || 0, 
      icon: Users, 
      color: 'bg-purple-500',
      trend: '+5%'
    },
    { 
      title: t.projects, 
      value: stats?.projects || 0, 
      icon: FolderOpen, 
      color: 'bg-orange-500',
      trend: '+20%'
    },
    { 
      title: t.activeProjects, 
      value: stats?.active_projects || 0, 
      icon: Activity, 
      color: 'bg-cyan-500',
      trend: '+10%'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">{t.title}</h1>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value.toLocaleString()}</p>
                  <div className="flex items-center mt-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-600 ml-1">{stat.trend}</span>
                  </div>
                </div>
                <div className={`p-3 rounded-full ${stat.color}`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="mt-8">
        <DashboardStatsChart stats={stats} />
      </div>

      {/* Revenue Card */}
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
            {t.monthlyRevenue}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t.monthlyRevenue}</p>
              <p className="text-2xl font-bold text-gray-900">
                €{stats?.monthly_revenue?.toLocaleString() || '0'}
              </p>
            </div>
            <div className="p-3 rounded-full bg-green-500">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>{t.quickActions}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button className="h-20 flex flex-col items-center justify-center gap-2">
              <Plus className="h-5 w-5" />
              <span className="text-sm">{t.addSupplier}</span>
            </Button>
            <Button className="h-20 flex flex-col items-center justify-center gap-2">
              <Plus className="h-5 w-5" />
              <span className="text-sm">{t.addClient}</span>
            </Button>
            <Button className="h-20 flex flex-col items-center justify-center gap-2">
              <FolderOpen className="h-5 w-5" />
              <span className="text-sm">{t.newProject}</span>
            </Button>
            <Button className="h-20 flex flex-col items-center justify-center gap-2">
              <Activity className="h-5 w-5" />
              <span className="text-sm">{t.generateReport}</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>{t.recentActivity}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0">
                    <Activity className="h-5 w-5 text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.description}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Geen recente activiteit</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

