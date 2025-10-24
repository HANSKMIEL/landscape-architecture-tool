import React, { useCallback, useMemo, useState } from 'react'
import { useLanguage } from '../i18n/LanguageProvider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Settings as SettingsIcon,
  Shield,
  Palette,
  BarChart3,
  Brain,
  Archive,
  Link
} from 'lucide-react'
import AppearanceSettings from './settings/AppearanceSettings'
import APISettings from './settings/APISettings'
import AISettings from './settings/AISettings'
import BulkDataSettings from './settings/BulkDataSettings'
import ReportSettings from './settings/ReportSettings'

const translationDefaults = {
  page: {
    title: 'Settings',
    subtitle: 'Configure your landscape architecture application preferences'
  },
  tabs: {
    appearance: {
      label: 'Appearance',
      description: 'Customize colors, fonts, and branding'
    },
    bulkData: {
      label: 'Bulk Data Management',
      description: 'Import, export, and data processing settings'
    },
    ai: {
      label: 'AI Assistant',
      description: 'Configure intelligent automation and recommendations'
    },
    apis: {
      label: 'API Integrations',
      description: 'Connect with external software and services'
    },
    reports: {
      label: 'Report Generation',
      description: 'Configure report templates and automation'
    },
    security: {
      label: 'Security & Access',
      description: 'Manage user permissions and security settings'
    }
  },
  states: {
    comingSoon: 'Coming Soon',
    sectionAvailableSoon: 'This section will be available soon.'
  }
}

const getTranslationDefault = (path) =>
  path
    .split('.')
    .reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults)

const Settings = () => {
  const { t } = useLanguage()
  const [activeTab, setActiveTab] = useState('appearance')

  const translate = useCallback(
    (key) => t(`settings.overview.${key}`, getTranslationDefault(key) ?? key),
    [t]
  )

  const uiText = useMemo(
    () => ({
      title: translate('page.title'),
      subtitle: translate('page.subtitle'),
      tabs: {
        appearance: {
          label: translate('tabs.appearance.label'),
          description: translate('tabs.appearance.description')
        },
        bulkData: {
          label: translate('tabs.bulkData.label'),
          description: translate('tabs.bulkData.description')
        },
        ai: {
          label: translate('tabs.ai.label'),
          description: translate('tabs.ai.description')
        },
        apis: {
          label: translate('tabs.apis.label'),
          description: translate('tabs.apis.description')
        },
        reports: {
          label: translate('tabs.reports.label'),
          description: translate('tabs.reports.description')
        },
        security: {
          label: translate('tabs.security.label'),
          description: translate('tabs.security.description')
        }
      },
      states: {
        comingSoon: translate('states.comingSoon'),
        sectionAvailableSoon: translate('states.sectionAvailableSoon')
      }
    }),
    [translate]
  )

  const settingsTabs = useMemo(
    () => [
      {
        id: 'appearance',
        label: uiText.tabs.appearance.label,
        description: uiText.tabs.appearance.description,
        icon: Palette,
        enabled: true
      },
      {
        id: 'bulk-data',
        label: uiText.tabs.bulkData.label,
        description: uiText.tabs.bulkData.description,
        icon: Archive,
        enabled: true
      },
      {
        id: 'ai',
        label: uiText.tabs.ai.label,
        description: uiText.tabs.ai.description,
        icon: Brain,
        enabled: true
      },
      {
        id: 'apis',
        label: uiText.tabs.apis.label,
        description: uiText.tabs.apis.description,
        icon: Link,
        enabled: true
      },
      {
        id: 'reports',
        label: uiText.tabs.reports.label,
        description: uiText.tabs.reports.description,
        icon: BarChart3,
        enabled: true
      },
      {
        id: 'security',
        label: uiText.tabs.security.label,
        description: uiText.tabs.security.description,
        icon: Shield,
        enabled: false
      }
    ],
    [uiText]
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'appearance':
        return <AppearanceSettings />
      case 'bulk-data':
        return <BulkDataSettings />
      case 'ai':
        return <AISettings />
      case 'apis':
        return <APISettings />
      case 'reports':
        return <ReportSettings />
      case 'security':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-600" />
                {uiText.tabs.security.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="py-8 text-center">
                <Shield className="mx-auto mb-4 h-16 w-16 text-gray-400" />
                <h3 className="mb-2 text-lg font-semibold text-gray-900">{uiText.states.comingSoon}</h3>
                <p className="text-gray-500">{uiText.tabs.security.description}</p>
              </div>
            </CardContent>
          </Card>
        )
      default:
        return (
          <Card>
            <CardContent className="p-12">
              <div className="text-center">
                <SettingsIcon className="mx-auto mb-4 h-16 w-16 text-gray-400" />
                <h3 className="mb-2 text-lg font-semibold text-gray-900">{uiText.states.comingSoon}</h3>
                <p className="text-gray-500">{uiText.states.sectionAvailableSoon}</p>
              </div>
            </CardContent>
          </Card>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{uiText.title}</h1>
        <p className="text-gray-600">{uiText.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="p-4">
              <nav className="space-y-2">
                {settingsTabs.map((tab) => {
                  const IconComponent = tab.icon
                  const isActive = activeTab === tab.id

                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full rounded-lg border p-3 text-left transition-colors ${isActive
                          ? 'border-blue-200 bg-blue-100 text-blue-700'
                          : tab.enabled
                            ? 'border-gray-200 bg-white hover:bg-gray-50'
                            : 'cursor-not-allowed border-gray-100 bg-gray-50 text-gray-400'
                        }`}
                      disabled={!tab.enabled}
                    >
                      <div className="flex items-center gap-3">
                        <IconComponent
                          className={`h-5 w-5 ${isActive ? 'text-blue-600' : tab.enabled ? 'text-gray-600' : 'text-gray-400'
                            }`}
                        />
                        <div>
                          <div className="font-medium">{tab.label}</div>
                          <div className="text-xs text-gray-500">{tab.description}</div>
                        </div>
                      </div>
                      {!tab.enabled && (
                        <div className="ml-8 mt-1 text-xs text-gray-400">{uiText.states.comingSoon}</div>
                      )}
                    </button>
                  )
                })}
              </nav>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-3">{renderTabContent()}</div>
      </div>
    </div>
  )
}

export default Settings

