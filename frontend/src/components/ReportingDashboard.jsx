import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
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
} from 'recharts';
import { 
  TrendingUp, 
  Users, 
  Leaf, 
  DollarSign, 
  Activity, 
  Download,
  Calendar,
  RefreshCw
} from 'lucide-react';

const ReportingDashboard = ({ language = 'en' }) => {
  const [analyticsData, setAnalyticsData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({ 
    start: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0], // Start of year
    end: new Date().toISOString().split('T')[0] // Today
  });

  const translations = {
    en: {
      title: 'Reporting Dashboard',
      subtitle: 'Comprehensive business intelligence and analytics',
      overview: 'Overview',
      plants: 'Plant Analytics',
      projects: 'Project Performance',
      clients: 'Client Insights',
      financial: 'Financial Reports',
      loading: 'Loading analytics...',
      error: 'Error loading data',
      refresh: 'Refresh Data',
      export: 'Export',
      dateRange: 'Date Range',
      from: 'From',
      to: 'To',
      apply: 'Apply',
      totalProjects: 'Total Projects',
      totalClients: 'Total Clients',
      totalRevenue: 'Total Revenue',
      avgBudget: 'Average Budget',
      popularPlants: 'Most Popular Plants',
      projectStatus: 'Project Status Distribution',
      clientTypes: 'Client Types',
      monthlyTrends: 'Monthly Trends',
      plantCategories: 'Plant Categories',
      revenueByType: 'Revenue by Project Type',
      budgetDistribution: 'Budget Distribution',
      recommendationEffectiveness: 'Recommendation System Performance',
      plantUsageOverTime: 'Plant Usage Over Time',
      clientAcquisition: 'Client Acquisition',
      projectsCreated: 'Projects Created',
      revenue: 'Revenue',
      count: 'Count',
      projectCount: 'Projects',
      month: 'Month',
      noData: 'No data available'
    },
    nl: {
      title: 'Rapportage Dashboard',
      subtitle: 'Uitgebreide business intelligence en analytics',
      overview: 'Overzicht',
      plants: 'Plant Analytics',
      projects: 'Project Prestaties',
      clients: 'Klant Inzichten',
      financial: 'Financiële Rapporten',
      loading: 'Analytics laden...',
      error: 'Fout bij laden van data',
      refresh: 'Vernieuw Data',
      export: 'Exporteren',
      dateRange: 'Datumbereik',
      from: 'Van',
      to: 'Tot',
      apply: 'Toepassen',
      totalProjects: 'Totaal Projecten',
      totalClients: 'Totaal Klanten',
      totalRevenue: 'Totale Omzet',
      avgBudget: 'Gemiddeld Budget',
      popularPlants: 'Populairste Planten',
      projectStatus: 'Project Status Verdeling',
      clientTypes: 'Klant Types',
      monthlyTrends: 'Maandelijkse Trends',
      plantCategories: 'Plant Categorieën',
      revenueByType: 'Omzet per Project Type',
      budgetDistribution: 'Budget Verdeling',
      recommendationEffectiveness: 'Aanbevelingssysteem Prestaties',
      plantUsageOverTime: 'Plant Gebruik Over Tijd',
      clientAcquisition: 'Klant Acquisitie',
      projectsCreated: 'Projecten Gemaakt',
      revenue: 'Omzet',
      count: 'Aantal',
      projectCount: 'Projecten',
      month: 'Maand',
      noData: 'Geen data beschikbaar'
    }
  };

  const t = translations[language];

  // Color palette for charts
  const COLORS = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', 
    '#d084d0', '#ffb347', '#87ceeb', '#dda0dd', '#98fb98'
  ];

  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (dateRange.start) params.append('start_date', dateRange.start);
      if (dateRange.end) params.append('end_date', dateRange.end);

      const response = await fetch(`/api/analytics/overview?${params}`);
      if (!response.ok) throw new Error('Failed to fetch analytics data');
      
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const handleDateRangeChange = () => {
    fetchAnalyticsData();
  };

  const handleExport = async (format = 'pdf') => {
    try {
      const params = new URLSearchParams();
      if (dateRange.start) params.append('start_date', dateRange.start);
      if (dateRange.end) params.append('end_date', dateRange.end);
      params.append('format', format);

      const response = await fetch(`/api/reports/business-summary?${params}`);
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `business_summary_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span>{t.loading}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="p-6">
          <div className="text-center">
            <p className="text-red-600 mb-4">{t.error}: {error}</p>
            <Button onClick={fetchAnalyticsData} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              {t.refresh}
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const overviewMetrics = [
    {
      title: t.totalProjects,
      value: analyticsData.project_performance?.budget_performance?.total_projects || 0,
      icon: Activity,
      color: 'bg-blue-500'
    },
    {
      title: t.totalClients,
      value: analyticsData.client_insights?.retention_metrics?.total_clients || 0,
      icon: Users,
      color: 'bg-green-500'
    },
    {
      title: t.totalRevenue,
      value: `€${(analyticsData.financial_reporting?.financial_summary?.total_budget || 0).toLocaleString()}`,
      icon: DollarSign,
      color: 'bg-yellow-500'
    },
    {
      title: t.avgBudget,
      value: `€${(analyticsData.financial_reporting?.financial_summary?.avg_budget || 0).toLocaleString()}`,
      icon: TrendingUp,
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600">{t.subtitle}</p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Date Range Selector */}
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4" />
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            />
            <span>-</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
              className="border border-gray-300 rounded px-2 py-1 text-sm"
            />
            <Button onClick={handleDateRangeChange} size="sm">
              {t.apply}
            </Button>
          </div>
          
          <Button onClick={fetchAnalyticsData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t.refresh}
          </Button>
          
          <Button onClick={() => handleExport('pdf')} size="sm">
            <Download className="h-4 w-4 mr-2" />
            {t.export}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">{t.overview}</TabsTrigger>
          <TabsTrigger value="plants">{t.plants}</TabsTrigger>
          <TabsTrigger value="projects">{t.projects}</TabsTrigger>
          <TabsTrigger value="clients">{t.clients}</TabsTrigger>
          <TabsTrigger value="financial">{t.financial}</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {overviewMetrics.map((metric, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className={`${metric.color} p-2 rounded-lg`}>
                      <metric.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                      <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Overview Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Project Status */}
            <Card>
              <CardHeader>
                <CardTitle>{t.projectStatus}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.project_performance?.status_distribution || []}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                      label={({status, count}) => `${status} (${count})`}
                    >
                      {(analyticsData.project_performance?.status_distribution || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Monthly Trends */}
            <Card>
              <CardHeader>
                <CardTitle>{t.monthlyTrends}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.financial_reporting?.monthly_revenue || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [`€${value.toLocaleString()}`, t.revenue]} />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" stroke="#8884d8" name={t.revenue} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Plant Analytics Tab */}
        <TabsContent value="plants" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Popular Plants */}
            <Card>
              <CardHeader>
                <CardTitle>{t.popularPlants}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.plant_usage?.popular_plants?.slice(0, 8) || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="project_count" fill="#82ca9d" name={t.projectCount} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Plant Categories */}
            <Card>
              <CardHeader>
                <CardTitle>{t.plantCategories}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.plant_usage?.category_distribution || []}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="project_count"
                      label={({category, project_count}) => `${category} (${project_count})`}
                    >
                      {(analyticsData.plant_usage?.category_distribution || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Plant Usage Trends */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>{t.plantUsageOverTime}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.plant_usage?.usage_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="projects_with_plants" stroke="#8884d8" name={t.projectCount} />
                    <Line type="monotone" dataKey="total_plants_used" stroke="#82ca9d" name="Total Plants" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Project Performance Tab */}
        <TabsContent value="projects" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Project Types */}
            <Card>
              <CardHeader>
                <CardTitle>Project Types</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.project_performance?.type_distribution || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="project_type" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#ffc658" name={t.count} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Project Creation Trends */}
            <Card>
              <CardHeader>
                <CardTitle>{t.projectsCreated}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.project_performance?.creation_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="projects_created" stroke="#ff7300" name={t.projectsCreated} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Client Insights Tab */}
        <TabsContent value="clients" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Client Types */}
            <Card>
              <CardHeader>
                <CardTitle>{t.clientTypes}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.client_insights?.client_type_distribution || []}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="client_count"
                      label={({client_type, client_count}) => `${client_type} (${client_count})`}
                    >
                      {(analyticsData.client_insights?.client_type_distribution || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Client Acquisition */}
            <Card>
              <CardHeader>
                <CardTitle>{t.clientAcquisition}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.client_insights?.acquisition_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="new_clients" stroke="#8dd1e1" name="New Clients" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Top Clients */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Top Clients</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {(analyticsData.client_insights?.top_clients || []).slice(0, 5).map((client, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{client.name}</p>
                        <p className="text-sm text-gray-600">{client.client_type}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{client.project_count} projects</p>
                        <p className="text-sm text-gray-600">€{client.total_budget.toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Financial Tab */}
        <TabsContent value="financial" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue by Type */}
            <Card>
              <CardHeader>
                <CardTitle>{t.revenueByType}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.financial_reporting?.revenue_by_type || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="project_type" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`€${value.toLocaleString()}`, t.revenue]} />
                    <Bar dataKey="revenue" fill="#d084d0" name={t.revenue} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Budget Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>{t.budgetDistribution}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.financial_reporting?.budget_distribution || []}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                      label={({range, count}) => `${range} (${count})`}
                    >
                      {(analyticsData.financial_reporting?.budget_distribution || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Monthly Revenue */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Monthly Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.financial_reporting?.monthly_revenue || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`€${value.toLocaleString()}`, t.revenue]} />
                    <Legend />
                    <Bar dataKey="revenue" fill="#ffb347" name={t.revenue} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReportingDashboard;