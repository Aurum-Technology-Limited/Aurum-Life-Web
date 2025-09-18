import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { SkeletonDashboard } from '../enhanced/SkeletonLoading';
import { useMobileDetection } from '../enhanced/MobileEnhancements';
import aurumLogo from 'figma:asset/a76e299ce637adb8c75472e2d4c5e50cfbb65bac.png';

interface LoadingScreenProps {
  message?: string;
  showLogo?: boolean;
  timeout?: number;
  onTimeout?: () => void;
  showSkeleton?: boolean;
}

export default function LoadingScreen({ 
  message = 'Initializing your personal operating system...', 
  showLogo = true,
  timeout = 5000, // Shorter default timeout
  onTimeout,
  showSkeleton = false
}: LoadingScreenProps) {
  const [showTimeoutMessage, setShowTimeoutMessage] = useState(false);
  const [phase, setPhase] = useState<'loading' | 'skeleton' | 'timeout'>('loading');
  const { isMobile } = useMobileDetection();

  useEffect(() => {
    // Use the provided timeout with safety bounds
    const safeTimeout = Math.min(Math.max(timeout, 1000), 10000); // Between 1-10 seconds
    
    if (safeTimeout > 0) {
      // Show skeleton after 1 second if showSkeleton is true
      const skeletonTimer = showSkeleton ? setTimeout(() => {
        try {
          setPhase('skeleton');
        } catch (error) {
          console.log('Skeleton phase error (non-critical):', error);
        }
      }, 1000) : null;
      
      // Show timeout after specified timeout
      const timeoutTimer = setTimeout(() => {
        try {
          console.log('LoadingScreen timeout triggered after', safeTimeout, 'ms');
          setPhase('timeout');
          setShowTimeoutMessage(true);
          onTimeout?.();
        } catch (error) {
          console.log('Timeout handler error (non-critical):', error);
          // Force reload as last resort
          window.location.reload();
        }
      }, safeTimeout);

      return () => {
        try {
          if (skeletonTimer) clearTimeout(skeletonTimer);
          clearTimeout(timeoutTimer);
        } catch (error) {
          console.log('Cleanup error (non-critical):', error);
        }
      };
    }
  }, [timeout, onTimeout, showSkeleton]);

  // Show skeleton loading for app initialization
  if (phase === 'skeleton') {
    return (
      <div className="min-h-screen bg-background p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8 text-center"
          >
            <div className="shimmer h-8 w-48 mx-auto mb-2 rounded" />
            <div className="shimmer h-4 w-64 mx-auto rounded" />
          </motion.div>
          <SkeletonDashboard />
        </div>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-[#0B0D14] flex items-center justify-center relative overflow-hidden">
      {/* Animated background gradient */}
      <motion.div 
        className="absolute inset-0"
        style={{
          background: `radial-gradient(circle at 50% 50%, rgba(244, 208, 63, 0.03) 0%, transparent 70%), 
                       radial-gradient(circle at 25% 25%, rgba(244, 208, 63, 0.05) 0%, transparent 50%), 
                       radial-gradient(circle at 75% 75%, rgba(244, 208, 63, 0.05) 0%, transparent 50%)`,
        }}
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      {/* Floating particles */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-[#F4D03F] opacity-20"
          style={{
            left: `${20 + i * 15}%`,
            top: `${30 + (i % 3) * 20}%`,
          }}
          animate={{
            y: [-20, 20, -20],
            opacity: [0.2, 0.8, 0.2],
          }}
          transition={{
            duration: 3 + i * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.3,
          }}
        />
      ))}

      <motion.div 
        className="text-center relative z-10"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        {showLogo && (
          <motion.div 
            className="mb-12"
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          >
            {/* Premium logo container with multiple layers */}
            <motion.div 
              className="relative mx-auto mb-6"
              animate={{
                rotate: [0, 360],
              }}
              transition={{
                duration: 20,
                repeat: Infinity,
                ease: "linear"
              }}
            >
              {/* Outer glow ring */}
              <div className="w-32 h-32 rounded-full bg-gradient-to-r from-[#F4D03F] to-[#F7DC6F] p-[2px] mx-auto">
                <div className="w-full h-full rounded-full bg-[#0B0D14] flex items-center justify-center relative">
                  {/* Inner glow ring */}
                  <motion.div 
                    className="w-24 h-24 rounded-full bg-gradient-to-br from-[#F4D03F]/20 to-[#F7DC6F]/20 flex items-center justify-center"
                    animate={{
                      scale: [1, 1.05, 1],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    {/* Logo container */}
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#F4D03F] to-[#F7DC6F] flex items-center justify-center shadow-2xl">
                      <img src={aurumLogo} alt="Aurum Life" className="w-12 h-12" />
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
            
            <motion.h1 
              className="aurum-text-gradient text-4xl font-bold mb-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              Aurum Life
            </motion.h1>
            <motion.p 
              className="text-[#B8BCC8] text-sm opacity-75"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            >
              Personal Operating System
            </motion.p>
          </motion.div>
        )}
        
        {/* Elegant loading indicator */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          {/* Progress bar */}
          <div className="w-64 h-1 mx-auto bg-[#1A1D29] rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-[#F4D03F] to-[#F7DC6F] rounded-full"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
          </div>
          
          {/* Loading message */}
          {!showTimeoutMessage ? (
            <motion.p 
              className="text-[#B8BCC8] text-lg font-medium"
              animate={{
                opacity: [0.7, 1, 0.7],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {message}
            </motion.p>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4 max-w-sm mx-auto"
            >
              <div className="flex items-center justify-center space-x-2 text-[#F59E0B]">
                <AlertCircle className="w-5 h-5" />
                <span className="text-sm font-medium">Loading is taking longer than expected</span>
              </div>
              
              <p className="text-[#B8BCC8] text-sm text-center">
                This might be due to a slow connection or temporary service issue.
              </p>
              
              <Button
                onClick={() => window.location.reload()}
                className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] font-medium"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Page
              </Button>
            </motion.div>
          )}
        </motion.div>
        
        {/* Premium animated dots pattern */}
        <motion.div 
          className="flex justify-center space-x-3 mt-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1 }}
        >
          {[0, 1, 2, 3, 4].map((i) => (
            <motion.div
              key={i}
              className="relative"
            >
              {/* Outer glow */}
              <motion.div
                className="w-3 h-3 rounded-full bg-[#F4D03F] opacity-20 absolute inset-0"
                animate={{
                  scale: [1, 2, 1],
                  opacity: [0.2, 0, 0.2],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 0.15,
                  ease: "easeOut"
                }}
              />
              {/* Core dot */}
              <motion.div
                className="w-3 h-3 rounded-full bg-gradient-to-br from-[#F4D03F] to-[#F7DC6F] relative z-10"
                animate={{
                  scale: [0.6, 1, 0.6],
                  opacity: [0.4, 1, 0.4],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 0.15,
                  ease: "easeInOut"
                }}
              />
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}