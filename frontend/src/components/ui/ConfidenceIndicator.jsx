import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

/**
 * ConfidenceIndicator Component - Visual representation of AI confidence levels
 * Shows confidence as a progress bar with color coding and trend indicators
 */
const ConfidenceIndicator = ({ 
  confidence = 0, 
  showPercentage = true, 
  showTrend = false,
  trend = null, // 'up', 'down', 'stable'
  size = 'md',
  orientation = 'horizontal',
  className = ''
}) => {
  // Confidence level styling
  const getConfidenceStyle = (score) => {
    if (score >= 0.8) return { 
      color: 'bg-green-500', 
      textColor: 'text-green-400',
      label: 'High Confidence'
    };
    if (score >= 0.6) return { 
      color: 'bg-yellow-500', 
      textColor: 'text-yellow-400',
      label: 'Medium Confidence'
    };
    if (score >= 0.4) return { 
      color: 'bg-orange-500', 
      textColor: 'text-orange-400',
      label: 'Low Confidence'
    };
    return { 
      color: 'bg-red-500', 
      textColor: 'text-red-400',
      label: 'Very Low Confidence'
    };
  };

  const confidenceStyle = getConfidenceStyle(confidence);
  const percentage = Math.round(confidence * 100);

  // Size variants
  const sizeConfig = {
    sm: { height: 'h-1', width: 'w-16', text: 'text-xs' },
    md: { height: 'h-2', width: 'w-24', text: 'text-sm' },
    lg: { height: 'h-3', width: 'w-32', text: 'text-base' }
  };

  const config = sizeConfig[size];

  // Trend icon
  const getTrendIcon = () => {
    if (!showTrend || !trend) return null;
    
    const iconClass = `h-3 w-3 ${confidenceStyle.textColor}`;
    switch (trend) {
      case 'up': return <TrendingUp className={iconClass} />;
      case 'down': return <TrendingDown className={iconClass} />;
      case 'stable': return <Minus className={iconClass} />;
      default: return null;
    }
  };

  if (orientation === 'vertical') {
    return (
      <div className={`flex flex-col items-center space-y-2 ${className}`}>
        <div className={`${config.width} ${config.height} bg-gray-700 rounded-full overflow-hidden rotate-90`}>
          <div
            className={`${config.height} ${confidenceStyle.color} transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {showPercentage && (
          <div className={`flex items-center space-x-1 ${config.text} ${confidenceStyle.textColor}`}>
            {getTrendIcon()}
            <span>{percentage}%</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <div className={`${config.width} ${config.height} bg-gray-700 rounded-full overflow-hidden`}>
        <div
          className={`${config.height} ${confidenceStyle.color} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showPercentage && (
        <div className={`flex items-center space-x-1 ${config.text} ${confidenceStyle.textColor}`}>
          {getTrendIcon()}
          <span>{percentage}%</span>
        </div>
      )}
    </div>
  );
};

export default ConfidenceIndicator;