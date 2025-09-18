import React, { forwardRef } from 'react';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import CharacterLimitIndicator, { getCharacterLimitStatus } from '../shared/CharacterLimitIndicator';
import { cn } from '../../lib/utils';

interface LimitedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  maxLength: number;
  showProgress?: boolean;
  showIcon?: boolean;
  warningThreshold?: number;
  dangerThreshold?: number;
  helperText?: string;
  value?: string;
  onValueChange?: (value: string) => void;
}

const LimitedInput = forwardRef<HTMLInputElement, LimitedInputProps>(({
  label,
  maxLength,
  showProgress = true,
  showIcon = true,
  warningThreshold = 80,
  dangerThreshold = 95,
  helperText,
  className,
  value = '',
  onValueChange,
  onChange,
  id,
  ...props
}, ref) => {
  const currentLength = value.length;
  const status = getCharacterLimitStatus(currentLength, maxLength, warningThreshold, dangerThreshold);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    
    // Prevent exceeding the limit
    if (newValue.length <= maxLength) {
      onValueChange?.(newValue);
      onChange?.(e);
    }
  };

  const getInputClassName = () => {
    let baseClass = 'glassmorphism-card border-0 bg-input';
    
    if (status.isDanger || status.isAtLimit) {
      baseClass += ' border-destructive/50 focus:border-destructive';
    } else if (status.isWarning) {
      baseClass += ' border-warning/50 focus:border-warning';
    }
    
    return cn(baseClass, className);
  };

  const inputId = id || (label ? `input-${label.toLowerCase().replace(/\s+/g, '-')}` : undefined);

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between">
          <Label htmlFor={inputId} className="text-sm font-medium">
            {label}
          </Label>
          <CharacterLimitIndicator
            currentLength={currentLength}
            maxLength={maxLength}
            showProgress={showProgress}
            showIcon={showIcon}
            warningThreshold={warningThreshold}
            dangerThreshold={dangerThreshold}
            className="text-xs"
          />
        </div>
      )}
      
      <Input
        ref={ref}
        id={inputId}
        value={value}
        onChange={handleChange}
        className={getInputClassName()}
        maxLength={maxLength}
        {...props}
      />
      
      {helperText && (
        <p className="text-xs text-muted-foreground">{helperText}</p>
      )}
      
      {(status.isWarning || status.isDanger || status.isAtLimit) && (
        <p className={`text-xs ${
          status.isAtLimit || status.isDanger 
            ? 'text-destructive' 
            : 'text-warning'
        }`}>
          {status.isAtLimit 
            ? 'Character limit reached. Cannot add more characters.'
            : status.isDanger 
              ? `Only ${status.remaining} characters remaining.`
              : `Approaching character limit. ${status.remaining} characters remaining.`
          }
        </p>
      )}
    </div>
  );
});

LimitedInput.displayName = 'LimitedInput';

export default LimitedInput;