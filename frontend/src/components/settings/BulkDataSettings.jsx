import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Archive, Download, Upload, Database, Settings as SettingsIcon, Check } from 'lucide-react';
import ExcelImportManager from '../ExcelImportManager';
import { useLanguage } from '../../i18n/LanguageProvider';

const translationDefaults = {
  title: 'Bulk Data Management',
  subtitle: 'Configure import, export, and data processing settings',
  tools: {
    sectionTitle: 'Import/Export Tools',
    description: 'Access bulk data management tools'
  },
  import: {
    sectionTitle: 'Import Settings',
    description: 'Configure how data is imported from Excel files',
    validationTitle: 'Data Validation',
    validationDescription: 'Set validation rules for data quality',
    backupTitle: 'Backup Settings',
    backupDescription: 'Configure automatic backups before imports',
    options: {
      validateDuplicates: {
        label: 'Validate for duplicates',
        description: 'Check for duplicate entries during import'
      },
      autoCorrectData: {
        label: 'Auto-correct data',
        description: 'Automatically fix common data errors'
      },
      requireAllFields: {
        label: 'Require all fields',
        description: 'All fields must be filled before import'
      },
      maxBatchSize: {
        label: 'Maximum batch size',
        description: 'Number of records to process at once'
      },
      enableBackup: {
        label: 'Enable automatic backup',
        description: 'Create backup before each import operation'
      }
    }
  },
  export: {
    sectionTitle: 'Export Settings',
    description: 'Configure how data is exported to files',
    options: {
      includeEmptyFields: 'Include empty fields in export',
      includeImages: 'Include images in export',
      dateFormat: 'Date format',
      compressionLevel: 'File compression level'
    },
    compressionLevels: {
      none: 'None',
      low: 'Low',
      medium: 'Medium',
      high: 'High'
    }
  },
  summary: {
    sectionTitle: 'Current Settings',
    importLabel: 'Import',
    exportLabel: 'Export'
  },
  actions: {
    save: 'Save Settings',
    reset: 'Reset Defaults',
    saveSuccess: 'Bulk data settings saved!',
    saveError: 'Unable to save bulk data settings. Please try again.',
    resetSuccess: 'Bulk data settings reset to defaults!'
  }
};

const getTranslationDefault = (path) =>
  path.split('.').reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults);

const DEFAULT_IMPORT_SETTINGS = {
  validateDuplicates: true,
  autoCorrectData: true,
  requireAllFields: false,
  maxBatchSize: 1000,
  enableBackup: true
};

const DEFAULT_EXPORT_SETTINGS = {
  includeEmptyFields: false,
  dateFormat: 'DD-MM-YYYY',
  includeImages: false,
  compressionLevel: 'medium'
};

const DATE_FORMAT_OPTIONS = [
  { value: 'DD-MM-YYYY', label: '31-12-2024' },
  { value: 'MM/DD/YYYY', label: '12/31/2024' },
  { value: 'YYYY-MM-DD', label: '2024-12-31' },
  { value: 'DD.MM.YYYY', label: '31.12.2024' }
];

const BulkDataSettings = () => {
  const { t } = useLanguage();

  const [importSettings, setImportSettings] = useState(DEFAULT_IMPORT_SETTINGS);
  const [exportSettings, setExportSettings] = useState(DEFAULT_EXPORT_SETTINGS);

  useEffect(() => {
    try {
      const storedSettings = localStorage.getItem('bulkDataSettings');
      if (!storedSettings) {
        return;
      }

      const parsedSettings = JSON.parse(storedSettings);
      if (parsedSettings.import) {
        setImportSettings((prev) => ({ ...prev, ...parsedSettings.import }));
      }
      if (parsedSettings.export) {
        setExportSettings((prev) => ({ ...prev, ...parsedSettings.export }));
      }
    } catch (error) {
      console.error('Failed to load bulk data settings from storage:', error);
    }
  }, []);

  const translate = useCallback(
    (key) => t(`settings.bulkData.${key}`, getTranslationDefault(key) ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      toolsTitle: translate('tools.sectionTitle'),
      toolsDescription: translate('tools.description'),
      importSectionTitle: translate('import.sectionTitle'),
      importDescription: translate('import.description'),
      validationTitle: translate('import.validationTitle'),
      validationDescription: translate('import.validationDescription'),
      backupTitle: translate('import.backupTitle'),
      backupDescription: translate('import.backupDescription'),
      options: {
        validateDuplicates: {
          label: translate('import.options.validateDuplicates.label'),
          description: translate('import.options.validateDuplicates.description')
        },
        autoCorrectData: {
          label: translate('import.options.autoCorrectData.label'),
          description: translate('import.options.autoCorrectData.description')
        },
        requireAllFields: {
          label: translate('import.options.requireAllFields.label'),
          description: translate('import.options.requireAllFields.description')
        },
        maxBatchSize: {
          label: translate('import.options.maxBatchSize.label'),
          description: translate('import.options.maxBatchSize.description')
        },
        enableBackup: {
          label: translate('import.options.enableBackup.label'),
          description: translate('import.options.enableBackup.description')
        }
      },
      exportSectionTitle: translate('export.sectionTitle'),
      exportDescription: translate('export.description'),
      exportOptions: {
        includeEmptyFields: translate('export.options.includeEmptyFields'),
        includeImages: translate('export.options.includeImages'),
        dateFormat: translate('export.options.dateFormat'),
        compressionLevel: translate('export.options.compressionLevel')
      },
      compressionLabels: {
        none: translate('export.compressionLevels.none'),
        low: translate('export.compressionLevels.low'),
        medium: translate('export.compressionLevels.medium'),
        high: translate('export.compressionLevels.high')
      },
      summaryTitle: translate('summary.sectionTitle'),
      summaryImportLabel: translate('summary.importLabel'),
      summaryExportLabel: translate('summary.exportLabel'),
      save: translate('actions.save'),
      reset: translate('actions.reset'),
      saveSuccess: translate('actions.saveSuccess'),
      saveError: translate('actions.saveError'),
      resetSuccess: translate('actions.resetSuccess')
    }),
    [translate]
  );

  const compressionOptions = useMemo(
    () => [
      { value: 'none', label: uiText.compressionLabels.none },
      { value: 'low', label: uiText.compressionLabels.low },
      { value: 'medium', label: uiText.compressionLabels.medium },
      { value: 'high', label: uiText.compressionLabels.high }
    ],
    [uiText.compressionLabels]
  );

  const toggleImportOption = useCallback((key) => (event) => {
    const { checked } = event.target;
    setImportSettings((prev) => ({
      ...prev,
      [key]: checked
    }));
  }, []);

  const toggleExportOption = useCallback((key) => (event) => {
    const { checked } = event.target;
    setExportSettings((prev) => ({
      ...prev,
      [key]: checked
    }));
  }, []);

  const handleBatchSizeChange = useCallback((event) => {
    const { value } = event.target;
    setImportSettings((prev) => ({
      ...prev,
      maxBatchSize: Number.parseInt(value, 10)
    }));
  }, []);

  const handleDateFormatChange = useCallback((event) => {
    const { value } = event.target;
    setExportSettings((prev) => ({
      ...prev,
      dateFormat: value
    }));
  }, []);

  const handleCompressionChange = useCallback((event) => {
    const { value } = event.target;
    setExportSettings((prev) => ({
      ...prev,
      compressionLevel: value
    }));
  }, []);

  const saveSettings = useCallback(() => {
    const settingsToSave = {
      import: importSettings,
      export: exportSettings,
      timestamp: new Date().toISOString()
    };

    try {
      localStorage.setItem('bulkDataSettings', JSON.stringify(settingsToSave));
      window.alert(uiText.saveSuccess);
    } catch (error) {
      console.error('Failed to save bulk data settings:', error);
      window.alert(uiText.saveError);
    }
  }, [exportSettings, importSettings, uiText.saveError, uiText.saveSuccess]);

  const resetDefaults = useCallback(() => {
    setImportSettings(DEFAULT_IMPORT_SETTINGS);
    setExportSettings(DEFAULT_EXPORT_SETTINGS);

    try {
      localStorage.removeItem('bulkDataSettings');
    } catch (error) {
      console.error('Failed to clear bulk data settings from storage:', error);
    }

    window.alert(uiText.resetSuccess);
  }, [uiText.resetSuccess]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{uiText.title}</h2>
        <p className="text-gray-600">{uiText.subtitle}</p>
      </div>

      {/* Import/Export Tools */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Archive className="h-5 w-5 text-blue-600" />
            {uiText.toolsTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.toolsDescription}</p>
        </CardHeader>
        <CardContent>
          <ExcelImportManager />
        </CardContent>
      </Card>

      {/* Import Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5 text-green-600" />
            {uiText.importSectionTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.importDescription}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Validation Settings */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600" />
              {uiText.validationTitle}
            </h4>
            <p className="text-xs text-gray-500 mb-3">{uiText.validationDescription}</p>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{uiText.options.validateDuplicates.label}</div>
                  <div className="text-xs text-gray-500">{uiText.options.validateDuplicates.description}</div>
                </div>
                <input
                  type="checkbox"
                  checked={importSettings.validateDuplicates}
                  onChange={toggleImportOption('validateDuplicates')}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{uiText.options.autoCorrectData.label}</div>
                  <div className="text-xs text-gray-500">{uiText.options.autoCorrectData.description}</div>
                </div>
                <input
                  type="checkbox"
                  checked={importSettings.autoCorrectData}
                  onChange={toggleImportOption('autoCorrectData')}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{uiText.options.requireAllFields.label}</div>
                  <div className="text-xs text-gray-500">{uiText.options.requireAllFields.description}</div>
                </div>
                <input
                  type="checkbox"
                  checked={importSettings.requireAllFields}
                  onChange={toggleImportOption('requireAllFields')}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Batch Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.options.maxBatchSize.label}
            </label>
            <p className="text-xs text-gray-500 mb-2">{uiText.options.maxBatchSize.description}</p>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="100"
                max="5000"
                step="100"
                value={importSettings.maxBatchSize}
                onChange={handleBatchSizeChange}
                className="flex-1"
              />
              <span className="w-16 text-sm font-medium text-gray-900">{importSettings.maxBatchSize}</span>
            </div>
          </div>

          {/* Backup Settings */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-600" />
              {uiText.backupTitle}
            </h4>
            <p className="text-xs text-gray-500 mb-3">{uiText.backupDescription}</p>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.options.enableBackup.label}</div>
                <div className="text-xs text-gray-500">{uiText.options.enableBackup.description}</div>
              </div>
              <input
                type="checkbox"
                checked={importSettings.enableBackup}
                  onChange={toggleImportOption('enableBackup')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-purple-600" />
            {uiText.exportSectionTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.exportDescription}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Export Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.exportOptions.includeEmptyFields}</div>
              </div>
              <input
                type="checkbox"
                  checked={exportSettings.includeEmptyFields}
                  onChange={toggleExportOption('includeEmptyFields')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.exportOptions.includeImages}</div>
              </div>
              <input
                type="checkbox"
                  checked={exportSettings.includeImages}
                  onChange={toggleExportOption('includeImages')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Date Format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.exportOptions.dateFormat}
            </label>
            <select
              value={exportSettings.dateFormat}
              onChange={handleDateFormatChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {DATE_FORMAT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          {/* Compression Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.exportOptions.compressionLevel}
            </label>
            <select
              value={exportSettings.compressionLevel}
              onChange={handleCompressionChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {compressionOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Current Settings Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5 text-gray-600" />
            {uiText.summaryTitle}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-sm text-gray-900 mb-3">{uiText.summaryImportLabel}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Duplicaten valideren:</span>
                  <span className={importSettings.validateDuplicates ? 'text-green-600' : 'text-red-600'}>
                    {importSettings.validateDuplicates ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Auto-correctie:</span>
                  <span className={importSettings.autoCorrectData ? 'text-green-600' : 'text-red-600'}>
                    {importSettings.autoCorrectData ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Batch grootte:</span>
                  <span className="text-gray-900 font-medium">{importSettings.maxBatchSize}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-900 mb-3">{uiText.summaryExportLabel}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Datumformaat:</span>
                  <span className="text-gray-900 font-medium">{exportSettings.dateFormat}</span>
                </div>
                <div className="flex justify-between">
                  <span>Compressie:</span>
                  <span className="text-gray-900 font-medium capitalize">{exportSettings.compressionLevel}</span>
                </div>
                <div className="flex justify-between">
                  <span>Afbeeldingen:</span>
                  <span className={exportSettings.includeImages ? 'text-green-600' : 'text-red-600'}>
                    {exportSettings.includeImages ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
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

export default BulkDataSettings;