import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  BarChart3, 
  FileText, 
  Printer, 
  Calendar,
  Settings as SettingsIcon,
  Download,
  Mail,
  Image,
  Clock
} from 'lucide-react'

const ReportSettings = ({ language = 'nl' }) => {
  const [reportSettings, setReportSettings] = useState({
    defaultFormat: 'pdf',
    includeImages: true,
    includePricing: true,
    autoGenerateQuotes: true,
    language: 'nl',
    companyBranding: true,
    watermark: false
  })

  const [templates, setTemplates] = useState({
    projectReport: true,
    quoteTemplate: true,
    invoiceTemplate: true,
    plantCatalog: false,
    maintenanceSchedule: false
  })

  const [automation, setAutomation] = useState({
    scheduleReports: false,
    emailReports: false,
    frequency: 'weekly',
    recipients: ''
  })

  const translations = {
    en: {
      title: 'Report Generation Settings',
      subtitle: 'Configure report templates, formats, and automation',
      formatsSection: 'Output Formats',
      formatsDesc: 'Configure default report formats and options',
      templatesSection: 'Report Templates',
      templatesDesc: 'Enable or disable available report templates',
      automationSection: 'Report Automation',
      automationDesc: 'Configure automated report generation and delivery',
      brandingSection: 'Branding & Styling',
      brandingDesc: 'Customize report appearance and company branding',
      defaultFormat: 'Default Format',
      includeImages: 'Include Images',
      includeImagesDesc: 'Add project photos and plant images to reports',
      includePricing: 'Include Pricing Information',
      includePricingDesc: 'Add cost estimates and pricing details',
      autoGenerateQuotes: 'Auto-generate Quotes',
      autoGenerateQuotesDesc: 'Automatically create quotes from project data',
      reportLanguage: 'Report Language',
      companyBranding: 'Company Branding',
      companyBrandingDesc: 'Include company logo and colors',
      watermark: 'Add Watermark',
      watermarkDesc: 'Add watermark to draft reports',
      projectReport: 'Project Report Template',
      projectReportDesc: 'Comprehensive project documentation',
      quoteTemplate: 'Quote Template',
      quoteTemplateDesc: 'Professional quote generation',
      invoiceTemplate: 'Invoice Template',
      invoiceTemplateDesc: 'Invoice with Dutch VAT calculation',
      plantCatalog: 'Plant Catalog Template',
      plantCatalogDesc: 'Detailed plant information sheets',
      maintenanceSchedule: 'Maintenance Schedule Template',
      maintenanceScheduleDesc: 'Plant care and maintenance schedules',
      scheduleReports: 'Schedule Automatic Reports',
      scheduleReportsDesc: 'Generate reports automatically on schedule',
      emailReports: 'Email Reports Automatically',
      emailReportsDesc: 'Send reports via email to specified recipients',
      frequency: 'Report Frequency',
      recipients: 'Email Recipients',
      recipientsPlaceholder: 'Enter email addresses separated by commas',
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      quarterly: 'Quarterly',
      saveSettings: 'Save Settings',
      resetDefaults: 'Reset Defaults',
      previewReport: 'Preview Report',
      exportTemplate: 'Export Template',
      currentSettings: 'Current Settings Summary',
      enabledTemplates: 'Enabled Templates',
      outputSettings: 'Output Settings'
    },
    nl: {
      title: 'Rapportage Generatie Instellingen',
      subtitle: 'Configureer rapportsjablonen, formaten en automatisering',
      formatsSection: 'Uitvoerformaten',
      formatsDesc: 'Configureer standaard rapportformaten en opties',
      templatesSection: 'Rapportsjablonen',
      templatesDesc: 'Schakel beschikbare rapportsjablonen in of uit',
      automationSection: 'Rapport Automatisering',
      automationDesc: 'Configureer geautomatiseerde rapportgeneratie en levering',
      brandingSection: 'Branding & Styling',
      brandingDesc: 'Pas rapportweergave en bedrijfsbranding aan',
      defaultFormat: 'Standaardformaat',
      includeImages: 'Afbeeldingen Opnemen',
      includeImagesDesc: 'Voeg projectfoto\'s en plantafbeeldingen toe aan rapporten',
      includePricing: 'Prijsinformatie Opnemen',
      includePricingDesc: 'Voeg kostenramingen en prijsdetails toe',
      autoGenerateQuotes: 'Automatisch Offertes Genereren',
      autoGenerateQuotesDesc: 'Maak automatisch offertes van projectgegevens',
      reportLanguage: 'Rapporttaal',
      companyBranding: 'Bedrijfsbranding',
      companyBrandingDesc: 'Voeg bedrijfslogo en kleuren toe',
      watermark: 'Watermerk Toevoegen',
      watermarkDesc: 'Voeg watermerk toe aan conceptrapporten',
      projectReport: 'Projectrapport Sjabloon',
      projectReportDesc: 'Uitgebreide projectdocumentatie',
      quoteTemplate: 'Offerte Sjabloon',
      quoteTemplateDesc: 'Professionele offertegeneratie',
      invoiceTemplate: 'Factuur Sjabloon',
      invoiceTemplateDesc: 'Factuur met Nederlandse BTW-berekening',
      plantCatalog: 'Plantencatalogus Sjabloon',
      plantCatalogDesc: 'Gedetailleerde plantinformatiesheets',
      maintenanceSchedule: 'Onderhoudsschema Sjabloon',
      maintenanceScheduleDesc: 'Plantenverzorging en onderhoudsschema\'s',
      scheduleReports: 'Plan Automatische Rapporten',
      scheduleReportsDesc: 'Genereer rapporten automatisch volgens schema',
      emailReports: 'E-mail Rapporten Automatisch',
      emailReportsDesc: 'Verstuur rapporten via e-mail naar opgegeven ontvangers',
      frequency: 'Rapportfrequentie',
      recipients: 'E-mail Ontvangers',
      recipientsPlaceholder: 'Voer e-mailadressen in gescheiden door komma\'s',
      daily: 'Dagelijks',
      weekly: 'Wekelijks',
      monthly: 'Maandelijks',
      quarterly: 'Kwartaal',
      saveSettings: 'Instellingen Opslaan',
      resetDefaults: 'Standaardwaarden Herstellen',
      previewReport: 'Rapport Voorvertoning',
      exportTemplate: 'Sjabloon Exporteren',
      currentSettings: 'Huidige Instellingen Overzicht',
      enabledTemplates: 'Ingeschakelde Sjablonen',
      outputSettings: 'Uitvoerinstellingen'
    }
  }

  const t = translations[language]

  const saveSettings = () => {
    const settings = {
      reportSettings,
      templates,
      automation,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('reportSettings', JSON.stringify(settings))
    alert(language === 'nl' ? 'Rapportinstellingen opgeslagen!' : 'Report settings saved!')
  }

  const resetDefaults = () => {
    setReportSettings({
      defaultFormat: 'pdf',
      includeImages: true,
      includePricing: true,
      autoGenerateQuotes: true,
      language: 'nl',
      companyBranding: true,
      watermark: false
    })
    setTemplates({
      projectReport: true,
      quoteTemplate: true,
      invoiceTemplate: true,
      plantCatalog: false,
      maintenanceSchedule: false
    })
    setAutomation({
      scheduleReports: false,
      emailReports: false,
      frequency: 'weekly',
      recipients: ''
    })
    localStorage.removeItem('reportSettings')
  }

  const formatOptions = [
    { value: 'pdf', label: 'PDF' },
    { value: 'docx', label: 'Word (DOCX)' },
    { value: 'xlsx', label: 'Excel (XLSX)' },
    { value: 'html', label: 'HTML' }
  ]

  const languageOptions = [
    { value: 'nl', label: 'Nederlands' },
    { value: 'en', label: 'English' }
  ]

  const frequencyOptions = [
    { value: 'daily', label: t.daily },
    { value: 'weekly', label: t.weekly },
    { value: 'monthly', label: t.monthly },
    { value: 'quarterly', label: t.quarterly }
  ]

  const templateList = [
    {
      key: 'projectReport',
      name: t.projectReport,
      description: t.projectReportDesc,
      icon: <FileText className="h-5 w-5 text-blue-600" />,
      enabled: templates.projectReport
    },
    {
      key: 'quoteTemplate',
      name: t.quoteTemplate,
      description: t.quoteTemplateDesc,
      icon: <BarChart3 className="h-5 w-5 text-green-600" />,
      enabled: templates.quoteTemplate
    },
    {
      key: 'invoiceTemplate',
      name: t.invoiceTemplate,
      description: t.invoiceTemplateDesc,
      icon: <Printer className="h-5 w-5 text-purple-600" />,
      enabled: templates.invoiceTemplate
    },
    {
      key: 'plantCatalog',
      name: t.plantCatalog,
      description: t.plantCatalogDesc,
      icon: <Image className="h-5 w-5 text-orange-600" />,
      enabled: templates.plantCatalog
    },
    {
      key: 'maintenanceSchedule',
      name: t.maintenanceSchedule,
      description: t.maintenanceScheduleDesc,
      icon: <Calendar className="h-5 w-5 text-red-600" />,
      enabled: templates.maintenanceSchedule
    }
  ]

  const enabledTemplatesCount = Object.values(templates).filter(Boolean).length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{t.title}</h2>
        <p className="text-gray-600">{t.subtitle}</p>
      </div>

      {/* Output Formats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-blue-600" />
            {t.formatsSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.formatsDesc}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Default Format */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.defaultFormat}
            </label>
            <select
              value={reportSettings.defaultFormat}
              onChange={(e) => setReportSettings(prev => ({...prev, defaultFormat: e.target.value}))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {formatOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          {/* Report Language */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.reportLanguage}
            </label>
            <select
              value={reportSettings.language}
              onChange={(e) => setReportSettings(prev => ({...prev, language: e.target.value}))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          {/* Content Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.includeImages}</div>
                <div className="text-xs text-gray-500">{t.includeImagesDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={reportSettings.includeImages}
                onChange={(e) => setReportSettings(prev => ({...prev, includeImages: e.target.checked}))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.includePricing}</div>
                <div className="text-xs text-gray-500">{t.includePricingDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={reportSettings.includePricing}
                onChange={(e) => setReportSettings(prev => ({...prev, includePricing: e.target.checked}))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.autoGenerateQuotes}</div>
                <div className="text-xs text-gray-500">{t.autoGenerateQuotesDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={reportSettings.autoGenerateQuotes}
                onChange={(e) => setReportSettings(prev => ({...prev, autoGenerateQuotes: e.target.checked}))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Branding & Styling */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Image className="h-5 w-5 text-purple-600" />
            {t.brandingSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.brandingDesc}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-sm">{t.companyBranding}</div>
              <div className="text-xs text-gray-500">{t.companyBrandingDesc}</div>
            </div>
            <input
              type="checkbox"
              checked={reportSettings.companyBranding}
              onChange={(e) => setReportSettings(prev => ({...prev, companyBranding: e.target.checked}))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-sm">{t.watermark}</div>
              <div className="text-xs text-gray-500">{t.watermarkDesc}</div>
            </div>
            <input
              type="checkbox"
              checked={reportSettings.watermark}
              onChange={(e) => setReportSettings(prev => ({...prev, watermark: e.target.checked}))}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>
        </CardContent>
      </Card>

      {/* Report Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-green-600" />
            {t.templatesSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.templatesDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {templateList.map((template) => (
              <div key={template.key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  {template.icon}
                  <div>
                    <div className="font-medium text-sm">{template.name}</div>
                    <div className="text-xs text-gray-500">{template.description}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={template.enabled}
                    onChange={(e) => setTemplates(prev => ({...prev, [template.key]: e.target.checked}))}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <button className="px-3 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded">
                    {t.previewReport}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Report Automation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-orange-600" />
            {t.automationSection}
          </CardTitle>
          <p className="text-sm text-gray-600">{t.automationDesc}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Schedule Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.scheduleReports}</div>
                <div className="text-xs text-gray-500">{t.scheduleReportsDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={automation.scheduleReports}
                onChange={(e) => setAutomation(prev => ({...prev, scheduleReports: e.target.checked}))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{t.emailReports}</div>
                <div className="text-xs text-gray-500">{t.emailReportsDesc}</div>
              </div>
              <input
                type="checkbox"
                checked={automation.emailReports}
                onChange={(e) => setAutomation(prev => ({...prev, emailReports: e.target.checked}))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>

          {(automation.scheduleReports || automation.emailReports) && (
            <>
              {/* Frequency */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t.frequency}
                </label>
                <select
                  value={automation.frequency}
                  onChange={(e) => setAutomation(prev => ({...prev, frequency: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {frequencyOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              {/* Email Recipients */}
              {automation.emailReports && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t.recipients}
                  </label>
                  <input
                    type="text"
                    value={automation.recipients}
                    onChange={(e) => setAutomation(prev => ({...prev, recipients: e.target.value}))}
                    placeholder={t.recipientsPlaceholder}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}
            </>
          )}
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
              <h4 className="font-semibold text-sm text-gray-900 mb-3">{t.outputSettings}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Formaat:</span>
                  <span className="text-gray-900 font-medium uppercase">{reportSettings.defaultFormat}</span>
                </div>
                <div className="flex justify-between">
                  <span>Taal:</span>
                  <span className="text-gray-900 font-medium">{reportSettings.language === 'nl' ? 'Nederlands' : 'English'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Afbeeldingen:</span>
                  <span className={reportSettings.includeImages ? 'text-green-600' : 'text-red-600'}>
                    {reportSettings.includeImages ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Prijzen:</span>
                  <span className={reportSettings.includePricing ? 'text-green-600' : 'text-red-600'}>
                    {reportSettings.includePricing ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-900 mb-3">{t.enabledTemplates}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Actieve sjablonen:</span>
                  <span className="text-gray-900 font-medium">{enabledTemplatesCount}/5</span>
                </div>
                <div className="flex justify-between">
                  <span>Automatisering:</span>
                  <span className={automation.scheduleReports ? 'text-green-600' : 'text-red-600'}>
                    {automation.scheduleReports ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>E-mail verzending:</span>
                  <span className={automation.emailReports ? 'text-green-600' : 'text-red-600'}>
                    {automation.emailReports ? '✓' : '✗'}
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
        <button
          onClick={() => alert(language === 'nl' ? 'Exportfunctie komt binnenkort!' : 'Export feature coming soon!')}
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
        >
          {t.exportTemplate}
        </button>
      </div>
    </div>
  )
}

export default ReportSettings