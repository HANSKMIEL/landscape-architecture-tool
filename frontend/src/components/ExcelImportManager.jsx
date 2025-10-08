import React, { useState, useEffect } from 'react';
import { Upload, Download, FileSpreadsheet, AlertCircle, CheckCircle, X, Info } from 'lucide-react';
import apiService from '../services/api';

const ExcelImportManager = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [importType, setImportType] = useState('suppliers');
  const [updateExisting, setUpdateExisting] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const importTypes = [
    { value: 'suppliers', label: 'Leveranciers', icon: '🏢' },
    { value: 'plants', label: 'Planten', icon: '🌱' },
    { value: 'products', label: 'Producten', icon: '📦' },
    { value: 'clients', label: 'Klanten', icon: '👥' }
  ];

  useEffect(() => {
    loadImportStatus();
  }, []);

  const loadImportStatus = async () => {
    try {
      const response = await apiService.getImportStatus();
      setStatus(response);
    } catch (err) {
      setError('Fout bij laden import status: ' + err.message);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setValidationResult(null);
      setImportResult(null);
      setError(null);
    }
  };

  const validateFile = async () => {
    if (!selectedFile) {
      setError('Selecteer eerst een bestand');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('type', importType);

      const response = await apiService.validateImportFile(formData);
      setValidationResult(response);
    } catch (err) {
      setError('Fout bij valideren bestand: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const processImport = async () => {
    if (!validationResult || !validationResult.valid) {
      setError('Valideer eerst het bestand');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('type', importType);
      formData.append('update_existing', updateExisting.toString());

      const response = await apiService.processImport(formData);
      setImportResult(response);
      
      // Refresh status after successful import
      if (response.success) {
        await loadImportStatus();
      }
    } catch (err) {
      setError('Fout bij verwerken import: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = async (type) => {
    try {
      // Create a temporary link to download the template
      const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/import/template/${type}`;
      const link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.download = `${type}_import_template.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError('Fout bij downloaden template: ' + err.message);
    }
  };

  const resetForm = () => {
    setSelectedFile(null);
    setValidationResult(null);
    setImportResult(null);
    setError(null);
    document.getElementById('file-input').value = '';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const selectedImportType = importTypes.find(t => t.value === importType);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Excel Import Manager
        </h1>
        <p className="text-gray-600">
          Importeer grote hoeveelheden data uit Excel- of CSV-bestanden
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400 mr-3 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Fout</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Current Status */}
      {status && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-3">Huidige Database Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {Object.entries(status.current_counts).map(([key, count]) => {
              const type = importTypes.find(t => t.value === key);
              return (
                <div key={key} className="flex items-center">
                  <span className="mr-2">{type?.icon}</span>
                  <span className="text-blue-700">
                    {type?.label}: <strong>{count}</strong>
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Import Type Selection */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">1. Kies Import Type</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {importTypes.map((type) => (
            <button
              key={type.value}
              onClick={() => setImportType(type.value)}
              className={`p-4 border-2 rounded-lg text-center transition-colors ${
                importType === type.value
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-2">{type.icon}</div>
              <div className="font-medium">{type.label}</div>
            </button>
          ))}
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="update-existing"
              checked={updateExisting}
              onChange={(e) => setUpdateExisting(e.target.checked)}
              className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label htmlFor="update-existing" className="ml-2 text-sm text-gray-700">
              Bestaande records bijwerken
            </label>
          </div>

          <button
            onClick={() => downloadTemplate(importType)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <Download className="h-4 w-4 mr-2" />
            Template Downloaden
          </button>
        </div>
      </div>

      {/* File Upload */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">2. Upload Bestand</h2>
        
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <FileSpreadsheet className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          
          {selectedFile ? (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {formatFileSize(selectedFile.size)} • {selectedFile.type || 'Unknown type'}
              </p>
              <div className="flex justify-center space-x-3 mt-4">
                <button
                  onClick={validateFile}
                  disabled={loading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Valideren...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Valideren
                    </>
                  )}
                </button>
                <button
                  onClick={resetForm}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <X className="h-4 w-4 mr-2" />
                  Verwijderen
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p className="text-gray-600 mb-4">
                Sleep uw Excel- of CSV-bestand hier of klik om te selecteren
              </p>
              <input
                id="file-input"
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileSelect}
                className="hidden"
              />
              <label
                htmlFor="file-input"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 cursor-pointer"
              >
                <Upload className="h-4 w-4 mr-2" />
                Bestand Selecteren
              </label>
              <p className="text-xs text-gray-500 mt-2">
                Ondersteunde formaten: .xlsx, .xls, .csv (max 10MB)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Validation Results */}
      {validationResult && (
        <div className="bg-white shadow-md rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">3. Validatie Resultaat</h2>
          
          <div className={`p-4 rounded-md ${validationResult.valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex">
              {validationResult.valid ? (
                <CheckCircle className="h-5 w-5 text-green-400 mr-3 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-400 mr-3 mt-0.5" />
              )}
              <div className="flex-1">
                <h3 className={`text-sm font-medium ${validationResult.valid ? 'text-green-800' : 'text-red-800'}`}>
                  {validationResult.valid ? 'Bestand is geldig!' : 'Bestand bevat fouten'}
                </h3>
                <div className="mt-2 text-sm">
                  <p className={validationResult.valid ? 'text-green-700' : 'text-red-700'}>
                    {validationResult.total_rows} rijen gevonden
                  </p>
                  
                  {validationResult.missing_columns && validationResult.missing_columns.length > 0 && (
                    <p className="text-red-700 mt-1">
                      Ontbrekende kolommen: {validationResult.missing_columns.join(', ')}
                    </p>
                  )}
                  
                  {validationResult.data_issues && validationResult.data_issues.length > 0 && (
                    <div className="mt-2">
                      <p className="text-red-700 font-medium">Data problemen:</p>
                      <ul className="text-red-700 list-disc list-inside">
                        {validationResult.data_issues.map((issue, index) => (
                          <li key={index}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {validationResult.recommendations && validationResult.recommendations.length > 0 && (
                    <div className="mt-2">
                      <p className="text-blue-700 font-medium">Aanbevelingen:</p>
                      <ul className="text-blue-700 list-disc list-inside">
                        {validationResult.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {validationResult.sample_data && validationResult.sample_data.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Voorbeeld Data (eerste 3 rijen):</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-200 rounded-md">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(validationResult.sample_data[0]).map((header, index) => (
                        <th key={index} className="px-3 py-2 border-b border-gray-200 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {validationResult.sample_data.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {Object.values(row).map((cell, cellIndex) => (
                          <td key={cellIndex} className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200">
                            {String(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {validationResult.valid && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={processImport}
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Importeren...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Data Importeren
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Import Results */}
      {importResult && (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">4. Import Resultaat</h2>
          
          <div className={`p-4 rounded-md ${importResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex">
              {importResult.success ? (
                <CheckCircle className="h-5 w-5 text-green-400 mr-3 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-400 mr-3 mt-0.5" />
              )}
              <div className="flex-1">
                <h3 className={`text-sm font-medium ${importResult.success ? 'text-green-800' : 'text-red-800'}`}>
                  {importResult.message}
                </h3>
                
                {importResult.success && (
                  <div className="mt-2 text-sm text-green-700">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <span className="font-medium">Totaal rijen:</span> {importResult.total_rows}
                      </div>
                      <div>
                        <span className="font-medium">Succesvol:</span> {importResult.successful_imports}
                      </div>
                      {importResult.updated_records > 0 && (
                        <div>
                          <span className="font-medium">Bijgewerkt:</span> {importResult.updated_records}
                        </div>
                      )}
                      {importResult.failed_imports > 0 && (
                        <div className="text-red-700">
                          <span className="font-medium">Gefaald:</span> {importResult.failed_imports}
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {importResult.errors && importResult.errors.length > 0 && (
                  <div className="mt-2">
                    <p className="text-red-700 font-medium">Fouten:</p>
                    <ul className="text-red-700 list-disc list-inside text-sm">
                      {importResult.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>

          {importResult.success && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={resetForm}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Nieuwe Import Starten
              </button>
            </div>
          )}
        </div>
      )}

      {/* Help Info */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <Info className="h-5 w-5 text-blue-400 mr-3 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-blue-800">Instructies</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ol className="list-decimal list-inside space-y-1">
                <li>Kies het type data dat u wilt importeren ({selectedImportType?.label})</li>
                <li>Download de template om te zien welke kolommen vereist zijn</li>
                <li>Vul uw data in de template in volgens het voorbeeldformaat</li>
                <li>Upload het ingevulde bestand en valideer de inhoud</li>
                <li>Als de validatie succesvol is, start de import</li>
              </ol>
              <p className="mt-3 font-medium">
                Tips: Gebruik unieke email-adressen voor klanten en leveranciers. 
                Zorg ervoor dat leverancier IDs bestaan voordat u planten of producten importeert.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExcelImportManager;