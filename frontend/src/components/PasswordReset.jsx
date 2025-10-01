import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Eye, EyeOff, Lock, AlertCircle, CheckCircle, KeyRound } from 'lucide-react';
import { useLanguage } from '../i18n/LanguageProvider';

const PasswordReset = () => {
  const { t } = useLanguage();
  const [formData, setFormData] = useState({
    new_password: '',
    confirm_password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [token, setToken] = useState('');
  const [tokenValid, setTokenValid] = useState(null);

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const resetToken = searchParams.get('token');
    if (resetToken) {
      setToken(resetToken);
      validateToken(resetToken);
    } else {
      setError('Invalid reset link. Please request a new password reset.');
    }
  }, [searchParams]);

  const validateToken = async (_resetToken) => {
    try {
      // We'll validate the token when the user submits the form
      // For now, just assume it's valid if it exists
      setTokenValid(true);
    } catch {
      setError('Invalid or expired reset token.');
      setTokenValid(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear errors when user starts typing
    if (error) setError('');
  };

  const validatePassword = (password) => {
    if (password.length < 8) {
      return t('password.validation.minLength', 'Password must be at least 8 characters long');
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return t('password.validation.lowercase', 'Password must contain at least one lowercase letter');
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return t('password.validation.uppercase', 'Password must contain at least one uppercase letter');
    }
    if (!/(?=.*\d)/.test(password)) {
      return t('password.validation.number', 'Password must contain at least one number');
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validate passwords match
    if (formData.new_password !== formData.confirm_password) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    // Validate password strength
    const passwordError = validatePassword(formData.new_password);
    if (passwordError) {
      setError(passwordError);
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: formData.new_password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Password reset successfully! Redirecting to login...');
        setTimeout(() => {
          navigate('/login?success=' + encodeURIComponent('Password reset successfully. Please log in with your new password.'));
        }, 2000);
      } else {
        if (response.status === 400) {
          setError('Invalid or expired reset token. Please request a new password reset.');
        } else {
          setError(data.error || 'Failed to reset password');
        }
      }
    } catch (_err) {
      console.error('Password reset error:', _err);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getPasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/(?=.*[a-z])/.test(password)) strength++;
    if (/(?=.*[A-Z])/.test(password)) strength++;
    if (/(?=.*\d)/.test(password)) strength++;
    if (/(?=.*[@$!%*?&])/.test(password)) strength++;

    return strength;
  };

  const getStrengthColor = (strength) => {
    if (strength < 2) return 'bg-red-500';
    if (strength < 3) return 'bg-yellow-500';
    if (strength < 4) return 'bg-blue-500';
    return 'bg-green-500';
  };

  const getStrengthText = (strength) => {
    if (strength < 2) return 'Weak';
    if (strength < 3) return 'Fair';
    if (strength < 4) return 'Good';
    return 'Strong';
  };

  if (tokenValid === false) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-red-600">Invalid Reset Link</CardTitle>
            <CardDescription>
              This password reset link is invalid or has expired.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                Please request a new password reset from the login page.
              </AlertDescription>
            </Alert>
            <Button 
              onClick={() => navigate('/login')}
              className="w-full"
            >
              Back to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-green-600 to-blue-600 rounded-xl flex items-center justify-center mb-4">
            <KeyRound className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Reset Your Password
          </CardTitle>
          <CardDescription>
            Enter your new password below
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
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

            <div className="space-y-2">
              <Label htmlFor="new_password" className="text-sm font-medium text-gray-700">
                New Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="new_password"
                  name="new_password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.new_password}
                  onChange={handleInputChange}
                  placeholder={t("password.placeholder.new", "Enter your new password")}
                  className="pl-10 pr-10"
                  required
                  disabled={isLoading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              
              {/* Password Strength Indicator */}
              {formData.new_password && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${getStrengthColor(getPasswordStrength(formData.new_password))}`}
                        style={{ width: `${(getPasswordStrength(formData.new_password) / 5) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">
                      {getStrengthText(getPasswordStrength(formData.new_password))}
                    </span>
                  </div>
                  <div className="text-xs text-gray-600">
                    Password must contain:
                    <ul className="mt-1 space-y-1">
                      <li className={formData.new_password.length >= 8 ? 'text-green-600' : 'text-gray-400'}>
                        ✓ At least 8 characters
                      </li>
                      <li className={/(?=.*[a-z])/.test(formData.new_password) ? 'text-green-600' : 'text-gray-400'}>
                        ✓ One lowercase letter
                      </li>
                      <li className={/(?=.*[A-Z])/.test(formData.new_password) ? 'text-green-600' : 'text-gray-400'}>
                        ✓ One uppercase letter
                      </li>
                      <li className={/(?=.*\d)/.test(formData.new_password) ? 'text-green-600' : 'text-gray-400'}>
                        ✓ One number
                      </li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm_password" className="text-sm font-medium text-gray-700">
                Confirm New Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="confirm_password"
                  name="confirm_password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirm_password}
                  onChange={handleInputChange}
                  placeholder={t("password.placeholder.confirm", "Confirm your new password")}
                  className="pl-10 pr-10"
                  required
                  disabled={isLoading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  disabled={isLoading}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              
              {/* Password Match Indicator */}
              {formData.confirm_password && (
                <div className="text-xs">
                  {formData.new_password === formData.confirm_password ? (
                    <span className="text-green-600">✓ Passwords match</span>
                  ) : (
                    <span className="text-red-600">✗ Passwords do not match</span>
                  )}
                </div>
              )}
            </div>

            <div className="space-y-3">
              <Button 
                type="submit" 
                className="w-full bg-green-600 hover:bg-green-700"
                disabled={isLoading || !formData.new_password || !formData.confirm_password}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Resetting Password...
                  </>
                ) : (
                  'Reset Password'
                )}
              </Button>

              <Button 
                type="button"
                onClick={() => navigate('/login')}
                className="w-full"
                variant="outline"
                disabled={isLoading}
              >
                Back to Login
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default PasswordReset;
