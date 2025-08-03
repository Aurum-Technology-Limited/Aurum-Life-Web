import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import Login from './Login';
import OnboardingWizard from './OnboardingWizard';
import api from '../services/api';

const AppWrapper = ({ children, onNavigateToSection }) => {
  const { user, loading, refreshUser } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false); // Track if onboarding was just completed

  // Check onboarding status when user becomes available
  useEffect(() => {
    if (user && !loading) {
      setIsCheckingOnboarding(true);
      
      // Check if user has completed onboarding
      const hasCompletedOnboarding = user.has_completed_onboarding;
      
      // Don't override onboarding completion if it was just completed
      if (!hasCompletedOnboarding && !onboardingCompleted) {
        console.log('🎯 New user detected - showing onboarding');
        setShowOnboarding(true);
      } else {
        console.log('🏠 Existing user or onboarding just completed - going to dashboard');
        setShowOnboarding(false);
      }
      
      setIsCheckingOnboarding(false);
    }
  }, [user, loading, onboardingCompleted]);

  const handleOnboardingComplete = async () => {
    console.log('🎉 Onboarding completed - refreshing user data and navigating to dashboard');
    
    // Refresh user data to get updated onboarding status
    try {
      await refreshUser();
      console.log('✅ User data refreshed after onboarding completion');
    } catch (error) {
      console.error('⚠️ Failed to refresh user data after onboarding:', error);
    }
    
    setShowOnboarding(false);
    
    // Navigate to dashboard
    if (onNavigateToSection) {
      onNavigateToSection('dashboard');
    }
  };

  const handleOnboardingClose = async () => {
    console.log('⏩ Onboarding skipped - marking as completed');
    
    // Mark onboarding as completed in backend even when skipped
    try {
      await api.post('/api/auth/complete-onboarding');
      console.log('✅ Onboarding marked as completed (skipped) in backend');
      await refreshUser();
    } catch (error) {
      console.error('⚠️ Failed to mark onboarding as completed:', error);
    }
    
    setShowOnboarding(false);
  };

  // Loading state
  if (loading || isCheckingOnboarding) {
    return (
      <div className="min-h-screen bg-[#0B0D14] flex items-center justify-center">
        <div className="text-center">
          <div className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-bold text-xl mb-4 inline-block">
            AL
          </div>
          <div className="text-white text-lg">Loading...</div>
        </div>
      </div>
    );
  }

  // Not authenticated - show login
  if (!user) {
    return <Login />;
  }

  // Authenticated but needs onboarding - show onboarding wizard
  if (showOnboarding) {
    return (
      <OnboardingWizard
        onComplete={handleOnboardingComplete}
        onClose={handleOnboardingClose}
      />
    );
  }

  // Authenticated and onboarding completed - show main app
  return children;
};

export default AppWrapper;