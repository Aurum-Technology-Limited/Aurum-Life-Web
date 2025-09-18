import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowLeft, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { useOnboardingStore } from '../../stores/onboardingStore';

interface OnboardingLayoutProps {
  children: React.ReactNode;
  showProgress?: boolean;
  showBack?: boolean;
  showSkip?: boolean;
  onBack?: () => void;
  onSkip?: () => void;
  className?: string;
}

export default function OnboardingLayout({
  children,
  showProgress = true,
  showBack = true,
  showSkip = false,
  onBack,
  onSkip,
  className = ""
}: OnboardingLayoutProps) {
  const { currentStep, totalSteps, previousStep } = useOnboardingStore();
  
  const progress = (currentStep / totalSteps) * 100;
  
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      previousStep();
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0D14] relative overflow-hidden">


      {/* Navigation Header */}
      <AnimatePresence>
        {(showProgress || showBack || showSkip) && (
          <motion.header
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -50, opacity: 0 }}
            className="relative z-10 p-6"
          >
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-between">
                {/* Back Button */}
                {showBack && currentStep > 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleBack}
                    className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                )}
                
                {(!showBack || currentStep === 1) && <div />}

                {/* Progress Bar */}
                {showProgress && (
                  <div className="flex-1 max-w-md mx-8">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-[#B8BCC8]">
                        Step {currentStep} of {totalSteps}
                      </span>
                      <span className="text-sm text-[#F4D03F] font-medium">
                        {Math.round(progress)}%
                      </span>
                    </div>
                    <Progress 
                      value={progress} 
                      className="h-2 bg-[rgba(244,208,63,0.1)]"
                    />
                  </div>
                )}

                {/* Skip Button */}
                {showSkip && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onSkip}
                    className="text-[#B8BCC8] hover:text-white"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Skip
                  </Button>
                )}
                
                {!showSkip && <div />}
              </div>
            </div>
          </motion.header>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className={`relative z-10 ${className}`}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className="min-h-[calc(100vh-120px)] flex items-center justify-center"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>


    </div>
  );
}