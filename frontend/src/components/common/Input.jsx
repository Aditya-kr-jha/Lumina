import { useState } from 'react';
import { Eye, EyeOff, X, Search } from 'lucide-react';

const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  error,
  helperText,
  required = false,
  disabled = false,
  readOnly = false,
  className = '',
  size = 'md',
  leftIcon,
  rightIcon,
  onRightIconClick,
  showPasswordToggle = false,
  showClearButton = false,
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);
  
  const inputType = showPasswordToggle ? (showPassword ? 'text' : 'password') : type;
  
  const sizeStyles = {
    sm: 'h-8 px-3 text-sm rounded-md',
    md: 'h-10 px-4 text-base rounded-lg',
    lg: 'h-12 px-5 text-base rounded-lg',
  };
  
  const handleClear = () => {
    if (onChange) {
      onChange({ target: { value: '' } });
    }
  };
  
  const getInputClassName = () => {
    let baseClasses = `w-full border transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-0 ${sizeStyles[size]}`;
    
    // Left icon padding
    if (leftIcon) {
      baseClasses += ' pl-10';
    }
    
    // Right icon/button padding
    if (rightIcon || showPasswordToggle || showClearButton) {
      baseClasses += ' pr-10';
    }
    
    // State-based styling
    if (error) {
      baseClasses += ' border-red-500 focus:ring-red-500 focus:border-red-500';
    } else {
      baseClasses += ' border-gray-300 focus:ring-purple-500 focus:border-purple-500';
    }
    
    // Disabled/readonly styling
    if (disabled) {
      baseClasses += ' bg-gray-100 cursor-not-allowed text-gray-500';
    } else if (readOnly) {
      baseClasses += ' bg-gray-50 cursor-default';
    } else {
      baseClasses += ' bg-white';
    }
    
    return baseClasses;
  };
  
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-900 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {/* Left Icon */}
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {leftIcon}
          </div>
        )}
        
        <input
          type={inputType}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          className={getInputClassName()}
          {...props}
        />
        
        {/* Right Icons/Buttons */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {showClearButton && value && (
            <button
              type="button"
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X size={16} />
            </button>
          )}
          
          {showPasswordToggle && type === 'password' && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          )}
          
          {rightIcon && (
            <button
              type="button"
              onClick={onRightIconClick}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              {rightIcon}
            </button>
          )}
        </div>
      </div>
      
      {/* Helper Text or Error Message */}
      {error ? (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      ) : helperText ? (
        <p className="mt-1 text-sm text-gray-500">{helperText}</p>
      ) : null}
    </div>
  );
};

export default Input;
