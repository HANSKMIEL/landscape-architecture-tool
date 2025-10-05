import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts'
import { 
  Download, 
  FileText, 
  TrendingUp, 
  Users, 
  DollarSign, 
  BarChart3,
  RefreshCw,
  Calendar,
  Filter,
  Printer,
  Mail,
  Loader2
} from 'lucide-react'
import ApiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const Reports = () => {
  const { t } = useLanguage()
  
  // State management
  const [__analyticsData, set_analyticsData] = useState({})
  const [__loading, set_loading] = useState(false)
  const [__error, set_error] = useState(null)
  const [__selectedReportType, set_selectedReportType] = useState('overview')
  const [__dateRange, set_dateRange] = useState({
    start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [__filters, set_filters] = useState({
    client: '',
    project: '',
    supplier: '',
    category: ''
  })
  const [__generatingReport, set_generatingReport] = useState(false)

  // Report types
  const reportTypes = [
    { id: 'overview', label: t('reports.types.overview', 'Business Overview'), icon: BarChart3 },
    { id: 'clients', label: t('reports.types.clients', 'Client Analysis'), icon: Users },
    { id: 'projects', label: t('reports.types.projects', 'Project Performance'), icon: TrendingUp },
    { id: 'plants', label: t('reports.types.plants', 'Plant Analytics'), icon: FileText },
    { id: 'financial', label: t('reports.types.financial', 'Financial Summary'), icon: DollarSign }
  ]

  // Chart colors
  const chartColors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316']

  // Load analytics data
  const loadAnalyticsData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const __params = {
        start_date: dateRange.start,
        end_date: dateRange.end,
        ...filters
      }
      
      // Load different data based on report type
      let data = {}
      
      switch (selectedReportType) {
        case 'overview':
          data = await loadOverviewData(params)
          break
        case 'clients':
          data = await loadClientAnalytics(params)
          break
        case 'projects':
          data = await loadProjectAnalytics(params)
          break
        case 'plants':
          data = await loadPlantAnalytics(params)
          break
        case 'financial':
          data = await loadFinancialData(params)
          break
        default:
          data = await loadOverviewData(params)
      }
      
      setAnalyticsData(data)
    } catch (err) {
      console.error('Error loading analytics data:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [selectedReportType, dateRange, filters])

  // Load overview data
  const loadOverviewData = async (params) => {
    const [stats, clientData, projectData, plantData] = await Promise.all([
      ApiService.getDashboardStats(),
      ApiService.getClients({ limit: 10 }),
      ApiService.getProjects({ limit: 10 }),
      ApiService.getPlants({ limit: 10 })
    ])

    return {
      stats,
      topClients: clientData.clients?.slice(0, 5) || [],
      recentProjects: projectData.projects?.slice(0, 5) || [],
      popularPlants: plantData.plants?.slice(0, 5) || [],
      monthlyData: generateMockMonthlyData(),
      statusDistribution: generateMockStatusData()
    }
  }

  // Load client analytics
  const loadClientAnalytics = async (params) => {
    const clientData = await ApiService.getClients()
    const projectData = await ApiService.getProjects()
    
    const __clientProjects = {}
    projectData.projects?.forEach(project => {
      if (project.client_id) {
        clientProjects[project.client_id] = (clientProjects[project.client_id] || 0) + 1
      }
    })

    const clientAnalytics = clientData.clients?.map(client => ({
      ...client,
      projectCount: clientProjects[client.id] || 0,
      totalBudget: projectData.projects
        ?.filter(p => p.client_id === client.id)
        ?.reduce((sum, p) => sum + (parseFloat(p.budget) || 0), 0) || 0
    })) || []

    return {
      clients: clientAnalytics,
      topClientsByProjects: clientAnalytics
        .sort((a, b) => b.projectCount - a.projectCount)
        .slice(0, 10),
      topClientsByBudget: clientAnalytics
        .sort((a, b) => b.totalBudget - a.totalBudget)
        .slice(0, 10)
    }
  }

  // Load project analytics
  const loadProjectAnalytics = async (params) => {
    const projectData = await ApiService.getProjects()
    const projects = projectData.projects || []

    const __statusCounts = {}
    const __monthlyProjects = {}
    let totalBudget = 0

    projects.forEach(project => {
      // Status distribution
      const status = project.status || 'unknown'
      statusCounts[status] = (statusCounts[status] || 0) + 1

      // Monthly distribution
      if (project.start_date) {
        const month = new Date(project.start_date).toISOString().slice(0, 7)
        monthlyProjects[month] = (monthlyProjects[month] || 0) + 1
      }

      // Budget calculation
      totalBudget += parseFloat(project.budget) || 0
    })

    return {
      projects,
      totalProjects: projects.length,
      totalBudget,
      averageBudget: projects.length > 0 ? totalBudget / projects.length : 0,
      statusDistribution: Object.entries(statusCounts).map(([status, count]) => ({
        name: t(`projects.statuses.${status}`, status),
        value: count
      })),
      monthlyDistribution: Object.entries(monthlyProjects)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([month, count]) => ({
          month: new Date(month + '-01').toLocaleDateString('nl-NL', { month: 'short', year: 'numeric' }),
          projects: count
        }))
    }
  }

  // Load plant analytics
  const loadPlantAnalytics = async (params) => {
    const plantData = await ApiService.getPlants()
    const plants = plantData.plants || []

    const __categoryCounts = {}
    const __supplierCounts = {}

    plants.forEach(plant => {
      // Category distribution
      const category = plant.category || 'other'
      categoryCounts[category] = (categoryCounts[category] || 0) + 1

      // Supplier distribution
      if (plant.supplier_id) {
        supplierCounts[plant.supplier_id] = (supplierCounts[plant.supplier_id] || 0) + 1
      }
    })

    return {
      plants,
      totalPlants: plants.length,
      categoryDistribution: Object.entries(categoryCounts).map(([category, count]) => ({
        name: t(`plants.categories.${category}`, category),
        value: count
      })),
      topPlantsByPrice: plants
        .filter(p => p.price)
        .sort((a, b) => parseFloat(b.price) - parseFloat(a.price))
        .slice(0, 10),
      nativePlants: plants.filter(p => p.native).length,
      nativePercentage: plants.length > 0 ? (plants.filter(p => p.native).length / plants.length) * 100 : 0
    }
  }

  // Load financial data
  const loadFinancialData = async (params) => {
    const projectData = await ApiService.getProjects()
    const projects = projectData.projects || []

    const __monthlyRevenue = {}
    let totalRevenue = 0
    let completedProjects = 0

    projects.forEach(project => {
      const budget = parseFloat(project.budget) || 0
      totalRevenue += budget

      if (project.status === 'completed') {
        completedProjects++
        
        if (project.end_date) {
          const month = new Date(project.end_date).toISOString().slice(0, 7)
          monthlyRevenue[month] = (monthlyRevenue[month] || 0) + budget
        }
      }
    })

    return {
      totalRevenue,
      completedProjects,
      averageProjectValue: projects.length > 0 ? totalRevenue / projects.length : 0,
      monthlyRevenue: Object.entries(monthlyRevenue)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([month, revenue]) => ({
          month: new Date(month + '-01').toLocaleDateString('nl-NL', { month: 'short', year: 'numeric' }),
          revenue
        }))
    }
  }

  // Generate mock data for demonstration
  const generateMockMonthlyData = () => {
    const months = []
    for (let i = 11; i >= 0; i--) {
      const date = new Date()
      date.setMonth(date.getMonth() - i)
      months.push({
        month: date.toLocaleDateString('nl-NL', { month: 'short' }),
        projects: Math.floor(Math.random() * 10) + 1,
        revenue: Math.floor(Math.random() * 50000) + 10000
      })
    }
    return months
  }

  const generateMockStatusData = () => [
    { name: t('projects.statuses.planning', 'Planning'), value: 15 },
    { name: t('projects.statuses.design', 'Design'), value: 25 },
    { name: t('projects.statuses.construction', 'Construction'), value: 30 },
    { name: t('projects.statuses.completed', 'Completed'), value: 20 },
    { name: t('projects.statuses.on_hold', 'On Hold'), value: 10 }
  ]

  // Generate PDF report
  const generatePDFReport = async () => {
    try {
      setGeneratingReport(true)
      
      const __reportData = {
        type: selectedReportType,
        dateRange,
        filters,
        data: analyticsData,
        language: 'nl', // User preference for Dutch reports
        timestamp: new Date().toISOString()
      }

      // Call backend API to generate PDF
      const response = await fetch('/api/reports/generate-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData)
      })

      if (!response.ok) {
        throw new Error('Failed to generate PDF report')
      }

      // Download the PDF
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `landscape-report-${selectedReportType}-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      alert(t('reports.generated', 'Report generated successfully'))
    } catch (err) {
      console.error('Error generating PDF report:', err)
      alert(t('reports.error', 'Error generating report: ') + err.message)
    } finally {
      setGeneratingReport(false)
    }
  }

  // Export data as CSV
  const exportCSV = () => {
    try {
      let csvData = []
      let filename = `landscape-data-${selectedReportType}-${new Date().toISOString().split('T')[0]}.csv`

      switch (selectedReportType) {
        case 'clients':
          csvData = analyticsData.clients?.map(client => ({
            Name: client.name,
            Email: client.email,
            Phone: client.phone,
            City: client.city,
            Projects: client.projectCount || 0,
            'Total Budget': client.totalBudget || 0
          })) || []
          break
        case 'projects':
          csvData = analyticsData.projects?.map(project => ({
            Name: project.name,
            Status: project.status,
            Budget: project.budget,
            'Start Date': project.start_date,
            'End Date': project.end_date
          })) || []
          break
        case 'plants':
          csvData = analyticsData.plants?.map(plant => ({
            'Scientific Name': plant.name,
            'Common Name': plant.common_name,
            Category: plant.category,
            Price: plant.price,
            Native: plant.native ? 'Yes' : 'No'
          })) || []
          break
        default:
          csvData = [{ message: 'No CSV data available for this report type' }]
      }

      if (csvData.length === 0) {
        alert(t('reports.noData', 'No data available for export'))
        return
      }

      const headers = Object.keys(csvData[0])
      const csvContent = [
        headers.join(','),
        ...csvData.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      alert(t('reports.exported', 'Data exported successfully'))
    } catch (err) {
      console.error('Error exporting CSV:', err)
      alert(t('reports.exportError', 'Error exporting data: ') + err.message)
    }
  }

  useEffect(() => {
    loadAnalyticsData()
  }, [loadAnalyticsData])

  // Render chart based on data
  const renderChart = (data, type) => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          {t('reports.noData', 'No data available')}
        </div>
      )
    }

    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        )
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="projects" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        )
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )
      default:
        return null
    }
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {t('reports.title', 'Reports')}
            </h1>
            <p className="text-gray-600">
              {t('reports.subtitle', 'Generate comprehensive reports and analytics')}
            </p>
          </div>
        </div>
        <Card>
          <CardContent className="p-12">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-red-800 mb-2">
                {t('reports.errorLoading', 'Error Loading Reports')}
              </h2>
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={loadAnalyticsData} variant="destructive">
                {t('common.tryAgain', 'Try Again')}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {t('reports.title', 'Reports')}
          </h1>
          <p className="text-gray-600">
            {t('reports.subtitle', 'Generate comprehensive reports and analytics')}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button 
            variant="outline"
            onClick={exportCSV}
            className="flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>{t('reports.exportCSV', 'Export CSV')}</span>
          </Button>
          <Button 
            onClick={generatePDFReport}
            disabled={generatingReport}
            className="flex items-center space-x-2"
          >
            {generatingReport ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            <span>
              {generatingReport 
                ? t('reports.generating', 'Generating...') 
                : t('reports.generatePDF', 'Generate PDF')
              }
            </span>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            {t('reports.filters', 'Filters')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('reports.startDate', 'Start Date')}
              </label>
              <Input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('reports.endDate', 'End Date')}
              </label>
              <Input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                {t('reports.client', 'Client')}
              </label>
              <Input
                placeholder={t('reports.selectClient', 'Select client...')}
                value={filters.client}
                onChange={(e) => setFilters(prev => ({ ...prev, client: e.target.value }))}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={loadAnalyticsData} disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                {t('reports.refresh', 'Refresh')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report Type Tabs */}
      <Tabs value={selectedReportType} onValueChange={setSelectedReportType}>
        <TabsList className="grid w-full grid-cols-5">
          {reportTypes.map((type) => (
            <TabsTrigger key={type.id} value={type.id} className="flex items-center space-x-2">
              <type.icon className="h-4 w-4" />
              <span className="hidden sm:inline">{type.label}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {loading ? (
            <Card>
              <CardContent className="p-12">
                <div className="flex justify-center items-center">
                  <Loader2 className="h-8 w-8 animate-spin text-green-600" />
                  <span className="ml-2 text-gray-600">{t('reports.loading', 'Loading...')}</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>{t('reports.monthlyTrends', 'Monthly Trends')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderChart(analyticsData.monthlyData, 'line')}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t('reports.projectStatus', 'Project Status Distribution')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderChart(analyticsData.statusDistribution, 'pie')}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Client Analytics Tab */}
        <TabsContent value="clients" className="space-y-6">
          {loading ? (
            <Card>
              <CardContent className="p-12">
                <div className="flex justify-center items-center">
                  <Loader2 className="h-8 w-8 animate-spin text-green-600" />
                  <span className="ml-2 text-gray-600">{t('reports.loading', 'Loading...')}</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>{t('reports.topClientsByProjects', 'Top Clients by Projects')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderChart(
                    analyticsData.topClientsByProjects?.map(client => ({
                      name: client.name,
                      value: client.projectCount
                    })) || [],
                    'bar'
                  )}
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t('reports.topClientsByBudget', 'Top Clients by Budget')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderChart(
                    analyticsData.topClientsByBudget?.map(client => ({
                      name: client.name,
                      value: client.totalBudget
                    })) || [],
                    'bar'
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Project Analytics Tab */}
        <TabsContent value="projects" className="space-y-6">
          {loading ? (
            <Card>
              <CardContent className="p-12">
                <div className="flex justify-center items-center">
                  <Loader2 className="h-8 w-8 animate-spin text-green-600" />
                  <span className="ml-2 text-gray-600">{t('reports.loading', 'Loading...')}</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <BarChart3 className="h-8 w-8 text-green-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.totalProjects', 'Total Projects')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          {analyticsData.totalProjects || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <DollarSign className="h-8 w-8 text-blue-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.totalBudget', 'Total Budget')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          €{(analyticsData.totalBudget || 0).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <TrendingUp className="h-8 w-8 text-purple-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.averageBudget', 'Average Budget')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          €{(analyticsData.averageBudget || 0).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>{t('reports.projectStatusDistribution', 'Project Status Distribution')}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderChart(analyticsData.statusDistribution, 'pie')}
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle>{t('reports.monthlyProjectDistribution', 'Monthly Project Distribution')}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderChart(analyticsData.monthlyDistribution, 'bar')}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Plant Analytics Tab */}
        <TabsContent value="plants" className="space-y-6">
          {loading ? (
            <Card>
              <CardContent className="p-12">
                <div className="flex justify-center items-center">
                  <Loader2 className="h-8 w-8 animate-spin text-green-600" />
                  <span className="ml-2 text-gray-600">{t('reports.loading', 'Loading...')}</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <FileText className="h-8 w-8 text-green-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.totalPlants', 'Total Plants')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          {analyticsData.totalPlants || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <Users className="h-8 w-8 text-blue-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.nativePlants', 'Native Plants')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          {analyticsData.nativePlants || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <TrendingUp className="h-8 w-8 text-purple-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.nativePercentage', 'Native %')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          {(analyticsData.nativePercentage || 0).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t('reports.plantCategoryDistribution', 'Plant Category Distribution')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderChart(analyticsData.categoryDistribution, 'pie')}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* Financial Tab */}
        <TabsContent value="financial" className="space-y-6">
          {loading ? (
            <Card>
              <CardContent className="p-12">
                <div className="flex justify-center items-center">
                  <Loader2 className="h-8 w-8 animate-spin text-green-600" />
                  <span className="ml-2 text-gray-600">{t('reports.loading', 'Loading...')}</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <DollarSign className="h-8 w-8 text-green-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.totalRevenue', 'Total Revenue')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          €{(analyticsData.totalRevenue || 0).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <BarChart3 className="h-8 w-8 text-blue-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.completedProjects', 'Completed Projects')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          {analyticsData.completedProjects || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center">
                      <TrendingUp className="h-8 w-8 text-purple-600" />
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">
                          {t('reports.averageProjectValue', 'Average Project Value')}
                        </p>
                        <p className="text-2xl font-bold text-gray-900">
                          €{(analyticsData.averageProjectValue || 0).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t('reports.monthlyRevenue', 'Monthly Revenue')}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderChart(analyticsData.monthlyRevenue, 'line')}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Reports
