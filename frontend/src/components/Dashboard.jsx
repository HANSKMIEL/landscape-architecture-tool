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
import { DashboardStatsChart } from './Charts/LandscapeCharts'

const Dashboard = ({ language }) => {
  const [stats, setStats] = useState(null)
  const [recentActivity, setRecentActivity] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        const [statsResponse, activityResponse] = await Promise.all([
          apiService.get('/dashboard/stats'),
          apiService.get('/dashboard/recent-activity')
        ])
        
        setStats(statsResponse.data)
        setRecentActivity(activityResponse.data)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        toast.error('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const statCards = [
    {
      title: language === 'nl' ? 'Leveranciers' : 'Suppliers',
      value: stats?.suppliers || 0,
      icon: Building2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: language === 'nl' ? 'Planten' : 'Plants',
      value: stats?.plants || 0,
      icon: Leaf,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: language === 'nl' ? 'Producten' : 'Products',
      value: stats?.products || 0,
      icon: Package,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: language === 'nl' ? 'Klanten' : 'Clients',
      value: stats?.clients || 0,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    },
    {
      title: language === 'nl' ? 'Projecten' : 'Projects',
      value: stats?.projects || 0,
      icon: FolderOpen,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50'
    },
    {
      title: language === 'nl' ? 'Totale Waarde' : 'Total Value',
      value: stats?.total_value ? `€${stats.total_value.toLocaleString()}` : '€0',
      icon: TrendingUp,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50'
    }
  ]

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1 className="dashboard-title">
            {language === 'nl' ? 'Dashboard' : 'Dashboard'}
          </h1>
        </div>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>{language === 'nl' ? 'Gegevens laden...' : 'Loading data...'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">
          {language === 'nl' ? 'Landschapsarchitectuur Dashboard' : 'Landscape Architecture Dashboard'}
        </h1>
        <p className="dashboard-subtitle">
          {language === 'nl' 
            ? 'Overzicht van uw projecten en gegevens' 
            : 'Overview of your projects and data'
          }
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        {statCards.map((stat, index) => {
          const IconComponent = stat.icon
          return (
            <Card key={index} className="stat-card">
              <CardContent className="stat-card-content">
                <div className="stat-card-header">
                  <div className={`stat-icon ${stat.bgColor}`}>
                    <IconComponent className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="stat-info">
                    <p className="stat-title">{stat.title}</p>
                    <p className="stat-value">{stat.value}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <Card className="chart-card">
          <CardHeader>
            <CardTitle className="chart-title">
              {language === 'nl' ? 'Gegevensoverzicht' : 'Data Overview'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <DashboardStatsChart data={stats} language={language} />
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <Card className="activity-card">
          <CardHeader className="activity-header">
            <CardTitle className="activity-title">
              <Activity className="h-5 w-5" />
              {language === 'nl' ? 'Recente Activiteit' : 'Recent Activity'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentActivity.length > 0 ? (
              <div className="activity-list">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      <div className="activity-dot"></div>
                    </div>
                    <div className="activity-content">
                      <p className="activity-text">{activity.description}</p>
                      <p className="activity-time">{activity.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-activity">
                {language === 'nl' 
                  ? 'Geen recente activiteit' 
                  : 'No recent activity'
                }
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <Card className="actions-card">
          <CardHeader>
            <CardTitle className="actions-title">
              {language === 'nl' ? 'Snelle Acties' : 'Quick Actions'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="actions-grid">
              <Button className="action-button" variant="outline">
                <Plus className="h-4 w-4" />
                {language === 'nl' ? 'Nieuw Project' : 'New Project'}
              </Button>
              <Button className="action-button" variant="outline">
                <Building2 className="h-4 w-4" />
                {language === 'nl' ? 'Leverancier Toevoegen' : 'Add Supplier'}
              </Button>
              <Button className="action-button" variant="outline">
                <Leaf className="h-4 w-4" />
                {language === 'nl' ? 'Plant Toevoegen' : 'Add Plant'}
              </Button>
              <Button className="action-button" variant="outline">
                <Users className="h-4 w-4" />
                {language === 'nl' ? 'Klant Toevoegen' : 'Add Client'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard

