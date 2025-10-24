import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  BarChart3,
  FileText,
  Printer,
  Calendar,
  Settings as SettingsIcon,
  Download,
  Image,
  Clock
} from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageProvider';

const DEFAULT_REPORT_SETTINGS = {
  defaultFormat: 'pdf',
  includeImages: true,
  includePricing: true,
  autoGenerateQuotes: true,
  language: 'nl',
  companyBranding: true,
  watermark: false
};

const DEFAULT_TEMPLATES = {
  projectReport: true,
  quoteTemplate: true,
  invoiceTemplate: true,
  plantCatalog: false,
  maintenanceSchedule: false
};

const DEFAULT_AUTOMATION = {
  scheduleReports: false,
  emailReports: false,
  frequency: 'weekly',
  recipients: ''
};

const FORMAT_LABELS = {
  pdf: 'PDF',
  docx: 'Word (DOCX)',
  xlsx: 'Excel (XLSX)',
  html: 'HTML'
};

const formatOptions = [
  { value: 'pdf', label: 'PDF' },
  { value: 'docx', label: 'Word (DOCX)' },
  { value: 'xlsx', label: 'Excel (XLSX)' },
  { value: 'html', label: 'HTML' }
];

const translationDefaults = {
  title: 'Report Generation Settings',
  subtitle: 'Configure report templates, formats, and automation',
  sections: {
    formats: {
      title: 'Output Formats',
      description: 'Configure default report formats and options'
    },
    branding: {
      title: 'Branding & Styling',
      description: 'Customize report appearance and company branding'
    },
    templates: {
      title: 'Report Templates',
      description: 'Enable or disable available report templates'
    },
    automation: {
      title: 'Report Automation',
      description: 'Configure automated report generation and delivery'
    },
    summary: {
      title: 'Current Settings Summary',
      outputTitle: 'Output Settings',
      templatesTitle: 'Enabled Templates'
    }
  },
  fields: {
    defaultFormat: 'Default Format',
    reportLanguage: 'Report Language',
    includeImages: {
      label: 'Include Images',
      description: 'Add project photos and plant images to reports'
    },
    includePricing: {
      label: 'Include Pricing Information',
      description: 'Add cost estimates and pricing details'
    },
    autoGenerateQuotes: {
      label: 'Auto-generate Quotes',
      description: 'Automatically create quotes from project data'
    },
    companyBranding: {
      label: 'Company Branding',
      description: 'Include company logo and colors'
    },
    watermark: {
      label: 'Add Watermark',
      description: 'Add watermark to draft reports'
    },
    scheduleReports: {
      label: 'Schedule Automatic Reports',
      description: 'Generate reports automatically on schedule'
    },
    emailReports: {
      label: 'Email Reports Automatically',
      description: 'Send reports via email to specified recipients'
    },
    frequency: 'Report Frequency',
    recipients: 'Email Recipients',
    recipientsPlaceholder: 'Enter email addresses separated by commas'
  },
  templates: {
    projectReport: {
      name: 'Project Report Template',
      description: 'Comprehensive project documentation'
    },
    quoteTemplate: {
      name: 'Quote Template',
      description: 'Professional quote generation'
    },
    invoiceTemplate: {
      name: 'Invoice Template',
      description: 'Invoice with Dutch VAT calculation'
    },
    plantCatalog: {
      name: 'Plant Catalog Template',
      description: 'Detailed plant information sheets'
    },
    maintenanceSchedule: {
      name: 'Maintenance Schedule Template',
      description: 'Plant care and maintenance schedules'
    },
    preview: 'Preview Report'
  },
  frequencyOptions: {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    quarterly: 'Quarterly'
  },
  buttons: {
    save: 'Save Settings',
    reset: 'Reset Defaults',
    export: 'Export Template'
  },
  alerts: {
    saveSuccess: 'Report settings saved!',
    saveError: 'Unable to save report settings. Please try again.',
    resetSuccess: 'Report settings reset to defaults!',
    exportComingSoon: 'Export feature coming soon!'
  },
  summary: {
    labels: {
      format: 'Format',
      language: 'Language',
      images: 'Images',
      pricing: 'Pricing',
      activeTemplates: 'Active templates',
      automation: 'Automation',
      email: 'Email delivery'
    },
    status: {
      enabled: 'Enabled',
      disabled: 'Disabled'
    }
  },
  languageNames: {
    nl: 'Dutch',
    en: 'English'
  }
};

const getTranslationDefault = (path) =>
  path
    .split('.')
    .reduce((acc, segment) => (acc && acc[segment] !== undefined ? acc[segment] : undefined), translationDefaults);

const ReportSettings = () => {
  const { t } = useLanguage();

  const [reportSettings, setReportSettings] = useState(DEFAULT_REPORT_SETTINGS);
  const [templates, setTemplates] = useState(DEFAULT_TEMPLATES);
  const [automation, setAutomation] = useState(DEFAULT_AUTOMATION);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('reportSettings');
      if (!stored) {
        return;
      }

      const parsed = JSON.parse(stored);
      if (parsed.reportSettings) {
        setReportSettings((prev) => ({ ...prev, ...parsed.reportSettings }));
      }
      if (parsed.templates) {
        setTemplates((prev) => ({ ...prev, ...parsed.templates }));
      }
      if (parsed.automation) {
        setAutomation((prev) => ({ ...prev, ...parsed.automation }));
      }
    } catch (error) {
      console.error('Failed to load report settings from storage:', error);
    }
  }, []);

  const translate = useCallback(
    (key) => t(`settings.report.${key}`, getTranslationDefault(key) ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      formatsTitle: translate('sections.formats.title'),
      formatsDescription: translate('sections.formats.description'),
      brandingTitle: translate('sections.branding.title'),
      brandingDescription: translate('sections.branding.description'),
      templatesTitle: translate('sections.templates.title'),
      templatesDescription: translate('sections.templates.description'),
      automationTitle: translate('sections.automation.title'),
      automationDescription: translate('sections.automation.description'),
      summaryTitle: translate('sections.summary.title'),
      summaryOutputTitle: translate('sections.summary.outputTitle'),
      summaryTemplatesTitle: translate('sections.summary.templatesTitle'),
      fields: {
        defaultFormat: translate('fields.defaultFormat'),
        reportLanguage: translate('fields.reportLanguage'),
        includeImages: {
          label: translate('fields.includeImages.label'),
          description: translate('fields.includeImages.description')
        },
        includePricing: {
          label: translate('fields.includePricing.label'),
          description: translate('fields.includePricing.description')
        },
        autoGenerateQuotes: {
          label: translate('fields.autoGenerateQuotes.label'),
          description: translate('fields.autoGenerateQuotes.description')
        },
        companyBranding: {
          label: translate('fields.companyBranding.label'),
          description: translate('fields.companyBranding.description')
        },
        watermark: {
          label: translate('fields.watermark.label'),
          description: translate('fields.watermark.description')
        },
        scheduleReports: {
          label: translate('fields.scheduleReports.label'),
          description: translate('fields.scheduleReports.description')
        },
        emailReports: {
          label: translate('fields.emailReports.label'),
          description: translate('fields.emailReports.description')
        },
        frequency: translate('fields.frequency'),
        recipients: translate('fields.recipients'),
        recipientsPlaceholder: translate('fields.recipientsPlaceholder')
      },
      templates: {
        projectReport: {
          name: translate('templates.projectReport.name'),
          description: translate('templates.projectReport.description')
        },
        quoteTemplate: {
          name: translate('templates.quoteTemplate.name'),
          description: translate('templates.quoteTemplate.description')
        },
        invoiceTemplate: {
          name: translate('templates.invoiceTemplate.name'),
          description: translate('templates.invoiceTemplate.description')
        },
        plantCatalog: {
          name: translate('templates.plantCatalog.name'),
          description: translate('templates.plantCatalog.description')
        },
        maintenanceSchedule: {
          name: translate('templates.maintenanceSchedule.name'),
          description: translate('templates.maintenanceSchedule.description')
        },
        preview: translate('templates.preview')
      },
      frequencyOptions: {
        daily: translate('frequencyOptions.daily'),
        weekly: translate('frequencyOptions.weekly'),
        monthly: translate('frequencyOptions.monthly'),
        quarterly: translate('frequencyOptions.quarterly')
      },
      buttons: {
        save: translate('buttons.save'),
        reset: translate('buttons.reset'),
        export: translate('buttons.export')
      },
      alerts: {
        saveSuccess: translate('alerts.saveSuccess'),
        saveError: translate('alerts.saveError'),
        resetSuccess: translate('alerts.resetSuccess'),
        exportComingSoon: translate('alerts.exportComingSoon')
      },
      summaryLabels: {
        format: translate('summary.labels.format'),
        language: translate('summary.labels.language'),
        images: translate('summary.labels.images'),
        pricing: translate('summary.labels.pricing'),
        activeTemplates: translate('summary.labels.activeTemplates'),
        automation: translate('summary.labels.automation'),
        email: translate('summary.labels.email')
      },
      summaryStatus: {
        enabled: translate('summary.status.enabled'),
        disabled: translate('summary.status.disabled')
      },
      languageNames: {
        nl: translate('languageNames.nl'),
        en: translate('languageNames.en')
      }
    }),
    [translate]
  );

  const languageOptions = useMemo(
    () => [
      { value: 'nl', label: uiText.languageNames.nl ?? 'Dutch' },
      { value: 'en', label: uiText.languageNames.en ?? 'English' }
    ],
    [uiText.languageNames.en, uiText.languageNames.nl]
  );

  const frequencyOptions = useMemo(
    () => [
      { value: 'daily', label: uiText.frequencyOptions.daily ?? translationDefaults.frequencyOptions.daily },
      { value: 'weekly', label: uiText.frequencyOptions.weekly ?? translationDefaults.frequencyOptions.weekly },
      { value: 'monthly', label: uiText.frequencyOptions.monthly ?? translationDefaults.frequencyOptions.monthly },
      { value: 'quarterly', label: uiText.frequencyOptions.quarterly ?? translationDefaults.frequencyOptions.quarterly }
    ],
    [uiText.frequencyOptions.daily, uiText.frequencyOptions.monthly, uiText.frequencyOptions.quarterly, uiText.frequencyOptions.weekly]
  );

  const templateList = useMemo(
    () => [
      {
        key: 'projectReport',
        name: uiText.templates.projectReport.name,
        description: uiText.templates.projectReport.description,
        icon: <FileText className="h-5 w-5 text-blue-600" />,
        enabled: templates.projectReport
      },
      {
        key: 'quoteTemplate',
        name: uiText.templates.quoteTemplate.name,
        description: uiText.templates.quoteTemplate.description,
        icon: <BarChart3 className="h-5 w-5 text-green-600" />,
        enabled: templates.quoteTemplate
      },
      {
        key: 'invoiceTemplate',
        name: uiText.templates.invoiceTemplate.name,
        description: uiText.templates.invoiceTemplate.description,
        icon: <Printer className="h-5 w-5 text-purple-600" />,
        enabled: templates.invoiceTemplate
      },
      {
        key: 'plantCatalog',
        name: uiText.templates.plantCatalog.name,
        description: uiText.templates.plantCatalog.description,
        icon: <Image className="h-5 w-5 text-orange-600" />,
        enabled: templates.plantCatalog
      },
      {
        key: 'maintenanceSchedule',
        name: uiText.templates.maintenanceSchedule.name,
        description: uiText.templates.maintenanceSchedule.description,
        icon: <Calendar className="h-5 w-5 text-red-600" />,
        enabled: templates.maintenanceSchedule
      }
    ],
    [templates.invoiceTemplate, templates.maintenanceSchedule, templates.plantCatalog, templates.projectReport, templates.quoteTemplate, uiText.templates]
  );

  const enabledTemplatesCount = useMemo(
    () => Object.values(templates).filter(Boolean).length,
    [templates]
  );

  const handleReportSettingChange = useCallback(
    (key) => (event) => {
      const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
      setReportSettings((prev) => ({
        ...prev,
        [key]: value
      }));
    },
    []
  );

  const handleTemplateToggle = useCallback(
    (key) => (event) => {
      const { checked } = event.target;
      setTemplates((prev) => ({
        ...prev,
        [key]: checked
      }));
    },
    []
  );

  const handleAutomationChange = useCallback(
    (key) => (event) => {
      const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
      setAutomation((prev) => ({
        ...prev,
        [key]: value
      }));
    },
    []
  );

  const saveSettings = useCallback(() => {
    const settingsToSave = {
      reportSettings,
      templates,
      automation,
      timestamp: new Date().toISOString()
    };

    try {
      localStorage.setItem('reportSettings', JSON.stringify(settingsToSave));
      window.alert(uiText.alerts.saveSuccess ?? translationDefaults.alerts.saveSuccess);
    } catch (error) {
      console.error('Failed to save report settings:', error);
      window.alert(uiText.alerts.saveError ?? translationDefaults.alerts.saveError);
    }
  }, [automation, reportSettings, templates, uiText.alerts.saveError, uiText.alerts.saveSuccess]);

  const resetDefaults = useCallback(() => {
    setReportSettings(DEFAULT_REPORT_SETTINGS);
    setTemplates(DEFAULT_TEMPLATES);
    setAutomation(DEFAULT_AUTOMATION);

    try {
      localStorage.removeItem('reportSettings');
    } catch (error) {
      console.error('Failed to clear report settings from storage:', error);
    }

    window.alert(uiText.alerts.resetSuccess ?? translationDefaults.alerts.resetSuccess);
  }, [uiText.alerts.resetSuccess]);

  const handleExportClick = useCallback(() => {
    window.alert(uiText.alerts.exportComingSoon ?? translationDefaults.alerts.exportComingSoon);
  }, [uiText.alerts.exportComingSoon]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">{uiText.title}</h2>
        <p className="text-gray-600">{uiText.subtitle}</p>
      </div>

      {/* Output Formats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-blue-600" />
            {uiText.formatsTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.formatsDescription}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.fields.defaultFormat}
            </label>
            <select
              value={reportSettings.defaultFormat}
              onChange={handleReportSettingChange('defaultFormat')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {formatOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {uiText.fields.reportLanguage}
            </label>
            <select
              value={reportSettings.language}
              onChange={handleReportSettingChange('language')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {languageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.fields.includeImages.label}</div>
                <div className="text-xs text-gray-500">{uiText.fields.includeImages.description}</div>
              </div>
              <input
                type="checkbox"
                checked={reportSettings.includeImages}
                onChange={handleReportSettingChange('includeImages')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.fields.includePricing.label}</div>
                <div className="text-xs text-gray-500">{uiText.fields.includePricing.description}</div>
              </div>
              <input
                type="checkbox"
                checked={reportSettings.includePricing}
                onChange={handleReportSettingChange('includePricing')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.fields.autoGenerateQuotes.label}</div>
                <div className="text-xs text-gray-500">{uiText.fields.autoGenerateQuotes.description}</div>
              </div>
              <input
                type="checkbox"
                checked={reportSettings.autoGenerateQuotes}
                onChange={handleReportSettingChange('autoGenerateQuotes')}
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
            {uiText.brandingTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.brandingDescription}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-sm">{uiText.fields.companyBranding.label}</div>
              <div className="text-xs text-gray-500">{uiText.fields.companyBranding.description}</div>
            </div>
            <input
              type="checkbox"
              checked={reportSettings.companyBranding}
              onChange={handleReportSettingChange('companyBranding')}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-sm">{uiText.fields.watermark.label}</div>
              <div className="text-xs text-gray-500">{uiText.fields.watermark.description}</div>
            </div>
            <input
              type="checkbox"
              checked={reportSettings.watermark}
              onChange={handleReportSettingChange('watermark')}
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
            {uiText.templatesTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.templatesDescription}</p>
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
                    onChange={handleTemplateToggle(template.key)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <Button variant="outline" size="sm">
                    {uiText.templates.preview}
                  </Button>
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
            {uiText.automationTitle}
          </CardTitle>
          <p className="text-sm text-gray-600">{uiText.automationDescription}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.fields.scheduleReports.label}</div>
                <div className="text-xs text-gray-500">{uiText.fields.scheduleReports.description}</div>
              </div>
              <input
                type="checkbox"
                checked={automation.scheduleReports}
                onChange={handleAutomationChange('scheduleReports')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{uiText.fields.emailReports.label}</div>
                <div className="text-xs text-gray-500">{uiText.fields.emailReports.description}</div>
              </div>
              <input
                type="checkbox"
                checked={automation.emailReports}
                onChange={handleAutomationChange('emailReports')}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </div>
          </div>

          {(automation.scheduleReports || automation.emailReports) && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {uiText.fields.frequency}
                </label>
                <select
                  value={automation.frequency}
                  onChange={handleAutomationChange('frequency')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {frequencyOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {automation.emailReports && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {uiText.fields.recipients}
                  </label>
                  <input
                    type="text"
                    value={automation.recipients}
                    onChange={handleAutomationChange('recipients')}
                    placeholder={uiText.fields.recipientsPlaceholder}
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
            {uiText.summaryTitle}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-sm text-gray-900 mb-3">{uiText.summaryOutputTitle}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.format}:</span>
                  <span className="text-gray-900 font-medium">
                    {FORMAT_LABELS[reportSettings.defaultFormat] ?? reportSettings.defaultFormat.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.language}:</span>
                  <span className="text-gray-900 font-medium">
                    {uiText.languageNames[reportSettings.language] ?? reportSettings.language.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.images}:</span>
                  <span className={reportSettings.includeImages ? 'text-green-600' : 'text-red-600'}>
                    {reportSettings.includeImages ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.pricing}:</span>
                  <span className={reportSettings.includePricing ? 'text-green-600' : 'text-red-600'}>
                    {reportSettings.includePricing ? '✓' : '✗'}
                  </span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-sm text-gray-900 mb-3">{uiText.summaryTemplatesTitle}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.activeTemplates}:</span>
                  <span className="text-gray-900 font-medium">{enabledTemplatesCount}/5</span>
                </div>
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.automation}:</span>
                  <span className={automation.scheduleReports ? 'text-green-600' : 'text-red-600'}>
                    {automation.scheduleReports ? '✓' : '✗'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>{uiText.summaryLabels.email}:</span>
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
      <div className="flex flex-wrap gap-4">
        <Button onClick={saveSettings}>{uiText.buttons.save}</Button>
        <Button variant="secondary" onClick={resetDefaults}>
          {uiText.buttons.reset}
        </Button>
        <Button
          variant="outline"
          className="border-green-600 text-green-700 hover:bg-green-50"
          onClick={handleExportClick}
        >
          {uiText.buttons.export}
        </Button>
      </div>
    </div>
  );
};

export default ReportSettings;