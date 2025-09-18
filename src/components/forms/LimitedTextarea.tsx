import React, { forwardRef } from 'react';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import CharacterLimitIndicator, { getCharacterLimitStatus } from '../shared/CharacterLimitIndicator';
import { cn } from '../../lib/utils';

interface LimitedTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  maxLength: number;
  showProgress?: boolean;
  showIcon?: boolean;
  warningThreshold?: number;
  dangerThreshold?: number;
  helperText?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  showWordCount?: boolean;
}

const LimitedTextarea = forwardRef<HTMLTextAreaElement, LimitedTextareaProps>(({
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
  showWordCount = false,
  id,
  ...props
}, ref) => {
  const currentLength = value.length;
  const status = getCharacterLimitStatus(currentLength, maxLength, warningThreshold, dangerThreshold);
  
  // Calculate word count
  const wordCount = value.trim() === '' ? 0 : value.trim().split(/\s+/).length;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    
    // Prevent exceeding the limit
    if (newValue.length <= maxLength) {
      onValueChange?.(newValue);
      onChange?.(e);
    }
  };

  const getTextareaClassName = () => {
    let baseClass = 'glassmorphism-card border-0 bg-input';
    
    if (status.isDanger || status.isAtLimit) {
      baseClass += ' border-destructive/50 focus:border-destructive';
    } else if (status.isWarning) {
      baseClass += ' border-warning/50 focus:border-warning';
    }
    
    return cn(baseClass, className);
  };

  const textareaId = id || (label ? `textarea-${label.toLowerCase().replace(/\s+/g, '-')}` : undefined);

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between">
          <Label htmlFor={textareaId} className="text-sm font-medium">
            {label}
          </Label>
          <div className="flex items-center space-x-4">
            {showWordCount && (
              <span className="text-xs text-muted-foreground">
                {wordCount.toLocaleString()} words
              </span>
            )}
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
        </div>
      )}
      
      <Textarea
        ref={ref}
        id={textareaId}
        value={value}
        onChange={handleChange}
        className={getTextareaClassName()}
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

LimitedTextarea.displayName = 'LimitedTextarea';

export default LimitedTextarea;