import { useLanguage } from "../../i18n/LanguageProvider";
import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Link, 
  Settings as SettingsIcon, 
  CheckCircle, 
  AlertCircle,
  ExternalLink,
  Zap,
  Globe,
  Camera,
  Gamepad2,
  Users,
  Database
} from 'lucide-react'

// --- Simple AES encryption helpers using Web Crypto API ---

// Converts a string to ArrayBuffer
function str2ab(str) {
  const buf = new ArrayBuffer(str.length * 2);
  const bufView = new Uint16Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

// Converts ArrayBuffer to string
function ab2str(buf) {
  return String.fromCharCode.apply(null, new Uint16Array(buf));
}

// Derive a crypto key from passphrase
async function getKeyMaterial(passphrase) {
  const enc = new TextEncoder();
  return window.crypto.subtle.importKey(
    "raw",
    enc.encode(passphrase),
    "PBKDF2",
    false,
    ["deriveBits", "deriveKey"]
  );
}

async function getKey(passphrase, salt) {
  const keyMaterial = await getKeyMaterial(passphrase);
  return window.crypto.subtle.deriveKey(
    {
      "name": "PBKDF2",
      salt: salt,
      "iterations": 100000,
      "hash": "SHA-256"
    },
    keyMaterial,
    { "name": "AES-GCM", "length": 256 },
    true,
    ["encrypt", "decrypt"]
  );
}

async function encrypt(text, passphrase) {
  const enc = new TextEncoder();
  const salt = window.crypto.getRandomValues(new Uint8Array(16));
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const key = await getKey(passphrase, salt);
  const ciphertext = await window.crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    key,
    enc.encode(text)
  );
  return btoa(
    JSON.stringify({
      ciphertext: Array.from(new Uint8Array(ciphertext)),
      iv: Array.from(iv),
      salt: Array.from(salt)
    })
  );
}

async function decrypt(encryptedData, passphrase) {
  try {
    const obj = JSON.parse(atob(encryptedData));
    const iv = new Uint8Array(obj.iv);
    const salt = new Uint8Array(obj.salt);
    const ciphertext = new Uint8Array(obj.ciphertext);
    const key = await getKey(passphrase, salt);
    const decrypted = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      key,
      ciphertext
    );
    const dec = new TextDecoder();
    return dec.decode(decrypted);
  } catch(e) {
    return null;
  }
}

async function encryptApiKeys(apiKeys, passphrase) {
  const encrypted = {};
  for (let [k, v] of Object.entries(apiKeys)) {
    encrypted[k] = v ? await encrypt(v, passphrase) : "";
  }
  return encrypted;
}

// Optionally, a decryptApiKeys function can be created similarly

const APISettings = ({ language = 'nl' }) => {
  const [apiKeys, setApiKeys] = useState({
    vectorworks: '',
    n8n: '',
    hubspot: '',
    mailchimp: '',
    openweather: ''
  })
  
  const [apiEndpoints, setApiEndpoints] = useState({
    n8n: 'https://your-n8n-instance.com',
    vectorworks: 'https://api.vectorworks.net',
    photogrammetry: 'https://api.photogrammetry-service.com'
  })

  const [connectionStatus, setConnectionStatus] = useState({
    vectorworks: 'disconnected',
    n8n: 'disconnected',
    hubspot: 'disconnected',
    mailchimp: 'disconnected',
    openweather: 'disconnected'
  })

  const translations = {
    en: {
      title: 'API Integrations',
      subtitle: 'Connect with external software and services',
      cadSection: 'CAD Software Integration',
      cadDesc: 'Connect with Vectorworks and other CAD applications',
      automationSection: 'Workflow Automation',
      automationDesc: 'Configure N8N and automated processes',
      crmSection: 'CRM & Marketing',
      crmDesc: 'Integrate with customer relationship management systems',
      servicesSection: 'External Services',
      servicesDesc: 'Connect with weather, location, and other services',
      futureSection: 'Future Integrations',
      futureDesc: 'Planned integrations for advanced workflows',
      vectorworks: 'Vectorworks',
      vectorworksDesc: 'CAD design automation and file synchronization',
      n8n: 'N8N Workflow Automation',
      n8nDesc: 'Automate client onboarding and project workflows',
      hubspot: 'HubSpot CRM',
      hubspotDesc: 'Customer relationship management integration',
      mailchimp: 'Mailchimp',
      mailchimpDesc: 'Email marketing and client communication',
      openweather: 'OpenWeather API',
      openweatherDesc: 'Weather data for plant recommendations',
      photogrammetry: 'Photogrammetry Service',
      photogrammetryDesc: 'Automated 3D model generation from photos',
      unreal: 'Unreal Engine',
      unrealDesc: 'Advanced 3D visualization and VR experiences',
      apiKey: 'API Key',
      apiKeyPlaceholder: 'Enter API key...',
      endpoint: 'Endpoint URL',
      endpointPlaceholder: 'Enter endpoint URL...',
      testConnection: 'Test Connection',
      saveSettings: 'Save Settings',
      resetDefaults: 'Reset Defaults',
      connectionStatus: 'Connection Status',
      connected: 'Connected',
      disconnected: 'Not Connected',
      testing: 'Testing...',
      error: 'Connection Error',
      configure: 'Configure',
      comingSoon: 'Coming Soon',
      documentation: 'View Documentation',
      status: 'Status',
      activeIntegrations: 'Active Integrations',
      pendingSetup: 'Pending Setup'
    },
    nl: {
      title: 'API Integraties',
      subtitle: 'Verbind met externe software en diensten',
      cadSection: 'CAD Software Integratie',
      cadDesc: 'Verbind met Vectorworks en andere CAD-applicaties',
      automationSection: 'Workflow Automatisering',
      automationDesc: 'Configureer N8N en geautomatiseerde processen',
      crmSection: 'CRM & Marketing',
      crmDesc: 'Integreer met klantrelatiebeheersystemen',
      servicesSection: 'Externe Diensten',
      servicesDesc: 'Verbind met weer-, locatie- en andere diensten',
      futureSection: 'Toekomstige Integraties',
      futureDesc: 'Geplande integraties voor geavanceerde workflows',
      vectorworks: 'Vectorworks',
      vectorworksDesc: 'CAD ontwerpautomatisering en bestandssynchronisatie',
      n8n: 'N8N Workflow Automatisering',
      n8nDesc: 'Automatiseer klant onboarding en projectworkflows',
      hubspot: 'HubSpot CRM',
      hubspotDesc: 'Klantrelatiebeheersysteem integratie',
      mailchimp: 'Mailchimp',
      mailchimpDesc: 'E-mailmarketing en klantcommunicatie',
      openweather: 'OpenWeather API',
      openweatherDesc: 'Weergegevens voor plantaanbevelingen',
      photogrammetry: 'Fotogrammetrie Service',
      photogrammetryDesc: 'Geautomatiseerde 3D-modelgeneratie uit foto\'s',
      unreal: 'Unreal Engine',
      unrealDesc: 'Geavanceerde 3D-visualisatie en VR-ervaringen',
      apiKey: 'API Sleutel',
      apiKeyPlaceholder: 'Voer API sleutel in...',
      endpoint: 'Endpoint URL',
      endpointPlaceholder: 'Voer endpoint URL in...',
      testConnection: 'Test Verbinding',
      saveSettings: 'Instellingen Opslaan',
      resetDefaults: 'Standaardwaarden Herstellen',
      connectionStatus: 'Verbindingsstatus',
      connected: 'Verbonden',
      disconnected: 'Niet Verbonden',
      testing: 'Testen...',
      error: 'Verbindingsfout',
      configure: 'Configureren',
      comingSoon: 'Binnenkort',
      documentation: 'Bekijk Documentatie',
      status: 'Status',
      activeIntegrations: 'Actieve Integraties',
      pendingSetup: 'Setup Vereist'
    }
  }

  const t = t

  const testConnection = async (service) => {
    setConnectionStatus(prev => ({ ...prev, [service]: 'testing' }))
    
    try {
      // Simulate API test - in real implementation, this would test the actual API
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock response based on whether API key is provided
      if (apiKeys[service] && apiKeys[service].trim()) {
        setConnectionStatus(prev => ({ ...prev, [service]: 'connected' }))
      } else {
        setConnectionStatus(prev => ({ ...prev, [service]: 'error' }))
      }
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, [service]: 'error' }))
    }
  }

  const saveSettings = async () => {
    // Prompt user for passphrase for encrypting keys
    let passphrase = window.prompt(language === 'nl' ? "Voer wachtwoord voor encryptie van API sleutels in:" : "Enter passphrase to encrypt API keys:");
    if (!passphrase || passphrase.length < 5) {
      alert(language === 'nl' ? "Wachtwoord te kort. Instellingen niet opgeslagen." : "Passphrase too short. Settings not saved.");
      return;
    }
    const encryptedApiKeys = await encryptApiKeys(apiKeys, passphrase);
    const settings = {
      apiKeys: encryptedApiKeys,
      apiEndpoints,
      connectionStatus,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('apiSettings', JSON.stringify(settings))
    alert(language === 'nl' ? 'API instellingen opgeslagen!' : 'API settings saved!')
  }

  const resetDefaults = () => {
    setApiKeys({
      vectorworks: '',
      n8n: '',
      hubspot: '',
      mailchimp: '',
      openweather: ''
    })
    setApiEndpoints({
      n8n: 'https://your-n8n-instance.com',
      vectorworks: 'https://api.vectorworks.net',
      photogrammetry: 'https://api.photogrammetry-service.com'
    })
    setConnectionStatus({
      vectorworks: 'disconnected',
      n8n: 'disconnected',
      hubspot: 'disconnected',
      mailchimp: 'disconnected',
      openweather: 'disconnected'
    })
    localStorage.removeItem('apiSettings')
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'testing':
        return <div className="h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-green-600'
      case 'testing':
        return 'text-blue-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return t.connected
      case 'testing':
        return t.testing
      case 'error':
        return t.error
      default:
        return t.disconnected
    }
  }

  const currentIntegrations = [
    {
      name: t.vectorworks,
      description: t.vectorworksDesc,
      icon: '🏗️',
      status: connectionStatus.vectorworks,
      enabled: true,
      keyField: 'vectorworks'
    },
    {
      name: t.n8n,
      description: t.n8nDesc,
      icon: '⚡',
      status: connectionStatus.n8n,
      enabled: true,
      keyField: 'n8n'
    },
    {
      name: t.hubspot,
      description: t.hubspotDesc,
      icon: '👥',
      status: connectionStatus.hubspot,
      enabled: true,
      keyField: 'hubspot'
    },
    {
      name: t.mailchimp,
      description: t.mailchimpDesc,
      icon: '📧',
      status: connectionStatus.mailchimp,
      enabled: true,
      keyField: 'mailchimp'
    },
    {
      name: t.openweather,
      description: t.openweatherDesc,
      icon: '🌤️',
      status: connectionStatus.openweather,
      enabled: true,
      keyField: 'openweather'
    }
  ]

  const futureIntegrations = [
    {
      name: t.photogrammetry,
      description: t.photogrammetryDesc,
      icon: <Camera className="h-5 w-5" />,
      category: 'AI/ML'
    },
    {
      name: t.unreal,
      description: t.unrealDesc,
      icon: <Gamepad2 className="h-5 w-5" />,
      category: 'Visualization'
    }
  ]

  const connectedCount = Object.values(connectionStatus).filter(status => status === 'connected').length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{t.title}</h2>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      {/* Integration Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-blue-600" />
            {t.status}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{connectedCount}</div>
              <div className="text-sm text-gray-600">{t.activeIntegrations}</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{currentIntegrations.length - connectedCount}</div>
              <div className="text-sm text-gray-600">{t.pendingSetup}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Integrations */}
      <div className="space-y-4">
        {currentIntegrations.map((integration, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{integration.icon}</span>
                  <div>
                    <div className="text-lg">{integration.name}</div>
                    <div className="text-sm text-gray-600 font-normal">{integration.description}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(integration.status)}
                  <span className={`text-sm font-medium ${getStatusColor(integration.status)}`}>
                    {getStatusText(integration.status)}
                  </span>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* API Key Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t.apiKey}
                </label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={apiKeys[integration.keyField]}
                    onChange={(e) => setApiKeys(prev => ({
                      ...prev,
                      [integration.keyField]: e.target.value
                    }))}
                    placeholder={t.apiKeyPlaceholder}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={() => testConnection(integration.keyField)}
                    disabled={connectionStatus[integration.keyField] === 'testing'}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {t.testConnection}
                  </button>
                </div>
              </div>

              {/* Endpoint Configuration for services that need it */}
              {(integration.keyField === 'n8n' || integration.keyField === 'vectorworks') && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t.endpoint}
                  </label>
                  <input
                    type="url"
                    value={apiEndpoints[integration.keyField] || ''}
                    onChange={(e) => setApiEndpoints(prev => ({
                      ...prev,
                      [integration.keyField]: e.target.value
                    }))}
                    placeholder={t.endpointPlaceholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              {/* Documentation Link */}
              <div className="flex items-center gap-2 text-sm text-blue-600">
                <ExternalLink className="h-4 w-4" />
                <a href="#" className="hover:underline">{t.documentation}</a>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Future Integrations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-orange-600" />
            {t.futureSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.futureDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {futureIntegrations.map((integration, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-gray-200 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="text-gray-500">{integration.icon}</div>
                  <div>
                    <h4 className="font-semibold text-gray-800">{integration.name}</h4>
                    <p className="text-sm text-gray-600">{integration.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="px-3 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded-full">
                    {integration.category}
                  </div>
                  <div className="px-3 py-1 bg-orange-100 text-orange-600 text-sm font-medium rounded-full">
                    {t.comingSoon}
                  </div>
                </div>
              </div>
            ))}
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

export default APISettings