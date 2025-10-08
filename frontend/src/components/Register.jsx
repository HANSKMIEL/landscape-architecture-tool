import React, { useState, useMemo, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Eye, EyeOff, Mail, Lock, User, AlertCircle, CheckCircle } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageProvider';

const translationDefaults = {
  title: 'Create Account',
  subtitle: 'Join the Landscape Architecture Tool',
  usernameLabel: 'Username',
  usernamePlaceholder: 'Enter your username',
  emailLabel: 'Email',
  emailPlaceholder: 'Enter your email',
  passwordLabel: 'Password',
  passwordPlaceholder: 'Enter your password',
  confirmPasswordLabel: 'Confirm Password',
  confirmPasswordPlaceholder: 'Confirm your password',
  createAccountButton: 'Create Account',
  creatingAccountLabel: 'Creating Account...',
  alreadyHaveAccount: 'Already have an account?',
  signInHere: 'Sign in here',
  registrationSuccess: 'Registration successful! Please log in with your new account.',
  loginRedirectSuccess: 'Account created successfully! Please log in.',
  usernameTooShort: 'Username must be at least 3 characters long',
  invalidEmail: 'Please enter a valid email address',
  passwordTooShort: 'Password must be at least 6 characters long',
  passwordMismatch: 'Passwords do not match',
  duplicateAccount: 'Username or email already exists',
  invalidRegistrationData: 'Invalid registration data',
  registrationFailed: 'Registration failed',
  networkError: 'Network error. Please try again.',
  formHeading: 'Create Account'
};

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();
  const { t } = useLanguage();

  const translate = useCallback(
    (key) => t(`register.${key}`, translationDefaults[key] ?? key),
    [t]
  );

  const uiText = useMemo(
    () => ({
      title: translate('title'),
      subtitle: translate('subtitle'),
      usernameLabel: translate('usernameLabel'),
      usernamePlaceholder: translate('usernamePlaceholder'),
      emailLabel: translate('emailLabel'),
      emailPlaceholder: translate('emailPlaceholder'),
      passwordLabel: translate('passwordLabel'),
      passwordPlaceholder: translate('passwordPlaceholder'),
      confirmPasswordLabel: translate('confirmPasswordLabel'),
      confirmPasswordPlaceholder: translate('confirmPasswordPlaceholder'),
      createAccountButton: translate('createAccountButton'),
      creatingAccountLabel: translate('creatingAccountLabel'),
      alreadyHaveAccount: translate('alreadyHaveAccount'),
      signInHere: translate('signInHere'),
      registrationSuccess: translate('registrationSuccess'),
      loginRedirectSuccess: translate('loginRedirectSuccess'),
      usernameTooShort: translate('usernameTooShort'),
      invalidEmail: translate('invalidEmail'),
      passwordTooShort: translate('passwordTooShort'),
      passwordMismatch: translate('passwordMismatch'),
      duplicateAccount: translate('duplicateAccount'),
      invalidRegistrationData: translate('invalidRegistrationData'),
      registrationFailed: translate('registrationFailed'),
      networkError: translate('networkError')
    }),
    [translate]
  );

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear errors when user starts typing
    if (error) setError('');
  };

  const validateForm = () => {
    if (!formData.username || formData.username.length < 3) {
      setError(uiText.usernameTooShort);
      return false;
    }
    if (!formData.email || !formData.email.includes('@')) {
      setError(uiText.invalidEmail);
      return false;
    }
    if (!formData.password || formData.password.length < 6) {
      setError(uiText.passwordTooShort);
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError(uiText.passwordMismatch);
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(uiText.registrationSuccess);
        setTimeout(() => {
          navigate(`/login?success=${encodeURIComponent(uiText.loginRedirectSuccess)}`);
        }, 2000);
      } else {
        // Handle specific error cases
        if (response.status === 409) {
          setError(data.error || uiText.duplicateAccount);
        } else if (response.status === 400) {
          setError(data.error || uiText.invalidRegistrationData);
        } else {
          setError(data.error || uiText.registrationFailed);
        }
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError(uiText.networkError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            {uiText.title}
          </CardTitle>
          <CardDescription className="text-gray-600">
            {uiText.subtitle}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            {success && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="username" className="text-sm font-medium text-gray-700">
                {uiText.usernameLabel}
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder={uiText.usernamePlaceholder}
                  value={formData.username}
                  onChange={handleInputChange}
                  className="pl-10"
                  required
                  minLength={3}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                {uiText.emailLabel}
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder={uiText.emailPlaceholder}
                  value={formData.email}
                  onChange={handleInputChange}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                {uiText.passwordLabel}
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={uiText.passwordPlaceholder}
                  value={formData.password}
                  onChange={handleInputChange}
                  className="pl-10 pr-10"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                {uiText.confirmPasswordLabel}
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder={uiText.confirmPasswordPlaceholder}
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="pl-10 pr-10"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {uiText.creatingAccountLabel}
                </>
              ) : (
                uiText.createAccountButton
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              {uiText.alreadyHaveAccount}{' '}
              <Link 
                to="/login" 
                className="font-medium text-green-600 hover:text-green-500 transition-colors"
              >
                {uiText.signInHere}
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Register;
