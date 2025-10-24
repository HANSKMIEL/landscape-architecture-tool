import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Camera, CheckCircle, ExternalLink, Gamepad2, Globe, Zap } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageProvider';

const translationDefaults = {
  title: 'API Integrations',
  subtitle: 'Connect with external software and services',
  overview: {
    statusTitle: 'Status',
    activeLabel: 'Active Integrations',
    pendingLabel: 'Pending Setup'
  },
  integrations: {
    vectorworks: {
      name: 'Vectorworks',
      description: 'CAD design automation and file synchronization'
    },
    n8n: {
      name: 'N8N Workflow Automation',
      description: 'Automate client onboarding and project workflows'
    },
    hubspot: {
      name: 'HubSpot CRM',
      description: 'Customer relationship management integration'
    },
    mailchimp: {
      name: 'Mailchimp',
      description: 'Email marketing and client communication'
    },
    openweather: {
      name: 'OpenWeather API',
      description: 'Weather data for plant recommendations'
    }
  },
  fields: {
    apiKeyLabel: 'API Key',
    apiKeyPlaceholder: 'Enter API key...',
    endpointLabel: 'Endpoint URL',
    endpointPlaceholder: 'Enter endpoint URL...'
  },
  actions: {
    testConnection: 'Test Connection',
    save: 'Save Settings',
    reset: 'Reset Defaults',
    saveSuccess: 'API settings saved!',
    saveError: 'Unable to save API settings. Please try again.',
    resetSuccess: 'API settings reset to defaults!'
  },
  status: {
    label: 'Connection Status',
    connected: 'Connected',
    disconnected: 'Not Connected',
    testing: 'Testing...',
    error: 'Connection Error'
  },
  future: {
    sectionTitle: 'Future Integrations',
    description: 'Planned integrations for advanced workflows',
    comingSoon: 'Coming Soon',
    categories: {
      ai: 'AI/ML',
      visualization: 'Visualization'
    },
    photogrammetry: {
      name: 'Photogrammetry Service',
      description: 'Automated 3D model generation from photos'
    },
    unreal: {
      name: 'Unreal Engine',
      description: 'Advanced 3D visualization and VR experiences'
    }
  },
  documentation: 'View Documentation'
};

const getTranslationDefault = (path) =>
  path.split('.').reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults);

const DEFAULT_API_KEYS = {
  vectorworks: '',
  n8n: '',
  hubspot: '',
  mailchimp: '',
  openweather: ''
};

const DEFAULT_ENDPOINTS = {
  n8n: 'https://your-n8n-instance.com',
  vectorworks: 'https://api.vectorworks.net',
  photogrammetry: 'https://api.photogrammetry-service.com'
};

const DEFAULT_CONNECTION_STATUS = {
  vectorworks: 'disconnected',
  n8n: 'disconnected',
  hubspot: 'disconnected',
  mailchimp: 'disconnected',
  openweather: 'disconnected'
};

const APISettings = () => {
  const { t } = useLanguage();

  const [apiKeys, setApiKeys] = useState(DEFAULT_API_KEYS);
  const [apiEndpoints, setApiEndpoints] = useState(DEFAULT_ENDPOINTS);
  const [connectionStatus, setConnectionStatus] = useState(DEFAULT_CONNECTION_STATUS);

  useEffect(() => {
    try {
      const storedSettings = localStorage.getItem('apiSettings');
      if (!storedSettings) {
        return;
      }

      const parsedSettings = JSON.parse(storedSettings);
      if (parsedSettings.apiKeys) {
        setApiKeys((prev) => ({ ...prev, ...parsedSettings.apiKeys }));
      }
      if (parsedSettings.apiEndpoints) {
        setApiEndpoints((prev) => ({ ...prev, ...parsedSettings.apiEndpoints }));
      }
      if (parsedSettings.connectionStatus) {
        setConnectionStatus((prev) => ({ ...prev, ...parsedSettings.connectionStatus }));
      }
    } catch (error) {
      console.error('Failed to load API settings from storage:', error);
    }
  }, []);

  const translate = useCallback(
    (key) => t(`settings.apiSettings.${key}`, getTranslationDefault(key) ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      statusTitle: translate('overview.statusTitle'),
      activeLabel: translate('overview.activeLabel'),
      pendingLabel: translate('overview.pendingLabel'),
      apiKeyLabel: translate('fields.apiKeyLabel'),
      apiKeyPlaceholder: translate('fields.apiKeyPlaceholder'),
      endpointLabel: translate('fields.endpointLabel'),
      endpointPlaceholder: translate('fields.endpointPlaceholder'),
      documentation: translate('documentation'),
      testConnection: translate('actions.testConnection'),
      save: translate('actions.save'),
      reset: translate('actions.reset'),
      saveSuccess: translate('actions.saveSuccess'),
      saveError: translate('actions.saveError'),
      resetSuccess: translate('actions.resetSuccess'),
      statusLabel: translate('status.label'),
      statusConnected: translate('status.connected'),
      statusDisconnected: translate('status.disconnected'),
      statusTesting: translate('status.testing'),
      statusError: translate('status.error'),
      futureTitle: translate('future.sectionTitle'),
      futureDescription: translate('future.description'),
      comingSoon: translate('future.comingSoon'),
      futureCategories: {
        ai: translate('future.categories.ai'),
        visualization: translate('future.categories.visualization')
      },
      integrations: {
        vectorworks: {
          name: translate('integrations.vectorworks.name'),
          description: translate('integrations.vectorworks.description')
        },
        n8n: {
          name: translate('integrations.n8n.name'),
          description: translate('integrations.n8n.description')
        },
        hubspot: {
          name: translate('integrations.hubspot.name'),
          description: translate('integrations.hubspot.description')
        },
        mailchimp: {
          name: translate('integrations.mailchimp.name'),
          description: translate('integrations.mailchimp.description')
        },
        openweather: {
          name: translate('integrations.openweather.name'),
          description: translate('integrations.openweather.description')
        }
      },
      futureIntegrations: {
        photogrammetry: {
          name: translate('future.photogrammetry.name'),
          description: translate('future.photogrammetry.description')
        },
        unreal: {
          name: translate('future.unreal.name'),
          description: translate('future.unreal.description')
        }
      }
    }),
    [translate]
  );

  const integrationList = useMemo(
    () => [
      {
        key: 'vectorworks',
        icon: '🏗️',
        name: uiText.integrations.vectorworks.name,
        description: uiText.integrations.vectorworks.description,
        supportsEndpoint: true
      },
      {
        key: 'n8n',
        icon: '⚡',
        name: uiText.integrations.n8n.name,
        description: uiText.integrations.n8n.description,
        supportsEndpoint: true
      },
      {
        key: 'hubspot',
        icon: '👥',
        name: uiText.integrations.hubspot.name,
        description: uiText.integrations.hubspot.description,
        supportsEndpoint: false
      },
      {
        key: 'mailchimp',
        icon: '📧',
        name: uiText.integrations.mailchimp.name,
        description: uiText.integrations.mailchimp.description,
        supportsEndpoint: false
      },
      {
        key: 'openweather',
        icon: '🌤️',
        name: uiText.integrations.openweather.name,
        description: uiText.integrations.openweather.description,
        supportsEndpoint: false
      }
    ],
    [uiText.integrations]
  );

  const futureIntegrationList = useMemo(
    () => [
      {
        key: 'photogrammetry',
        icon: <Camera className="h-5 w-5" />,
        name: uiText.futureIntegrations.photogrammetry.name,
        description: uiText.futureIntegrations.photogrammetry.description,
        category: uiText.futureCategories.ai
      },
      {
        key: 'unreal',
        icon: <Gamepad2 className="h-5 w-5" />,
        name: uiText.futureIntegrations.unreal.name,
        description: uiText.futureIntegrations.unreal.description,
        category: uiText.futureCategories.visualization
      }
    ],
    [uiText.futureCategories.ai, uiText.futureCategories.visualization, uiText.futureIntegrations]
  );

  const statusIcon = useCallback((status) => {
    if (status === 'connected') {
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    }
    if (status === 'testing') {
      return <div className="h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
    }
    if (status === 'error') {
      return <AlertCircle className="h-4 w-4 text-red-600" />;
    }
    return <AlertCircle className="h-4 w-4 text-gray-400" />;
  }, []);

  const statusLabel = useCallback(
    (status) => {
      if (status === 'connected') {
        return uiText.statusConnected;
      }
      if (status === 'testing') {
        return uiText.statusTesting;
      }
      if (status === 'error') {
        return uiText.statusError;
      }
      return uiText.statusDisconnected;
    },
    [uiText.statusConnected, uiText.statusDisconnected, uiText.statusError, uiText.statusTesting]
  );

  const statusClass = useCallback((status) => {
    if (status === 'connected') {
      return 'text-green-600';
    }
    if (status === 'testing') {
      return 'text-blue-600';
    }
    if (status === 'error') {
      return 'text-red-600';
    }
    return 'text-gray-400';
  }, []);

  const integrationsConnected = useMemo(
    () => Object.values(connectionStatus).filter((status) => status === 'connected').length,
    [connectionStatus]
  );

  const handleKeyChange = useCallback((integrationKey) => (event) => {
    const { value } = event.target;
    setApiKeys((prev) => ({
      ...prev,
      [integrationKey]: value
    }));
  }, []);

  const handleEndpointChange = useCallback((integrationKey) => (event) => {
    const { value } = event.target;
    setApiEndpoints((prev) => ({
      ...prev,
      [integrationKey]: value
    }));
  }, []);

  const testConnection = useCallback(
    async (integrationKey) => {
      setConnectionStatus((prev) => ({
        ...prev,
        [integrationKey]: 'testing'
      }));

      try {
        await new Promise((resolve) => {
          setTimeout(resolve, 2000);
        });

        setConnectionStatus((prev) => ({
          ...prev,
          [integrationKey]: apiKeys[integrationKey]?.trim() ? 'connected' : 'error'
        }));
      } catch (error) {
        console.error('API connection test failed:', error);
        setConnectionStatus((prev) => ({
          ...prev,
          [integrationKey]: 'error'
        }));
      }
    },
    [apiKeys]
  );

  const saveSettings = useCallback(() => {
    const settingsToSave = {
      apiKeys,
      apiEndpoints,
      connectionStatus,
      timestamp: new Date().toISOString()
    };

    try {
      localStorage.setItem('apiSettings', JSON.stringify(settingsToSave));
      window.alert(uiText.saveSuccess);
    } catch (error) {
      console.error('Failed to save API settings:', error);
      window.alert(uiText.saveError);
    }
  }, [apiEndpoints, apiKeys, connectionStatus, uiText.saveError, uiText.saveSuccess]);

  const resetDefaults = useCallback(() => {
    setApiKeys(DEFAULT_API_KEYS);
    setApiEndpoints(DEFAULT_ENDPOINTS);
    setConnectionStatus(DEFAULT_CONNECTION_STATUS);

    try {
      localStorage.removeItem('apiSettings');
    } catch (error) {
      console.error('Failed to clear API settings from storage:', error);
    }

    window.alert(uiText.resetSuccess);
  }, [uiText.resetSuccess]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{uiText.title}</h2>
        <p className="text-gray-600">{uiText.subtitle}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-blue-600" />
            {uiText.statusTitle}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{integrationsConnected}</div>
              <div className="text-sm text-gray-600">{uiText.activeLabel}</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{integrationList.length - integrationsConnected}</div>
              <div className="text-sm text-gray-600">{uiText.pendingLabel}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {integrationList.map((integration) => (
          <Card key={integration.key}>
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
                  {statusIcon(connectionStatus[integration.key])}
                  <span className={`text-sm font-medium ${statusClass(connectionStatus[integration.key])}`}>
                    {statusLabel(connectionStatus[integration.key])}
                  </span>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">{uiText.apiKeyLabel}</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={apiKeys[integration.key]}
                    onChange={handleKeyChange(integration.key)}
                    placeholder={uiText.apiKeyPlaceholder}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <Button
                    onClick={() => testConnection(integration.key)}
                    disabled={connectionStatus[integration.key] === 'testing'}
                    className="px-4"
                  >
                    {uiText.testConnection}
                  </Button>
                </div>
              </div>

              {integration.supportsEndpoint && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{uiText.endpointLabel}</label>
                  <input
                    type="url"
                    value={apiEndpoints[integration.key] || ''}
                    onChange={handleEndpointChange(integration.key)}
                    placeholder={uiText.endpointPlaceholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              <div className="flex items-center gap-2 text-sm text-blue-600">
                <ExternalLink className="h-4 w-4" />
                <a href="#" className="hover:underline">{uiText.documentation}</a>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-orange-600" />
            {uiText.futureTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.futureDescription}</p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {futureIntegrationList.map((integration) => (
              <div
                key={integration.key}
                className="flex items-center justify-between p-4 border border-gray-200 bg-gray-50 rounded-lg"
              >
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
                    {uiText.comingSoon}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-4">
        <Button onClick={saveSettings} className="px-6">
          {uiText.save}
        </Button>
        <Button onClick={resetDefaults} variant="outline" className="px-6">
          {uiText.reset}
        </Button>
      </div>
    </div>
  );
};

export default APISettings;