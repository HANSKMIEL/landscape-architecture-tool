import React, { useState } from 'react'
import { useLanguage } from '../i18n/LanguageProvider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Settings as SettingsIcon, 
  FileSpreadsheet, 
  Download, 
  Upload, 
  Database,
  Zap,
  Cpu,
  Link,
  Shield,
  Globe,
  Palette,
  BarChart3,
  Brain,
  Archive
} from 'lucide-react'
import ExcelImportManager from './ExcelImportManager'
import AppearanceSettings from './settings/AppearanceSettings'
import APISettings from './settings/APISettings'
import AISettings from './settings/AISettings'
import BulkDataSettings from './settings/BulkDataSettings'
import ReportSettings from './settings/ReportSettings'

const Settings = () => {
  const [__activeTab, set_activeTab] = useState('appearance')

  const __translations = {
    en: {
      title: 'Settings',
      subtitle: 'Configure your landscape architecture application preferences',
      appearance: 'Appearance',
      appearanceDesc: 'Customize colors, fonts, and branding',
      apis: 'API Integrations',
      apisDesc: 'Connect with external software and services',
      ai: 'AI Assistant',
      aiDesc: 'Configure intelligent automation and recommendations',
      bulkData: 'Bulk Data Management',
      bulkDataDesc: 'Import, export, and data processing settings',
      reports: 'Report Generation',
      reportsDesc: 'Configure report templates and automation',
      security: 'Security & Access',
      securityDesc: 'Manage user permissions and security settings',
      comingSoon: 'Coming Soon',
      enabledFeatures: 'Enabled Features',
      futureIntegrations: 'Future Integrations',
      vectorworks: 'Vectorworks CAD Integration',
      vectorworksDesc: 'Direct integration with Vectorworks for design automation',
      crm: 'CRM System Integration', 
      crmDesc: 'Connect with popular CRM systems for client management',
      n8n: 'N8N Workflow Automation',
      n8nDesc: 'Automated workflows for client onboarding and project management',
      photogrammetry: 'Photogrammetry Processing',
      photogrammetryDesc: 'Automated 3D model generation from project photos',
      unreal: 'Unreal Engine Visualization',
      unrealDesc: 'Advanced 3D visualization and virtual reality experiences'
    },
    nl: {
      title: 'Instellingen',
      subtitle: 'Configureer uw landschapsarchitectuur applicatie voorkeuren',
      appearance: 'Uiterlijk',
      appearanceDesc: 'Pas kleuren, lettertypen en branding aan',
      apis: 'API Integraties',
      apisDesc: 'Verbind met externe software en diensten',
      ai: 'AI Assistent',
      aiDesc: 'Configureer intelligente automatisering en aanbevelingen',
      bulkData: 'Bulkgegevensbeheer',
      bulkDataDesc: 'Import, export en gegevensverwerkingsinstellingen',
      reports: 'Rapportage Generatie',
      reportsDesc: 'Configureer rapportsjablonen en automatisering',
      security: 'Beveiliging & Toegang',
      securityDesc: 'Beheer gebruikersrechten en beveiligingsinstellingen',
      comingSoon: 'Binnenkort Beschikbaar',
      enabledFeatures: 'Ingeschakelde Functies',
      futureIntegrations: 'Toekomstige Integraties',
      vectorworks: 'Vectorworks CAD Integratie',
      vectorworksDesc: 'Directe integratie met Vectorworks voor ontwerpautomatisering',
      crm: 'CRM Systeem Integratie',
      crmDesc: 'Verbind met populaire CRM-systemen voor klantbeheer',
      n8n: 'N8N Workflow Automatisering',
      n8nDesc: 'Geautomatiseerde workflows voor klant onboarding en projectbeheer',
      photogrammetry: 'Fotogrammetrie Verwerking',
      photogrammetryDesc: 'Geautomatiseerde 3D-modelgeneratie uit projectfoto\'s',
      unreal: 'Unreal Engine Visualisatie',
      unrealDesc: 'Geavanceerde 3D-visualisatie en virtual reality ervaringen'
    }
  }

  const { t, currentLanguage } = useLanguage()
  const currentTranslations = translations[currentLanguage] || translations.nl

  const settingsTabs = [
    {
      id: 'appearance',
      label: currentTranslations.appearance,
      description: currentTranslations.appearanceDesc,
      icon: Palette,
      enabled: true
    },
    {
      id: 'bulk-data',
      label: currentTranslations.bulkData,
      description: currentTranslations.bulkDataDesc,
      icon: Archive,
      enabled: true
    },
    {
      id: 'ai', 
      label: currentTranslations.ai,
      description: currentTranslations.aiDesc,
      icon: Brain,
      enabled: true
    },
    {
      id: 'apis',
      label: currentTranslations.apis,
      description: currentTranslations.apisDesc,
      icon: Link,
      enabled: true
    },
    {
      id: 'reports',
      label: currentTranslations.reports,
      description: currentTranslations.reportsDesc,
      icon: BarChart3,
      enabled: true
    },
    {
      id: 'security',
      label: currentTranslations.security,
      description: currentTranslations.securityDesc,
      icon: Shield,
      enabled: false
    }
  ]

  const futureIntegrations = [
    {
      name: currentTranslations.vectorworks,
      description: currentTranslations.vectorworksDesc,
      icon: '🏗️',
      category: 'CAD'
    },
    {
      name: currentTranslations.crm,
      description: currentTranslations.crmDesc,
      icon: '👥',
      category: 'Business'
    },
    {
      name: currentTranslations.n8n,
      description: currentTranslations.n8nDesc,
      icon: '⚡',
      category: 'Automation'
    },
    {
      name: currentTranslations.photogrammetry,
      description: currentTranslations.photogrammetryDesc,
      icon: '📸',
      category: 'AI/ML'
    },
    {
      name: currentTranslations.unreal,
      description: currentTranslations.unrealDesc,
      icon: '🎮',
      category: 'Visualization'
    }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'appearance':
        return <AppearanceSettings  />
      
      case 'bulk-data':
        return <BulkDataSettings  />
      
      case 'ai':
        return <AISettings  />
      
      case 'apis':
        return <APISettings  />
      
      case 'reports':
        return <ReportSettings  />
      
      case 'security':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-600" />
                {currentTranslations.security}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{currentTranslations.comingSoon}</h3>
                <p className="text-gray-500 mb-4">{currentTranslations.securityDesc}</p>
              </div>
            </CardContent>
          </Card>
        )
      
      default:
        return (
          <Card>
            <CardContent className="p-12">
              <div className="text-center">
                <SettingsIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('common.comingSoon', 'Coming Soon')}</h3>
                <p className="text-gray-500">{t('settings.sectionAvailableSoon', 'This section will be available soon.')}</p>
              </div>
            </CardContent>
          </Card>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{currentTranslations.title}</h1>
        <p className="text-gray-600">{currentTranslations.subtitle}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="p-4">
              <nav className="space-y-2">
                {settingsTabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700 border border-blue-200'
                          : tab.enabled 
                            ? 'bg-white hover:bg-gray-50 border border-gray-200'
                            : 'bg-gray-50 text-gray-400 border border-gray-100 cursor-not-allowed'
                      }`}
                      disabled={!tab.enabled}
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`h-5 w-5 ${
                          activeTab === tab.id ? 'text-blue-600' : tab.enabled ? 'text-gray-600' : 'text-gray-400'
                        }`} />
                        <div>
                          <div className="font-medium">{tab.label}</div>
                          <div className="text-xs text-gray-500">{tab.description}</div>
                        </div>
                      </div>
                      {!tab.enabled && (
                        <div className="text-xs text-gray-400 mt-1 ml-8">{t('common.comingSoon', 'Coming Soon')}</div>
                      )}
                    </button>
                  )
                })}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default Settings

