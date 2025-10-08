import { useLanguage } from "../i18n/LanguageProvider";
import React, { useState, useEffect, useMemo, useCallback } from 'react';
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
  Download, 
  TrendingUp, 
  Users, 
  DollarSign, 
  BarChart3,
  RefreshCw,
  FileText
} from 'lucide-react';

const translationDefaults = {
  title: 'Advanced Reporting Dashboard',
  subtitle: 'Comprehensive business intelligence and analytics',
  overview: 'Overview',
  plantAnalytics: 'Plant Analytics',
  projectPerformance: 'Project Performance',
  clientInsights: 'Client Insights',
  financialReports: 'Financial Reports',
  refresh: 'Refresh Data',
  export: 'Export Report',
  loading: 'Loading analytics...',
  error: 'Error loading data',
  noData: 'No data available for the selected period',
  mostUsedPlants: 'Most Used Plants',
  categoryDistribution: 'Plant Category Distribution',
  projectStatusDistribution: 'Project Status Distribution',
  budgetAnalysis: 'Budget Analysis',
  revenueTracking: 'Revenue Tracking',
  clientPerformance: 'Top Clients',
  projectTimeline: 'Project Timeline Analysis',
  month: 'Month',
  projects: 'Projects',
  revenue: 'Revenue',
  budget: 'Budget',
  count: 'Count',
  totalBudget: 'Total Budget',
  avgBudget: 'Average Budget',
  projectCount: 'Total Projects',
  topClients: 'Top Clients by Project Count',
  activeClients: 'Active Clients',
  durationDays: 'Duration (days)',
  totalValue: 'Total Value',
  projectTypeProfitability: 'Project Type Profitability'
};

const ReportingDashboard = () => {
  const { t } = useLanguage();

  const translate = useCallback(
    (key) => t(`reportingDashboard.${key}`, translationDefaults[key] ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      overview: translate('overview'),
      plantAnalytics: translate('plantAnalytics'),
      projectPerformance: translate('projectPerformance'),
      clientInsights: translate('clientInsights'),
      financialReports: translate('financialReports'),
      refresh: translate('refresh'),
      export: translate('export'),
      loading: translate('loading'),
      error: translate('error'),
      noData: translate('noData'),
      mostUsedPlants: translate('mostUsedPlants'),
      categoryDistribution: translate('categoryDistribution'),
      projectStatusDistribution: translate('projectStatusDistribution'),
      budgetAnalysis: translate('budgetAnalysis'),
      revenueTracking: translate('revenueTracking'),
      clientPerformance: translate('clientPerformance'),
      projectTimeline: translate('projectTimeline'),
      month: translate('month'),
      projects: translate('projects'),
      revenue: translate('revenue'),
      budget: translate('budget'),
      count: translate('count'),
      totalBudget: translate('totalBudget'),
      avgBudget: translate('avgBudget'),
      projectCount: translate('projectCount'),
      topClients: translate('topClients'),
      activeClients: translate('activeClients'),
      durationDays: translate('durationDays'),
      totalValue: translate('totalValue'),
      projectTypeProfitability: translate('projectTypeProfitability')
    }),
    [translate]
  );

  const [analyticsData, setAnalyticsData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  // Color palette for charts
  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#ff00ff'];

  const loadAnalyticsData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [plantUsage, projectPerformance, clientInsights, financial] = await Promise.all([
        fetch(`/api/analytics/plant-usage?start_date=${dateRange.start}&end_date=${dateRange.end}`).then((response) => response.json()),
        fetch('/api/analytics/project-performance').then((response) => response.json()),
        fetch('/api/analytics/client-insights').then((response) => response.json()),
        fetch(`/api/analytics/financial?start_date=${dateRange.start}&end_date=${dateRange.end}`).then((response) => response.json())
      ]);

      setAnalyticsData({
        plantUsage,
        projectPerformance,
        clientInsights,
        financial
      });
    } catch (err) {
      console.error('Error loading analytics:', err);
      setAnalyticsData({});
      setError(err?.message ?? uiText.error);
    } finally {
      setLoading(false);
    }
  }, [dateRange.end, dateRange.start, uiText.error]);

  useEffect(() => {
    loadAnalyticsData();
  }, [loadAnalyticsData]);

  const exportToPDF = async () => {
    try {
      const response = await fetch('/api/reports/business-summary?format=pdf', {
        method: 'GET'
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `business_report_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error exporting PDF:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">{uiText.loading}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{uiText.title}</h1>
          <p className="text-gray-600">{uiText.subtitle}</p>
        </div>
        <div className="flex space-x-2">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          <Button onClick={loadAnalyticsData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {uiText.refresh}
          </Button>
          <Button onClick={exportToPDF}>
            <Download className="h-4 w-4 mr-2" />
            {uiText.export}
          </Button>
        </div>
      </div>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 text-red-800">
          {error || uiText.error}
        </div>
      ) : null}

      {/* Dashboard Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>{uiText.overview}</span>
          </TabsTrigger>
          <TabsTrigger value="plants" className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>{uiText.plantAnalytics}</span>
          </TabsTrigger>
          <TabsTrigger value="projects" className="flex items-center space-x-2">
            <FileText className="h-4 w-4" />
            <span>{uiText.projectPerformance}</span>
          </TabsTrigger>
          <TabsTrigger value="clients" className="flex items-center space-x-2">
            <Users className="h-4 w-4" />
            <span>{uiText.clientInsights}</span>
          </TabsTrigger>
          <TabsTrigger value="financial" className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4" />
            <span>{uiText.financialReports}</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{uiText.totalBudget}</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  €{Number(analyticsData.financial?.revenue_summary?.total_revenue ?? 0).toLocaleString()}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{uiText.projectCount}</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData.projectPerformance?.budget_analysis?.project_count || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{uiText.avgBudget}</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  €{Math.round(analyticsData.projectPerformance?.budget_analysis?.avg_budget || 0).toLocaleString()}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{uiText.activeClients}</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analyticsData.clientInsights?.total_clients || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Overview Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{uiText.projectStatusDistribution}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(analyticsData.projectPerformance?.status_distribution || {}).map(([status, count]) => ({
                        name: status,
                        value: count
                      }))}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label
                    >
                      {Object.entries(analyticsData.projectPerformance?.status_distribution || {}).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{uiText.revenueTracking}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.financial?.revenue_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`€${Number(value ?? 0).toLocaleString()}`, uiText.revenue]} />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Plant Analytics Tab */}
        <TabsContent value="plants" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{uiText.mostUsedPlants}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.plantUsage?.most_used_plants?.slice(0, 10) || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="project_count" fill="#82ca9d" name={uiText.projects} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{uiText.categoryDistribution}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.plantUsage?.category_distribution || []}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#ffc658"
                      dataKey="project_count"
                      label
                    >
                      {(analyticsData.plantUsage?.category_distribution || []).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Project Performance Tab */}
        <TabsContent value="projects" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{uiText.budgetAnalysis}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">{uiText.totalBudget}</p>
                      <p className="text-xl font-bold">€{analyticsData.projectPerformance?.budget_analysis?.total_budget?.toLocaleString() || '0'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">{uiText.avgBudget}</p>
                      <p className="text-xl font-bold">€{Math.round(analyticsData.projectPerformance?.budget_analysis?.avg_budget || 0).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{uiText.projectTimeline}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.projectPerformance?.timeline_analysis || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="duration_days" fill="#ff7300" name={uiText.durationDays} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Client Insights Tab */}
        <TabsContent value="clients" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{uiText.topClients}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={analyticsData.clientInsights?.top_clients?.slice(0, 10) || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'project_count' ? value : `€${Number(value ?? 0).toLocaleString()}`, 
                    name === 'project_count' ? uiText.projects : uiText.totalValue
                  ]} />
                  <Legend />
                  <Bar dataKey="project_count" fill="#8884d8" name={uiText.projects} />
                  <Bar dataKey="total_value" fill="#82ca9d" name={uiText.totalValue} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Financial Reports Tab */}
        <TabsContent value="financial" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>{uiText.revenueTracking}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.financial?.revenue_trends || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`€${Number(value ?? 0).toLocaleString()}`, uiText.revenue]} />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{uiText.projectTypeProfitability}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.financial?.profitability_by_type || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="project_type" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`€${Number(value ?? 0).toLocaleString()}`, uiText.revenue]} />
                    <Legend />
                    <Bar dataKey="revenue" fill="#82ca9d" name={uiText.revenue} />
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