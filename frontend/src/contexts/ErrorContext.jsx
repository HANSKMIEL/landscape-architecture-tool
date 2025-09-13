import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { handleApiError, handleGenericError, errorAnalytics } from '../utils/errorHandling';
import { ErrorToast } from '../components/EnhancedErrorDisplay';

/**
 * Error Management Context
 * Provides centralized error handling, display, and analytics
 */

// Action types for error reducer
const ERROR_ACTIONS = {
  ADD_ERROR: 'ADD_ERROR',
  REMOVE_ERROR: 'REMOVE_ERROR',
  CLEAR_ERRORS: 'CLEAR_ERRORS',
  SET_GLOBAL_ERROR: 'SET_GLOBAL_ERROR',
  CLEAR_GLOBAL_ERROR: 'CLEAR_GLOBAL_ERROR'
};

// Initial state
const initialState = {
  errors: [], // Array of active errors
  globalError: null, // Global error that blocks the entire UI
  toasts: [] // Toast notifications
};

// Error reducer
const errorReducer = (state, action) => {
  switch (action.type) {
    case ERROR_ACTIONS.ADD_ERROR:
      return {
        ...state,
        errors: [...state.errors, action.payload],
        toasts: action.payload.showToast 
          ? [...state.toasts, action.payload] 
          : state.toasts
      };

    case ERROR_ACTIONS.REMOVE_ERROR:
      return {
        ...state,
        errors: state.errors.filter(error => error.id !== action.payload.id),
        toasts: state.toasts.filter(error => error.id !== action.payload.id)
      };

    case ERROR_ACTIONS.CLEAR_ERRORS:
      return {
        ...state,
        errors: [],
        toasts: []
      };

    case ERROR_ACTIONS.SET_GLOBAL_ERROR:
      return {
        ...state,
        globalError: action.payload
      };

    case ERROR_ACTIONS.CLEAR_GLOBAL_ERROR:
      return {
        ...state,
        globalError: null
      };

    default:
      return state;
  }
};

// Create context
const ErrorContext = createContext();

/**
 * Error Provider Component
 */
export const ErrorProvider = ({ children }) => {
  const [state, dispatch] = useReducer(errorReducer, initialState);

  // Add error with analytics tracking
  const addError = useCallback((errorData, options = {}) => {
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const errorWithId = {
      ...errorData,
      id: errorId,
      showToast: options.showToast || false,
      autoHide: options.autoHide !== false, // Default to true
      persistent: options.persistent || false
    };

    dispatch({
      type: ERROR_ACTIONS.ADD_ERROR,
      payload: errorWithId
    });

    // Auto-remove non-persistent errors after delay
    if (!options.persistent && options.autoHide !== false) {
      setTimeout(() => {
        dispatch({
          type: ERROR_ACTIONS.REMOVE_ERROR,
          payload: { id: errorId }
        });
      }, options.autoHideDuration || 5000);
    }

    return errorId;
  }, []);

  // Remove specific error
  const removeError = useCallback((errorId) => {
    dispatch({
      type: ERROR_ACTIONS.REMOVE_ERROR,
      payload: { id: errorId }
    });
  }, []);

  // Clear all errors
  const clearErrors = useCallback(() => {
    dispatch({ type: ERROR_ACTIONS.CLEAR_ERRORS });
  }, []);

  // Set global error (blocks UI)
  const setGlobalError = useCallback((errorData) => {
    dispatch({
      type: ERROR_ACTIONS.SET_GLOBAL_ERROR,
      payload: errorData
    });
  }, []);

  // Clear global error
  const clearGlobalError = useCallback(() => {
    dispatch({ type: ERROR_ACTIONS.CLEAR_GLOBAL_ERROR });
  }, []);

  // Handle API errors with context
  const handleApiErrorWithContext = useCallback(async (response, context = {}) => {
    const formattedError = await handleApiError(response, context);
    
    if (response.status >= 500) {
      // Server errors are global
      setGlobalError(formattedError);
    } else {
      // Client errors are local
      addError(formattedError, { 
        showToast: true,
        autoHideDuration: 8000
      });
    }

    return formattedError;
  }, [addError, setGlobalError]);

  // Handle generic errors with context
  const handleGenericErrorWithContext = useCallback((error, context = {}) => {
    const formattedError = handleGenericError(error, context);
    
    // Critical errors are global
    if (formattedError.severity === 'critical') {
      setGlobalError(formattedError);
    } else {
      addError(formattedError, { 
        showToast: true,
        autoHideDuration: 6000
      });
    }

    return formattedError;
  }, [addError, setGlobalError]);

  // Show success message
  const showSuccess = useCallback((message, options = {}) => {
    const successData = {
      title: 'Succes',
      message,
      category: 'success',
      severity: 'low',
      suggestions: []
    };

    addError(successData, {
      showToast: true,
      autoHideDuration: options.duration || 3000,
      ...options
    });
  }, [addError]);

  // Show warning message
  const showWarning = useCallback((message, options = {}) => {
    const warningData = {
      title: 'Waarschuwing',
      message,
      category: 'warning',
      severity: 'medium',
      suggestions: options.suggestions || []
    };

    addError(warningData, {
      showToast: true,
      autoHideDuration: options.duration || 5000,
      ...options
    });
  }, [addError]);

  // Get error statistics
  const getErrorStats = useCallback(() => {
    return errorAnalytics.getStatistics();
  }, []);

  const value = {
    // State
    errors: state.errors,
    globalError: state.globalError,
    toasts: state.toasts,
    
    // Actions
    addError,
    removeError,
    clearErrors,
    setGlobalError,
    clearGlobalError,
    
    // Enhanced handlers
    handleApiError: handleApiErrorWithContext,
    handleGenericError: handleGenericErrorWithContext,
    
    // Convenience methods
    showSuccess,
    showWarning,
    getErrorStats
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
      
      {/* Render toast notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {state.toasts.map((error) => (
          <ErrorToast
            key={error.id}
            error={error}
            onDismiss={() => removeError(error.id)}
            autoHideDuration={error.autoHide ? 5000 : 0}
          />
        ))}
      </div>
      
      {/* Render global error overlay */}
      {state.globalError && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Kritieke fout
                </h2>
                <button
                  onClick={clearGlobalError}
                  className="text-gray-400 hover:text-gray-600"
                  aria-label="Fout sluiten"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mb-6">
                <p className="text-gray-600 mb-4">
                  Er is een kritieke fout opgetreden die de applicatie verhindert om correct te functioneren.
                </p>
                
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <h3 className="font-medium text-red-800 mb-2">{state.globalError.title}</h3>
                  <p className="text-red-700">{state.globalError.message}</p>
                  
                  {state.globalError.suggestions && state.globalError.suggestions.length > 0 && (
                    <div className="mt-3">
                      <p className="font-medium text-red-800 mb-1">Aanbevolen acties:</p>
                      <ul className="text-sm text-red-700 space-y-1">
                        {state.globalError.suggestions.map((suggestion, index) => (
                          <li key={index}>• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => window.location.reload()}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Pagina vernieuwen
                </button>
                <button
                  onClick={clearGlobalError}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Toch doorgaan
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </ErrorContext.Provider>
  );
};

/**
 * Hook to use error context
 */
export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};

/**
 * HOC for wrapping components with error handling
 */
export const withErrorHandling = (WrappedComponent) => {
  return React.forwardRef((props, ref) => {
    const { handleGenericError } = useError();

    // Create error handler prop
    const handleError = (error, context = {}) => {
      return handleGenericError(error, {
        component: WrappedComponent.name || 'Unknown',
        ...context
      });
    };

    return (
      <WrappedComponent
        ref={ref}
        {...props}
        onError={handleError}
      />
    );
  });
};

export default ErrorContext;