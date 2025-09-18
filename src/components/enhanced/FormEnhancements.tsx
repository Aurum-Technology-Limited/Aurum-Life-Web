import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Save, 
  AlertCircle, 
  CheckCircle, 
  HelpCircle, 
  Eye, 
  EyeOff,
  Loader2,
  Lightbulb,
  Sparkles
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Card, CardContent } from '../ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { toast } from 'sonner@2.0.3';

interface AutoSaveProps {
  data: any;
  onSave: (data: any) => Promise<void>;
  saveKey: string;
  interval?: number;
  className?: string;
}

export function AutoSave({ data, onSave, saveKey, interval = 5000, className }: AutoSaveProps) {
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const lastDataRef = useRef(data);

  const saveData = useCallback(async () => {
    if (!hasUnsavedChanges) return;
    
    setIsSaving(true);
    try {
      await onSave(data);
      setLastSaved(new Date());
      setHasUnsavedChanges(false);
      localStorage.setItem(`autosave-${saveKey}`, JSON.stringify(data));
    } catch (error) {
      console.error('Auto-save failed:', error);
      toast.error('Auto-save failed. Your changes may be lost.');
    } finally {
      setIsSaving(false);
    }
  }, [data, hasUnsavedChanges, onSave, saveKey]);

  useEffect(() => {
    const hasChanged = JSON.stringify(data) !== JSON.stringify(lastDataRef.current);
    if (hasChanged) {
      setHasUnsavedChanges(true);
      lastDataRef.current = data;
      
      // Clear existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // Set new timeout
      timeoutRef.current = setTimeout(saveData, interval);
    }
  }, [data, interval, saveData]);

  useEffect(() => {
    // Save on page unload
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const formatLastSaved = () => {
    if (!lastSaved) return 'Never';
    const now = new Date();
    const diff = now.getTime() - lastSaved.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes === 0) return 'Just now';
    if (minutes === 1) return '1 minute ago';
    return `${minutes} minutes ago`;
  };

  return (
    <motion.div
      className={cn("flex items-center gap-2 text-xs text-muted-foreground", className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <AnimatePresence mode="wait">
        {isSaving ? (
          <motion.div
            key="saving"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex items-center gap-1"
          >
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Saving...</span>
          </motion.div>
        ) : hasUnsavedChanges ? (
          <motion.div
            key="unsaved"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex items-center gap-1 text-yellow-400"
          >
            <AlertCircle className="w-3 h-3" />
            <span>Unsaved changes</span>
          </motion.div>
        ) : (
          <motion.div
            key="saved"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex items-center gap-1 text-green-400"
          >
            <CheckCircle className="w-3 h-3" />
            <span>Saved {formatLastSaved()}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface SmartValidationProps {
  value: string;
  rules: ValidationRule[];
  onChange: (value: string) => void;
  onValidation: (isValid: boolean, errors: string[]) => void;
  className?: string;
  placeholder?: string;
  type?: string;
}

interface ValidationRule {
  test: (value: string) => boolean;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export function SmartValidation({ 
  value, 
  rules, 
  onChange, 
  onValidation, 
  className,
  placeholder,
  type = 'text'
}: SmartValidationProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [validationResults, setValidationResults] = useState<Array<{
    rule: ValidationRule;
    passed: boolean;
  }>>([]);

  useEffect(() => {
    const results = rules.map(rule => ({
      rule,
      passed: rule.test(value)
    }));
    
    setValidationResults(results);
    
    const errors = results
      .filter(result => !result.passed && result.rule.severity === 'error')
      .map(result => result.rule.message);
    
    const isValid = errors.length === 0;
    onValidation(isValid, errors);
  }, [value, rules, onValidation]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'info': return 'text-blue-400';
      default: return 'text-muted-foreground';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error': return AlertCircle;
      case 'warning': return AlertCircle;
      case 'info': return HelpCircle;
      default: return CheckCircle;
    }
  };

  return (
    <div className="space-y-2">
      <div className="relative">
        <Input
          type={type === 'password' ? (showPassword ? 'text' : 'password') : type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={cn(
            "pr-10 transition-colors",
            validationResults.some(r => !r.passed && r.rule.severity === 'error') 
              ? "border-red-400/50 focus:border-red-400" 
              : validationResults.length > 0 && validationResults.every(r => r.passed)
              ? "border-green-400/50 focus:border-green-400"
              : "",
            className
          )}
        />
        
        {type === 'password' && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </Button>
        )}
      </div>

      <AnimatePresence>
        {validationResults.length > 0 && value && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-1"
          >
            {validationResults.map((result, index) => {
              const Icon = getSeverityIcon(result.rule.severity);
              
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "flex items-center gap-2 text-xs",
                    result.passed ? "text-green-400" : getSeverityColor(result.rule.severity)
                  )}
                >
                  <Icon className="w-3 h-3" />
                  <span className={result.passed ? "line-through opacity-60" : ""}>
                    {result.rule.message}
                  </span>
                  {result.passed && <CheckCircle className="w-3 h-3 text-green-400" />}
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface ContextualHelpProps {
  content: string;
  examples?: string[];
  tips?: string[];
  className?: string;
}

export function ContextualHelp({ content, examples = [], tips = [], className }: ContextualHelpProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <TooltipProvider>
      <Tooltip open={isOpen} onOpenChange={setIsOpen}>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={cn("h-6 w-6 p-0 text-muted-foreground hover:text-foreground", className)}
          >
            <HelpCircle className="w-4 h-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-sm p-4 space-y-3" sideOffset={8}>
          <p className="text-sm">{content}</p>
          
          {examples.length > 0 && (
            <div className="space-y-1">
              <h4 className="text-xs font-medium text-primary flex items-center gap-1">
                <Lightbulb className="w-3 h-3" />
                Examples:
              </h4>
              <ul className="space-y-1">
                {examples.map((example, index) => (
                  <li key={index} className="text-xs text-muted-foreground">
                    • {example}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {tips.length > 0 && (
            <div className="space-y-1">
              <h4 className="text-xs font-medium text-yellow-400 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Tips:
              </h4>
              <ul className="space-y-1">
                {tips.map((tip, index) => (
                  <li key={index} className="text-xs text-muted-foreground">
                    • {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

interface EnhancedFormFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  placeholder?: string;
  required?: boolean;
  help?: {
    content: string;
    examples?: string[];
    tips?: string[];
  };
  validation?: ValidationRule[];
  autoSave?: {
    onSave: (value: string) => Promise<void>;
    saveKey: string;
  };
  className?: string;
}

export function EnhancedFormField({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
  required = false,
  help,
  validation = [],
  autoSave,
  className
}: EnhancedFormFieldProps) {
  const [isValid, setIsValid] = useState(true);
  const [errors, setErrors] = useState<string[]>([]);

  const handleValidation = (valid: boolean, validationErrors: string[]) => {
    setIsValid(valid);
    setErrors(validationErrors);
  };

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <Label htmlFor={label} className="text-sm font-medium flex items-center gap-2">
          {label}
          {required && <span className="text-red-400">*</span>}
          {help && (
            <ContextualHelp
              content={help.content}
              examples={help.examples}
              tips={help.tips}
            />
          )}
        </Label>
        
        {autoSave && (
          <AutoSave
            data={value}
            onSave={async (data) => await autoSave.onSave(data)}
            saveKey={autoSave.saveKey}
          />
        )}
      </div>

      {validation.length > 0 ? (
        <SmartValidation
          value={value}
          rules={validation}
          onChange={onChange}
          onValidation={handleValidation}
          placeholder={placeholder}
          type={type}
        />
      ) : type === 'textarea' ? (
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="min-h-[100px] resize-none"
        />
      ) : (
        <Input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
        />
      )}

      <AnimatePresence>
        {errors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-1"
          >
            {errors.map((error, index) => (
              <motion.p
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-xs text-red-400 flex items-center gap-1"
              >
                <AlertCircle className="w-3 h-3" />
                {error}
              </motion.p>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function useFormAutoSave(key: string, defaultData: any = {}) {
  const [data, setData] = useState(defaultData);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Load saved data on mount
    const saved = localStorage.getItem(`form-${key}`);
    if (saved) {
      try {
        const parsedData = JSON.parse(saved);
        setData({ ...defaultData, ...parsedData });
      } catch (error) {
        console.error('Failed to parse saved form data:', error);
      }
    }
  }, [key, defaultData]);

  const saveData = useCallback(async (formData: any) => {
    setIsSaving(true);
    try {
      localStorage.setItem(`form-${key}`, JSON.stringify(formData));
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
    } finally {
      setIsSaving(false);
    }
  }, [key]);

  const updateField = useCallback((field: string, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
  }, []);

  const clearSaved = useCallback(() => {
    localStorage.removeItem(`form-${key}`);
    setData(defaultData);
  }, [key, defaultData]);

  return {
    data,
    updateField,
    saveData,
    clearSaved,
    isSaving
  };
}