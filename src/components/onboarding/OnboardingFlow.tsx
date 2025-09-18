import { useEffect } from 'react';
import { AnimatePresence } from 'motion/react';
import { useOnboardingStore } from '../../stores/onboardingStore';
import { useAuthStore } from '../../stores/authStore';

// Import all onboarding steps
import WelcomeScreen from './steps/WelcomeScreen';
import PAPTFrameworkExplanation from './steps/PAPTFrameworkExplanation';
import LifeOSPurpose from './steps/LifeOSPurpose';
import ProfileSetup from './steps/ProfileSetup';
import IntelligentTemplateSelection from './steps/IntelligentTemplateSelection';
import PillarCreation from './steps/PillarCreation';
import ReadyToLaunch from './steps/ReadyToLaunch';
// We'll create these next - for now, we'll skip to launch after pillars
// import AIPreferences from './steps/AIPreferences';
// import EmotionalBaseline from './steps/EmotionalBaseline';
// import FeatureTour from './steps/FeatureTour';

export default function OnboardingFlow() {
  const { currentStep, isOnboardingComplete, userData } = useOnboardingStore();
  const { user } = useAuthStore();

  // No longer need to initialize from user since name will be collected in onboarding

  // Don't render if onboarding is complete
  if (isOnboardingComplete) {
    return null;
  }

  // Log when demo users enter onboarding for verification
  if (user?.email?.includes('demo@aurumlife.com')) {
    console.log('Demo user entering onboarding flow - PAPT Framework education will be shown');
  }

  const renderCurrentStep = () => {
    // Check if user data is already available (from login/signup)
    const hasUserData = userData.firstName && userData.firstName.trim().length > 0;
    
    switch (currentStep) {
      case 1:
        return <WelcomeScreen />;
      case 2:
        return <PAPTFrameworkExplanation />;
      case 3:
        return <LifeOSPurpose />;
      case 4:
        // Skip ProfileSetup if user data already exists and go to template selection
        return hasUserData ? <IntelligentTemplateSelection /> : <ProfileSetup />;
      case 5:
        // Template selection or pillar creation depending on flow
        return hasUserData ? <PillarCreation /> : <IntelligentTemplateSelection />;
      case 6:
        // Pillar creation or launch depending on flow
        return hasUserData ? <ReadyToLaunch /> : <PillarCreation />;
      case 7:
        return <ReadyToLaunch />;
      default:
        return <WelcomeScreen />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-auto">
      <AnimatePresence mode="wait">
        {renderCurrentStep()}
      </AnimatePresence>
    </div>
  );
}