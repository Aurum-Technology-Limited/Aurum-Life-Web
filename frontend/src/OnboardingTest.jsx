import React from 'react';
import OnboardingWizard from './components/OnboardingWizard';

// Test component to always show onboarding wizard for UI testing
const OnboardingTest = () => {
  const handleComplete = () => {
    console.log('✅ Onboarding completed in test mode');
  };

  const handleClose = () => {
    console.log('❌ Onboarding closed in test mode');
  };

  return (
    <div>
      <OnboardingWizard 
        onComplete={handleComplete}
        onClose={handleClose}
      />
    </div>
  );
};

export default OnboardingTest;