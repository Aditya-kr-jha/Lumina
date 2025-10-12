import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import { FileText, Zap, Shield, Users, User, Lock, Mail, CheckCircle } from 'lucide-react';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import SocialLoginButton from '../components/common/SocialLoginButton';
import PasswordStrengthIndicator from '../components/common/PasswordStrengthIndicator';
import { showToast } from '../components/common/Toast';
import {
  validateUsername,
  validateEmail,
  validatePassword,
} from '../utils/validators';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
    // Clear error for this field
    if (errors[field]) {
      setErrors({ ...errors, [field]: null });
    }
  };
  
  const validate = () => {
    const newErrors = {};
    
    const usernameError = validateUsername(formData.username);
    if (usernameError) newErrors.username = usernameError;
    
    const emailError = validateEmail(formData.email);
    if (emailError) newErrors.email = emailError;
    
    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!termsAccepted) {
      newErrors.terms = 'You must accept the terms and conditions';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsLoading(true);
    
    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      
      showToast('Account created successfully!', 'success');
      
      // Auto-login after registration
      const loginResult = await login(formData.username, formData.password);
      
      if (loginResult.success) {
        navigate('/dashboard');
      } else {
        // If auto-login fails, redirect to login page
        navigate('/');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed';
      setErrors({ general: errorMessage });
      showToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (provider) => {
    showToast(`${provider} registration coming soon!`, 'info');
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 p-12 flex-col justify-between relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute top-20 right-20 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-20 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl"></div>
        
        {/* Logo Section */}
        <div className="flex items-center gap-3 relative z-10">
          <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg">
            <FileText className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Lumina</h1>
            <p className="text-purple-100 text-sm">AI-Powered Document Intelligence</p>
          </div>
        </div>

        {/* Hero Section */}
        <div className="flex-1 flex items-center justify-center relative z-10">
          <div className="text-center space-y-8">
            {/* Illustration Placeholder */}
            <div className="w-64 h-48 bg-white/10 backdrop-blur-md rounded-3xl flex items-center justify-center shadow-2xl border border-white/20">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-gradient-to-br from-white/30 to-white/10 rounded-full flex items-center justify-center mx-auto shadow-lg">
                  <Users className="text-white" size={32} />
                </div>
                <div className="space-y-2">
                  <div className="w-12 h-2 bg-white/30 rounded-full mx-auto"></div>
                  <div className="w-8 h-2 bg-white/20 rounded-full mx-auto"></div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h2 className="text-4xl font-bold text-white leading-tight">
                Join Our Community! 🎉
              </h2>
              <p className="text-purple-100 text-lg max-w-md mx-auto leading-relaxed">
                Start analyzing your documents with AI today. Free to get started, powerful features included.
              </p>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="space-y-6 relative z-10">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center mx-auto mb-2 shadow-lg">
                <Zap className="text-white" size={22} />
              </div>
              <p className="text-white text-sm font-medium">Free to start</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center mx-auto mb-2 shadow-lg">
                <Shield className="text-white" size={22} />
              </div>
              <p className="text-white text-sm font-medium">Data Privacy</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-xl flex items-center justify-center mx-auto mb-2 shadow-lg">
                <CheckCircle className="text-white" size={22} />
              </div>
              <p className="text-white text-sm font-medium">10,000+ users</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12 bg-white/80 backdrop-blur-sm">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <FileText className="text-white" size={24} />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">Lumina</h1>
          </div>

          <div className="space-y-6 bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
            <div className="text-center lg:text-left">
              <h2 className="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent">
                Create your account
              </h2>
              <p className="mt-3 text-gray-600 text-lg">
                Start your free trial today ✨
              </p>
            </div>

            {/* Error Message */}
            {errors.general && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl animate-shake">
                <p className="text-sm text-red-600 flex items-center gap-2">
                  <span className="text-lg">⚠️</span>
                  {errors.general}
                </p>
              </div>
            )}

            {/* Registration Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                label="Username"
                type="text"
                value={formData.username}
                onChange={handleChange('username')}
                placeholder="Choose a username"
                error={errors.username}
                leftIcon={<User size={18} />}
                required
              />
              
              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={handleChange('email')}
                placeholder="Enter your email"
                error={errors.email}
                leftIcon={<Mail size={18} />}
                required
              />
              
              <div>
                <Input
                  label="Password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange('password')}
                  placeholder="Create a password"
                  error={errors.password}
                  leftIcon={<Lock size={18} />}
                  showPasswordToggle
                  required
                />
                <PasswordStrengthIndicator password={formData.password} />
              </div>
              
              <Input
                label="Confirm Password"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange('confirmPassword')}
                placeholder="Confirm your password"
                error={errors.confirmPassword}
                leftIcon={<Lock size={18} />}
                showPasswordToggle
                required
              />

              {/* Terms and Conditions */}
              <div className="space-y-2">
                <label className="flex items-start gap-3 group cursor-pointer">
                  <input
                    type="checkbox"
                    checked={termsAccepted}
                    onChange={(e) => setTermsAccepted(e.target.checked)}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500 mt-0.5 cursor-pointer"
                  />
                  <span className="text-sm text-gray-600 group-hover:text-gray-900 transition-colors">
                    I agree to the{' '}
                    <Link to="/terms" className="text-purple-600 hover:text-purple-700 font-medium hover:underline">
                      Terms of Service
                    </Link>{' '}
                    and{' '}
                    <Link to="/privacy" className="text-purple-600 hover:text-purple-700 font-medium hover:underline">
                      Privacy Policy
                    </Link>
                  </span>
                </label>
                {errors.terms && (
                  <p className="text-sm text-red-600">{errors.terms}</p>
                )}
              </div>
              
              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                loading={isLoading}
                disabled={isLoading}
              >
                Create Account
              </Button>
            </form>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            {/* Social Login */}
            <div className="space-y-3">
              <SocialLoginButton
                provider="google"
                onClick={() => handleSocialLogin('Google')}
                loading={isLoading}
                disabled={isLoading}
              />
              <SocialLoginButton
                provider="github"
                onClick={() => handleSocialLogin('GitHub')}
                loading={isLoading}
                disabled={isLoading}
              />
            </div>

            {/* Login Link */}
            <p className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <Link 
                to="/" 
                className="text-purple-600 hover:text-purple-700 font-semibold hover:underline transition-all"
              >
                Sign in here 🚀
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
