import React, { useState, useEffect } from 'react';
import { Download, FileText, Euro, Calendar, User, MapPin, Package } from 'lucide-react';
import apiService from '../services/api';

const InvoiceQuoteManager = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingPdf, setGeneratingPdf] = useState(null);

  useEffect(() => {
    loadInvoiceableProjects();
  }, []);

  const loadInvoiceableProjects = async () => {
    try {
      setLoading(true);
      const response = await apiService.getInvoiceableProjects();
      setProjects(response.projects || []);
    } catch (err) {
      setError('Fout bij laden van projecten: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateQuote = async (projectId, format = 'pdf') => {
    try {
      setGeneratingPdf(projectId);
      
      if (format === 'pdf') {
        // Create a temporary link to download the PDF
        const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/invoices/quote/${projectId}?format=pdf`;
        const link = document.createElement('a');
        link.href = url;
        link.target = '_blank';
        link.download = `offerte_project_${projectId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        const response = await apiService.generateQuote(projectId, 'json');
        console.log('Quote data:', response);
      }
    } catch (err) {
      setError('Fout bij genereren offerte: ' + err.message);
    } finally {
      setGeneratingPdf(null);
    }
  };

  const generateInvoice = async (projectId, format = 'pdf') => {
    try {
      setGeneratingPdf(projectId);
      
      if (format === 'pdf') {
        const response = await apiService.generateInvoice(projectId, { format: 'pdf' });
        
        // Create a temporary link to download the PDF
        const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/invoices/invoice/${projectId}`;
        const link = document.createElement('a');
        link.href = url;
        link.target = '_blank';
        link.download = `factuur_project_${projectId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        const response = await apiService.generateInvoice(projectId, { format: 'json' });
        console.log('Invoice data:', response);
      }
    } catch (err) {
      setError('Fout bij genereren factuur: ' + err.message);
    } finally {
      setGeneratingPdf(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'planning':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Afgerond';
      case 'in_progress':
        return 'Bezig';
      case 'planning':
        return 'Planning';
      default:
        return 'Onbekend';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Niet ingesteld';
    return new Date(dateString).toLocaleDateString('nl-NL');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('nl-NL', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Offertes & Facturen
        </h1>
        <p className="text-gray-600">
          Genereer professionele offertes en facturen voor uw projecten
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Fout</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Factureerbare Projecten ({projects.length})
          </h2>
        </div>

        {projects.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Geen factureerbare projecten
            </h3>
            <p className="text-gray-600">
              Er zijn momenteel geen projecten beschikbaar voor facturering.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {projects.map((project) => (
              <div key={project.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {project.name}
                      </h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                        {getStatusText(project.status)}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <User className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{project.client_name}</span>
                      </div>
                      
                      {project.area_size > 0 && (
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{project.area_size} m²</span>
                        </div>
                      )}
                      
                      {project.plant_count > 0 && (
                        <div className="flex items-center">
                          <Package className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{project.plant_count} planten</span>
                        </div>
                      )}

                      {project.budget > 0 && (
                        <div className="flex items-center">
                          <Euro className="h-4 w-4 mr-2 text-gray-400" />
                          <span>{formatCurrency(project.budget)}</span>
                        </div>
                      )}
                    </div>

                    {project.created_at && (
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-2" />
                        <span>Aangemaakt: {formatDate(project.created_at)}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 ml-6">
                    <button
                      onClick={() => generateQuote(project.id)}
                      disabled={generatingPdf === project.id}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generatingPdf === project.id ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700 mr-2"></div>
                          Genereren...
                        </>
                      ) : (
                        <>
                          <FileText className="h-4 w-4 mr-2" />
                          Offerte
                        </>
                      )}
                    </button>

                    <button
                      onClick={() => generateInvoice(project.id)}
                      disabled={generatingPdf === project.id}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generatingPdf === project.id ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Genereren...
                        </>
                      ) : (
                        <>
                          <Download className="h-4 w-4 mr-2" />
                          Factuur
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Informatie</h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li>Offertes bevatten een gedetailleerde prijsopgave voor het project</li>
                <li>Facturen worden automatisch gegenereerd op basis van de offerte gegevens</li>
                <li>Alle documenten worden als PDF gedownload met professionele opmaak</li>
                <li>Prijzen zijn inclusief 21% BTW volgens Nederlandse wetgeving</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoiceQuoteManager;