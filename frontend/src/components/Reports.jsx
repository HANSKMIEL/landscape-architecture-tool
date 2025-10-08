import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  FileText,
  TrendingUp,
  Users,
  DollarSign,
  BarChart3,
  RefreshCw,
  Filter,
  Loader2
} from 'lucide-react';
import ApiService from '../services/api';
import { useLanguage } from '../i18n/LanguageProvider';

const chartColors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316'];

const translationDefaults = {
  title: 'Reports',
  subtitle: 'Generate comprehensive reports and analytics',
  exportCSV: 'Export CSV',
  generatePDF: 'Generate PDF',
  generating: 'Generating...',
  filters: 'Filters',
  startDate: 'Start Date',
  endDate: 'End Date',
  client: 'Client',
  selectClient: 'Select client...',
  refresh: 'Refresh',
  loading: 'Loading...',
  noData: 'No data available',
  errorLoading: 'Error Loading Reports',
  tryAgain: 'Try Again',
  generated: 'Report generated successfully',
  error: 'Error generating report',
  exported: 'Data exported successfully',
  exportError: 'Error exporting data',
  noDataExport: 'No data available for export',
  yes: 'Yes',
  no: 'No',
  metrics: {
    projects: 'Projects',
    revenue: 'Revenue'
  },
  types: {
    overview: 'Business Overview',
    clients: 'Client Analysis',
    projects: 'Project Performance',
    plants: 'Plant Analytics',
    financial: 'Financial Summary'
  },
  monthlyTrends: 'Monthly Trends',
  projectStatus: 'Project Status Distribution',
  topClientsByProjects: 'Top Clients by Projects',
  topClientsByBudget: 'Top Clients by Budget',
  totalProjects: 'Total Projects',
  totalBudget: 'Total Budget',
  averageBudget: 'Average Budget',
  projectStatusDistribution: 'Project Status Distribution',
  monthlyProjectDistribution: 'Monthly Project Distribution',
  totalPlants: 'Total Plants',
  nativePlants: 'Native Plants',
  nativePercentage: 'Native %',
  plantCategoryDistribution: 'Plant Category Distribution',
  totalRevenue: 'Total Revenue',
  completedProjects: 'Completed Projects',
  averageProjectValue: 'Average Project Value',
  monthlyRevenue: 'Monthly Revenue'
};

const getTranslationDefault = (path) =>
  path.split('.').reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults);

const formatCurrency = (value) => `€${Number(value ?? 0).toLocaleString()}`;

const Reports = () => {
  const { t } = useLanguage();

  const translate = useCallback(
    (key) => t(`reports.${key}`, getTranslationDefault(key) ?? key),
    [t]
  );

  const translateCommon = useCallback(
    (key, fallback) => t(`common.${key}`, fallback ?? key),
    [t]
  );

  const translateProjectStatus = useCallback(
    (status, fallback) => t(`projects.statuses.${status}`, fallback ?? status),
    [t]
  );

  const translatePlantCategory = useCallback(
    (category, fallback) => t(`plants.categories.${category}`, fallback ?? category),
    [t]
  );

  const [analyticsData, setAnalyticsData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedReportType, setSelectedReportType] = useState('overview');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });
  const [filters, setFilters] = useState({
    client: '',
    project: '',
    supplier: '',
    category: ''
  });
  const [generatingReport, setGeneratingReport] = useState(false);

  const reportTypes = useMemo(
    () => [
      { id: 'overview', label: translate('types.overview'), icon: BarChart3 },
      { id: 'clients', label: translate('types.clients'), icon: Users },
      { id: 'projects', label: translate('types.projects'), icon: TrendingUp },
      { id: 'plants', label: translate('types.plants'), icon: FileText },
      { id: 'financial', label: translate('types.financial'), icon: DollarSign }
    ],
    [translate]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      exportCsv: translate('exportCSV'),
      generatePdf: translate('generatePDF'),
      generating: translate('generating'),
      filters: translate('filters'),
      startDate: translate('startDate'),
      endDate: translate('endDate'),
      client: translate('client'),
      selectClient: translate('selectClient'),
      refresh: translate('refresh'),
      loading: translate('loading'),
      noData: translate('noData'),
      errorLoading: translate('errorLoading'),
      tryAgain: translateCommon('tryAgain', translationDefaults.tryAgain),
      monthlyTrends: translate('monthlyTrends'),
      projectStatus: translate('projectStatus'),
      topClientsByProjects: translate('topClientsByProjects'),
      topClientsByBudget: translate('topClientsByBudget'),
      totalProjects: translate('totalProjects'),
      totalBudget: translate('totalBudget'),
      averageBudget: translate('averageBudget'),
      projectStatusDistribution: translate('projectStatusDistribution'),
      monthlyProjectDistribution: translate('monthlyProjectDistribution'),
      totalPlants: translate('totalPlants'),
      nativePlants: translate('nativePlants'),
      nativePercentage: translate('nativePercentage'),
      plantCategoryDistribution: translate('plantCategoryDistribution'),
      totalRevenue: translate('totalRevenue'),
      completedProjects: translate('completedProjects'),
      averageProjectValue: translate('averageProjectValue'),
      monthlyRevenue: translate('monthlyRevenue'),
      yes: translate('yes'),
      no: translate('no'),
      generated: translate('generated'),
      reportError: translate('error'),
      exported: translate('exported'),
      exportError: translate('exportError'),
      csvNoData: translate('noDataExport'),
      projectsLabel: translate('metrics.projects'),
      revenueLabel: translate('metrics.revenue')
    }),
    [translate, translateCommon]
  );

  const formatMonthLabel = useCallback(
    (month) => new Date(`${month}-01`).toLocaleDateString('nl-NL', { month: 'short', year: 'numeric' }),
    []
  );

  const generateMockMonthlyData = useCallback(() => {
    const months = [];
    for (let i = 11; i >= 0; i -= 1) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      months.push({
        month: date.toLocaleDateString('nl-NL', { month: 'short', year: 'numeric' }),
        projects: Math.floor(Math.random() * 10) + 1,
        revenue: Math.floor(Math.random() * 50000) + 10000
      });
    }
    return months;
  }, []);

  const generateMockStatusData = useCallback(
    () => [
      { name: translateProjectStatus('planning', 'Planning'), value: 15 },
      { name: translateProjectStatus('design', 'Design'), value: 25 },
      { name: translateProjectStatus('construction', 'Construction'), value: 30 },
      { name: translateProjectStatus('completed', 'Completed'), value: 20 },
      { name: translateProjectStatus('on_hold', 'On Hold'), value: 10 }
    ],
    [translateProjectStatus]
  );

  const loadOverviewData = useCallback(async () => {
    const [stats, clientData, projectData, plantData] = await Promise.all([
      ApiService.getDashboardStats(),
      ApiService.getClients({ limit: 10 }),
      ApiService.getProjects({ limit: 10 }),
      ApiService.getPlants({ limit: 10 })
    ]);

    return {
      stats,
      topClients: clientData.clients?.slice(0, 5) ?? [],
      recentProjects: projectData.projects?.slice(0, 5) ?? [],
      popularPlants: plantData.plants?.slice(0, 5) ?? [],
      monthlyData: generateMockMonthlyData(),
      statusDistribution: generateMockStatusData()
    };
  }, [generateMockMonthlyData, generateMockStatusData]);

  const loadClientAnalytics = useCallback(async () => {
    const [clientData, projectData] = await Promise.all([
      ApiService.getClients(),
      ApiService.getProjects()
    ]);

    const clientProjectCounts = {};
    projectData.projects?.forEach((project) => {
      if (project.client_id) {
        clientProjectCounts[project.client_id] = (clientProjectCounts[project.client_id] || 0) + 1;
      }
    });

    const clientAnalytics = (clientData.clients ?? []).map((client) => {
      const relatedProjects = (projectData.projects ?? []).filter((project) => project.client_id === client.id);
      const totalBudget = relatedProjects.reduce((sum, project) => sum + (Number.parseFloat(project.budget) || 0), 0);
      return {
        ...client,
        projectCount: clientProjectCounts[client.id] || 0,
        totalBudget
      };
    });

    return {
      clients: clientAnalytics,
      topClientsByProjects: [...clientAnalytics].sort((a, b) => b.projectCount - a.projectCount).slice(0, 10),
      topClientsByBudget: [...clientAnalytics].sort((a, b) => b.totalBudget - a.totalBudget).slice(0, 10)
    };
  }, []);

  const loadProjectAnalytics = useCallback(async () => {
    const projectResponse = await ApiService.getProjects();
    const projects = projectResponse.projects ?? [];

    const statusCounts = {};
    const monthlyProjects = {};
    let totalBudget = 0;

    projects.forEach((project) => {
      const status = project.status || 'unknown';
      statusCounts[status] = (statusCounts[status] || 0) + 1;

      if (project.start_date) {
        const month = new Date(project.start_date).toISOString().slice(0, 7);
        monthlyProjects[month] = (monthlyProjects[month] || 0) + 1;
      }

      totalBudget += Number.parseFloat(project.budget) || 0;
    });

    return {
      projects,
      totalProjects: projects.length,
      totalBudget,
      averageBudget: projects.length > 0 ? totalBudget / projects.length : 0,
      statusDistribution: Object.entries(statusCounts).map(([status, count]) => ({
        name: translateProjectStatus(status, status),
        value: count
      })),
      monthlyDistribution: Object.entries(monthlyProjects)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([month, count]) => ({
          month: formatMonthLabel(month),
          projects: count
        }))
    };
  }, [formatMonthLabel, translateProjectStatus]);

  const loadPlantAnalytics = useCallback(async () => {
    const plantResponse = await ApiService.getPlants();
    const plants = plantResponse.plants ?? [];

    const categoryCounts = {};
    const supplierCounts = {};

    plants.forEach((plant) => {
      const category = plant.category || 'other';
      categoryCounts[category] = (categoryCounts[category] || 0) + 1;

      if (plant.supplier_id) {
        supplierCounts[plant.supplier_id] = (supplierCounts[plant.supplier_id] || 0) + 1;
      }
    });

    const nativeCount = plants.filter((plant) => plant.native).length;

    return {
      plants,
      totalPlants: plants.length,
      categoryDistribution: Object.entries(categoryCounts).map(([category, count]) => ({
        name: translatePlantCategory(category, category),
        value: count
      })),
      supplierDistribution: supplierCounts,
      topPlantsByPrice: plants
        .filter((plant) => plant.price)
        .sort((a, b) => Number.parseFloat(b.price) - Number.parseFloat(a.price))
        .slice(0, 10),
      nativePlants: nativeCount,
      nativePercentage: plants.length > 0 ? (nativeCount / plants.length) * 100 : 0
    };
  }, [translatePlantCategory]);

  const loadFinancialData = useCallback(async () => {
    const projectResponse = await ApiService.getProjects();
    const projects = projectResponse.projects ?? [];

    const monthlyRevenue = {};
    let totalRevenue = 0;
    let completedProjects = 0;

    projects.forEach((project) => {
      const budget = Number.parseFloat(project.budget) || 0;
      totalRevenue += budget;

      if (project.status === 'completed') {
        completedProjects += 1;

        if (project.end_date) {
          const month = new Date(project.end_date).toISOString().slice(0, 7);
          monthlyRevenue[month] = (monthlyRevenue[month] || 0) + budget;
        }
      }
    });

    return {
      totalRevenue,
      completedProjects,
      averageProjectValue: projects.length > 0 ? totalRevenue / projects.length : 0,
      monthlyRevenue: Object.entries(monthlyRevenue)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([month, revenue]) => ({
          month: formatMonthLabel(month),
          revenue
        }))
    };
  }, [formatMonthLabel]);

  const loadAnalyticsData = useCallback(async () => {
    setLoading(true);
    setError('');

    const params = {
      start_date: dateRange.start,
      end_date: dateRange.end,
      ...filters
    };

    try {
      let data = {};

      switch (selectedReportType) {
        case 'clients':
          data = await loadClientAnalytics(params);
          break;
        case 'projects':
          data = await loadProjectAnalytics(params);
          break;
        case 'plants':
          data = await loadPlantAnalytics(params);
          break;
        case 'financial':
          data = await loadFinancialData(params);
          break;
        case 'overview':
        default:
          data = await loadOverviewData(params);
          break;
      }

      setAnalyticsData(data);
    } catch (err) {
      console.error('Error loading analytics data:', err);
      setError(err?.message ?? uiText.errorLoading);
    } finally {
      setLoading(false);
    }
  }, [
    dateRange,
    filters,
    loadClientAnalytics,
    loadFinancialData,
    loadOverviewData,
    loadPlantAnalytics,
    loadProjectAnalytics,
    selectedReportType,
    uiText.errorLoading
  ]);

  useEffect(() => {
    loadAnalyticsData();
  }, [loadAnalyticsData]);

  const renderChart = useCallback(
    (data, type) => {
      if (!data || data.length === 0) {
        return (
          <div className="flex items-center justify-center h-64 text-gray-500">
            {uiText.noData}
          </div>
        );
      }

      if (type === 'bar') {
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [value, uiText.projectsLabel]} />
              <Legend />
              <Bar dataKey="value" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        );
      }

      if (type === 'line') {
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip
                formatter={(value, key) =>
                  key === 'revenue'
                    ? [formatCurrency(value), uiText.revenueLabel]
                    : [value, uiText.projectsLabel]
                }
              />
              <Legend />
              <Line type="monotone" dataKey="projects" stroke="#10b981" strokeWidth={2} name={uiText.projectsLabel} />
              <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name={uiText.revenueLabel} />
            </LineChart>
          </ResponsiveContainer>
        );
      }

      if (type === 'pie') {
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
              <Tooltip formatter={(value) => [value, uiText.projectsLabel]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );
      }

      return null;
    },
    [uiText.noData, uiText.projectsLabel, uiText.revenueLabel]
  );

  const generatePDFReport = useCallback(async () => {
    setGeneratingReport(true);

    const reportPayload = {
      type: selectedReportType,
      dateRange,
      filters,
      data: analyticsData,
      language: 'nl',
      timestamp: new Date().toISOString()
    };

    try {
      const response = await fetch('/api/reports/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportPayload)
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF report');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `landscape-report-${selectedReportType}-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(anchor);

      window.alert(uiText.generated);
    } catch (err) {
      console.error('Error generating PDF report:', err);
      window.alert(`${uiText.reportError}: ${err.message}`);
    } finally {
      setGeneratingReport(false);
    }
  }, [analyticsData, dateRange, filters, selectedReportType, uiText.generated, uiText.reportError]);

  const exportCSV = useCallback(() => {
    try {
      let csvData = [];

      switch (selectedReportType) {
        case 'clients':
          csvData = (analyticsData.clients ?? []).map((client) => ({
            Name: client.name,
            Email: client.email,
            Phone: client.phone,
            City: client.city,
            Projects: client.projectCount || 0,
            'Total Budget': client.totalBudget || 0
          }));
          break;
        case 'projects':
          csvData = (analyticsData.projects ?? []).map((project) => ({
            Name: project.name,
            Status: project.status,
            Budget: project.budget,
            'Start Date': project.start_date,
            'End Date': project.end_date
          }));
          break;
        case 'plants':
          csvData = (analyticsData.plants ?? []).map((plant) => ({
            'Scientific Name': plant.name,
            'Common Name': plant.common_name,
            Category: plant.category,
            Price: plant.price,
            Native: plant.native ? uiText.yes : uiText.no
          }));
          break;
        default:
          csvData = [];
          break;
      }

      if (csvData.length === 0) {
        window.alert(uiText.csvNoData);
        return;
      }

      const headers = Object.keys(csvData[0]);
      const csvContent = [
        headers.join(','),
        ...csvData.map((row) => headers.map((header) => `"${row[header] ?? ''}"`).join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `landscape-data-${selectedReportType}-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(anchor);
      anchor.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(anchor);

      window.alert(uiText.exported);
    } catch (err) {
      console.error('Error exporting CSV:', err);
      window.alert(`${uiText.exportError}: ${err.message}`);
    }
  }, [analyticsData.clients, analyticsData.plants, analyticsData.projects, selectedReportType, uiText.csvNoData, uiText.exportError, uiText.exported, uiText.no, uiText.yes]);

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{uiText.title}</h1>
            <p className="text-gray-600">{uiText.subtitle}</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-12">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 mx-auto bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-red-800">{uiText.errorLoading}</h2>
              <p className="text-red-600">{error}</p>
              <Button onClick={loadAnalyticsData} variant="destructive">
                {uiText.tryAgain}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{uiText.title}</h1>
          <p className="text-gray-600">{uiText.subtitle}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={exportCSV} className="flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>{uiText.exportCsv}</span>
          </Button>
          <Button onClick={generatePDFReport} disabled={generatingReport} className="flex items-center space-x-2">
            {generatingReport ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
            <span>{generatingReport ? uiText.generating : uiText.generatePdf}</span>
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            {uiText.filters}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">{uiText.startDate}</label>
              <Input
                type="date"
                value={dateRange.start}
                onChange={(event) => setDateRange((prev) => ({ ...prev, start: event.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{uiText.endDate}</label>
              <Input
                type="date"
                value={dateRange.end}
                onChange={(event) => setDateRange((prev) => ({ ...prev, end: event.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">{uiText.client}</label>
              <Input
                placeholder={uiText.selectClient}
                value={filters.client}
                onChange={(event) => setFilters((prev) => ({ ...prev, client: event.target.value }))}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={loadAnalyticsData} disabled={loading} className="flex items-center">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                {uiText.refresh}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

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
  );
};

export default Reports;
