import React from 'react';
import { handleGenericError, errorAnalytics, ERROR_CATEGORIES } from '../utils/errorHandling';
import EnhancedErrorDisplay from './EnhancedErrorDisplay';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      formattedError: null,
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Enhanced error processing with analytics
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    const formattedError = handleGenericError(error, {
      component: 'ErrorBoundary',
      action: 'componentRender',
      errorBoundary: true,
      componentStack: errorInfo.componentStack
    });

    // Track critical error in analytics
    errorAnalytics.trackError(formattedError, {
      errorBoundary: true,
      componentStack: errorInfo.componentStack,
      retryCount: this.state.retryCount
    });

    this.setState({
      error: error,
      errorInfo: errorInfo,
      formattedError: formattedError
    });

    // Notify error tracking service if available
    if (window.gtag && import.meta.env.PROD) {
      window.gtag('event', 'exception', {
        description: error.toString(),
        fatal: true,
        error_boundary: true
      });
    }
  }

  // Handle retry mechanism
  handleRetry = () => {
    const retryCount = this.state.retryCount + 1;
    
    // Track retry attempt
    if (window.gtag && import.meta.env.PROD) {
      window.gtag('event', 'error_boundary_retry', {
        retry_count: retryCount,
        error_category: this.state.formattedError?.category
      });
    }

    // Reset error state to retry rendering
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null, 
      formattedError: null,
      retryCount: retryCount
    });
  };

  // Handle navigation to dashboard
  handleGoToDashboard = () => {
    // Track navigation attempt
    if (window.gtag && import.meta.env.PROD) {
      window.gtag('event', 'error_boundary_navigate', {
        destination: 'dashboard'
      });
    }

    // Navigate to dashboard
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      const { formattedError } = this.state;
      
      // Enhanced fallback UI with accessibility
      return (
        <div 
          className="min-h-screen bg-gray-50 flex items-center justify-center p-6"
          role="main"
          aria-labelledby="error-title"
        >
          <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
            {/* Header with icon and title */}
            <div className="flex items-center mb-6">
              <div 
                className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4"
                role="img"
                aria-label="Fout pictogram"
              >
                <svg 
                  className="w-6 h-6 text-red-600" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
                  />
                </svg>
              </div>
              <div>
                <h1 id="error-title" className="text-xl font-semibold text-gray-900">
                  {formattedError?.title || 'Er is iets misgegaan'}
                </h1>
                <p className="text-gray-600">
                  {formattedError?.message || 'De applicatie heeft een onverwachte fout ondervonden.'}
                </p>
              </div>
            </div>
            
            {/* Enhanced error display */}
            {formattedError && (
              <div className="mb-6">
                <EnhancedErrorDisplay
                  error={formattedError}
                  onRetry={this.handleRetry}
                  showSuggestions={true}
                  showRetry={true}
                  compact={false}
                  analyticsContext={{
                    component: 'ErrorBoundary',
                    retryCount: this.state.retryCount
                  }}
                />
              </div>
            )}

            {/* Action buttons */}
            <div className="flex flex-col sm:flex-row gap-3 mb-6">
              <button
                onClick={this.handleRetry}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                aria-label="Pagina opnieuw laden"
              >
                <svg className="inline-block w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Pagina vernieuwen
              </button>
              <button
                onClick={this.handleGoToDashboard}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                aria-label="Naar dashboard gaan"
              >
                <svg className="inline-block w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Naar dashboard
              </button>
            </div>

            {/* Error details for development */}
            {import.meta.env.VITE_SHOW_ERROR_DETAILS === 'true' && this.state.errorInfo && (
              <details className="mt-6">
                <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800 focus:outline-none focus:underline">
                  Technische details tonen
                </summary>
                <div className="mt-3 space-y-3">
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <h3 className="text-sm text-red-800 font-medium mb-2">Foutbericht:</h3>
                    <pre className="text-sm text-red-700 whitespace-pre-wrap">
                      {this.state.error && this.state.error.toString()}
                    </pre>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                    <h3 className="text-sm text-gray-800 font-medium mb-2">Component Stack:</h3>
                    <pre className="text-xs text-gray-600 overflow-auto max-h-40 whitespace-pre-wrap">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </div>
                  {formattedError && (
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                      <h3 className="text-sm text-blue-800 font-medium mb-2">Fout analyse:</h3>
                      <pre className="text-xs text-blue-700 whitespace-pre-wrap">
                        {JSON.stringify({
                          category: formattedError.category,
                          severity: formattedError.severity,
                          retryCount: this.state.retryCount,
                          timestamp: formattedError.timestamp
                        }, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}

            {/* Help text */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Heeft u hulp nodig?</strong> Als deze fout blijft optreden, neem dan contact op met de ondersteuning 
                en vermeld wat u deed toen de fout optrad.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;