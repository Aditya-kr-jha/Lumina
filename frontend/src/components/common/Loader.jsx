const Loader = ({ 
  size = 'md', 
  color = 'primary', 
  variant = 'spinner', 
  className = '' 
}) => {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  };
  
  const colorStyles = {
    primary: 'text-purple-600',
    secondary: 'text-gray-600',
    white: 'text-white',
  };
  
  const dotSizeStyles = {
    sm: 'w-1 h-1',
    md: 'w-1.5 h-1.5',
    lg: 'w-2 h-2',
    xl: 'w-2.5 h-2.5',
  };
  
  // Spinner Variant
  if (variant === 'spinner') {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <svg
          className={`animate-spin ${colorStyles[color]} ${sizeStyles[size]}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
    );
  }
  
  // Dots Variant
  if (variant === 'dots') {
    return (
      <div className={`flex items-center justify-center gap-1 ${className}`}>
        <div
          className={`${dotSizeStyles[size]} ${colorStyles[color]} rounded-full animate-bounce`}
          style={{ animationDelay: '0ms' }}
        />
        <div
          className={`${dotSizeStyles[size]} ${colorStyles[color]} rounded-full animate-bounce`}
          style={{ animationDelay: '150ms' }}
        />
        <div
          className={`${dotSizeStyles[size]} ${colorStyles[color]} rounded-full animate-bounce`}
          style={{ animationDelay: '300ms' }}
        />
      </div>
    );
  }
  
  // Progress Bar Variant
  if (variant === 'bar') {
    return (
      <div className={`w-full bg-gray-200 rounded-full ${size === 'sm' ? 'h-1' : 'h-2'} ${className}`}>
        <div
          className={`bg-purple-600 rounded-full transition-all duration-300 animate-pulse`}
          style={{ width: '60%' }}
        />
      </div>
    );
  }
  
  return null;
};

export default Loader;
