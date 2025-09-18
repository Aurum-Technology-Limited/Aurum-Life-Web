import { forwardRef, useState } from 'react';
import { motion } from 'motion/react';
import { Input } from '../ui/input';
import { cn } from '../ui/utils';

interface AnimatedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  icon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const AnimatedInput = forwardRef<HTMLInputElement, AnimatedInputProps>(
  ({ className, error, icon, rightIcon, onFocus, onBlur, ...props }, ref) => {
    const [isFocused, setIsFocused] = useState(false);

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      onBlur?.(e);
    };

    return (
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8] transition-colors duration-200">
            {icon}
          </div>
        )}
        
        <motion.div
          animate={{
            scale: isFocused ? 1.02 : 1,
          }}
          transition={{ duration: 0.2 }}
        >
          <Input
            ref={ref}
            className={cn(
              "glassmorphism-panel border-[rgba(244,208,63,0.2)] bg-[rgba(26,29,41,0.4)]",
              "text-white placeholder:text-[#6B7280]",
              "focus:border-[#F4D03F] focus:ring-2 focus:ring-[rgba(244,208,63,0.2)]",
              "transition-all duration-300",
              "h-12 text-base",
              icon && "pl-10",
              rightIcon && "pr-10",
              error && "border-[#EF4444] focus:border-[#EF4444] focus:ring-[rgba(239,68,68,0.2)]",
              isFocused && "shadow-lg shadow-[rgba(244,208,63,0.1)]",
              className
            )}
            onFocus={handleFocus}
            onBlur={handleBlur}
            {...props}
          />
        </motion.div>
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#B8BCC8] transition-colors duration-200">
            {rightIcon}
          </div>
        )}
        
        {/* Focus ring animation */}
        <motion.div
          className="absolute inset-0 rounded-lg pointer-events-none"
          animate={{
            opacity: isFocused ? 1 : 0,
            scale: isFocused ? 1 : 0.95,
          }}
          transition={{ duration: 0.2 }}
          style={{
            background: 'linear-gradient(90deg, rgba(244,208,63,0.1) 0%, rgba(244,208,63,0.2) 50%, rgba(244,208,63,0.1) 100%)',
            filter: 'blur(8px)',
          }}
        />
      </div>
    );
  }
);

AnimatedInput.displayName = 'AnimatedInput';

export default AnimatedInput;