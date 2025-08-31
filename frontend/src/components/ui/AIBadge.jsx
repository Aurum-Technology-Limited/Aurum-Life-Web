import React from 'react';
import { Brain, Sparkles } from 'lucide-react';

/**
 * AIBadge Component - Shows AI confidence scores and insights
 * Used to indicate AI-powered features and confidence levels
 */
const AIBadge = ({ 
  confidence = 0, 
  onClick = null, 
  variant = 'default', 
  size = 'sm',
  showIcon = true,
  showText = true,
  className = ''
}) => {
  // Determine confidence level and styling
  const getConfidenceLevel = (score) => {
    if (score >= 0.8) return { level: 'high', color: 'text-green-400', bg: 'bg-green-500/20', border: 'border-green-500/30' };
    if (score >= 0.6) return { level: 'medium', color: 'text-yellow-400', bg: 'bg-yellow-500/20', border: 'border-yellow-500/30' };
    if (score >= 0.4) return { level: 'low', color: 'text-orange-400', bg: 'bg-orange-500/20', border: 'border-orange-500/30' };
    return { level: 'very-low', color: 'text-red-400', bg: 'bg-red-500/20', border: 'border-red-500/30' };
  };

  const confidenceStyle = getConfidenceLevel(confidence);
  
  // Size variants
  const sizeClasses = {
    xs: 'text-[10px] px-1.5 py-0.5',
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  // Icon sizes
  const iconSizes = {
    xs: 'h-3 w-3',
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  };

  const baseClasses = `
    inline-flex items-center space-x-1 rounded-full font-medium transition-all duration-200
    ${sizeClasses[size]}
    ${confidenceStyle.bg} ${confidenceStyle.border} ${confidenceStyle.color}
    ${onClick ? 'cursor-pointer hover:scale-105 hover:shadow-lg' : ''}
    ${className}
  `;

  const content = (
    <>
      {showIcon && (
        variant === 'sparkles' ? 
          <Sparkles className={iconSizes[size]} /> : 
          <Brain className={iconSizes[size]} />
      )}
      {showText && (
        <span>
          {variant === 'confidence' ? `${Math.round(confidence * 100)}%` : 'AI'}
        </span>
      )}
    </>
  );

  if (onClick) {
    return (
      <button
        onClick={onClick}
        className={`${baseClasses} border`}
        title={`AI Confidence: ${Math.round(confidence * 100)}% (${confidenceStyle.level})`}
      >
        {content}
      </button>
    );
  }

  return (
    <span 
      className={`${baseClasses} border`}
      title={`AI Confidence: ${Math.round(confidence * 100)}% (${confidenceStyle.level})`}
    >
      {content}
    </span>
  );
};

export default AIBadge;