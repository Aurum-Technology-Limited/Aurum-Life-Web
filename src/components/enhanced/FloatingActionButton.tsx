import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Plus, Mic, PenTool, Calendar, Target, X } from 'lucide-react';
import { Button } from '../ui/button';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { cn } from '../../lib/utils';

interface FloatingActionOption {
  id: string;
  label: string;
  icon: React.ReactNode;
  action: () => void;
  color: string;
}

interface FloatingActionButtonProps {
  className?: string;
  isMobile?: boolean;
}

export default function FloatingActionButton({ className, isMobile = false }: FloatingActionButtonProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { openQuickCapture, startVoiceRecording } = useEnhancedFeaturesStore();

  const options: FloatingActionOption[] = [
    {
      id: 'quick-capture',
      label: 'Quick Capture',
      icon: <PenTool className="w-5 h-5" />,
      action: () => {
        openQuickCapture();
        setIsExpanded(false);
      },
      color: 'text-[#F4D03F]'
    },
    {
      id: 'voice-note',
      label: 'Voice Note',
      icon: <Mic className="w-5 h-5" />,
      action: () => {
        openQuickCapture();
        // Start voice recording after a brief delay to allow modal to open
        setTimeout(() => {
          startVoiceRecording();
        }, 300);
        setIsExpanded(false);
      },
      color: 'text-blue-400'
    },
    {
      id: 'time-block',
      label: 'Time Block',
      icon: <Calendar className="w-5 h-5" />,
      action: () => {
        // TODO: Open time blocking modal
        setIsExpanded(false);
      },
      color: 'text-green-400'
    },
    {
      id: 'goal',
      label: 'Goal',
      icon: <Target className="w-5 h-5" />,
      action: () => {
        // TODO: Open goal creation modal
        setIsExpanded(false);
      },
      color: 'text-purple-400'
    }
  ];

  return (
    <div className={cn(
      isMobile 
        ? "relative" // Mobile: positioned relatively within OneHandedLayout
        : "fixed bottom-6 right-6 z-50", // Desktop: fixed positioning
      className
    )}>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className={cn(
              "absolute space-y-3",
              isMobile ? "bottom-14 right-0" : "bottom-16 right-0"
            )}
          >
            {options.map((option, index) => (
              <motion.div
                key={option.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-end space-x-3"
              >
                <div className="glassmorphism-card px-3 py-2 rounded-lg">
                  <span className="text-sm text-white whitespace-nowrap">
                    {option.label}
                  </span>
                </div>
                <Button
                  size="sm"
                  onClick={option.action}
                  className={cn(
                    "rounded-full glassmorphism-card border-0 hover:bg-[rgba(244,208,63,0.1)] hover:scale-110 transition-all duration-200",
                    isMobile ? "w-10 h-10" : "w-12 h-12",
                    option.color
                  )}
                >
                  <div className={cn(isMobile ? "scale-90" : "scale-100")}>
                    {option.icon}
                  </div>
                </Button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main FAB */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          size="lg"
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            "rounded-full aurum-gradient hover:shadow-lg hover:shadow-[rgba(244,208,63,0.3)] border-0 relative overflow-hidden",
            isMobile ? "w-12 h-12" : "w-14 h-14"
          )}
        >
          <motion.div
            animate={{ rotate: isExpanded ? 45 : 0 }}
            transition={{ duration: 0.2 }}
          >
            {isExpanded ? (
              <X className={cn(isMobile ? "w-5 h-5" : "w-6 h-6", "text-[#0B0D14]")} />
            ) : (
              <Plus className={cn(isMobile ? "w-5 h-5" : "w-6 h-6", "text-[#0B0D14]")} />
            )}
          </motion.div>
          
          {/* Subtle pulse animation */}
          <motion.div
            className="absolute inset-0 rounded-full bg-[#F4D03F] opacity-30"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
        </Button>
      </motion.div>
    </div>
  );
}