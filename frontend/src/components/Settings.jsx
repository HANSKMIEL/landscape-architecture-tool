import React, { useState } from 'react'
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
  Palette
} from 'lucide-react'
import ExcelImportManager from './ExcelImportManager'

const Settings = ({ language = 'nl' }) => {
  const [activeTab, setActiveTab] = useState('data-management')

  const translations = {
    en: {
      title: 'Settings',
      subtitle: 'Configure your landscape architecture application preferences',
      dataManagement: 'Data Management',
      dataManagementDesc: 'Import, export, and manage your business data',
      integrations: 'Integrations',
      integrationsDesc: 'Connect with external software and APIs',
      aiAssistant: 'AI Assistant',
      aiAssistantDesc: 'Configure intelligent data mapping and automation',
      appearance: 'Appearance',
      appearanceDesc: 'Customize the look and feel of your application',
      security: 'Security',
      securityDesc: 'Manage user access and security settings',
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
      dataManagement: 'Gegevensbeheer',
      dataManagementDesc: 'Importeer, exporteer en beheer uw bedrijfsgegevens',
      integrations: 'Integraties',
      integrationsDesc: 'Verbind met externe software en API\'s',
      aiAssistant: 'AI Assistent',
      aiAssistantDesc: 'Configureer intelligente gegevenstoewijzing en automatisering',
      appearance: 'Uiterlijk',
      appearanceDesc: 'Pas het uiterlijk van uw applicatie aan',
      security: 'Beveiliging',
      securityDesc: 'Beheer gebruikerstoegang en beveiligingsinstellingen',
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

  const t = translations[language]

  const settingsTabs = [
    {
      id: 'data-management',
      label: t.dataManagement,
      description: t.dataManagementDesc,
      icon: Database,
      enabled: true
    },
    {
      id: 'ai-assistant', 
      label: t.aiAssistant,
      description: t.aiAssistantDesc,
      icon: Cpu,
      enabled: false
    },
    {
      id: 'integrations',
      label: t.integrations,
      description: t.integrationsDesc,
      icon: Link,
      enabled: false
    },
    {
      id: 'appearance',
      label: t.appearance,
      description: t.appearanceDesc,
      icon: Palette,
      enabled: false
    },
    {
      id: 'security',
      label: t.security,
      description: t.securityDesc,
      icon: Shield,
      enabled: false
    }
  ]

  const futureIntegrations = [
    {
      name: t.vectorworks,
      description: t.vectorworksDesc,
      icon: '🏗️',
      category: 'CAD'
    },
    {
      name: t.crm,
      description: t.crmDesc,
      icon: '👥',
      category: 'Business'
    },
    {
      name: t.n8n,
      description: t.n8nDesc,
      icon: '⚡',
      category: 'Automation'
    },
    {
      name: t.photogrammetry,
      description: t.photogrammetryDesc,
      icon: '📸',
      category: 'AI/ML'
    },
    {
      name: t.unreal,
      description: t.unrealDesc,
      icon: '🎮',
      category: 'Visualization'
    }
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case 'data-management':
        return <ExcelImportManager />
      
      case 'ai-assistant':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cpu className="h-5 w-5 text-blue-600" />
                {t.aiAssistant}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Cpu className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
                <p className="text-gray-500 mb-4">{t.aiAssistantDesc}</p>
                <div className="text-sm text-gray-600">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <h4 className="font-semibold text-blue-800 mb-2">Geplande AI Functies:</h4>
                    <ul className="text-blue-700 text-left space-y-1">
                      <li>• Intelligente Excel kolom toewijzing</li>
                      <li>• Automatische data validatie en correctie</li>
                      <li>• Nederlandse bedrijfsdata aanbevelingen</li>
                      <li>• Slim ontbreken van velden opvullen</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      
      case 'integrations':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Link className="h-5 w-5 text-green-600" />
                  {t.enabledFeatures}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <div className="flex items-center justify-between p-4 border border-green-200 bg-green-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <FileSpreadsheet className="h-8 w-8 text-green-600" />
                      <div>
                        <h4 className="font-semibold text-green-800">Excel Import/Export</h4>
                        <p className="text-sm text-green-600">Bulk data management voor leveranciers, planten, producten en klanten</p>
                      </div>
                    </div>
                    <div className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">Actief</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-blue-600" />
                  {t.futureIntegrations}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  {futureIntegrations.map((integration, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border border-gray-200 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="text-2xl">{integration.icon}</div>
                        <div>
                          <h4 className="font-semibold text-gray-800">{integration.name}</h4>
                          <p className="text-sm text-gray-600">{integration.description}</p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded-full">{integration.category}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )
      
      default:
        return (
          <Card>
            <CardContent className="p-12">
              <div className="text-center">
                <SettingsIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{t.comingSoon}</h3>
                <p className="text-gray-500">Deze sectie wordt binnenkort beschikbaar.</p>
              </div>
            </CardContent>
          </Card>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
        <p className="text-gray-600">{t.subtitle}</p>
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
                        <div className="text-xs text-gray-400 mt-1 ml-8">Binnenkort</div>
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

