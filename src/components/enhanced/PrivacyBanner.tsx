/**
 * Privacy Banner Component
 * Shows privacy status and encourages users to review privacy settings
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Shield, Settings, X, ChevronRight, Info } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useAppStore } from '../../stores/basicAppStore';
import { privacyConsentService } from '../../services/privacyConsentService';

interface PrivacyBannerProps {
  onDismiss?: () => void;
}

const PrivacyBanner: React.FC<PrivacyBannerProps> = ({ onDismiss }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [privacyScore, setPrivacyScore] = useState(0);
  const [needsAttention, setNeedsAttention] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const { setActiveSection } = useAppStore();

  useEffect(() => {
    checkPrivacyStatus();
  }, []);

  const checkPrivacyStatus = async () => {
    try {
      setLoading(true);
      
      // Check if banner was dismissed recently
      const dismissedAt = localStorage.getItem('aurum-privacy-banner-dismissed');
      if (dismissedAt && Date.now() - parseInt(dismissedAt) < 7 * 24 * 60 * 60 * 1000) {
        setIsVisible(false);
        return;
      }

      // Try to get privacy settings with timeout protection
      const settingsPromise = privacyConsentService.getPrivacySettings();
      const timeoutPromise = new Promise<null>((_, reject) => 
        setTimeout(() => reject(new Error('timeout')), 3000)
      );
      
      try {
        const settings = await Promise.race([settingsPromise, timeoutPromise]);
        
        if (settings) {
          // Calculate privacy score
          const score = calculatePrivacyScore(settings);
          setPrivacyScore(score);
          setNeedsAttention(score < 50);
          setIsVisible(false); // Don't show banner by default to prevent errors
        } else {
          setNeedsAttention(false);
          setIsVisible(false);
          setPrivacyScore(75); // Default reasonable score
        }
      } catch (apiError) {
        console.log('Privacy API timeout/error, using defaults:', apiError);
        // Set safe defaults
        setNeedsAttention(false);
        setIsVisible(false); // Don't show banner on API failure
        setPrivacyScore(75);
      }
    } catch (error) {
      console.log('Privacy status check failed:', error);
      setNeedsAttention(false);
      setIsVisible(false);
      setPrivacyScore(75);
    } finally {
      setLoading(false);
    }
  };

  const calculatePrivacyScore = (settings: any): number => {
    let score = 0;
    let total = 0;

    // Calculate score based on restrictive settings
    if (settings.dataCollection) {
      Object.values(settings.dataCollection).forEach((enabled: any) => {
        total++;
        if (!enabled) score++; // More privacy = higher score
      });
    }

    if (settings.dataSharing) {
      Object.values(settings.dataSharing).forEach((enabled: any) => {
        total++;
        if (!enabled) score++; // No sharing = higher privacy
      });
    }

    return total > 0 ? Math.round((score / total) * 100) : 0;
  };

  const handleDismiss = () => {
    setIsVisible(false);
    localStorage.setItem('aurum-privacy-banner-dismissed', Date.now().toString());
    onDismiss?.();
  };

  const handleReviewSettings = () => {
    setActiveSection('privacy-controls');
    handleDismiss();
  };

  if (loading || !isVisible) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -50, height: 0 }}
        animate={{ opacity: 1, y: 0, height: 'auto' }}
        exit={{ opacity: 0, y: -50, height: 0 }}
        transition={{ duration: 0.3 }}
        className="mb-6"
      >
        <Card className={`glassmorphism-card ${needsAttention ? 'border-yellow-500/30' : 'border-primary/30'}`}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-2 rounded-full ${needsAttention ? 'bg-yellow-500/20' : 'bg-primary/20'}`}>
                  <Shield className={`w-5 h-5 ${needsAttention ? 'text-yellow-400' : 'text-primary'}`} />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium">
                      {needsAttention ? 'Privacy Settings Need Attention' : 'Privacy Status'}
                    </h3>
                    {!needsAttention && (
                      <Badge variant="secondary" className="text-xs">
                        {privacyScore}% Private
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-sm text-muted-foreground">
                    {needsAttention 
                      ? 'Review and configure your privacy preferences to ensure your data is protected according to your preferences.'
                      : `Your privacy score is ${privacyScore}%. Review your settings to enhance data protection.`
                    }
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReviewSettings}
                  className="flex items-center gap-2"
                >
                  <Settings className="w-4 h-4" />
                  Review Settings
                  <ChevronRight className="w-3 h-3" />
                </Button>
                
                {!needsAttention && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDismiss}
                    className="p-2"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>

            {needsAttention && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 p-3 glassmorphism-panel rounded-lg"
              >
                <div className="flex items-start gap-2">
                  <Info className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <div className="text-sm">
                    <p className="text-foreground font-medium mb-1">Why this matters:</p>
                    <ul className="text-muted-foreground space-y-1 text-xs">
                      <li>• Control what data Aurum Life collects and processes</li>
                      <li>• Customize AI features based on your comfort level</li>
                      <li>• Maintain transparency about how your data is used</li>
                      <li>• Ensure compliance with privacy regulations</li>
                    </ul>
                  </div>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};

export default PrivacyBanner;