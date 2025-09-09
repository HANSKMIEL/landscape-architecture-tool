import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Brain, 
  Settings as SettingsIcon, 
  Key, 
  Zap,
  FileText,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Lightbulb
} from 'lucide-react'

const AISettings = ({ language = 'nl' }) => {
  const [openaiKey, setOpenaiKey] = useState('')
  const [aiFeatures, setAiFeatures] = useState({
    plantRecommendations: true,
    dataMapping: true,
    smartCorrection: true,
    languageDetection: true
  })
  const [aiLevel, setAiLevel] = useState('balanced')
  const [customPrompts, setCustomPrompts] = useState({
    plantRecommendation: '',
    dataMapping: '',
    errorCorrection: ''
  })

  const translations = {
    en: {
      title: 'AI Assistant Settings',
      subtitle: 'Configure intelligent automation and AI features',
      apiSection: 'API Configuration',
      apiDesc: 'Configure AI service connections',
      featuresSection: 'AI Features',
      featuresDesc: 'Enable or disable AI capabilities',
      promptsSection: 'Custom Prompts',
      promptsDesc: 'Customize AI behavior with specific instructions',
      performanceSection: 'Performance Settings',
      performanceDesc: 'Configure AI processing level and speed',
      openaiKey: 'OpenAI API Key',
      openaiKeyPlaceholder: 'Enter your OpenAI API key...',
      openaiKeyDesc: 'Required for AI-powered features like data mapping and plant recommendations',
      plantRecommendations: 'Plant Recommendations',
      plantRecommendationsDesc: 'AI-powered plant suggestions based on project requirements',
      dataMapping: 'Intelligent Data Mapping',
      dataMappingDesc: 'Automatically map Excel columns to database fields',
      smartCorrection: 'Smart Data Correction',
      smartCorrectionDesc: 'Automatically fix common data entry errors',
      languageDetection: 'Language Detection',
      languageDetectionDesc: 'Automatically detect and handle Dutch/English content',
      aiLevelTitle: 'AI Processing Level',
      conservative: 'Conservative',
      conservativeDesc: 'Slower but more accurate processing',
      balanced: 'Balanced',
      balancedDesc: 'Good balance of speed and accuracy',
      aggressive: 'Aggressive',
      aggressiveDesc: 'Faster processing with higher token usage',
      plantPrompt: 'Plant Recommendation Prompt',
      plantPromptPlaceholder: 'Custom instructions for plant recommendations...',
      mappingPrompt: 'Data Mapping Prompt',
      mappingPromptPlaceholder: 'Custom instructions for data mapping...',
      correctionPrompt: 'Error Correction Prompt',
      correctionPromptPlaceholder: 'Custom instructions for error correction...',
      testConnection: 'Test AI Connection',
      saveSettings: 'Save Settings',
      resetDefaults: 'Reset Defaults',
      connectionStatus: 'Connection Status',
      connected: 'Connected',
      disconnected: 'Not Connected',
      testing: 'Testing...',
      aiUsageStats: 'AI Usage Statistics',
      tokensUsed: 'Tokens Used (This Month)',
      requestsMade: 'Requests Made',
      successRate: 'Success Rate'
    },
    nl: {
      title: 'AI Assistent Instellingen',
      subtitle: 'Configureer intelligente automatisering en AI-functies',
      apiSection: 'API Configuratie',
      apiDesc: 'Configureer AI-service verbindingen',
      featuresSection: 'AI Functies',
      featuresDesc: 'Schakel AI-mogelijkheden in of uit',
      promptsSection: 'Aangepaste Prompts',
      promptsDesc: 'Pas AI-gedrag aan met specifieke instructies',
      performanceSection: 'Prestatie Instellingen',
      performanceDesc: 'Configureer AI-verwerkingsniveau en snelheid',
      openaiKey: 'OpenAI API Sleutel',
      openaiKeyPlaceholder: 'Voer uw OpenAI API sleutel in...',
      openaiKeyDesc: 'Vereist voor AI-functies zoals gegevenstoewijzing en plantaanbevelingen',
      plantRecommendations: 'Plantaanbevelingen',
      plantRecommendationsDesc: 'AI-gestuurde plantsuggesties op basis van projectvereisten',
      dataMapping: 'Intelligente Gegevenstoewijzing',
      dataMappingDesc: 'Wijs automatisch Excel-kolommen toe aan databasevelden',
      smartCorrection: 'Slimme Gegevenscorrectie',
      smartCorrectionDesc: 'Corrigeer automatisch veelvoorkomende invoerfouten',
      languageDetection: 'Taaldetectie',
      languageDetectionDesc: 'Detecteer en verwerk automatisch Nederlandse/Engelse inhoud',
      aiLevelTitle: 'AI Verwerkingsniveau',
      conservative: 'Conservatief',
      conservativeDesc: 'Langzamer maar nauwkeurigere verwerking',
      balanced: 'Uitgebalanceerd',
      balancedDesc: 'Goede balans tussen snelheid en nauwkeurigheid',
      aggressive: 'Agressief',
      aggressiveDesc: 'Snellere verwerking met hoger tokengebruik',
      plantPrompt: 'Plantaanbeveling Prompt',
      plantPromptPlaceholder: 'Aangepaste instructies voor plantaanbevelingen...',
      mappingPrompt: 'Gegevenstoewijzing Prompt',
      mappingPromptPlaceholder: 'Aangepaste instructies voor gegevenstoewijzing...',
      correctionPrompt: 'Foutcorrectie Prompt',
      correctionPromptPlaceholder: 'Aangepaste instructies voor foutcorrectie...',
      testConnection: 'Test AI Verbinding',
      saveSettings: 'Instellingen Opslaan',
      resetDefaults: 'Standaardwaarden Herstellen',
      connectionStatus: 'Verbindingsstatus',
      connected: 'Verbonden',
      disconnected: 'Niet Verbonden',
      testing: 'Testen...',
      aiUsageStats: 'AI Gebruiksstatistieken',
      tokensUsed: 'Tokens Gebruikt (Deze Maand)',
      requestsMade: 'Verzoeken Gedaan',
      successRate: 'Succespercentage'
    }
  }

  const t = translations[language]

  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [testingConnection, setTestingConnection] = useState(false)

  const testAIConnection = async () => {
    if (!openaiKey.trim()) {
      alert(language === 'nl' ? 'Voer eerst een API sleutel in' : 'Please enter an API key first')
      return
    }

    setTestingConnection(true)
    setConnectionStatus('testing')

    try {
      // Simulate API test - in real implementation, this would test the actual OpenAI connection
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock successful connection
      setConnectionStatus('connected')
      alert(language === 'nl' ? 'AI verbinding succesvol!' : 'AI connection successful!')
    } catch (error) {
      setConnectionStatus('disconnected')
      alert(language === 'nl' ? 'AI verbinding mislukt' : 'AI connection failed')
    } finally {
      setTestingConnection(false)
    }
  }

  const saveSettings = () => {
    const settings = {
      openaiKey,
      aiFeatures,
      aiLevel,
      customPrompts,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('aiSettings', JSON.stringify(settings))
    alert(language === 'nl' ? 'AI instellingen opgeslagen!' : 'AI settings saved!')
  }

  const resetDefaults = () => {
    setOpenaiKey('')
    setAiFeatures({
      plantRecommendations: true,
      dataMapping: true,
      smartCorrection: true,
      languageDetection: true
    })
    setAiLevel('balanced')
    setCustomPrompts({
      plantRecommendation: '',
      dataMapping: '',
      errorCorrection: ''
    })
    setConnectionStatus('disconnected')
    localStorage.removeItem('aiSettings')
  }

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'testing':
        return <div className="h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      default:
        return <AlertCircle className="h-5 w-5 text-red-600" />
    }
  }

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return t.connected
      case 'testing':
        return t.testing
      default:
        return t.disconnected
    }
  }

  const mockStats = {
    tokensUsed: 15420,
    requestsMade: 87,
    successRate: 96.5
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{t.title}</h2>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      {/* API Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5 text-blue-600" />
            {t.apiSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.apiDesc}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.openaiKey}
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder={t.openaiKeyPlaceholder}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={testAIConnection}
                disabled={testingConnection || !openaiKey.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {t.testConnection}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">{t.openaiKeyDesc}</p>
          </div>

          {/* Connection Status */}
          <div className="flex items-center gap-2 p-3 border rounded-lg bg-gray-50">
            {getStatusIcon()}
            <span className="text-sm font-medium">{t.connectionStatus}:</span>
            <span className={`text-sm ${
              connectionStatus === 'connected' ? 'text-green-600' : 
              connectionStatus === 'testing' ? 'text-blue-600' : 'text-red-600'
            }`}>
              {getStatusText()}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* AI Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            {t.featuresSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.featuresDesc}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.plantRecommendations}</div>
                <div className="text-xs text-gray-500">{t.plantRecommendationsDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={aiFeatures.plantRecommendations}
                onChange={(e) => setAiFeatures({...aiFeatures, plantRecommendations: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.dataMapping}</div>
                <div className="text-xs text-gray-500">{t.dataMappingDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={aiFeatures.dataMapping}
                onChange={(e) => setAiFeatures({...aiFeatures, dataMapping: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.smartCorrection}</div>
                <div className="text-xs text-gray-500">{t.smartCorrectionDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={aiFeatures.smartCorrection}
                onChange={(e) => setAiFeatures({...aiFeatures, smartCorrection: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.languageDetection}</div>
                <div className="text-xs text-gray-500">{t.languageDetectionDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={aiFeatures.languageDetection}
                onChange={(e) => setAiFeatures({...aiFeatures, languageDetection: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-600" />
            {t.performanceSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.performanceDesc}</p>
        </CardHeader>
        <CardContent>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              {t.aiLevelTitle}
            </label>
            <div className="space-y-3">
              {[
                { id: 'conservative', label: t.conservative, desc: t.conservativeDesc },
                { id: 'balanced', label: t.balanced, desc: t.balancedDesc },
                { id: 'aggressive', label: t.aggressive, desc: t.aggressiveDesc }
              ].map((level) => (
                <div key={level.id} className="flex items-start gap-3">
                  <input
                    type="radio"
                    id={level.id}
                    name="aiLevel"
                    value={level.id}
                    checked={aiLevel === level.id}
                    onChange={(e) => setAiLevel(e.target.value)}
                    className="mt-1 w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <label htmlFor={level.id} className="flex-1 cursor-pointer">
                    <div className="font-medium text-sm">{level.label}</div>
                    <div className="text-xs text-gray-500">{level.desc}</div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Custom Prompts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-green-600" />
            {t.promptsSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.promptsDesc}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.plantPrompt}
            </label>
            <textarea
              value={customPrompts.plantRecommendation}
              onChange={(e) => setCustomPrompts({...customPrompts, plantRecommendation: e.target.value})}
              placeholder={t.plantPromptPlaceholder}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.mappingPrompt}
            </label>
            <textarea
              value={customPrompts.dataMapping}
              onChange={(e) => setCustomPrompts({...customPrompts, dataMapping: e.target.value})}
              placeholder={t.mappingPromptPlaceholder}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.correctionPrompt}
            </label>
            <textarea
              value={customPrompts.errorCorrection}
              onChange={(e) => setCustomPrompts({...customPrompts, errorCorrection: e.target.value})}
              placeholder={t.correctionPromptPlaceholder}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Usage Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-orange-600" />
            {t.aiUsageStats}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{mockStats.tokensUsed.toLocaleString()}</div>
              <div className="text-sm text-gray-600">{t.tokensUsed}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{mockStats.requestsMade}</div>
              <div className="text-sm text-gray-600">{t.requestsMade}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{mockStats.successRate}%</div>
              <div className="text-sm text-gray-600">{t.successRate}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={saveSettings}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          {t.saveSettings}
        </button>
        <button
          onClick={resetDefaults}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
        >
          {t.resetDefaults}
        </button>
      </div>
    </div>
  )
}

export default AISettings