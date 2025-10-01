import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card as _Card, CardContent as _CardContent, CardDescription as _CardDescription, CardHeader as _CardHeader, CardTitle as _CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Eye, EyeOff, Mail, Lock, User, AlertCircle, CheckCircle, LogIn } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageProvider';

const Login = ({ onLogin }) => {
  const [__formData, set_formData] = useState({
    username: '',
    password: ''
  });
  const [__showPassword, set_showPassword] = useState(false);
  const [__isLoading, set_isLoading] = useState(false);
  const [__error, set_error] = useState('');
  const [__errorType, set_errorType] = useState(''); // 'network', 'auth', 'validation', 'server'
  const [__retryCount, set_retryCount] = useState(0);
  const [__success, set_success] = useState('');
  const [__showForgotPassword, set_showForgotPassword] = useState(false);
  const [__forgotPasswordEmail, set_forgotPasswordEmail] = useState('');
  const [__forgotPasswordLoading, set_forgotPasswordLoading] = useState(false);
  const [__forgotPasswordSuccess, set_forgotPasswordSuccess] = useState(false);
  const [__isRetrying, set_isRetrying] = useState(false);
  const [__focusedField, set_focusedField] = useState('');
  
  const navigate = useNavigate();
  const location = useLocation();
  const { t: _t } = useLanguage();

  // Error analytics logging
  const logError = (errorType, errorMessage, context = {}) => {
    const __errorData = {
      timestamp: new Date().toISOString(),
      type: errorType,
      message: errorMessage,
      userAgent: navigator.userAgent,
      url: window.location.href,
      retryCount,
      ...context
    };
    
    // Log to console for development
    console.error('Login Error Analytics:', errorData);
    
    // In production, this would send to analytics service
    // analytics.track('login_error', errorData);
  };

  // Check for success messages from URL params (e.g., after password reset)
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const successMessage = urlParams.get('success');
    if (successMessage) {
      setSuccess(decodeURIComponent(successMessage));
      // Clean up URL
      navigate('/login', { replace: true });
    }
  }, [location, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear errors when user starts typing
    if (error) setError('');
  };

  // Enhanced error handling function with improved UX messages
  const handleApiError = (error, response) => {
    let errorMessage = '';
    let errorType = '';
    
    if (!response) {
      // Network error
      errorType = 'network';
      errorMessage = '🌐 Connection issue detected. Please check your internet connection and try again.';
      logError('network', 'Network connection failed', { error: error?.message });
    } else {
      const status = response.status;
      const apiError = error?.error || 'Unknown error';

      switch (status) {
        case 400:
          errorType = 'validation';
          if (apiError === 'Invalid input') {
            errorMessage = '📝 Please ensure all fields are filled out correctly and try again.';
          } else {
            errorMessage = '📝 The information provided appears to be invalid. Please double-check and try again.';
          }
          logError('validation', apiError, { status, formData: { username: formData.username } });
          break;
        
        case 401:
          errorType = 'auth';
          if (apiError === 'Invalid credentials') {
            errorMessage = '🔐 The username or password you entered is incorrect. Please check your credentials and try again.';
          } else {
            errorMessage = '🔐 Authentication failed. Please verify your login information.';
          }
          logError('authentication', apiError, { status, username: formData.username });
          break;
        
        case 423:
          errorType = 'auth';
          errorMessage = '🔒 Your account has been temporarily locked for security reasons. Please try again in a few minutes or contact support.';
          logError('account_locked', apiError, { status, username: formData.username });
          break;
        
        case 429:
          errorType = 'server';
          errorMessage = '⏱️ Too many login attempts detected. Please wait a moment before trying again to ensure security.';
          logError('rate_limited', apiError, { status, retryCount });
          break;
        
        case 500:
        case 502:
        case 503:
          errorType = 'server';
          errorMessage = '🔧 Our servers are experiencing temporary issues. Please try again in a few moments.';
          logError('server_error', apiError, { status });
          break;
        
        default:
          errorType = 'server';
          errorMessage = '❗ An unexpected error occurred. Please try again or contact support if the problem persists.';
          logError('unknown_error', apiError, { status });
          break;
      }
    }

    setErrorType(errorType);
    return errorMessage;
  };

  // Enhanced retry mechanism with loading states
  const handleRetry = async () => {
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    setError('');
    setErrorType('');
    
    // Small delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const __syntheticEvent = {
      preventDefault: () => {},
      target: { checkValidity: () => true }
    };
    
    await handleSubmit(syntheticEvent);
    setIsRetrying(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setErrorType('');

    // Validation
    if (!formData.username.trim()) {
      setError('Username is required');
      setErrorType('validation');
      setIsLoading(false);
      return;
    }

    if (!formData.password.trim()) {
      setError('Password is required');
      setErrorType('validation');
      setIsLoading(false);
      return;
    }

    try {
      // Use the onLogin prop which is actually handleLogin from App.jsx
      await onLogin(formData);
      setSuccess('Login successful! Redirecting...');
      setRetryCount(0); // Reset retry count on success
      
      // Redirect to intended page or dashboard
      const from = location.state?.from?.pathname || '/dashboard';
      setTimeout(() => {
        navigate(from, { replace: true });
      }, 500);
    } catch (err) {
      console.error('Login error:', err);
      // Enhanced error handling with better UX messages
      const errorMessage = handleApiError(err, null);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setForgotPasswordLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: forgotPasswordEmail }),
      });

      const data = await response.json();

      if (response.ok) {
        setForgotPasswordSuccess(true);
        setForgotPasswordEmail('');
      } else {
        setError(data.error || 'Failed to send reset email');
      }
    } catch (err) {
      console.error('Forgot password error:', err);
      setError('Network error. Please try again.');
    } finally {
      setForgotPasswordLoading(false);
    }
  };

  const resetForgotPasswordForm = () => {
    setShowForgotPassword(false);
    setForgotPasswordEmail('');
    setForgotPasswordSuccess(false);
    setError('');
  };

  if (showForgotPassword) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="text-center mb-8">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-green-600 to-blue-600 rounded-xl flex items-center justify-center mb-6">
              <span className="text-white text-2xl font-bold">LA</span>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Wachtwoord Vergeten
            </h2>
            <p className="text-gray-600">
              Voer uw e-mailadres in om een reset link te ontvangen
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-xl p-8">
            {forgotPasswordSuccess ? (
              <div className="space-y-4">
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    Als het e-mailadres bestaat, is er een reset link verzonden.
                  </AlertDescription>
                </Alert>
                <Button 
                  onClick={resetForgotPasswordForm}
                  className="w-full"
                  variant="outline"
                >
                  Terug naar inloggen
                </Button>
              </div>
            ) : (
              <form onSubmit={handleForgotPassword} className="space-y-4">
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-800">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                    E-mailadres
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="email"
                      type="email"
                      value={forgotPasswordEmail}
                      onChange={(e) => setForgotPasswordEmail(e.target.value)}
                      placeholder="Voer uw e-mailadres in"
                      className="pl-10"
                      required
                      disabled={forgotPasswordLoading}
                    />
                  </div>
                </div>

                <div className="space-y-3">
                  <Button 
                    type="submit" 
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    disabled={forgotPasswordLoading || !forgotPasswordEmail}
                  >
                    {forgotPasswordLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Verzenden...
                      </>
                    ) : (
                      'Reset Link Verzenden'
                    )}
                  </Button>

                  <Button 
                    type="button"
                    onClick={resetForgotPasswordForm}
                    className="w-full"
                    variant="outline"
                    disabled={forgotPasswordLoading}
                  >
                    Terug naar inloggen
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Header */}
        <div className="text-center">
          <div className="mx-auto w-20 h-20 bg-gradient-to-br from-green-600 to-blue-600 rounded-xl flex items-center justify-center mb-6">
            <span className="text-white text-2xl font-bold">LA</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Landschapsarchitectuur Tool
          </h2>
          <p className="text-gray-600">
            Inloggen om toegang te krijgen tot uw projecten
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert 
                id="login-error"
                role="alert"
                aria-live="polite"
                aria-atomic="true"
                className={`border-l-4 ${
                  errorType === 'network' ? 'border-orange-400 bg-orange-50' : 'border-red-400 bg-red-50'
                }`}
              >
                <AlertCircle className={`h-4 w-4 ${
                  errorType === 'network' ? 'text-orange-600' : 'text-red-600'
                }`} />
                <div>
                  <AlertDescription className={`${
                    errorType === 'network' ? 'text-orange-800' : 'text-red-800'
                  }`}>
                    {error}
                  </AlertDescription>
                  {/* Show retry button for network errors or server errors */}
                  {(errorType === 'network' || errorType === 'server') && retryCount < 3 && (
                    <div className="flex items-center gap-2 mt-2">
                      <Button
                        type="button"
                        onClick={handleRetry}
                        variant="outline"
                        size="sm"
                        className="text-xs"
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                            Retrying...
                          </>
                        ) : (
                          'Try Again'
                        )}
                      </Button>
                      {retryCount > 0 && (
                        <span className="text-xs text-gray-500">
                          Attempt {retryCount + 1}/3
                        </span>
                      )}
                    </div>
                  )}
                  
                  {/* Help text based on error type */}
                  {errorType === 'auth' && (
                    <div className="mt-2 text-xs text-gray-600">
                      <button
                        type="button"
                        onClick={() => setShowForgotPassword(true)}
                        className="text-blue-600 hover:text-blue-800 underline"
                      >
                        Forgot your password?
                      </button>
                    </div>
                  )}
                  
                  {errorType === 'validation' && (
                    <div className="mt-2 text-xs text-gray-600">
                      Please check that all fields are filled correctly.
                    </div>
                  )}
                </div>
              </Alert>
            )}

            {success && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  {success}
                </AlertDescription>
              </Alert>
            )}

            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Gebruikersnaam of E-mail
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  onFocus={() => setFocusedField('username')}
                  onBlur={() => setFocusedField('')}
                  className={`block w-full pl-10 pr-3 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-colors ${
                    errorType === 'validation' || errorType === 'auth' 
                      ? 'border-red-300 focus:ring-red-500' 
                      : 'border-gray-300 focus:ring-green-500'
                  }`}
                  placeholder="Voer uw gebruikersnaam of e-mail in"
                  disabled={isLoading || isRetrying}
                  aria-describedby={error ? "login-error" : undefined}
                  aria-invalid={errorType === 'validation' || errorType === 'auth'}
                  aria-label="Username or email address"
                  autoComplete="username"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Wachtwoord
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField('')}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && formData.username && formData.password) {
                      handleSubmit(e);
                    }
                  }}
                  className={`block w-full pl-10 pr-12 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-colors ${
                    errorType === 'validation' || errorType === 'auth' 
                      ? 'border-red-300 focus:ring-red-500' 
                      : 'border-gray-300 focus:ring-green-500'
                  }`}
                  placeholder="Voer uw wachtwoord in"
                  disabled={isLoading || isRetrying}
                  autoComplete="current-password"
                  aria-describedby={error ? "login-error" : undefined}
                  aria-invalid={errorType === 'validation' || errorType === 'auth'}
                  aria-label="Password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500 rounded"
                  disabled={isLoading || isRetrying}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  tabIndex={0}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || isRetrying || !formData.username || !formData.password}
              className="w-full flex justify-center items-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              aria-describedby={error ? "login-error" : undefined}
              aria-label={isLoading || isRetrying ? "Logging in, please wait" : "Log in to your account"}
            >
              {isLoading || isRetrying ? (
                <div className="flex items-center">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  {isRetrying ? 'Retrying...' : 'Inloggen...'}
                </div>
              ) : (
                <div className="flex items-center">
                  <LogIn className="h-4 w-4 mr-2" />
                  Inloggen
                </div>
              )}
            </button>

            {/* Forgot Password Button */}
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="w-full text-blue-600 hover:text-blue-800 text-sm font-medium py-2 transition-colors"
              disabled={isLoading}
            >
              Wachtwoord vergeten?
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Demo Toegangscodes:</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Beheerder:</strong> admin / admin123</div>
              <div><strong>Medewerker:</strong> employee / employee123</div>
              <div><strong>Klant:</strong> client / client123</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>© 2025 Landschapsarchitectuur Tool</p>
          <p>Veilig en professioneel projectbeheer</p>
        </div>
      </div>
    </div>
  );
};

export default Login;