import { useAuthStore } from '../../stores/authStore';
import { useOnboardingStore } from '../../stores/onboardingStore';

export default function AuthDebug() {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    error, 
    isFirstTimeUser 
  } = useAuthStore();
  
  const { isOnboardingComplete } = useOnboardingStore();

  // Only show in development
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 glassmorphism-card p-4 max-w-xs z-50">
      <h4 className="text-[#F4D03F] font-semibold mb-2">Auth Debug</h4>
      <div className="space-y-1 text-xs text-[#B8BCC8]">
        <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
        <div>Loading: {isLoading ? '⏳' : '✅'}</div>
        <div>First Time: {isFirstTimeUser ? '✅' : '❌'}</div>
        <div>Onboarding Complete: {isOnboardingComplete ? '✅' : '❌'}</div>
        {user && <div>User: {user.name || user.email}</div>}
        {error && <div className="text-[#EF4444]">Error: {error}</div>}
      </div>
    </div>
  );
}