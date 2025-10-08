import React, { useState, useCallback, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  Download, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  FileSpreadsheet,
  Database,
  Users,
  Leaf,
  Package,
  Building,
  Eye
} from 'lucide-react'
import ApiService from '../services/api'
import { useLanguage } from '../i18n/LanguageProvider'

const ImportExport = () => {
  const { t } = useLanguage()
  const fileInputRef = useRef(null)
  
  // State management
  const [activeTab, setActiveTab] = useState('import')
  const [selectedDataType, setSelectedDataType] = useState('clients')
  const [importFile, setImportFile] = useState(null)
  const [importProgress, setImportProgress] = useState(0)
  const [importStatus, setImportStatus] = useState('idle') // idle, validating, importing, completed, error
  const [importResults, setImportResults] = useState(null)
  const [validationResults, setValidationResults] = useState(null)
  const [exportProgress, setExportProgress] = useState(0)
  const [exportStatus, setExportStatus] = useState('idle')

  // Data types configuration
  const dataTypes = [
    { 
      id: 'clients', 
      label: t('clients.title', 'Clients'), 
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    { 
      id: 'plants', 
      label: t('plants.title', 'Plants'), 
      icon: Leaf,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    { 
      id: 'products', 
      label: t('products.title', 'Products'), 
      icon: Package,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    { 
      id: 'suppliers', 
      label: t('suppliers.title', 'Suppliers'), 
      icon: Building,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    }
  ]

  // File upload handler
  const handleFileSelect = useCallback((event) => {
    const file = event.target.files[0]
    if (file) {
      setImportFile(file)
      setImportStatus('idle')
      setImportResults(null)
      setValidationResults(null)
    }
  }, [])

  // Validate import file
  const validateImportFile = useCallback(async () => {
    if (!importFile) {
      alert(t('importExport.selectFile', 'Please select a file first'))
      return
    }

    try {
      setImportStatus('validating')
      setImportProgress(25)

      const formData = new FormData()
      formData.append('file', importFile)
      formData.append('type', selectedDataType)

      const response = await fetch('/api/import/validate-file', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.error || 'Validation failed')
      }

      setValidationResults(result)
      setImportProgress(50)
      setImportStatus('validated')

    } catch (error) {
      console.error('Validation error:', error)
      setImportStatus('error')
      alert(t('importExport.validationError', 'Validation error: ') + error.message)
    }
  }, [importFile, selectedDataType, t])

  // Process import
  const processImport = useCallback(async () => {
    if (!importFile || !validationResults?.valid) {
      alert(t('importExport.validateFirst', 'Please validate the file first'))
      return
    }

    try {
      setImportStatus('importing')
      setImportProgress(75)

      const formData = new FormData()
      formData.append('file', importFile)
      formData.append('type', selectedDataType)
      formData.append('update_existing', 'true')

      const response = await fetch('/api/import/process', {
        method: 'POST',
        body: formData
      })

      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.error || 'Import failed')
      }

      setImportResults(result)
      setImportProgress(100)
      setImportStatus('completed')

    } catch (error) {
      console.error('Import error:', error)
      setImportStatus('error')
      alert(t('importExport.importError', 'Import error: ') + error.message)
    }
  }, [importFile, validationResults, selectedDataType, t])

  // Export data
  const exportData = useCallback(async (format = 'csv') => {
    try {
      setExportStatus('exporting')
      setExportProgress(25)

      // Get data from API
      let data = []
      let filename = `${selectedDataType}_export_${new Date().toISOString().split('T')[0]}.${format}`

      switch (selectedDataType) {
        case 'clients': {
          const clientsResponse = await ApiService.getClients()
          data = clientsResponse.clients || []
          break
        }
        case 'plants': {
          const plantsResponse = await ApiService.getPlants()
          data = plantsResponse.plants || []
          break
        }
        case 'products': {
          const productsResponse = await ApiService.getProducts()
          data = productsResponse.products || []
          break
        }
        case 'suppliers': {
          const suppliersResponse = await ApiService.getSuppliers()
          data = suppliersResponse.suppliers || []
          break
        }
        default:
          throw new Error('Invalid data type')
      }

      setExportProgress(75)

      if (data.length === 0) {
        alert(t('importExport.noDataToExport', 'No data available to export'))
        setExportStatus('idle')
        return
      }

      // Convert to CSV
      if (format === 'csv') {
        const headers = Object.keys(data[0])
        const csvContent = [
          headers.join(','),
          ...data.map(row => 
            headers.map(header => `"${row[header] || ''}"`).join(',')
          )
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }

      setExportProgress(100)
      setExportStatus('completed')
      
      setTimeout(() => {
        setExportStatus('idle')
        setExportProgress(0)
      }, 2000)

    } catch (error) {
      console.error('Export error:', error)
      setExportStatus('error')
      alert(t('importExport.exportError', 'Export error: ') + error.message)
    }
  }, [selectedDataType, t])

  // Download template
  const downloadTemplate = useCallback(() => {
  const templates = {
      clients: [
        { name: 'Example Client', email: 'client@example.com', phone: '+31 6 12345678', address: 'Main Street 123', city: 'Amsterdam', postal_code: '1000 AB', country: 'Netherlands' }
      ],
      plants: [
        { name: 'Acer platanoides', common_name: 'Norway Maple', category: 'tree', height_min: '15', height_max: '25', sun_requirements: 'full_sun', water_needs: 'medium', native: 'false' }
      ],
      products: [
        { name: 'Garden Soil', category: 'materials', price: '25.50', unit: 'bag', description: 'Premium garden soil mix' }
      ],
      suppliers: [
        { name: 'Garden Supply Co', contact_person: 'John Doe', email: 'info@gardensupply.com', phone: '+31 20 1234567', address: 'Industrial Road 45', city: 'Utrecht', postal_code: '3500 AB', country: 'Netherlands' }
      ]
    }

  const templateData = templates[selectedDataType]
    const headers = Object.keys(templateData[0])
    const csvContent = [
      headers.join(','),
      ...templateData.map(row => 
        headers.map(header => `"${row[header] || ''}"`).join(',')
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedDataType}_template.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }, [selectedDataType])

  // Reset import state
  const resetImport = useCallback(() => {
    setImportFile(null)
    setImportStatus('idle')
    setImportProgress(0)
    setImportResults(null)
    setValidationResults(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {t('importExport.title', 'Import & Export')}
          </h1>
          <p className="text-gray-600">
            {t('importExport.subtitle', 'Manage bulk data operations and file transfers')}
          </p>
        </div>
      </div>

      {/* Data Type Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="h-5 w-5 mr-2" />
            {t('importExport.selectDataType', 'Select Data Type')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {dataTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => setSelectedDataType(type.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedDataType === type.id
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex flex-col items-center space-y-2">
                  <type.icon className={`h-8 w-8 ${type.color}`} />
                  <span className="font-medium text-sm">{type.label}</span>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="import" className="flex items-center space-x-2">
            <Upload className="h-4 w-4" />
            <span>{t('importExport.import', 'Import')}</span>
          </TabsTrigger>
          <TabsTrigger value="export" className="flex items-center space-x-2">
            <Download className="h-4 w-4" />
            <span>{t('importExport.export', 'Export')}</span>
          </TabsTrigger>
        </TabsList>

        {/* Import Tab */}
        <TabsContent value="import" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* File Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileSpreadsheet className="h-5 w-5 mr-2" />
                  {t('importExport.fileUpload', 'File Upload')}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls,.csv"
                    onChange={handleFileSelect}
                    className="mb-2"
                  />
                  <p className="text-sm text-gray-500">
                    {t('importExport.supportedFormats', 'Supported formats: Excel (.xlsx, .xls) and CSV (.csv)')}
                  </p>
                </div>

                {importFile && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <FileText className="h-4 w-4 text-gray-600" />
                      <span className="text-sm font-medium">{importFile.name}</span>
                      <span className="text-sm text-gray-500">
                        ({(importFile.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                  </div>
                )}

                <div className="flex space-x-2">
                  <Button
                    onClick={downloadTemplate}
                    variant="outline"
                    className="flex-1"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    {t('importExport.downloadTemplate', 'Download Template')}
                  </Button>
                  <Button
                    onClick={resetImport}
                    variant="outline"
                    disabled={importStatus === 'validating' || importStatus === 'importing'}
                  >
                    {t('common.reset', 'Reset')}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Import Process */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2" />
                  {t('importExport.importProcess', 'Import Process')}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {importStatus !== 'idle' && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{t('importExport.progress', 'Progress')}</span>
                      <span>{importProgress}%</span>
                    </div>
                    <Progress value={importProgress} className="w-full" />
                  </div>
                )}

                <div className="space-y-2">
                  <Button
                    onClick={validateImportFile}
                    disabled={!importFile || importStatus === 'validating' || importStatus === 'importing'}
                    className="w-full"
                  >
                    {importStatus === 'validating' ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Eye className="h-4 w-4 mr-2" />
                    )}
                    {t('importExport.validateFile', 'Validate File')}
                  </Button>

                  <Button
                    onClick={processImport}
                    disabled={!validationResults?.valid || importStatus === 'importing'}
                    className="w-full"
                    variant={validationResults?.valid ? 'default' : 'secondary'}
                  >
                    {importStatus === 'importing' ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Upload className="h-4 w-4 mr-2" />
                    )}
                    {t('importExport.processImport', 'Process Import')}
                  </Button>
                </div>

                {/* Status Messages */}
                {importStatus === 'error' && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-2 text-red-800">
                      <AlertCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        {t('importExport.importFailed', 'Import Failed')}
                      </span>
                    </div>
                  </div>
                )}

                {importStatus === 'completed' && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-2 text-green-800">
                      <CheckCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        {t('importExport.importCompleted', 'Import Completed')}
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Validation Results */}
          {validationResults && (
            <Card>
              <CardHeader>
                <CardTitle>
                  {t('importExport.validationResults', 'Validation Results')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className={`p-3 rounded-lg ${
                    validationResults.valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}>
                    <div className={`flex items-center space-x-2 ${
                      validationResults.valid ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {validationResults.valid ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <AlertCircle className="h-4 w-4" />
                      )}
                      <span className="font-medium">
                        {validationResults.valid 
                          ? t('importExport.fileValid', 'File is valid and ready for import')
                          : t('importExport.fileInvalid', 'File has validation errors')
                        }
                      </span>
                    </div>
                  </div>

                  {validationResults.preview && (
                    <div>
                      <h4 className="font-medium mb-2">
                        {t('importExport.dataPreview', 'Data Preview')} ({validationResults.row_count} {t('common.total', 'total')})
                      </h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full border border-gray-200 rounded-lg">
                          <thead className="bg-gray-50">
                            <tr>
                              {validationResults.columns.map((column, index) => (
                                <th key={index} className="px-4 py-2 text-left text-sm font-medium text-gray-700 border-b">
                                  {column}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {validationResults.preview.slice(0, 5).map((row, index) => (
                              <tr key={index} className="border-b">
                                {validationResults.columns.map((column, colIndex) => (
                                  <td key={colIndex} className="px-4 py-2 text-sm text-gray-900">
                                    {row[column] || '-'}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {validationResults.recommendations && validationResults.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">
                        {t('importExport.recommendations', 'Recommendations')}
                      </h4>
                      <ul className="space-y-1">
                        {validationResults.recommendations.map((rec, index) => (
                          <li key={index} className="text-sm text-gray-600 flex items-start space-x-2">
                            <span className="text-yellow-500 mt-0.5">•</span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Import Results */}
          {importResults && (
            <Card>
              <CardHeader>
                <CardTitle>
                  {t('importExport.importResults', 'Import Results')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {importResults.successful_imports || 0}
                    </div>
                    <div className="text-sm text-green-700">
                      {t('importExport.successfulImports', 'Successful Imports')}
                    </div>
                  </div>
                  
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {importResults.updated_records || 0}
                    </div>
                    <div className="text-sm text-blue-700">
                      {t('importExport.updatedRecords', 'Updated Records')}
                    </div>
                  </div>
                  
                  <div className="p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {importResults.failed_imports || 0}
                    </div>
                    <div className="text-sm text-red-700">
                      {t('importExport.failedImports', 'Failed Imports')}
                    </div>
                  </div>
                </div>

                {importResults.errors && importResults.errors.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2 text-red-800">
                      {t('importExport.errors', 'Errors')}
                    </h4>
                    <div className="max-h-40 overflow-y-auto">
                      <ul className="space-y-1">
                        {importResults.errors.map((error, index) => (
                          <li key={index} className="text-sm text-red-600 bg-red-50 p-2 rounded">
                            {error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Export Tab */}
        <TabsContent value="export" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Download className="h-5 w-5 mr-2" />
                {t('importExport.exportData', 'Export Data')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-gray-600">
                {t('importExport.exportDescription', 'Export your data to CSV format for backup or external use.')}
              </div>

              {exportStatus !== 'idle' && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{t('importExport.progress', 'Progress')}</span>
                    <span>{exportProgress}%</span>
                  </div>
                  <Progress value={exportProgress} className="w-full" />
                </div>
              )}

              <div className="flex space-x-2">
                <Button
                  onClick={() => exportData('csv')}
                  disabled={exportStatus === 'exporting'}
                  className="flex-1"
                >
                  {exportStatus === 'exporting' ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                  )}
                  {t('importExport.exportCSV', 'Export as CSV')}
                </Button>
              </div>

              {exportStatus === 'completed' && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-2 text-green-800">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-sm font-medium">
                      {t('importExport.exportCompleted', 'Export completed successfully')}
                    </span>
                  </div>
                </div>
              )}

              {exportStatus === 'error' && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center space-x-2 text-red-800">
                    <AlertCircle className="h-4 w-4" />
                    <span className="text-sm font-medium">
                      {t('importExport.exportFailed', 'Export failed')}
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default ImportExport
