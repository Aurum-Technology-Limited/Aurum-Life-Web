import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/BackendAuthContext';
import Login from './Login';
import OnboardingWizard from './OnboardingWizard';
import { api } from '../services/api';

const AppWrapper = ({ children, onNavigateToSection }) => {
  const { user, loading, refreshUser } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);

  // Check onboarding status when user becomes available
  useEffect(() => {
    if (user && !loading && !isCheckingOnboarding) {
      setIsCheckingOnboarding(true);
      
      console.log('🔍 User object for onboarding check:', {
        id: user.id,
        has_completed_onboarding: user.has_completed_onboarding,
        level: user.level
      });
      
      // Check if user has completed onboarding from backend data (defensive default false)
      const hasCompletedOnboarding = user.has_completed_onboarding === true;
      
      // Also check localStorage for client-side completion flag
      const localCompletionFlag = localStorage.getItem(`onboarding_completed_${user.id}`);
      const isLocallyCompleted = localCompletionFlag === 'true';
      
      console.log('📊 Onboarding status:', {
        hasCompletedOnboarding,
        isLocallyCompleted,
        userHasCompletedField: user.has_completed_onboarding,
        userId: user.id
      });
      
      // Show onboarding if NOT completed AND user has no data
      const shouldShowOnboarding = (!hasCompletedOnboarding && !isLocallyCompleted);
      
      if (shouldShowOnboarding) {
        console.log('🎯 New user detected - showing onboarding');
        setShowOnboarding(true);
      } else {
        console.log('🏠 User has completed onboarding (backend or locally) - going to dashboard');
        setShowOnboarding(false);
        
        // If locally completed but backend hasn't updated yet, sync with backend
        if (isLocallyCompleted && !hasCompletedOnboarding) {
          console.log('🔄 Syncing local completion with backend...');
          syncOnboardingCompletion();
        }
      }
      
      // Always set checking to false after logic completes
      setTimeout(() => setIsCheckingOnboarding(false), 100);
    }
  }, [user?.id, user?.has_completed_onboarding, loading]); // Fixed dependency array

  const syncOnboardingCompletion = async () => {
    try {
      await api.post('/auth/complete-onboarding');
      await refreshUser();
      console.log('✅ Local completion synced with backend');
    } catch (error) {
      console.error('⚠️ Failed to sync completion with backend:', error);
    }
  };

  const handleOnboardingComplete = async () => {
    console.log('🎉 Onboarding completed - setting local flag and refreshing user data');
    
    // Immediately set local completion flag to prevent race conditions
    if (user?.id) {
      localStorage.setItem(`onboarding_completed_${user.id}`, 'true');
    }
    
    setShowOnboarding(false);
    
    // Refresh user data to get updated onboarding status
    try {
      await refreshUser();
      console.log('✅ User data refreshed after onboarding completion');
    } catch (error) {
      console.error('⚠️ Failed to refresh user data after onboarding:', error);
    }
    
    // Navigate to dashboard
    if (onNavigateToSection) {
      onNavigateToSection('dashboard');
    }
  };

  const handleOnboardingClose = async () => {
    console.log('⏩ Onboarding skipped - marking as completed');
    
    // Set local completion flag immediately
    if (user?.id) {
      localStorage.setItem(`onboarding_completed_${user.id}`, 'true');
    }
    
    setShowOnboarding(false);
    
    // Mark onboarding as completed in backend even when skipped
    try {
      await api.post('/auth/complete-onboarding');
      console.log('✅ Onboarding marked as completed (skipped) in backend');
      await refreshUser();
    } catch (error) {
      console.error('⚠️ Failed to mark onboarding as completed:', error);
    }
  };

  // Debug authentication state
  useEffect(() => {
    console.log('🔍 AppWrapper Debug - Auth State:', {
      user: !!user,
      userId: user?.id,
      loading,
      isCheckingOnboarding,
      showOnboarding,
      userEmail: user?.email,
      hasCompletedOnboarding: user?.has_completed_onboarding
    });
  }, [user, loading, isCheckingOnboarding, showOnboarding]);

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
    console.log('🔐 Showing login - no user object');
    return <Login />;
  }

  // Additional validation - ensure user has required fields
  if (!user.id || !user.email) {
    console.log('⚠️ User object incomplete, showing login');
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
  console.log('✅ Showing main app - user authenticated and onboarding complete');
  return children;
};

export default AppWrapper;