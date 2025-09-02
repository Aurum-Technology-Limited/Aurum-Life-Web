import React from 'react';
import { Loader2, ChevronRight } from 'lucide-react';

const AIActionButton = ({ 
  icon: Icon, 
  title, 
  description, 
  buttonText, 
  onClick, 
  disabled = false, 
  isLoading = false,
  variant = 'default',
  size = 'default',
  quotaRequired = true
}) => {
  const variants = {
    default: 'bg-yellow-400 text-black hover:bg-yellow-500',
    secondary: 'bg-gray-700 text-white hover:bg-gray-600 border border-gray-600',
    success: 'bg-green-600 text-white hover:bg-green-700',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };

  const sizes = {
    small: 'p-4 text-sm',
    default: 'p-6',
    large: 'p-8'
  };

  const iconSizes = {
    small: 20,
    default: 24,
    large: 28
  };

  return (
    <div className={`rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group ${sizes[size]}`}>
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-12 h-12 rounded-lg bg-yellow-400 flex items-center justify-center group-hover:scale-110 transition-transform">
          <Icon size={iconSizes[size]} style={{ color: '#0B0D14' }} />
        </div>
        <div>
          <h3 className={`font-semibold text-white ${size === 'small' ? 'text-base' : 'text-lg'}`}>
            {title}
          </h3>
          {quotaRequired && (
            <span className="text-xs text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded-full">
              Uses AI quota
            </span>
          )}
        </div>
      </div>
      <p className={`text-gray-400 mb-6 leading-relaxed ${size === 'small' ? 'text-sm' : ''}`}>
        {description}
      </p>
      <button
        onClick={onClick}
        disabled={disabled || isLoading}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 ${variants[variant]}`}
      >
        {isLoading ? (
          <Loader2 size={18} className="animate-spin" />
        ) : (
          <>
            <span>{buttonText}</span>
            <ChevronRight size={16} />
          </>
        )}
      </button>
    </div>
  );
};

export default AIActionButton;