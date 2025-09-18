import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Copy, Check, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { copyWithFeedback, ClipboardResult } from '../../utils/clipboard';
import { showClipboardSuccess, showClipboardError } from '../../utils/toast';

interface ClipboardButtonProps {
  text: string;
  label?: string;
  variant?: 'default' | 'outline' | 'ghost' | 'destructive' | 'secondary';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
  successMessage?: string;
  errorMessage?: string;
  disabled?: boolean;
  showLabel?: boolean;
  iconOnly?: boolean;
}

export default function ClipboardButton({
  text,
  label = 'Copy',
  variant = 'outline',
  size = 'sm',
  className = '',
  successMessage,
  errorMessage,
  disabled = false,
  showLabel = true,
  iconOnly = false
}: ClipboardButtonProps) {
  const [status, setStatus] = useState<'idle' | 'copying' | 'success' | 'error'>('idle');

  const handleCopy = async () => {
    if (disabled || !text) return;

    setStatus('copying');

    try {
      const result = await copyWithFeedback(
        text,
        (result: ClipboardResult) => {
          setStatus('success');
          if (successMessage) {
            toast.success(successMessage, {
              duration: 2000,
              style: {
                background: 'rgba(244, 208, 63, 0.1)',
                border: '1px solid rgba(244, 208, 63, 0.3)',
                color: '#F4D03F'
              }
            });
          }
          setTimeout(() => setStatus('idle'), 2000);
        },
        (result: ClipboardResult) => {
          setStatus('error');
          if (errorMessage) {
            toast.error(errorMessage, {
              duration: 4000,
              style: {
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#EF4444'
              }
            });
          }
          setTimeout(() => setStatus('idle'), 3000);
        }
      );

      // Show result-specific message if no custom messages provided
      if (!successMessage && !errorMessage) {
        if (result.success) {
          toast.success(result.message, {
            duration: 2000,
            style: {
              background: 'rgba(244, 208, 63, 0.1)',
              border: '1px solid rgba(244, 208, 63, 0.3)',
              color: '#F4D03F'
            }
          });
        } else {
          toast.error(result.message, {
            duration: 4000,
            style: {
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#EF4444'
            }
          });
        }
      }

    } catch (error) {
      setStatus('error');
      setTimeout(() => setStatus('idle'), 3000);
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'copying':
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Copy className="w-4 h-4" />
          </motion.div>
        );
      case 'success':
        return (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 500, damping: 15 }}
          >
            <Check className="w-4 h-4 text-green-500" />
          </motion.div>
        );
      case 'error':
        return (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 500, damping: 15 }}
          >
            <AlertCircle className="w-4 h-4 text-red-500" />
          </motion.div>
        );
      default:
        return <Copy className="w-4 h-4" />;
    }
  };

  const getLabel = () => {
    switch (status) {
      case 'copying':
        return 'Copying...';
      case 'success':
        return 'Copied!';
      case 'error':
        return 'Copy Failed';
      default:
        return label;
    }
  };

  const buttonClasses = `
    ${className}
    ${status === 'success' ? 'border-green-500/30 text-green-500' : ''}
    ${status === 'error' ? 'border-red-500/30 text-red-500' : ''}
    transition-all duration-200 ease-in-out
  `;

  if (iconOnly) {
    return (
      <Button
        variant={variant}
        size="icon"
        onClick={handleCopy}
        disabled={disabled || status === 'copying'}
        className={buttonClasses}
        title={`Copy ${label}`}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={status}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.15 }}
          >
            {getIcon()}
          </motion.div>
        </AnimatePresence>
      </Button>
    );
  }

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleCopy}
      disabled={disabled || status === 'copying'}
      className={buttonClasses}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={status}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 10 }}
          transition={{ duration: 0.15 }}
          className="flex items-center space-x-2"
        >
          {getIcon()}
          {showLabel && <span>{getLabel()}</span>}
        </motion.div>
      </AnimatePresence>
    </Button>
  );
}

// Specialized demo credentials button
export function DemoCredentialsButton({ className = '', ...props }: Omit<ClipboardButtonProps, 'text'>) {
  const demoCredentials = 'Email: demo@aurumlife.com\nPassword: demo123';
  
  return (
    <ClipboardButton
      text={demoCredentials}
      label="Copy Demo Credentials"
      successMessage="Demo credentials copied!"
      errorMessage="Demo credentials selected - press Ctrl+C to copy"
      className={`border-[rgba(244,208,63,0.3)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] ${className}`}
      {...props}
    />
  );
}

// Specialized formatted text button
export function FormattedTextButton({ 
  title, 
  content, 
  separator = '\n\n',
  ...props 
}: Omit<ClipboardButtonProps, 'text'> & { 
  title: string; 
  content: string; 
  separator?: string; 
}) {
  const formattedText = `${title}${separator}${content}`;
  
  return (
    <ClipboardButton
      text={formattedText}
      successMessage={`${title} copied!`}
      errorMessage={`${title} selected for manual copy`}
      {...props}
    />
  );
}