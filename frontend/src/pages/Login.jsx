import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FileText, Zap, Shield, Users, User, Lock } from 'lucide-react';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import SocialLoginButton from '../components/common/SocialLoginButton';
import { showToast } from '../components/common/Toast';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const validate = () => {
    const newErrors = {};
    
    if (!username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsLoading(true);
    const result = await login(username, password);
    setIsLoading(false);
    
    if (result.success) {
      showToast('Welcome back!', 'success');
      navigate('/dashboard');
    } else {
      setErrors({ general: result.error || 'Invalid username or password' });
      setPassword('');
    }
  };

  const handleSocialLogin = (provider) => {
    showToast(`${provider} login coming soon!`, 'info');
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
                  <FileText className="text-white" size={32} />
                </div>
                <div className="space-y-2">
                  <div className="w-12 h-2 bg-white/30 rounded-full mx-auto"></div>
                  <div className="w-8 h-2 bg-white/20 rounded-full mx-auto"></div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h2 className="text-4xl font-bold text-white leading-tight">
                Welcome Back! 👋
              </h2>
              <p className="text-purple-100 text-lg max-w-md mx-auto leading-relaxed">
                Continue your journey with AI-powered document analysis. Smart insights, instant answers.
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
              <p className="text-white text-sm font-medium">Instant Answers</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-xl flex items-center justify-center mx-auto mb-2 shadow-lg">
                <Shield className="text-white" size={22} />
              </div>
              <p className="text-white text-sm font-medium">Secure & Private</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-xl flex items-center justify-center mx-auto mb-2 shadow-lg">
                <Users className="text-white" size={22} />
              </div>
              <p className="text-white text-sm font-medium">AI-Powered</p>
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
                Welcome back
              </h2>
              <p className="mt-3 text-gray-600 text-lg">
                Sign in to continue your journey ✨
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

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              <Input
                label="Username or Email"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username or email"
                error={errors.username}
                leftIcon={<User size={18} />}
                required
              />
              
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                error={errors.password}
                leftIcon={<Lock size={18} />}
                showPasswordToggle
                required
              />

              <div className="flex items-center justify-between">
                <label className="flex items-center group cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500 cursor-pointer"
                  />
                  <span className="ml-2 text-sm text-gray-600 group-hover:text-gray-900 transition-colors">Remember me</span>
                </label>
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-purple-600 hover:text-purple-700 font-medium hover:underline transition-all"
                >
                  Forgot password?
                </Link>
              </div>
              
              <Button
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                loading={isLoading}
                disabled={isLoading}
              >
                Sign In
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

            {/* Register Link */}
            <p className="text-center text-sm text-gray-600">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                className="text-purple-600 hover:text-purple-700 font-semibold hover:underline transition-all"
              >
                Create one here 🚀
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
