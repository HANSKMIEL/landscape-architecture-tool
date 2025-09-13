import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { 
  categorizeError, 
  getErrorSeverity, 
  formatErrorMessage, 
  handleApiError, 
  handleGenericError,
  errorAnalytics,
  ERROR_CATEGORIES,
  ERROR_SEVERITY
} from '../errorHandling';

describe('Error Handling Utilities', () => {
  beforeEach(() => {
    // Clear error analytics before each test
    errorAnalytics.clearErrors();
    
    // Mock console.error to avoid noise in tests
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('categorizeError', () => {
    it('should categorize network errors correctly', () => {
      const networkError = new Error('Network request failed');
      networkError.name = 'NetworkError';
      
      expect(categorizeError(networkError)).toBe(ERROR_CATEGORIES.NETWORK);
    });

    it('should categorize authentication errors by status code', () => {
      const authError = { message: 'Unauthorized' };
      expect(categorizeError(authError, 401)).toBe(ERROR_CATEGORIES.AUTHENTICATION);
    });

    it('should categorize authorization errors by status code', () => {
      const authzError = { message: 'Forbidden' };
      expect(categorizeError(authzError, 403)).toBe(ERROR_CATEGORIES.AUTHORIZATION);
    });

    it('should categorize server errors by status code', () => {
      const serverError = { message: 'Internal Server Error' };
      expect(categorizeError(serverError, 500)).toBe(ERROR_CATEGORIES.SERVER);
    });

    it('should categorize validation errors by message content', () => {
      const validationError = { message: 'Validation failed: field is required' };
      expect(categorizeError(validationError)).toBe(ERROR_CATEGORIES.VALIDATION);
    });

    it('should default to unknown category', () => {
      const unknownError = { message: 'Something weird happened' };
      expect(categorizeError(unknownError)).toBe(ERROR_CATEGORIES.UNKNOWN);
    });
  });

  describe('getErrorSeverity', () => {
    it('should assign critical severity to server errors', () => {
      expect(getErrorSeverity(ERROR_CATEGORIES.SERVER)).toBe(ERROR_SEVERITY.CRITICAL);
    });

    it('should assign high severity to network errors', () => {
      expect(getErrorSeverity(ERROR_CATEGORIES.NETWORK)).toBe(ERROR_SEVERITY.HIGH);
    });

    it('should assign medium severity to validation errors', () => {
      expect(getErrorSeverity(ERROR_CATEGORIES.VALIDATION)).toBe(ERROR_SEVERITY.MEDIUM);
    });

    it('should assign low severity to unknown errors', () => {
      expect(getErrorSeverity(ERROR_CATEGORIES.UNKNOWN)).toBe(ERROR_SEVERITY.LOW);
    });
  });

  describe('formatErrorMessage', () => {
    it('should format network error with Dutch messages', () => {
      const error = { message: 'Network timeout' };
      const formatted = formatErrorMessage(ERROR_CATEGORIES.NETWORK, error);

      expect(formatted.title).toBe('Verbindingsprobleem');
      expect(formatted.message).toContain('netwerkverbinding');
      expect(formatted.suggestions).toContain('Controleer uw internetverbinding');
      expect(formatted.category).toBe(ERROR_CATEGORIES.NETWORK);
      expect(formatted.severity).toBe(ERROR_SEVERITY.HIGH);
    });

    it('should include context information', () => {
      const error = { message: 'Test error' };
      const context = { component: 'TestComponent', action: 'save' };
      const formatted = formatErrorMessage(ERROR_CATEGORIES.VALIDATION, error, context);

      expect(formatted.message).toContain('(TestComponent)');
      expect(formatted.suggestions[0]).toContain('save');
      expect(formatted.context).toEqual(context);
    });

    it('should include timestamp and original error', () => {
      const error = { message: 'Test error' };
      const formatted = formatErrorMessage(ERROR_CATEGORIES.CLIENT, error);

      expect(formatted.timestamp).toBeDefined();
      expect(formatted.originalError).toBe('Test error');
    });
  });

  describe('handleApiError', () => {
    it('should handle API error response with JSON', async () => {
      const mockResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: vi.fn().mockResolvedValue({ error: 'Invalid request data' })
      };

      const context = { endpoint: '/api/test', component: 'TestComponent' };
      const result = await handleApiError(mockResponse, context);

      expect(result.category).toBe(ERROR_CATEGORIES.CLIENT);
      expect(result.context.statusCode).toBe(400);
      expect(result.context.endpoint).toBe('/api/test');
      expect(mockResponse.json).toHaveBeenCalled();
    });

    it('should handle API error with invalid JSON response', async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON'))
      };

      const result = await handleApiError(mockResponse);

      expect(result.category).toBe(ERROR_CATEGORIES.SERVER);
      expect(result.originalError).toBe('Invalid response format');
    });

    it('should track errors in analytics', async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: vi.fn().mockResolvedValue({ error: 'Resource not found' })
      };

      await handleApiError(mockResponse, { endpoint: '/api/missing' });

      const stats = errorAnalytics.getStatistics();
      expect(stats.total).toBe(1);
      expect(stats.byCategory[ERROR_CATEGORIES.CLIENT]).toBe(1);
    });
  });

  describe('handleGenericError', () => {
    it('should handle JavaScript Error objects', () => {
      const jsError = new Error('Something went wrong');
      jsError.stack = 'Error stack trace...';

      const context = { component: 'TestComponent' };
      const result = handleGenericError(jsError, context);

      expect(result.originalError).toBe('Something went wrong');
      expect(result.context.component).toBe('TestComponent');
    });

    it('should track generic errors in analytics', () => {
      const error = new Error('Test error');
      handleGenericError(error, { component: 'TestComponent' });

      const stats = errorAnalytics.getStatistics();
      expect(stats.total).toBe(1);
    });
  });

  describe('errorAnalytics', () => {
    it('should track error occurrences', () => {
      const errorInfo = {
        title: 'Test Error',
        message: 'This is a test',
        category: ERROR_CATEGORIES.VALIDATION,
        severity: ERROR_SEVERITY.MEDIUM
      };

      const errorId = errorAnalytics.trackError(errorInfo);

      expect(errorId).toBeDefined();
      expect(errorId).toMatch(/^error_\d+_[a-z0-9]+$/);

      const stats = errorAnalytics.getStatistics();
      expect(stats.total).toBe(1);
      expect(stats.byCategory[ERROR_CATEGORIES.VALIDATION]).toBe(1);
      expect(stats.bySeverity[ERROR_SEVERITY.MEDIUM]).toBe(1);
    });

    it('should limit stored errors to maximum count', () => {
      // Add more errors than the maximum
      for (let i = 0; i < 150; i++) {
        errorAnalytics.trackError({
          title: `Error ${i}`,
          message: `Test error ${i}`,
          category: ERROR_CATEGORIES.UNKNOWN,
          severity: ERROR_SEVERITY.LOW
        });
      }

      const stats = errorAnalytics.getStatistics();
      expect(stats.total).toBe(100); // Should be limited to maxErrors
    });

    it('should provide error statistics', () => {
      // Add various types of errors
      errorAnalytics.trackError({
        category: ERROR_CATEGORIES.NETWORK,
        severity: ERROR_SEVERITY.HIGH
      });
      errorAnalytics.trackError({
        category: ERROR_CATEGORIES.NETWORK,
        severity: ERROR_SEVERITY.HIGH
      });
      errorAnalytics.trackError({
        category: ERROR_CATEGORIES.VALIDATION,
        severity: ERROR_SEVERITY.MEDIUM
      });

      const stats = errorAnalytics.getStatistics();
      expect(stats.total).toBe(3);
      expect(stats.byCategory[ERROR_CATEGORIES.NETWORK]).toBe(2);
      expect(stats.byCategory[ERROR_CATEGORIES.VALIDATION]).toBe(1);
      expect(stats.bySeverity[ERROR_SEVERITY.HIGH]).toBe(2);
      expect(stats.bySeverity[ERROR_SEVERITY.MEDIUM]).toBe(1);
    });

    it('should clear all errors', () => {
      // Add some errors
      errorAnalytics.trackError({
        category: ERROR_CATEGORIES.CLIENT,
        severity: ERROR_SEVERITY.LOW
      });

      expect(errorAnalytics.getStatistics().total).toBe(1);

      errorAnalytics.clearErrors();
      expect(errorAnalytics.getStatistics().total).toBe(0);
    });
  });

  describe('Error message localization', () => {
    it('should provide Dutch error messages for all categories', () => {
      const categories = Object.values(ERROR_CATEGORIES);
      
      categories.forEach(category => {
        const formatted = formatErrorMessage(category, { message: 'test' });
        
        // Should have Dutch title and message
        expect(formatted.title).toBeTruthy();
        expect(formatted.message).toBeTruthy();
        expect(formatted.suggestions.length).toBeGreaterThan(0);
        
        // Check for Dutch keywords
        const dutchText = formatted.title + ' ' + formatted.message + ' ' + formatted.suggestions.join(' ');
        const hasDutchContent = /(?:probleem|fout|error|gegevens|probeer|opnieuw|contact|beheerder)/i.test(dutchText);
        expect(hasDutchContent).toBe(true);
      });
    });
  });

  describe('Development vs Production behavior', () => {
    it('should log errors in development mode', () => {
      // Mock import.meta.env.DEV
      const originalEnv = import.meta.env.DEV;
      import.meta.env.DEV = true;

      const consoleSpy = vi.spyOn(console, 'error');
      
      errorAnalytics.trackError({
        title: 'Test Error',
        category: ERROR_CATEGORIES.CLIENT,
        severity: ERROR_SEVERITY.LOW
      });

      expect(consoleSpy).toHaveBeenCalled();

      // Restore
      import.meta.env.DEV = originalEnv;
    });

    it('should send analytics in production mode', () => {
      // Mock production environment
      const originalEnv = import.meta.env.PROD;
      import.meta.env.PROD = true;

      // Mock gtag
      const gtagSpy = vi.fn();
      global.window = { 
        gtag: gtagSpy,
        location: { href: 'http://test.com' }
      };

      errorAnalytics.trackError({
        title: 'Test Error',
        category: ERROR_CATEGORIES.NETWORK,
        severity: ERROR_SEVERITY.HIGH
      });

      expect(gtagSpy).toHaveBeenCalledWith('event', 'error', {
        error_category: ERROR_CATEGORIES.NETWORK,
        error_severity: ERROR_SEVERITY.HIGH,
        error_component: 'unknown'
      });

      // Restore
      import.meta.env.PROD = originalEnv;
      delete global.window;
    });
  });
});