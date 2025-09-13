/**
 * Comprehensive Error Handling Utilities
 * Provides consistent error categorization, formatting, and tracking
 */

// Error categories for consistent classification
export const ERROR_CATEGORIES = {
  NETWORK: 'network',
  SERVER: 'server', 
  VALIDATION: 'validation',
  AUTHENTICATION: 'authentication',
  AUTHORIZATION: 'authorization',
  CLIENT: 'client',
  UNKNOWN: 'unknown'
};

// Error severity levels
export const ERROR_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

/**
 * Categorizes errors based on common patterns
 * @param {Error|Object} error - The error object
 * @param {number} statusCode - HTTP status code if applicable
 * @returns {string} Error category
 */
export const categorizeError = (error, statusCode = null) => {
  // Network errors
  if (error?.name === 'NetworkError' || error?.code === 'NETWORK_ERROR' || 
      error?.message?.includes('network') || error?.message?.includes('fetch')) {
    return ERROR_CATEGORIES.NETWORK;
  }

  // HTTP status code based categorization
  if (statusCode) {
    if (statusCode === 401) return ERROR_CATEGORIES.AUTHENTICATION;
    if (statusCode === 403) return ERROR_CATEGORIES.AUTHORIZATION;
    if (statusCode >= 400 && statusCode < 500) return ERROR_CATEGORIES.CLIENT;
    if (statusCode >= 500) return ERROR_CATEGORIES.SERVER;
  }

  // Validation errors
  if (error?.name === 'ValidationError' || 
      error?.message?.includes('validation') ||
      error?.message?.includes('required') ||
      error?.message?.includes('invalid')) {
    return ERROR_CATEGORIES.VALIDATION;
  }

  // Authentication errors
  if (error?.message?.includes('unauthorized') || 
      error?.message?.includes('login') ||
      error?.message?.includes('token')) {
    return ERROR_CATEGORIES.AUTHENTICATION;
  }

  return ERROR_CATEGORIES.UNKNOWN;
};

/**
 * Determines error severity based on category and impact
 * @param {string} category - Error category
 * @param {Error} error - Original error object
 * @returns {string} Severity level
 */
export const getErrorSeverity = (category, error) => {
  switch (category) {
    case ERROR_CATEGORIES.NETWORK:
      return ERROR_SEVERITY.HIGH;
    case ERROR_CATEGORIES.SERVER:
      return ERROR_SEVERITY.CRITICAL;
    case ERROR_CATEGORIES.AUTHENTICATION:
    case ERROR_CATEGORIES.AUTHORIZATION:
      return ERROR_SEVERITY.HIGH;
    case ERROR_CATEGORIES.VALIDATION:
      return ERROR_SEVERITY.MEDIUM;
    case ERROR_CATEGORIES.CLIENT:
      return ERROR_SEVERITY.MEDIUM;
    default:
      return ERROR_SEVERITY.LOW;
  }
};

/**
 * Generates user-friendly error messages with actionable guidance
 * @param {string} category - Error category
 * @param {Error|Object} error - Original error
 * @param {Object} context - Additional context (component, action, etc.)
 * @returns {Object} Formatted error message with suggestions
 */
export const formatErrorMessage = (category, error, context = {}) => {
  const baseMessages = {
    [ERROR_CATEGORIES.NETWORK]: {
      title: 'Verbindingsprobleem',
      message: 'Er is een probleem met de netwerkverbinding. Controleer uw internetverbinding en probeer het opnieuw.',
      suggestions: [
        'Controleer uw internetverbinding',
        'Probeer de pagina te verversen',
        'Probeer het over een paar seconden opnieuw'
      ]
    },
    [ERROR_CATEGORIES.SERVER]: {
      title: 'Serverfout',
      message: 'De server ondervindt momenteel problemen. Probeer het later opnieuw.',
      suggestions: [
        'Probeer het over een paar minuten opnieuw',
        'Neem contact op met ondersteuning als het probleem aanhoudt',
        'Bewaar uw werk lokaal indien mogelijk'
      ]
    },
    [ERROR_CATEGORIES.VALIDATION]: {
      title: 'Invoerfout',
      message: 'De ingevoerde gegevens zijn niet correct. Controleer uw invoer en probeer opnieuw.',
      suggestions: [
        'Controleer alle verplichte velden',
        'Zorg ervoor dat de gegevens het juiste formaat hebben',
        'Lees de veldvereisten zorgvuldig door'
      ]
    },
    [ERROR_CATEGORIES.AUTHENTICATION]: {
      title: 'Inlogprobleem',
      message: 'U bent niet ingelogd of uw sessie is verlopen. Log opnieuw in.',
      suggestions: [
        'Log opnieuw in met uw gebruikersgegevens',
        'Controleer of uw gebruikersnaam en wachtwoord correct zijn',
        'Reset uw wachtwoord als u het bent vergeten'
      ]
    },
    [ERROR_CATEGORIES.AUTHORIZATION]: {
      title: 'Toegang geweigerd',
      message: 'U heeft geen toestemming voor deze actie. Neem contact op met een beheerder.',
      suggestions: [
        'Neem contact op met een beheerder voor toegang',
        'Controleer of u ingelogd bent met het juiste account',
        'Vraag de benodigde machtigingen aan'
      ]
    },
    [ERROR_CATEGORIES.CLIENT]: {
      title: 'Aanvraagfout',
      message: 'Er is een probleem met uw aanvraag. Controleer uw invoer en probeer opnieuw.',
      suggestions: [
        'Controleer alle ingevoerde gegevens',
        'Zorg ervoor dat alle velden correct zijn ingevuld',
        'Ververs de pagina en probeer opnieuw'
      ]
    },
    [ERROR_CATEGORIES.UNKNOWN]: {
      title: 'Onbekende fout',
      message: 'Er is een onverwachte fout opgetreden. Probeer het opnieuw.',
      suggestions: [
        'Ververs de pagina en probeer opnieuw',
        'Neem contact op met ondersteuning als het probleem aanhoudt',
        'Noteer wat u deed toen de fout optrad'
      ]
    }
  };

  const baseMessage = baseMessages[category] || baseMessages[ERROR_CATEGORIES.UNKNOWN];
  
  // Add context-specific information
  let contextualMessage = baseMessage.message;
  let contextualSuggestions = [...baseMessage.suggestions];

  if (context.component) {
    contextualMessage += ` (${context.component})`;
  }

  if (context.action) {
    contextualSuggestions.unshift(`Probeer de actie "${context.action}" opnieuw`);
  }

  return {
    title: baseMessage.title,
    message: contextualMessage,
    suggestions: contextualSuggestions,
    category,
    severity: getErrorSeverity(category, error),
    originalError: typeof error === 'string' ? error : (error?.message || error?.error || String(error)),
    timestamp: new Date().toISOString(),
    context
  };
};

/**
 * Error analytics tracking
 */
class ErrorAnalytics {
  constructor() {
    this.errors = [];
    this.maxErrors = 100; // Keep last 100 errors in memory
  }

  /**
   * Track an error occurrence
   * @param {Object} errorInfo - Formatted error information
   * @param {Object} metadata - Additional metadata (user, session, etc.)
   */
  trackError(errorInfo, metadata = {}) {
    const errorRecord = {
      id: this.generateErrorId(),
      ...errorInfo,
      metadata: {
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
        url: typeof window !== 'undefined' && window.location ? window.location.href : 'unknown',
        timestamp: new Date().toISOString(),
        ...metadata
      }
    };

    this.errors.unshift(errorRecord);
    
    // Keep only the most recent errors
    if (this.errors.length > this.maxErrors) {
      this.errors = this.errors.slice(0, this.maxErrors);
    }

    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('Error tracked:', errorRecord);
    }

    // In production, you could send to analytics service
    if (import.meta.env.PROD && typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'error', {
        error_category: errorInfo.category,
        error_severity: errorInfo.severity,
        error_component: errorInfo.context?.component || 'unknown'
      });
    }

    return errorRecord.id;
  }

  /**
   * Get error statistics
   * @returns {Object} Error statistics
   */
  getStatistics() {
    const stats = {
      total: this.errors.length,
      byCategory: {},
      bySeverity: {},
      recent: this.errors.slice(0, 10)
    };

    this.errors.forEach(error => {
      stats.byCategory[error.category] = (stats.byCategory[error.category] || 0) + 1;
      stats.bySeverity[error.severity] = (stats.bySeverity[error.severity] || 0) + 1;
    });

    return stats;
  }

  /**
   * Clear all tracked errors
   */
  clearErrors() {
    this.errors = [];
  }

  /**
   * Generate unique error ID
   * @returns {string} Unique identifier
   */
  generateErrorId() {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance for error tracking
export const errorAnalytics = new ErrorAnalytics();

/**
 * Enhanced error handler for API calls
 * @param {Response} response - Fetch response object
 * @param {Object} context - Context information
 * @returns {Promise<Object>} Formatted error information
 */
export const handleApiError = async (response, context = {}) => {
  let errorData;
  
  try {
    errorData = await response.json();
  } catch {
    errorData = { error: 'Invalid response format' };
  }

  const category = categorizeError(errorData, response.status);
  const formattedError = formatErrorMessage(category, errorData, {
    ...context,
    statusCode: response.status,
    statusText: response.statusText
  });

  // Track the error
  errorAnalytics.trackError(formattedError, {
    apiEndpoint: context.endpoint || 'unknown',
    httpStatus: response.status
  });

  return formattedError;
};

/**
 * Enhanced error handler for generic errors
 * @param {Error} error - JavaScript error object
 * @param {Object} context - Context information
 * @returns {Object} Formatted error information
 */
export const handleGenericError = (error, context = {}) => {
  const category = categorizeError(error);
  const formattedError = formatErrorMessage(category, error, context);

  // Track the error
  errorAnalytics.trackError(formattedError, {
    errorType: 'generic',
    stack: error?.stack
  });

  return formattedError;
};