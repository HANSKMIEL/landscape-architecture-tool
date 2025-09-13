import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import { ErrorProvider } from '../../contexts/ErrorContext';
import { LanguageProvider } from '../../i18n/LanguageProvider';

// Mock the language provider
vi.mock('../../i18n/LanguageProvider', () => ({
  useLanguage: () => ({ t: (key) => key }),
  LanguageProvider: ({ children }) => children
}));

// Mock fetch globally
global.fetch = vi.fn();

const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <LanguageProvider>
      <ErrorProvider>
        {children}
      </ErrorProvider>
    </LanguageProvider>
  </BrowserRouter>
);

describe('Enhanced Login Component', () => {
  const mockOnLogin = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    fetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  const renderLogin = (props = {}) => {
    return render(
      <TestWrapper>
        <Login onLogin={mockOnLogin} {...props} />
      </TestWrapper>
    );
  };

  describe('Basic rendering and accessibility', () => {
    it('should render login form with proper accessibility attributes', () => {
      renderLogin();

      // Check for proper form elements with labels
      expect(screen.getByLabelText(/gebruikersnaam of e-mail/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/wachtwoord/i)).toBeInTheDocument();
      
      // Check for submit button
      const submitButton = screen.getByRole('button', { name: /inloggen/i });
      expect(submitButton).toBeInTheDocument();
      expect(submitButton).toBeDisabled(); // Should be disabled when fields are empty
      
      // Check for password visibility toggle
      const passwordToggle = screen.getByRole('button', { name: /wachtwoord tonen|wachtwoord verbergen/i });
      expect(passwordToggle).toBeInTheDocument();
    });

    it('should enable submit button when both fields are filled', async () => {
      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Initially disabled
      expect(submitButton).toBeDisabled();

      // Fill in fields
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'testpass' } });

      // Should be enabled now
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });

    it('should toggle password visibility', () => {
      renderLogin();

      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const passwordToggle = screen.getByRole('button', { name: /wachtwoord tonen|wachtwoord verbergen/i });

      // Initially password type
      expect(passwordInput.type).toBe('password');

      // Click toggle
      fireEvent.click(passwordToggle);
      expect(passwordInput.type).toBe('text');

      // Click again
      fireEvent.click(passwordToggle);
      expect(passwordInput.type).toBe('password');
    });
  });

  describe('Successful login flow', () => {
    it('should handle successful login with enhanced success feedback', async () => {
      // Mock successful login response
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ user: { id: 1, username: 'testuser' } })
      });

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/inloggen.../i)).toBeInTheDocument();
      });

      // Should call onLogin with user data
      await waitFor(() => {
        expect(mockOnLogin).toHaveBeenCalledWith({ id: 1, username: 'testuser' });
      });

      // Should have called fetch with correct parameters
      expect(fetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'testuser', password: 'password123' })
      });
    });
  });

  describe('Enhanced error handling', () => {
    it('should display enhanced error for 401 authentication failure', async () => {
      // Mock 401 response
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: () => Promise.resolve({ error: 'Invalid credentials' })
      });

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
      fireEvent.click(submitButton);

      // Should show enhanced error display
      await waitFor(() => {
        expect(screen.getByText(/inlogprobleem/i)).toBeInTheDocument();
      });

      // Should show retry button
      expect(screen.getByRole('button', { name: /opnieuw proberen/i })).toBeInTheDocument();
      
      // Should show actionable suggestions
      expect(screen.getByText(/aanbevolen acties/i)).toBeInTheDocument();
    });

    it('should display enhanced error for 423 account lockout', async () => {
      // Mock 423 response
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 423,
        statusText: 'Locked',
        json: () => Promise.resolve({ error: 'Account locked' })
      });

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'lockeduser' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(submitButton);

      // Should show enhanced error display with appropriate severity
      await waitFor(() => {
        expect(screen.getByText(/account is tijdelijk vergrendeld/i)).toBeInTheDocument();
      });
    });

    it('should display enhanced error for network failures', async () => {
      // Mock network error
      fetch.mockRejectedValueOnce(new Error('Network request failed'));

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(submitButton);

      // Should show enhanced network error display
      await waitFor(() => {
        expect(screen.getByText(/verbindingsprobleem|netwerkfout/i)).toBeInTheDocument();
      });

      // Should show network-specific suggestions
      await waitFor(() => {
        expect(screen.getByText(/controleer uw internetverbinding/i)).toBeInTheDocument();
      });
    });

    it('should display enhanced error for server errors', async () => {
      // Mock 500 server error
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ error: 'Server error' })
      });

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(submitButton);

      // Should show enhanced server error display
      await waitFor(() => {
        expect(screen.getByText(/serverfout/i)).toBeInTheDocument();
      });

      // Should show server-specific suggestions
      await waitFor(() => {
        expect(screen.getByText(/probeer het over een paar minuten opnieuw/i)).toBeInTheDocument();
      });
    });

    it('should handle retry functionality', async () => {
      // Mock initial failure, then success
      fetch
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: () => Promise.resolve({ error: 'Server error' })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ user: { id: 1, username: 'testuser' } })
        });

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(submitButton);

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText(/serverfout/i)).toBeInTheDocument();
      });

      // Click retry button
      const retryButton = screen.getByRole('button', { name: /opnieuw proberen/i });
      fireEvent.click(retryButton);

      // Should succeed on retry
      await waitFor(() => {
        expect(mockOnLogin).toHaveBeenCalledWith({ id: 1, username: 'testuser' });
      });
    });

    it('should clear errors when user starts typing', async () => {
      // Mock error response
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: () => Promise.resolve({ error: 'Invalid credentials' })
      });

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form to trigger error
      fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
      fireEvent.click(submitButton);

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText(/inlogprobleem/i)).toBeInTheDocument();
      });

      // Start typing in username field
      fireEvent.change(usernameInput, { target: { value: 'newuser' } });

      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText(/inlogprobleem/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Forgot password functionality', () => {
    it('should show forgot password form when clicked', () => {
      renderLogin();

      const forgotPasswordButton = screen.getByRole('button', { name: /wachtwoord vergeten/i });
      fireEvent.click(forgotPasswordButton);

      // Should show forgot password form
      expect(screen.getByText(/wachtwoord vergeten/i)).toBeInTheDocument();
      expect(screen.getByText(/voer uw e-mailadres in/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/e-mailadres/i)).toBeInTheDocument();
    });

    it('should handle successful password reset request', async () => {
      // Mock successful reset response
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ message: 'Reset email sent' })
      });

      renderLogin();

      // Go to forgot password form
      const forgotPasswordButton = screen.getByRole('button', { name: /wachtwoord vergeten/i });
      fireEvent.click(forgotPasswordButton);

      const emailInput = screen.getByLabelText(/e-mailadres/i);
      const resetButton = screen.getByRole('button', { name: /reset link verzenden/i });

      // Fill in email and submit
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(resetButton);

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText(/als het e-mailadres bestaat/i)).toBeInTheDocument();
      });
    });

    it('should handle password reset errors with enhanced error display', async () => {
      // Mock error response
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: () => Promise.resolve({ error: 'Invalid email format' })
      });

      renderLogin();

      // Go to forgot password form
      const forgotPasswordButton = screen.getByRole('button', { name: /wachtwoord vergeten/i });
      fireEvent.click(forgotPasswordButton);

      const emailInput = screen.getByLabelText(/e-mailadres/i);
      const resetButton = screen.getByRole('button', { name: /reset link verzenden/i });

      // Fill in invalid email and submit
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(resetButton);

      // Should show enhanced error display
      await waitFor(() => {
        expect(screen.getByText(/aanvraagfout/i)).toBeInTheDocument();
      });

      // Should show retry button
      expect(screen.getByRole('button', { name: /opnieuw proberen/i })).toBeInTheDocument();
    });
  });

  describe('Loading states and user feedback', () => {
    it('should show loading state during login attempt', async () => {
      // Mock slow response
      let resolveResponse;
      const slowPromise = new Promise(resolve => {
        resolveResponse = resolve;
      });
      
      fetch.mockReturnValueOnce(slowPromise);

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(submitButton);

      // Should show loading state
      expect(screen.getByText(/inloggen.../i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      // Resolve the promise
      resolveResponse({
        ok: true,
        json: () => Promise.resolve({ user: { id: 1, username: 'testuser' } })
      });

      // Loading should clear
      await waitFor(() => {
        expect(screen.queryByText(/inloggen.../i)).not.toBeInTheDocument();
      });
    });

    it('should disable form elements during loading', async () => {
      // Mock slow response
      let resolveResponse;
      const slowPromise = new Promise(resolve => {
        resolveResponse = resolve;
      });
      
      fetch.mockReturnValueOnce(slowPromise);

      renderLogin();

      const usernameInput = screen.getByLabelText(/gebruikersnaam of e-mail/i);
      const passwordInput = screen.getByLabelText(/wachtwoord/i);
      const submitButton = screen.getByRole('button', { name: /inloggen/i });
      const forgotPasswordButton = screen.getByRole('button', { name: /wachtwoord vergeten/i });

      // Fill in and submit form
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(submitButton);

      // All form elements should be disabled during loading
      expect(usernameInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();
      expect(submitButton).toBeDisabled();
      expect(forgotPasswordButton).toBeDisabled();

      // Resolve the promise
      resolveResponse({
        ok: true,
        json: () => Promise.resolve({ user: { id: 1, username: 'testuser' } })
      });

      // Form elements should be enabled again
      await waitFor(() => {
        expect(usernameInput).not.toBeDisabled();
      });
    });
  });
});