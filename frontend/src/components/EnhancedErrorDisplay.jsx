import React, { useEffect, useRef } from 'react';
import { Alert, AlertDescription } from './ui/alert';
import { AlertCircle, RefreshCw, HelpCircle, X, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';
import { ERROR_SEVERITY } from '../utils/errorHandling';

/**
 * Enhanced Error Display Component with accessibility and analytics
 * 
 * Features:
 * - Screen reader support with ARIA labels
 * - Keyboard navigation
 * - Error categorization and severity display
 * - Actionable error suggestions
 * - Retry mechanisms
 * - Error analytics integration
 * - Color contrast compliance
 */
const EnhancedErrorDisplay = ({
  error,
  onRetry,
  onDismiss,
  showSuggestions = true,
  showRetry = true,
  showDismiss = false,
  compact = false,
  className = '',
  autoFocus = true,
  analyticsContext = {}
}) => {
  const errorRef = useRef(null);
  const retryButtonRef = useRef(null);

  // Auto-focus error for screen readers when it appears
  useEffect(() => {
    if (autoFocus && errorRef.current) {
      errorRef.current.focus();
    }
  }, [error, autoFocus]);

  if (!error) return null;

  // Determine severity styling
  const getSeverityStyles = (severity) => {
    switch (severity) {
      case ERROR_SEVERITY.CRITICAL:
        return {
          border: 'border-red-500 bg-red-50',
          icon: 'text-red-700',
          text: 'text-red-900',
          button: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
        };
      case ERROR_SEVERITY.HIGH:
        return {
          border: 'border-red-400 bg-red-50',
          icon: 'text-red-600',
          text: 'text-red-800',
          button: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
        };
      case ERROR_SEVERITY.MEDIUM:
        return {
          border: 'border-orange-400 bg-orange-50',
          icon: 'text-orange-600',
          text: 'text-orange-800',
          button: 'bg-orange-600 hover:bg-orange-700 focus:ring-orange-500'
        };
      default:
        return {
          border: 'border-yellow-400 bg-yellow-50',
          icon: 'text-yellow-600',
          text: 'text-yellow-800',
          button: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
        };
    }
  };

  const styles = getSeverityStyles(error.severity);

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && onDismiss) {
      onDismiss();
    }
  };

  // Enhanced retry with analytics
  const handleRetry = () => {
    if (onRetry) {
      // Track retry attempt
      if (window.gtag && import.meta.env.PROD) {
        window.gtag('event', 'error_retry', {
          error_category: error.category,
          error_severity: error.severity,
          ...analyticsContext
        });
      }
      onRetry();
    }
  };

  const compactView = compact ? (
    <Alert 
      className={`${styles.border} ${className}`}
      role="alert"
      aria-live="polite"
      ref={errorRef}
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      <AlertCircle className={`h-4 w-4 ${styles.icon}`} aria-hidden="true" />
      <div className="flex flex-1 items-center justify-between">
        <AlertDescription className={`${styles.text} font-medium`}>
          {error.title}: {error.message}
        </AlertDescription>
        <div className="flex items-center space-x-2 ml-4">
          {showRetry && onRetry && (
            <Button
              ref={retryButtonRef}
              size="sm"
              variant="outline"
              onClick={handleRetry}
              className={`${styles.button} text-white border-none`}
              aria-label={`Opnieuw proberen: ${error.title}`}
            >
              <RefreshCw className="h-3 w-3 mr-1" aria-hidden="true" />
              Opnieuw
            </Button>
          )}
          {showDismiss && onDismiss && (
            <Button
              size="sm"
              variant="ghost"
              onClick={onDismiss}
              className={`${styles.text} hover:bg-gray-100`}
              aria-label="Foutmelding sluiten"
            >
              <X className="h-3 w-3" aria-hidden="true" />
            </Button>
          )}
        </div>
      </div>
    </Alert>
  ) : (
    <Alert 
      className={`${styles.border} ${className}`}
      role="alert"
      aria-live="polite"
      ref={errorRef}
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      <AlertCircle 
        className={`h-5 w-5 ${styles.icon} mt-0.5 flex-shrink-0`} 
        aria-hidden="true" 
      />
      <div className="flex-1 space-y-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className={`font-semibold ${styles.text}`}>
              {error.title}
            </h3>
            <AlertDescription className={styles.text}>
              {error.message}
            </AlertDescription>
          </div>
          {showDismiss && onDismiss && (
            <Button
              size="sm"
              variant="ghost"
              onClick={onDismiss}
              className={`${styles.text} hover:bg-gray-100 -mt-1 -mr-1`}
              aria-label="Foutmelding sluiten"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </Button>
          )}
        </div>

        {/* Error suggestions */}
        {showSuggestions && error.suggestions && error.suggestions.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center space-x-1">
              <HelpCircle className={`h-4 w-4 ${styles.icon}`} aria-hidden="true" />
              <h4 className={`text-sm font-medium ${styles.text}`}>
                Aanbevolen acties:
              </h4>
            </div>
            <ul className={`text-sm ${styles.text} space-y-1 ml-5`} role="list">
              {error.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start">
                  <span className="inline-block w-1 h-1 bg-current rounded-full mt-2 mr-2 flex-shrink-0" aria-hidden="true" />
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-wrap gap-2 pt-1">
          {showRetry && onRetry && (
            <Button
              ref={retryButtonRef}
              size="sm"
              onClick={handleRetry}
              className={`${styles.button} text-white focus:ring-2 focus:ring-offset-1`}
              aria-label={`Opnieuw proberen: ${error.title}`}
            >
              <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
              Opnieuw proberen
            </Button>
          )}
          
          {/* Help link for complex errors */}
          {error.severity === ERROR_SEVERITY.CRITICAL && (
            <Button
              size="sm"
              variant="outline"
              className={`${styles.text} border-current hover:bg-current hover:text-white`}
              onClick={() => {
                // Track help request
                if (window.gtag && import.meta.env.PROD) {
                  window.gtag('event', 'error_help_requested', {
                    error_category: error.category,
                    error_severity: error.severity,
                    ...analyticsContext
                  });
                }
                // Open help or contact support
                window.open('/help/errors', '_blank');
              }}
              aria-label="Hulp krijgen voor deze fout"
            >
              <ExternalLink className="h-4 w-4 mr-2" aria-hidden="true" />
              Hulp krijgen
            </Button>
          )}
        </div>

        {/* Development details */}
        {import.meta.env.DEV && error.originalError && (
          <details className="mt-3">
            <summary className={`text-xs ${styles.text} cursor-pointer hover:underline`}>
              Technische details (alleen in ontwikkelingsmodus)
            </summary>
            <pre className={`text-xs ${styles.text} mt-2 p-2 bg-gray-100 rounded overflow-auto max-h-32 whitespace-pre-wrap`}>
              {JSON.stringify({
                category: error.category,
                severity: error.severity,
                originalError: error.originalError,
                context: error.context,
                timestamp: error.timestamp
              }, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </Alert>
  );

  return compactView;
};

/**
 * Error Toast Component for temporary notifications
 */
export const ErrorToast = ({ 
  error, 
  onDismiss, 
  autoHideDuration = 5000,
  className = '',
  ...props 
}) => {
  useEffect(() => {
    if (autoHideDuration > 0) {
      const timer = setTimeout(() => {
        onDismiss?.();
      }, autoHideDuration);

      return () => clearTimeout(timer);
    }
  }, [autoHideDuration, onDismiss]);

  return (
    <div 
      className={`fixed top-4 right-4 z-50 max-w-sm ${className}`}
      role="status"
      aria-live="polite"
    >
      <EnhancedErrorDisplay
        error={error}
        onDismiss={onDismiss}
        compact={true}
        showSuggestions={false}
        showDismiss={true}
        autoFocus={false}
        {...props}
      />
    </div>
  );
};

/**
 * Loading Error State Component
 */
export const LoadingErrorState = ({ 
  error, 
  onRetry, 
  title = "Laden mislukt",
  className = '' 
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center space-y-4 ${className}`}>
      <AlertCircle className="h-12 w-12 text-red-500" aria-hidden="true" />
      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        <p className="text-gray-600 max-w-md">
          {error?.message || 'Er is een fout opgetreden tijdens het laden van de gegevens.'}
        </p>
      </div>
      {onRetry && (
        <Button 
          onClick={onRetry}
          className="bg-red-600 hover:bg-red-700 text-white"
          aria-label="Gegevens opnieuw laden"
        >
          <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
          Opnieuw laden
        </Button>
      )}
    </div>
  );
};

export default EnhancedErrorDisplay;