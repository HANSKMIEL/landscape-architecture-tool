import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Archive, 
  FileSpreadsheet, 
  Download, 
  Upload, 
  Database,
  Settings as SettingsIcon,
  Check,
  AlertCircle,
  FileText,
  Filter
} from 'lucide-react'
import ExcelImportManager from '../ExcelImportManager'

const BulkDataSettings = ({ language = 'nl' }) => {
  const [importSettings, setImportSettings] = useState({
    validateDuplicates: true,
    autoCorrectData: true,
    requireAllFields: false,
    maxBatchSize: 1000,
    enableBackup: true
  })

  const [exportSettings, setExportSettings] = useState({
    includeEmptyFields: false,
    dateFormat: 'DD-MM-YYYY',
    includeImages: false,
    compressionLevel: 'medium'
  })

  const translations = {
    en: {
      title: 'Bulk Data Management',
      subtitle: 'Configure import, export, and data processing settings',
      importSection: 'Import Settings',
      importDesc: 'Configure how data is imported from Excel files',
      exportSection: 'Export Settings', 
      exportDesc: 'Configure how data is exported to files',
      validationSection: 'Data Validation',
      validationDesc: 'Set validation rules for data quality',
      backupSection: 'Backup Settings',
      backupDesc: 'Configure automatic backups before imports',
      validateDuplicates: 'Validate for duplicates',
      validateDuplicatesDesc: 'Check for duplicate entries during import',
      autoCorrectData: 'Auto-correct data',
      autoCorrectDataDesc: 'Automatically fix common data errors',
      requireAllFields: 'Require all fields',
      requireAllFieldsDesc: 'All fields must be filled before import',
      maxBatchSize: 'Maximum batch size',
      maxBatchSizeDesc: 'Number of records to process at once',
      enableBackup: 'Enable automatic backup',
      enableBackupDesc: 'Create backup before each import operation',
      includeEmptyFields: 'Include empty fields in export',
      dateFormat: 'Date format',
      includeImages: 'Include images in export',
      compressionLevel: 'File compression level',
      none: 'None',
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      saveSettings: 'Save Settings',
      resetDefaults: 'Reset Defaults',
      currentSettings: 'Current Settings',
      importExportTools: 'Import/Export Tools',
      toolsDesc: 'Access bulk data management tools'
    },
    nl: {
      title: 'Bulkgegevensbeheer',
      subtitle: 'Configureer import-, export- en gegevensverwerkingsinstellingen',
      importSection: 'Importinstellingen',
      importDesc: 'Configureer hoe gegevens uit Excel-bestanden worden geïmporteerd',
      exportSection: 'Exportinstellingen',
      exportDesc: 'Configureer hoe gegevens naar bestanden worden geëxporteerd',
      validationSection: 'Gegevensvalidatie',
      validationDesc: 'Stel validatieregels in voor gegevenskwaliteit',
      backupSection: 'Back-up Instellingen',
      backupDesc: 'Configureer automatische back-ups voor imports',
      validateDuplicates: 'Controleer op duplicaten',
      validateDuplicatesDesc: 'Controleer op dubbele invoer tijdens import',
      autoCorrectData: 'Automatisch corrigeren',
      autoCorrectDataDesc: 'Corrigeer automatisch veelvoorkomende gegevensfouten',
      requireAllFields: 'Alle velden vereist',
      requireAllFieldsDesc: 'Alle velden moeten zijn ingevuld voor import',
      maxBatchSize: 'Maximale batchgrootte',
      maxBatchSizeDesc: 'Aantal records om tegelijk te verwerken',
      enableBackup: 'Automatische back-up inschakelen',
      enableBackupDesc: 'Maak back-up voor elke importbewerking',
      includeEmptyFields: 'Lege velden opnemen in export',
      dateFormat: 'Datumformaat',
      includeImages: 'Afbeeldingen opnemen in export',
      compressionLevel: 'Bestandscompressieniveau',
      none: 'Geen',
      low: 'Laag',
      medium: 'Gemiddeld',
      high: 'Hoog',
      saveSettings: 'Instellingen Opslaan',
      resetDefaults: 'Standaardwaarden Herstellen',
      currentSettings: 'Huidige Instellingen',
      importExportTools: 'Import/Export Hulpmiddelen',
      toolsDesc: 'Toegang tot bulkgegevensbeheer hulpmiddelen'
    }
  }

  const t = translations[language]

  const saveSettings = () => {
    const settings = {
      import: importSettings,
      export: exportSettings,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('bulkDataSettings', JSON.stringify(settings))
    alert(language === 'nl' ? 'Instellingen opgeslagen!' : 'Settings saved!')
  }

  const resetDefaults = () => {
    setImportSettings({
      validateDuplicates: true,
      autoCorrectData: true,
      requireAllFields: false,
      maxBatchSize: 1000,
      enableBackup: true
    })
    setExportSettings({
      includeEmptyFields: false,
      dateFormat: 'DD-MM-YYYY',
      includeImages: false,
      compressionLevel: 'medium'
    })
    localStorage.removeItem('bulkDataSettings')
  }

  const compressionOptions = [
    { value: 'none', label: t.none },
    { value: 'low', label: t.low },
    { value: 'medium', label: t.medium },
    { value: 'high', label: t.high }
  ]

  const dateFormatOptions = [
    { value: 'DD-MM-YYYY', label: '31-12-2024' },
    { value: 'MM/DD/YYYY', label: '12/31/2024' },
    { value: 'YYYY-MM-DD', label: '2024-12-31' },
    { value: 'DD.MM.YYYY', label: '31.12.2024' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{t.title}</h2>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      {/* Import/Export Tools */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Archive className="h-5 w-5 text-blue-600" />
            {t.importExportTools}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.toolsDesc}</p>
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
            {t.importSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.importDesc}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Validation Settings */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Check className="h-4 w-4 text-green-600" />
              {t.validationSection}
            </h4>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{t.validateDuplicates}</div>
                  <div className="text-xs text-gray-500">{t.validateDuplicatesDesc}</div>
                </div>
                <input
                  type="checkbox"
                  checked={importSettings.validateDuplicates}
                  onChange={(e) => setImportSettings({...importSettings, validateDuplicates: e.target.checked})}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{t.autoCorrectData}</div>
                  <div className="text-xs text-gray-500">{t.autoCorrectDataDesc}</div>
                </div>
                <input
                  type="checkbox"
                  checked={importSettings.autoCorrectData}
                  onChange={(e) => setImportSettings({...importSettings, autoCorrectData: e.target.checked})}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{t.requireAllFields}</div>
                  <div className="text-xs text-gray-500">{t.requireAllFieldsDesc}</div>
                </div>
                <input
                  type="checkbox"
                  checked={importSettings.requireAllFields}
                  onChange={(e) => setImportSettings({...importSettings, requireAllFields: e.target.checked})}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Batch Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.maxBatchSize}
            </label>
            <p className="text-xs text-gray-500 mb-2">{t.maxBatchSizeDesc}</p>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="100"
                max="5000"
                step="100"
                value={importSettings.maxBatchSize}
                onChange={(e) => setImportSettings({...importSettings, maxBatchSize: parseInt(e.target.value)})}
                className="flex-1"
              />
              <span className="w-16 text-sm font-medium text-gray-900">{importSettings.maxBatchSize}</span>
            </div>
          </div>

          {/* Backup Settings */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-600" />
              {t.backupSection}
            </h4>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.enableBackup}</div>
                <div className="text-xs text-gray-500">{t.enableBackupDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={importSettings.enableBackup}
                onChange={(e) => setImportSettings({...importSettings, enableBackup: e.target.checked})}
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
            {t.exportSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.exportDesc}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Export Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.includeEmptyFields}</div>
              </div>
              <input
                type="checkbox"
                checked={exportSettings.includeEmptyFields}
                onChange={(e) => setExportSettings({...exportSettings, includeEmptyFields: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.includeImages}</div>
              </div>
              <input
                type="checkbox"
                checked={exportSettings.includeImages}
                onChange={(e) => setExportSettings({...exportSettings, includeImages: e.target.checked})}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Date Format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.dateFormat}
            </label>
            <select
              value={exportSettings.dateFormat}
              onChange={(e) => setExportSettings({...exportSettings, dateFormat: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {dateFormatOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          {/* Compression Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.compressionLevel}
            </label>
            <select
              value={exportSettings.compressionLevel}
              onChange={(e) => setExportSettings({...exportSettings, compressionLevel: e.target.value})}
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
            {t.currentSettings}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-sm text-gray-900 mb-3">Import</h4>
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
              <h4 className="font-semibold text-sm text-gray-900 mb-3">Export</h4>
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

export default BulkDataSettings