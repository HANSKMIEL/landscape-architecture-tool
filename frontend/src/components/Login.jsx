import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Eye, EyeOff, Mail, Lock, User, AlertCircle, CheckCircle, LogIn } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageProvider';
import { useError } from '../contexts/ErrorContext';
import EnhancedErrorDisplay from './EnhancedErrorDisplay';
import { handleApiError } from '../utils/errorHandling';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState('');
  const [forgotPasswordLoading, setForgotPasswordLoading] = useState(false);
  const [forgotPasswordSuccess, setForgotPasswordSuccess] = useState(false);
  const [formattedError, setFormattedError] = useState(null);
  
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();
  const { handleApiError: handleApiErrorWithContext, showSuccess } = useError();

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
    if (formattedError) setFormattedError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setFormattedError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Show success message
        showSuccess('Inloggen succesvol');
        onLogin(data.user);
        
        // Redirect to intended page or dashboard
        const from = location.state?.from?.pathname || '/dashboard';
        navigate(from, { replace: true });
      } else {
        // Use enhanced error handling
        const errorInfo = await handleApiErrorWithContext(response, {
          component: 'Login',
          action: 'authentication',
          endpoint: '/api/auth/login'
        });
        
        setFormattedError(errorInfo);
        
        // Keep backward compatibility for simple error display
        if (response.status === 423) {
          setError('Account is tijdelijk vergrendeld vanwege mislukte inlogpogingen');
        } else if (response.status === 401) {
          setError('Ongeldige gebruikersnaam of wachtwoord');
        } else {
          const data = await response.json().catch(() => ({}));
          setError(data.error || 'Inloggen mislukt');
        }
      }
    } catch (err) {
      console.error('Login error:', err);
      
      // Use enhanced error handling for network errors
      const errorInfo = await handleApiErrorWithContext({
        ok: false,
        status: 0,
        statusText: 'Network Error',
        json: () => Promise.resolve({ error: err.message })
      }, {
        component: 'Login',
        action: 'authentication',
        endpoint: '/api/auth/login'
      });
      
      setFormattedError(errorInfo);
      setError('Netwerkfout. Probeer het opnieuw.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setForgotPasswordLoading(true);
    setError('');
    setFormattedError(null);

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: forgotPasswordEmail }),
      });

      if (response.ok) {
        setForgotPasswordSuccess(true);
        setForgotPasswordEmail('');
        showSuccess('Reset link verzonden naar uw e-mailadres');
      } else {
        // Use enhanced error handling
        const errorInfo = await handleApiErrorWithContext(response, {
          component: 'Login',
          action: 'password_reset',
          endpoint: '/api/auth/forgot-password'
        });
        
        setFormattedError(errorInfo);
        
        const data = await response.json().catch(() => ({}));
        setError(data.error || 'Reset e-mail verzenden mislukt');
      }
    } catch (err) {
      console.error('Forgot password error:', err);
      
      // Use enhanced error handling for network errors
      const errorInfo = await handleApiErrorWithContext({
        ok: false,
        status: 0,
        statusText: 'Network Error',
        json: () => Promise.resolve({ error: err.message })
      }, {
        component: 'Login',
        action: 'password_reset',
        endpoint: '/api/auth/forgot-password'
      });
      
      setFormattedError(errorInfo);
      setError('Netwerkfout. Probeer het opnieuw.');
    } finally {
      setForgotPasswordLoading(false);
    }
  };

  const resetForgotPasswordForm = () => {
    setShowForgotPassword(false);
    setForgotPasswordEmail('');
    setForgotPasswordSuccess(false);
    setError('');
    setFormattedError(null);
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
                {/* Enhanced error display */}
                {formattedError && (
                  <EnhancedErrorDisplay
                    error={formattedError}
                    onRetry={() => handleForgotPassword({ preventDefault: () => {} })}
                    showSuggestions={true}
                    showRetry={true}
                    compact={false}
                    analyticsContext={{
                      component: 'Login',
                      action: 'password_reset'
                    }}
                  />
                )}
                
                {/* Fallback error display for backward compatibility */}
                {error && !formattedError && (
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
            {/* Enhanced error display */}
            {formattedError && (
              <EnhancedErrorDisplay
                error={formattedError}
                onRetry={() => handleSubmit({ preventDefault: () => {} })}
                showSuggestions={true}
                showRetry={true}
                compact={false}
                analyticsContext={{
                  component: 'Login',
                  action: 'authentication'
                }}
              />
            )}
            
            {/* Fallback error display for backward compatibility */}
            {error && !formattedError && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
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
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                  placeholder="Voer uw gebruikersnaam of e-mail in"
                  disabled={isLoading}
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
                  className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                  placeholder="Voer uw wachtwoord in"
                  disabled={isLoading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  disabled={isLoading}
                  aria-label={showPassword ? "Wachtwoord verbergen" : "Wachtwoord tonen"}
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
              disabled={isLoading || !formData.username || !formData.password}
              className="w-full flex justify-center items-center px-4 py-3 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Inloggen...
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