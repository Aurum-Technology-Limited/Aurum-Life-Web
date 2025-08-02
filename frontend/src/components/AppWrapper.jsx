import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import Login from './Login';
import OnboardingWizard from './OnboardingWizard';

const AppWrapper = ({ children, onNavigateToSection }) => {
  const { user, loading } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);

  // Debug: Log authentication state changes
  useEffect(() => {
    console.log('🔍 AppWrapper - Auth state changed:', {
      hasUser: !!user,
      loading,
      userEmail: user?.email,
      hasCompletedOnboarding: user?.has_completed_onboarding
    });
  }, [user, loading]);

  // Check onboarding status when user becomes available
  useEffect(() => {
    if (user && !loading) {
      setIsCheckingOnboarding(true);
      
      // Check if user has completed onboarding
      const hasCompletedOnboarding = user.has_completed_onboarding;
      
      if (!hasCompletedOnboarding) {
        console.log('🎯 New user detected - showing onboarding');
        setShowOnboarding(true);
      } else {
        console.log('🏠 Existing user - going to dashboard');
        setShowOnboarding(false);
      }
      
      setIsCheckingOnboarding(false);
    }
  }, [user, loading]);

  const handleOnboardingComplete = () => {
    console.log('🎉 Onboarding completed - navigating to dashboard');
    setShowOnboarding(false);
    
    // Navigate to dashboard
    if (onNavigateToSection) {
      onNavigateToSection('dashboard');
    }
  };

  const handleOnboardingClose = () => {
    console.log('⏩ Onboarding skipped');
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