import { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const Toast = ({ id, message, type = 'info', duration = 4000, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  
  useEffect(() => {
    if (isPaused) return;
    
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Wait for fade out animation
    }, duration);
    
    return () => clearTimeout(timer);
  }, [duration, onClose, isPaused]);
  
  const icons = {
    success: <CheckCircle className="text-white" size={20} />,
    error: <AlertCircle className="text-white" size={20} />,
    info: <Info className="text-white" size={20} />,
    warning: <AlertTriangle className="text-white" size={20} />,
  };
  
  const bgColors = {
    success: 'bg-green-500 border-green-500',
    error: 'bg-red-500 border-red-500',
    info: 'bg-blue-500 border-blue-500',
    warning: 'bg-yellow-500 border-yellow-500',
  };
  
  const iconBgColors = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-blue-600',
    warning: 'bg-yellow-600',
  };
  
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg transition-all duration-300 min-w-80 max-w-96 ${
        bgColors[type]
      } ${isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'}`}
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      role="alert"
      aria-live="polite"
    >
      {/* Icon Section */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full ${iconBgColors[type]} flex items-center justify-center`}>
        {icons[type]}
      </div>
      
      {/* Message Section */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white leading-relaxed">{message}</p>
      </div>
      
      {/* Close Button */}
      <button
        onClick={() => {
          setIsVisible(false);
          setTimeout(onClose, 300);
        }}
        className="flex-shrink-0 ml-2 text-white/80 hover:text-white transition-colors p-1 rounded"
      >
        <X size={16} />
      </button>
    </div>
  );
};

// Toast Container Component
export const ToastContainer = () => {
  const [toasts, setToasts] = useState([]);
  
  useEffect(() => {
    // Listen for custom toast events
    const handleToast = (event) => {
      const toast = {
        id: Date.now() + Math.random(), // Ensure unique ID
        ...event.detail,
      };
      setToasts((prev) => {
        const newToasts = [...prev, toast];
        // Limit to maximum 5 toasts
        return newToasts.slice(-5);
      });
    };
    
    window.addEventListener('show-toast', handleToast);
    return () => window.removeEventListener('show-toast', handleToast);
  }, []);
  
  const removeToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };
  
  return (
    <div className="fixed top-4 right-4 z-50 space-y-3">
      {toasts.map((toast, index) => (
        <div
          key={toast.id}
          style={{ 
            transform: `translateY(${index * 4}px)`,
            zIndex: 50 - index 
          }}
        >
          <Toast
            id={toast.id}
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
    </div>
  );
};

// Helper function to show toasts
export const showToast = (message, type = 'info', duration = 4000) => {
  const event = new CustomEvent('show-toast', {
    detail: { message, type, duration },
  });
  window.dispatchEvent(event);
};

export default Toast;
