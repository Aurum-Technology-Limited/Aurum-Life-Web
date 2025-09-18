import React from 'react';
import { AlertCircle, AlertTriangle } from 'lucide-react';
import { Progress } from '../ui/progress';

interface CharacterLimitIndicatorProps {
  currentLength: number;
  maxLength: number;
  showProgress?: boolean;
  showIcon?: boolean;
  className?: string;
  label?: string;
  warningThreshold?: number; // Percentage (default 80%)
  dangerThreshold?: number;  // Percentage (default 95%)
}

export default function CharacterLimitIndicator({
  currentLength,
  maxLength,
  showProgress = true,
  showIcon = true,
  className = '',
  label,
  warningThreshold = 80,
  dangerThreshold = 95
}: CharacterLimitIndicatorProps) {
  const percentage = (currentLength / maxLength) * 100;
  const isWarning = percentage >= warningThreshold && percentage < dangerThreshold;
  const isDanger = percentage >= dangerThreshold;
  const isAtLimit = currentLength >= maxLength;

  const getStatusColor = () => {
    if (isDanger || isAtLimit) return 'text-destructive';
    if (isWarning) return 'text-warning';
    return 'text-muted-foreground';
  };

  const getProgressClassName = () => {
    if (isDanger || isAtLimit) return '[&>[data-slot=progress-indicator]]:bg-destructive';
    if (isWarning) return '[&>[data-slot=progress-indicator]]:bg-warning';
    return '[&>[data-slot=progress-indicator]]:bg-primary';
  };

  const getIcon = () => {
    if (isDanger || isAtLimit) return <AlertCircle className="w-3 h-3" />;
    if (isWarning) return <AlertTriangle className="w-3 h-3" />;
    return null;
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {label && (
        <span className="text-sm text-muted-foreground">{label}</span>
      )}
      
      <div className="flex items-center space-x-2">
        {showIcon && getIcon()}
        
        <span className={`text-xs font-mono ${getStatusColor()}`}>
          {currentLength.toLocaleString()}/{maxLength.toLocaleString()}
        </span>
        
        {showProgress && (
          <div className="w-16 h-1.5">
            <Progress 
              value={Math.min(percentage, 100)} 
              className={`h-1.5 ${getProgressClassName()}`}
            />
          </div>
        )}
      </div>
      
      {(isWarning || isDanger || isAtLimit) && (
        <span className={`text-xs ${getStatusColor()}`}>
          {isAtLimit 
            ? 'Limit reached' 
            : isDanger 
              ? 'Near limit' 
              : 'Warning'
          }
        </span>
      )}
    </div>
  );
}

// Utility function to calculate character limit status
export const getCharacterLimitStatus = (
  currentLength: number, 
  maxLength: number, 
  warningThreshold = 80, 
  dangerThreshold = 95
) => {
  const percentage = (currentLength / maxLength) * 100;
  
  return {
    percentage,
    isWarning: percentage >= warningThreshold && percentage < dangerThreshold,
    isDanger: percentage >= dangerThreshold,
    isAtLimit: currentLength >= maxLength,
    remaining: maxLength - currentLength,
    status: currentLength >= maxLength 
      ? 'at-limit' 
      : percentage >= dangerThreshold 
        ? 'danger' 
        : percentage >= warningThreshold 
          ? 'warning' 
          : 'safe'
  };
};