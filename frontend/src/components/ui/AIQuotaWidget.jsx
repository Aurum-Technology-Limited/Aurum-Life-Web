import React from 'react';
import { Zap, AlertTriangle } from 'lucide-react';

const AIQuotaWidget = ({ remaining, total, showDetails = true, size = 'default' }) => {
  const percentage = total > 0 ? (remaining / total) * 100 : 0;
  const isLow = percentage < 20;
  const isCritical = remaining === 0;
  
  const sizeClasses = {
    small: 'text-xs',
    default: 'text-sm',
    large: 'text-base'
  };
  
  const iconSizes = {
    small: 16,
    default: 20,
    large: 24
  };

  if (size === 'small' && !showDetails) {
    return (
      <div className={`flex items-center space-x-2 ${sizeClasses[size]}`}>
        <Zap size={iconSizes[size]} className={isCritical ? 'text-red-400' : isLow ? 'text-orange-400' : 'text-yellow-400'} />
        <span className={isCritical ? 'text-red-400' : isLow ? 'text-orange-400' : 'text-white'}>
          {remaining}/{total}
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3 p-4 rounded-lg bg-gray-800/50 border border-gray-700">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
        isCritical ? 'bg-red-400/20' : isLow ? 'bg-orange-400/20' : 'bg-yellow-400/20'
      }`}>
        {isCritical ? (
          <AlertTriangle size={iconSizes[size]} className="text-red-400" />
        ) : (
          <Zap size={iconSizes[size]} className={isLow ? 'text-orange-400' : 'text-yellow-400'} />
        )}
      </div>
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className={`${sizeClasses[size]} text-gray-400`}>
            {showDetails ? 'AI Interactions This Month' : 'AI Quota'}
          </span>
          <span className={`${sizeClasses[size]} font-semibold ${
            isCritical ? 'text-red-400' : isLow ? 'text-orange-400' : 'text-white'
          }`}>
            {remaining}/{total}
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              isCritical ? 'bg-red-400' : isLow ? 'bg-orange-400' : 'bg-yellow-400'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {showDetails && (
          <div className="mt-2">
            {isCritical && (
              <p className="text-red-400 text-xs">Quota exhausted - resets next month</p>
            )}
            {isLow && !isCritical && (
              <p className="text-orange-400 text-xs">Low quota remaining</p>
            )}
            {!isLow && !isCritical && (
              <p className="text-gray-400 text-xs">
                {percentage.toFixed(0)}% remaining this month
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIQuotaWidget;