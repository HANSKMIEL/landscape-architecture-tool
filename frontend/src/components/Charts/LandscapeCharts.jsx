import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts'

// Color palette for landscape architecture theme
const __COLORS = {
  primary: '#22c55e',    // Green
  secondary: '#3b82f6',  // Blue
  accent: '#f59e0b',     // Amber
  success: '#10b981',    // Emerald
  warning: '#f97316',    // Orange
  danger: '#ef4444',     // Red
  info: '#06b6d4',       // Cyan
  purple: '#8b5cf6'      // Purple
}

const CHART_COLORS = [
  COLORS.primary,
  COLORS.secondary,
  COLORS.accent,
  COLORS.success,
  COLORS.warning,
  COLORS.info,
  COLORS.purple,
  COLORS.danger
]

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-medium text-gray-900">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

// Bar Chart Component
export const LandscapeBarChart = ({ data, dataKey, xAxisKey, title, height = 300 }) => {
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey={xAxisKey} 
            stroke="#6b7280"
            fontSize={12}
          />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar 
            dataKey={dataKey} 
            fill={COLORS.primary}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Pie Chart Component
export const LandscapePieChart = ({ data, dataKey, title, height = 300 }) => {
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey={dataKey}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

// Line Chart Component
export const LandscapeLineChart = ({ data, dataKey, xAxisKey, title, height = 300 }) => {
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey={xAxisKey} 
            stroke="#6b7280"
            fontSize={12}
          />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={COLORS.primary}
            strokeWidth={3}
            dot={{ fill: COLORS.primary, strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: COLORS.primary, strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// Area Chart Component
export const LandscapeAreaChart = ({ data, dataKey, xAxisKey, title, height = 300 }) => {
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey={xAxisKey} 
            stroke="#6b7280"
            fontSize={12}
          />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area 
            type="monotone" 
            dataKey={dataKey} 
            stroke={COLORS.primary}
            fill={COLORS.primary}
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// Multi-data Bar Chart Component
export const LandscapeMultiBarChart = ({ data, dataKeys, xAxisKey, title, height = 300 }) => {
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey={xAxisKey} 
            stroke="#6b7280"
            fontSize={12}
          />
          <YAxis stroke="#6b7280" fontSize={12} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {dataKeys.map((key, index) => (
            <Bar 
              key={key}
              dataKey={key} 
              fill={CHART_COLORS[index % CHART_COLORS.length]}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// Dashboard Stats Chart Component
export const DashboardStatsChart = ({ stats }) => {
  // Transform stats data for charts
  const chartData = [
    { name: 'Leveranciers', value: stats?.suppliers || 0, color: COLORS.primary },
    { name: 'Planten', value: stats?.plants || 0, color: COLORS.secondary },
    { name: 'Producten', value: stats?.products || 0, color: COLORS.accent },
    { name: 'Klanten', value: stats?.clients || 0, color: COLORS.success },
    { name: 'Projecten', value: stats?.projects || 0, color: COLORS.warning }
  ]

  const monthlyData = [
    { month: 'Jan', revenue: 12000, projects: 3 },
    { month: 'Feb', revenue: 15000, projects: 4 },
    { month: 'Mar', revenue: 18000, projects: 5 },
    { month: 'Apr', revenue: 22000, projects: 6 },
    { month: 'Mei', revenue: 25000, projects: 7 },
    { month: 'Jun', revenue: 28000, projects: 8 }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Overview Pie Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <LandscapePieChart 
          data={chartData}
          dataKey="value"
          nameKey="name"
          title="Overzicht Database"
          height={250}
        />
      </div>

      {/* Monthly Revenue Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <LandscapeAreaChart 
          data={monthlyData}
          dataKey="revenue"
          xAxisKey="month"
          title="Maandelijkse Omzet (€)"
          height={250}
        />
      </div>

      {/* Projects Bar Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm border lg:col-span-2">
        <LandscapeMultiBarChart 
          data={monthlyData}
          dataKeys={['revenue', 'projects']}
          xAxisKey="month"
          title="Omzet vs Projecten per Maand"
          height={300}
        />
      </div>
    </div>
  )
}

export default {
  LandscapeBarChart,
  LandscapePieChart,
  LandscapeLineChart,
  LandscapeAreaChart,
  LandscapeMultiBarChart,
  DashboardStatsChart
}

