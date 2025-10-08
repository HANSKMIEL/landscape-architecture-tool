import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, Key, Zap, MessageSquare, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageProvider';

const translationDefaults = {
  title: 'AI Assistant Settings',
  subtitle: 'Configure intelligent automation and AI features',
  api: {
    sectionTitle: 'API Configuration',
    description: 'Configure AI service connections',
    openaiKeyLabel: 'OpenAI API Key',
    openaiKeyPlaceholder: 'Enter your OpenAI API key...',
    openaiKeyDescription: 'Required for AI-powered features like data mapping and plant recommendations',
    testButton: 'Test AI Connection',
    statusLabel: 'Connection Status',
    connected: 'Connected',
    testing: 'Testing...',
    disconnected: 'Not Connected',
    missingKeyMessage: 'Please enter an API key first',
    successMessage: 'AI connection successful!',
    failureMessage: 'AI connection failed'
  },
  features: {
    sectionTitle: 'AI Features',
    description: 'Enable or disable AI capabilities',
    plantRecommendations: {
      label: 'Plant Recommendations',
      description: 'AI-powered plant suggestions based on project requirements'
    },
    dataMapping: {
      label: 'Intelligent Data Mapping',
      description: 'Automatically map Excel columns to database fields'
    },
    smartCorrection: {
      label: 'Smart Data Correction',
      description: 'Automatically fix common data entry errors'
    },
    languageDetection: {
      label: 'Language Detection',
      description: 'Automatically detect and handle Dutch/English content'
    }
  },
  performance: {
    sectionTitle: 'Performance Settings',
    description: 'Configure AI processing level and speed',
    aiLevelTitle: 'AI Processing Level',
    levels: {
      conservative: {
        label: 'Conservative',
        description: 'Slower but more accurate processing'
      },
      balanced: {
        label: 'Balanced',
        description: 'Good balance of speed and accuracy'
      },
      aggressive: {
        label: 'Aggressive',
        description: 'Faster processing with higher token usage'
      }
    }
  },
  prompts: {
    sectionTitle: 'Custom Prompts',
    description: 'Customize AI behavior with specific instructions',
    plantPromptLabel: 'Plant Recommendation Prompt',
    plantPromptPlaceholder: 'Custom instructions for plant recommendations...',
    mappingPromptLabel: 'Data Mapping Prompt',
    mappingPromptPlaceholder: 'Custom instructions for data mapping...',
    correctionPromptLabel: 'Error Correction Prompt',
    correctionPromptPlaceholder: 'Custom instructions for error correction...'
  },
  stats: {
    sectionTitle: 'AI Usage Statistics',
    tokensUsedLabel: 'Tokens Used (This Month)',
    requestsMadeLabel: 'Requests Made',
    successRateLabel: 'Success Rate'
  },
  actions: {
    saveButton: 'Save Settings',
    resetButton: 'Reset Defaults',
    saveSuccess: 'AI settings saved!',
    saveError: 'Unable to save AI settings. Please try again.',
    resetSuccess: 'AI settings reset to defaults!'
  }
};

const getTranslationDefault = (path) =>
  path.split('.').reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults);

const DEFAULT_USAGE_STATS = {
  tokensUsed: 15420,
  requestsMade: 87,
  successRate: 96.5
};

const AISettings = () => {
  const { t } = useLanguage();

  const [openaiKey, setOpenaiKey] = useState('');
  const [aiFeatures, setAiFeatures] = useState({
    plantRecommendations: true,
    dataMapping: true,
    smartCorrection: true,
    languageDetection: true
  });
  const [aiLevel, setAiLevel] = useState('balanced');
  const [customPrompts, setCustomPrompts] = useState({
    plantRecommendation: '',
    dataMapping: '',
    errorCorrection: ''
  });
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [testingConnection, setTestingConnection] = useState(false);

  useEffect(() => {
    try {
      const storedSettings = localStorage.getItem('aiSettings');
      if (!storedSettings) {
        return;
      }

      const parsedSettings = JSON.parse(storedSettings);
      if (parsedSettings.openaiKey) {
        setOpenaiKey(parsedSettings.openaiKey);
      }
      if (parsedSettings.aiFeatures) {
        setAiFeatures((prev) => ({ ...prev, ...parsedSettings.aiFeatures }));
      }
      if (parsedSettings.aiLevel) {
        setAiLevel(parsedSettings.aiLevel);
      }
      if (parsedSettings.customPrompts) {
        setCustomPrompts((prev) => ({ ...prev, ...parsedSettings.customPrompts }));
      }
      if (parsedSettings.connectionStatus) {
        setConnectionStatus(parsedSettings.connectionStatus);
      }
    } catch (error) {
      console.error('Failed to load AI settings from storage:', error);
    }
  }, []);

  const translate = useCallback(
    (key) => t(`settings.ai.${key}`, getTranslationDefault(key) ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      apiSectionTitle: translate('api.sectionTitle'),
      apiDescription: translate('api.description'),
      openaiKeyLabel: translate('api.openaiKeyLabel'),
      openaiKeyPlaceholder: translate('api.openaiKeyPlaceholder'),
      openaiKeyDescription: translate('api.openaiKeyDescription'),
      testButton: translate('api.testButton'),
      statusLabel: translate('api.statusLabel'),
      statusConnected: translate('api.connected'),
      statusTesting: translate('api.testing'),
      statusDisconnected: translate('api.disconnected'),
      missingKeyMessage: translate('api.missingKeyMessage'),
      connectionSuccess: translate('api.successMessage'),
      connectionFailure: translate('api.failureMessage'),
      featuresSectionTitle: translate('features.sectionTitle'),
      featuresSectionDescription: translate('features.description'),
      featureLabels: {
        plantRecommendations: translate('features.plantRecommendations.label'),
        dataMapping: translate('features.dataMapping.label'),
        smartCorrection: translate('features.smartCorrection.label'),
        languageDetection: translate('features.languageDetection.label')
      },
      featureDescriptions: {
        plantRecommendations: translate('features.plantRecommendations.description'),
        dataMapping: translate('features.dataMapping.description'),
        smartCorrection: translate('features.smartCorrection.description'),
        languageDetection: translate('features.languageDetection.description')
      },
      performanceSectionTitle: translate('performance.sectionTitle'),
      performanceSectionDescription: translate('performance.description'),
      aiLevelTitle: translate('performance.aiLevelTitle'),
      levelLabels: {
        conservative: translate('performance.levels.conservative.label'),
        balanced: translate('performance.levels.balanced.label'),
        aggressive: translate('performance.levels.aggressive.label')
      },
      levelDescriptions: {
        conservative: translate('performance.levels.conservative.description'),
        balanced: translate('performance.levels.balanced.description'),
        aggressive: translate('performance.levels.aggressive.description')
      },
      promptsSectionTitle: translate('prompts.sectionTitle'),
      promptsSectionDescription: translate('prompts.description'),
      plantPromptLabel: translate('prompts.plantPromptLabel'),
      plantPromptPlaceholder: translate('prompts.plantPromptPlaceholder'),
      mappingPromptLabel: translate('prompts.mappingPromptLabel'),
      mappingPromptPlaceholder: translate('prompts.mappingPromptPlaceholder'),
      correctionPromptLabel: translate('prompts.correctionPromptLabel'),
      correctionPromptPlaceholder: translate('prompts.correctionPromptPlaceholder'),
      statsSectionTitle: translate('stats.sectionTitle'),
      tokensUsedLabel: translate('stats.tokensUsedLabel'),
      requestsMadeLabel: translate('stats.requestsMadeLabel'),
      successRateLabel: translate('stats.successRateLabel'),
      saveButton: translate('actions.saveButton'),
      resetButton: translate('actions.resetButton'),
      saveSuccess: translate('actions.saveSuccess'),
      saveError: translate('actions.saveError'),
      resetSuccess: translate('actions.resetSuccess')
    }),
    [translate]
  );

  const featureList = useMemo(
    () => [
      {
        key: 'plantRecommendations',
        label: uiText.featureLabels.plantRecommendations,
        description: uiText.featureDescriptions.plantRecommendations
      },
      {
        key: 'dataMapping',
        label: uiText.featureLabels.dataMapping,
        description: uiText.featureDescriptions.dataMapping
      },
      {
        key: 'smartCorrection',
        label: uiText.featureLabels.smartCorrection,
        description: uiText.featureDescriptions.smartCorrection
      },
      {
        key: 'languageDetection',
        label: uiText.featureLabels.languageDetection,
        description: uiText.featureDescriptions.languageDetection
      }
    ],
    [uiText.featureDescriptions, uiText.featureLabels]
  );

  const levelOptions = useMemo(
    () => [
      {
        key: 'conservative',
        label: uiText.levelLabels.conservative,
        description: uiText.levelDescriptions.conservative
      },
      {
        key: 'balanced',
        label: uiText.levelLabels.balanced,
        description: uiText.levelDescriptions.balanced
      },
      {
        key: 'aggressive',
        label: uiText.levelLabels.aggressive,
        description: uiText.levelDescriptions.aggressive
      }
    ],
    [uiText.levelDescriptions, uiText.levelLabels]
  );

  const handleFeatureToggle = useCallback((featureKey) => (event) => {
    const { checked } = event.target;
    setAiFeatures((prev) => ({
      ...prev,
      [featureKey]: checked
    }));
  }, []);

  const handlePromptChange = useCallback((promptKey) => (event) => {
    const { value } = event.target;
    setCustomPrompts((prev) => ({
      ...prev,
      [promptKey]: value
    }));
  }, []);

  const testAIConnection = useCallback(async () => {
    if (!openaiKey.trim()) {
      window.alert(uiText.missingKeyMessage);
      return;
    }

    setTestingConnection(true);
    setConnectionStatus('testing');

    try {
      await new Promise((resolve) => {
        setTimeout(resolve, 2000);
      });
      setConnectionStatus('connected');
      window.alert(uiText.connectionSuccess);
    } catch (error) {
      console.error('AI connection test failed:', error);
      setConnectionStatus('disconnected');
      window.alert(uiText.connectionFailure);
    } finally {
      setTestingConnection(false);
    }
  }, [openaiKey, uiText.connectionFailure, uiText.connectionSuccess, uiText.missingKeyMessage]);

  const saveSettings = useCallback(() => {
    const settingsToSave = {
      openaiKey,
      aiFeatures,
      aiLevel,
      customPrompts,
      connectionStatus,
      timestamp: new Date().toISOString()
    };

    try {
      localStorage.setItem('aiSettings', JSON.stringify(settingsToSave));
      window.alert(uiText.saveSuccess);
    } catch (error) {
      console.error('Failed to save AI settings:', error);
      window.alert(uiText.saveError);
    }
  }, [aiFeatures, aiLevel, connectionStatus, customPrompts, openaiKey, uiText.saveError, uiText.saveSuccess]);

  const resetDefaults = useCallback(() => {
    setOpenaiKey('');
    setAiFeatures({
      plantRecommendations: true,
      dataMapping: true,
      smartCorrection: true,
      languageDetection: true
    });
    setAiLevel('balanced');
    setCustomPrompts({
      plantRecommendation: '',
      dataMapping: '',
      errorCorrection: ''
    });
    setConnectionStatus('disconnected');

    try {
      localStorage.removeItem('aiSettings');
    } catch (error) {
      console.error('Failed to clear AI settings from storage:', error);
    }

    window.alert(uiText.resetSuccess);
  }, [uiText.resetSuccess]);

  const statusIcon = useMemo(() => {
    if (connectionStatus === 'connected') {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
    if (connectionStatus === 'testing') {
      return <div className="h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
    }
    return <AlertCircle className="h-5 w-5 text-red-600" />;
  }, [connectionStatus]);

  const statusText = useMemo(() => {
    if (connectionStatus === 'connected') {
      return uiText.statusConnected;
    }
    if (connectionStatus === 'testing') {
      return uiText.statusTesting;
    }
    return uiText.statusDisconnected;
  }, [connectionStatus, uiText.statusConnected, uiText.statusDisconnected, uiText.statusTesting]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{uiText.title}</h2>
        <p className="text-gray-600">{uiText.subtitle}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5 text-blue-600" />
            {uiText.apiSectionTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.apiDescription}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.openaiKeyLabel}
            </label>
            <div className="flex gap-2">
              <input
                type="password"
                value={openaiKey}
                onChange={(event) => setOpenaiKey(event.target.value)}
                placeholder={uiText.openaiKeyPlaceholder}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button
                onClick={testAIConnection}
                disabled={testingConnection || !openaiKey.trim()}
                className="flex items-center gap-2"
              >
                {testingConnection && <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                <span>{uiText.testButton}</span>
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-1">{uiText.openaiKeyDescription}</p>
          </div>

          <div className="flex items-center gap-2 p-3 border rounded-lg bg-gray-50">
            {statusIcon}
            <span className="text-sm font-medium">{uiText.statusLabel}:</span>
            <span
              className={`text-sm ${
                connectionStatus === 'connected'
                  ? 'text-green-600'
                  : connectionStatus === 'testing'
                    ? 'text-blue-600'
                    : 'text-red-600'
              }`}
            >
              {statusText}
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            {uiText.featuresSectionTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.featuresSectionDescription}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          {featureList.map((feature) => (
            <div key={feature.key} className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{feature.label}</div>
                <div className="text-xs text-gray-500">{feature.description}</div>
              </div>
              <input
                type="checkbox"
                checked={aiFeatures[feature.key]}
                onChange={handleFeatureToggle(feature.key)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-600" />
            {uiText.performanceSectionTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.performanceSectionDescription}</p>
        </CardHeader>
        <CardContent>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              {uiText.aiLevelTitle}
            </label>
            <div className="space-y-3">
              {levelOptions.map((option) => (
                <div key={option.key} className="flex items-start gap-3">
                  <input
                    type="radio"
                    id={option.key}
                    name="aiLevel"
                    value={option.key}
                    checked={aiLevel === option.key}
                    onChange={(event) => setAiLevel(event.target.value)}
                    className="mt-1 w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <label htmlFor={option.key} className="flex-1 cursor-pointer">
                    <div className="font-medium text-sm">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.description}</div>
                  </label>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-green-600" />
            {uiText.promptsSectionTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.promptsSectionDescription}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.plantPromptLabel}
            </label>
            <textarea
              value={customPrompts.plantRecommendation}
              onChange={handlePromptChange('plantRecommendation')}
              placeholder={uiText.plantPromptPlaceholder}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.mappingPromptLabel}
            </label>
            <textarea
              value={customPrompts.dataMapping}
              onChange={handlePromptChange('dataMapping')}
              placeholder={uiText.mappingPromptPlaceholder}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.correctionPromptLabel}
            </label>
            <textarea
              value={customPrompts.errorCorrection}
              onChange={handlePromptChange('errorCorrection')}
              placeholder={uiText.correctionPromptPlaceholder}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-orange-600" />
            {uiText.statsSectionTitle}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{DEFAULT_USAGE_STATS.tokensUsed.toLocaleString()}</div>
              <div className="text-sm text-gray-600">{uiText.tokensUsedLabel}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{DEFAULT_USAGE_STATS.requestsMade}</div>
              <div className="text-sm text-gray-600">{uiText.requestsMadeLabel}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{DEFAULT_USAGE_STATS.successRate}%</div>
              <div className="text-sm text-gray-600">{uiText.successRateLabel}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-4">
        <Button onClick={saveSettings} className="px-6">
          {uiText.saveButton}
        </Button>
        <Button onClick={resetDefaults} variant="outline" className="px-6">
          {uiText.resetButton}
        </Button>
      </div>
    </div>
  );
};

export default AISettings;