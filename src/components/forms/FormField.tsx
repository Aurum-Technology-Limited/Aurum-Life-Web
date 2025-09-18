import { ReactNode } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { FieldError } from 'react-hook-form@7.55.0';
import { Label } from '../ui/label';
import { cn } from '../ui/utils';

interface FormFieldProps {
  label?: string;
  error?: FieldError;
  children: ReactNode;
  className?: string;
  required?: boolean;
  description?: string;
}

export default function FormField({ 
  label, 
  error, 
  children, 
  className,
  required,
  description 
}: FormFieldProps) {
  return (
    <motion.div 
      className={cn("space-y-2", className)}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {label && (
        <Label className={cn(
          "text-[#F4D03F] transition-colors duration-200",
          error && "text-[#EF4444]"
        )}>
          {label}
          {required && <span className="text-[#EF4444] ml-1">*</span>}
        </Label>
      )}
      
      {description && (
        <p className="text-sm text-[#B8BCC8]">
          {description}
        </p>
      )}
      
      <div className="relative">
        {children}
      </div>
      
      <AnimatePresence mode="wait">
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0, y: -10 }}
            animate={{ opacity: 1, height: 'auto', y: 0 }}
            exit={{ opacity: 0, height: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <p className="text-sm text-[#EF4444] flex items-center gap-2">
              <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error.message}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}