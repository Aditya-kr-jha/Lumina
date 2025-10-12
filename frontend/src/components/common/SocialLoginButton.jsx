import { Github, Chrome } from 'lucide-react';

const SocialLoginButton = ({ 
  provider, 
  onClick, 
  loading = false, 
  disabled = false,
  className = '' 
}) => {
  const providerConfig = {
    google: {
      icon: <Chrome className="w-5 h-5" />,
      text: 'Continue with Google',
      bgColor: 'hover:bg-gray-50',
    },
    github: {
      icon: <Github className="w-5 h-5" />,
      text: 'Continue with GitHub',
      bgColor: 'hover:bg-gray-50',
    },
  };

  const config = providerConfig[provider];
  
  if (!config) {
    console.warn(`Unknown provider: ${provider}`);
    return null;
  }

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className={`w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 bg-white transition-all duration-150 hover:border-gray-400 ${config.bgColor} disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 ${className}`}
    >
      {loading ? (
        <div className="w-5 h-5 border-2 border-gray-300 border-t-purple-600 rounded-full animate-spin" />
      ) : (
        config.icon
      )}
      <span>{config.text}</span>
    </button>
  );
};

export default SocialLoginButton;
