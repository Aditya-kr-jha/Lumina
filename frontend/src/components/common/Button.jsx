import Loader from './Loader';

const Button = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  fullWidth = false,
  loading = false,
  icon,
  iconPosition = 'left',
  ...props
}) => {
  const baseStyles = 'font-medium transition-all duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed active:scale-98';
  
  const variantStyles = {
    primary: 'bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-500 border border-transparent',
    secondary: 'bg-white text-purple-600 border-2 border-purple-600 hover:bg-purple-50 focus:ring-purple-500',
    ghost: 'bg-transparent text-purple-600 hover:bg-purple-50 focus:ring-purple-500 border border-transparent',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 border border-transparent',
  };
  
  const sizeStyles = {
    sm: 'h-8 px-4 text-sm rounded-md',
    md: 'h-10 px-6 text-base rounded-lg',
    lg: 'h-12 px-8 text-base rounded-lg',
  };
  
  const widthStyle = fullWidth ? 'w-full' : '';
  const isDisabled = disabled || loading;
  
  const renderContent = () => {
    if (loading) {
      return (
        <>
          <Loader size="sm" color="white" />
          {children}
        </>
      );
    }
    
    if (icon && iconPosition === 'left') {
      return (
        <>
          {icon}
          {children}
        </>
      );
    }
    
    if (icon && iconPosition === 'right') {
      return (
        <>
          {children}
          {icon}
        </>
      );
    }
    
    return children;
  };
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${widthStyle} ${className} flex items-center justify-center gap-2`}
      {...props}
    >
      {renderContent()}
    </button>
  );
};

export default Button;
