import { useEffect, useState } from 'react';
import Header from './components/layout/Header';
import Navigation from './components/layout/Navigation';
import HierarchyBreadcrumbs from './components/layout/HierarchyBreadcrumbs';
import LazySection from './components/utils/LazySection';
import SimpleErrorBoundary from './components/utils/SimpleErrorBoundary';
import TimeoutErrorBoundary from './components/utils/TimeoutErrorBoundary';
import SimpleNotifications from './components/sections/SimpleNotifications';
import OnboardingFlow from './components/onboarding/OnboardingFlow';
import TimeoutResistantLogin from './components/auth/TimeoutResistantLogin';
import FloatingActionButton from './components/enhanced/FloatingActionButton';
import QuickCaptureModal from './components/enhanced/QuickCaptureModal';
import SampleDataInitializer from './components/enhanced/SampleDataInitializer';
import JournalSampleData from './components/journal/JournalSampleData';
// import HierarchyDebug from './components/debug/HierarchyDebug';
import { BottomNavigation, OneHandedLayout, MobilePullToRefresh, useMobileDetection } from './components/enhanced/MobileEnhancements';
import { ErrorRecovery, useErrorRecovery } from './components/enhanced/ErrorRecovery';
import { useAppStore } from './stores/basicAppStore';
import { useEnhancedFeaturesStore } from './stores/enhancedFeaturesStore';
import { useOnboardingStore } from './stores/onboardingStore';
import { useAuthStore } from './stores/authStore';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useThemeInitialization } from './hooks/useThemeInitialization';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './components/ui/dialog';
import { Toaster } from './components/ui/sonner';
import LoadingScreen from './components/shared/LoadingScreen';
import CircuitBreaker from './utils/circuitBreaker';


function AppContent() {
  const [authInitialized, setAuthInitialized] = useState(false);
  const [initializationStarted, setInitializationStarted] = useState(false);
  const [initializationError, setInitializationError] = useState<string | null>(null);
  const [forceInitialized, setForceInitialized] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Mobile detection
  const { isMobile, isTouch } = useMobileDetection();
  
  // Error recovery
  const { error: appError, setError: setAppError, clearError: clearAppError, recover } = useErrorRecovery();

  // Global emergency reset - activate after 5 seconds (faster for better UX)
  useEffect(() => {
    const emergencyReset = setTimeout(() => {
      console.log('Global emergency reset - clearing all circuit breakers');
      try {
        CircuitBreaker.emergencyReset();
        if (!authInitialized) {
          console.log('Force completing due to global emergency reset');
          setAuthInitialized(true);
          setForceInitialized(true);
        }
      } catch (error) {
        console.log('Emergency reset error (non-critical):', error);
        // Force completion anyway
        setAuthInitialized(true);
        setForceInitialized(true);
      }
    }, 5000);

    return () => clearTimeout(emergencyReset);
  }, [authInitialized]);
  
  // Get individual values to prevent subscription issues
  const activeSection = useAppStore(state => state.activeSection);
  const activeSettingsSection = useAppStore(state => state.activeSettingsSection);
  const isNotificationsOpen = useAppStore(state => state.isNotificationsOpen);
  const isMobileMenuOpen = useAppStore(state => state.isMobileMenuOpen);
  
  // Get individual actions
  const setActiveSection = useAppStore(state => state.setActiveSection);
  const setActiveSettingsSection = useAppStore(state => state.setActiveSettingsSection);
  const openNotifications = useAppStore(state => state.openNotifications);
  const closeNotifications = useAppStore(state => state.closeNotifications);
  const openMobileMenu = useAppStore(state => state.openMobileMenu);
  const closeMobileMenu = useAppStore(state => state.closeMobileMenu);
  
  // Auth state with timeout protection
  const { 
    user, 
    isAuthenticated, 
    isLoading: authLoading, 
    error: authError,
    isFirstTimeUser,
    signIn, 
    signUp, 
    clearError,
    initializeAuth,
    markAsExistingUser
  } = useAuthStore();
  
  // Onboarding state
  const isOnboardingComplete = useOnboardingStore(state => state.isOnboardingComplete);

  // Robust initialization with timeout protection
  useEffect(() => {
    let isMounted = true;
    let initStarted = false;
    
    const initializeApp = async () => {
      if (initStarted) return;
      initStarted = true;
      
      try {
        // Clear any problematic circuit breakers with timeout
        const resetPromise = Promise.race([
          Promise.resolve(CircuitBreaker.emergencyReset()),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Reset timeout')), 500))
        ]);
        
        await resetPromise.catch(() => console.log('Circuit breaker reset timeout (non-critical)'));
        
        // Simple auth check with timeout
        const authPromise = Promise.race([
          new Promise(resolve => {
            try {
              const storedAuth = localStorage.getItem('aurum-auth');
              if (storedAuth) {
                const authData = JSON.parse(storedAuth);
                console.log('Found stored auth data');
              }
              resolve(true);
            } catch (e) {
              console.log('Invalid stored auth data, clearing');
              localStorage.removeItem('aurum-auth');
              resolve(true);
            }
          }),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Auth check timeout')), 500))
        ]);
        
        await authPromise.catch(() => console.log('Auth check timeout (non-critical)'));
        
        // Minimal delay for proper initialization
        await new Promise(resolve => setTimeout(resolve, 50));
        
        if (isMounted) {
          setAuthInitialized(true);
        }
      } catch (error) {
        console.log('Auth init failed, completing anyway:', error);
        if (isMounted) {
          setAuthInitialized(true);
          setForceInitialized(true);
        }
      }
    };
    
    // Start initialization immediately
    initializeApp();
    
    // Aggressive backup timeout for better UX
    const emergencyTimeout = setTimeout(() => {
      if (isMounted && !authInitialized) {
        console.log('Backup timeout - force completing initialization');
        setAuthInitialized(true);
        setForceInitialized(true);
      }
    }, 3000);
    
    return () => {
      isMounted = false;
      clearTimeout(emergencyTimeout);
    };
  }, [authInitialized]);

  // Initialize theme and appearance settings
  useThemeInitialization();

  // Expose stores globally for debugging in development
  useEffect(() => {
    if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
      window.useAppStore = useAppStore;
      window.useEnhancedFeaturesStore = useEnhancedFeaturesStore;
      console.log('🔧 Stores exposed globally for debugging');
    }
  }, []);

  // Keyboard shortcuts (only when authenticated)
  useKeyboardShortcuts({
    onSectionChange: setActiveSection,
    onNotificationsOpen: openNotifications,
  });

  // Handle notification actions and navigation globally
  useEffect(() => {
    const handleNotificationAction = (event: CustomEvent) => {
      const action = event.detail;
      
      switch (action.action) {
        case 'navigate':
          if (action.data?.section) {
            setActiveSection(action.data.section, action.data.settingsSection);
            // Close notifications panel if open
            if (isNotificationsOpen) {
              closeNotifications();
            }
          }
          break;
        default:
          break;
      }
    };

    const handleInAppNotification = (event: CustomEvent) => {
      const notification = event.detail;
      // Show toast notification for real-time notifications
      if (typeof window !== 'undefined' && window.dispatchEvent) {
        // This will be handled by the useNotifications hook
        console.log('In-app notification received:', notification.title);
      }
    };

    const handleAurumNavigate = (event: CustomEvent) => {
      const { section, settingsSection } = event.detail;
      if (section) {
        setActiveSection(section, settingsSection);
        // Close any open modals
        if (isNotificationsOpen) {
          closeNotifications();
        }
        if (isMobileMenuOpen) {
          closeMobileMenu();
        }
      }
    };

    window.addEventListener('aurumNotificationAction', handleNotificationAction);
    window.addEventListener('aurumNotification', handleInAppNotification);
    window.addEventListener('aurumNavigate', handleAurumNavigate);

    return () => {
      window.removeEventListener('aurumNotificationAction', handleNotificationAction);
      window.removeEventListener('aurumNotification', handleInAppNotification);
      window.removeEventListener('aurumNavigate', handleAurumNavigate);
    };
  }, [setActiveSection, isNotificationsOpen, closeNotifications, isMobileMenuOpen, closeMobileMenu]);

  // Handle successful authentication
  const handleAuthSuccess = () => {
    clearError();
    clearAppError();
  };

  // Handle onboarding completion
  useEffect(() => {
    if (isOnboardingComplete && isFirstTimeUser) {
      markAsExistingUser();
    }
  }, [isOnboardingComplete, isFirstTimeUser, markAsExistingUser]);

  // Ensure demo users always experience the full PAPT Framework onboarding
  useEffect(() => {
    const isDemoUser = user?.email === 'demo@aurumlife.com' || user?.email?.includes('demo@aurumlife.com');
    if (isDemoUser && isOnboardingComplete) {
      console.log('Demo user detected with completed onboarding - resetting for fresh PAPT experience');
      // Reset onboarding for demo users to showcase the full educational flow
      const onboardingStore = useOnboardingStore.getState();
      onboardingStore.resetOnboarding();
    }
  }, [user]);

  // Handle refresh functionality
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Simulate refresh delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Force re-render of sections
      window.location.reload();
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle app-level errors with comprehensive filtering
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      const message = event.error?.message || event.message || '';
      
      // Comprehensive non-critical error patterns
      const nonCriticalPatterns = [
        'timeout', 'getPage', 'timed out', 'response timed out',
        'Loading chunk', 'WebSocket', 'websocket', 'connection error',
        'Failed to fetch', 'Network error', 'fetch failed',
        'Non-Error promise rejection captured',
        'ResizeObserver loop limit exceeded',
        'Script error', 'Network request failed',
        'ChunkLoadError', 'Loading CSS chunk',
        'AbortError', 'The operation was aborted'
      ];
      
      const isNonCritical = nonCriticalPatterns.some(pattern => 
        message.toLowerCase().includes(pattern.toLowerCase())
      );
      
      if (isNonCritical) {
        console.log('Non-critical error filtered:', message);
        event.preventDefault?.();
      } else {
        console.error('Critical error:', event.error);
        // Only set app error for truly critical issues
        if (!message.includes('duplicate') && !message.includes('_aurumPatched')) {
          setAppError(event.error);
        }
      }
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const reason = String(event.reason || '');
      
      // Comprehensive non-critical rejection patterns
      const nonCriticalPatterns = [
        'timeout', 'getPage', 'timed out', 'response timed out',
        'Loading chunk', 'WebSocket', 'websocket', 'connection error',
        'Failed to fetch', 'Network error', 'fetch failed',
        'AbortError', 'The operation was aborted',
        'ChunkLoadError', 'Loading CSS chunk',
        'ResizeObserver loop limit exceeded',
        'Non-Error promise rejection captured'
      ];
      
      const isNonCritical = nonCriticalPatterns.some(pattern => 
        reason.toLowerCase().includes(pattern.toLowerCase())
      );
      
      if (isNonCritical) {
        console.log('Non-critical promise rejection filtered:', reason);
        event.preventDefault();
      } else {
        console.error('Critical promise rejection:', event.reason);
        // Only set app error for truly critical issues
        if (!reason.includes('duplicate') && !reason.includes('_aurumPatched')) {
          setAppError(new Error(reason));
        }
      }
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [setAppError]);

  // Show loading with aggressive timeout - maximum 3 seconds
  if (!authInitialized) {
    return (
      <LoadingScreen 
        timeout={3000}
        onTimeout={() => {
          console.log('Loading timeout - force completing');
          setAuthInitialized(true);
          setForceInitialized(true);
        }}
        message="Initializing Aurum Life..."
        showSkeleton={false}
      />
    );
  }

  // Show login/signup if not authenticated
  if (!isAuthenticated) {
    return (
      <TimeoutResistantLogin 
        onLogin={handleAuthSuccess}
        isLoading={authLoading}
        error={authError}
      />
    );
  }

  // Show onboarding for new users who haven't completed it
  // OR for demo users (to showcase the full PAPT Framework education experience)
  const isDemoUser = user?.email === 'demo@aurumlife.com' || user?.email?.includes('demo@aurumlife.com');
  const shouldShowOnboarding = (isFirstTimeUser && !isOnboardingComplete) || (isDemoUser && !isOnboardingComplete);
  
  if (shouldShowOnboarding) {
    return <OnboardingFlow />;
  }

  // Show app-level error if present
  if (appError) {
    return (
      <div className="min-h-screen bg-background dark flex items-center justify-center p-4">
        <ErrorRecovery
          error={appError}
          onRetry={async () => {
            try {
              await recover(async () => {
                clearAppError();
                // Small delay before reload to allow state cleanup
                await new Promise(resolve => setTimeout(resolve, 100));
              });
              // Reload after successful recovery
              window.location.reload();
            } catch (error) {
              console.error('Recovery failed:', error);
              // Force reload anyway
              window.location.reload();
            }
          }}
          onReport={(error) => {
            console.log('Error reported:', error);
            // Here you could send to error reporting service
          }}
          context="application"
          severity="high"
          suggestions={[
            'Try refreshing the page',
            'Clear your browser cache',
            'Check your internet connection'
          ]}
        />
      </div>
    );
  }

  return (
    <OneHandedLayout
      className="min-h-screen bg-background dark"
      actionButton={
        isMobile ? (
          <FloatingActionButton isMobile={true} />
        ) : null
      }
    >
      {/* Header - Always visible */}
      <Header 
        onSectionChange={setActiveSection}
        onNotificationsOpen={openNotifications}
        onMobileMenuOpen={openMobileMenu}
      />
      
      {/* Main Layout */}
      <div className="flex h-[calc(100vh-5rem)]"> {/* 5rem accounts for header height */}
        {/* Navigation Sidebar - Hidden on mobile */}
        <div className="w-64 flex-shrink-0 hidden lg:block">
          <div className="fixed top-20 left-0 w-64 h-[calc(100vh-5rem)] overflow-y-auto custom-scrollbar bg-[var(--aurum-secondary-bg)] border-r border-[var(--aurum-glass-border)]">
            <Navigation 
              activeSection={activeSection} 
              onSectionChange={setActiveSection} 
            />
          </div>
        </div>
        
        {/* Main Content - Scrollable with pull-to-refresh on mobile */}
        <main className="flex-1 overflow-y-auto custom-scrollbar p-4 sm:p-6 lg:p-8 pb-32 lg:pb-8 mobile-content-safe">
          {isMobile ? (
            <MobilePullToRefresh onRefresh={handleRefresh}>
              <div className="max-w-7xl mx-auto">
                <HierarchyBreadcrumbs />
                <TimeoutErrorBoundary>
                  <SimpleErrorBoundary>
                    <LazySection section={activeSection} />
                  </SimpleErrorBoundary>
                </TimeoutErrorBoundary>
              </div>
            </MobilePullToRefresh>
          ) : (
            <div className="max-w-7xl mx-auto">
              <HierarchyBreadcrumbs />
              <TimeoutErrorBoundary>
                <SimpleErrorBoundary>
                  <LazySection section={activeSection} />
                </SimpleErrorBoundary>
              </TimeoutErrorBoundary>
            </div>
          )}
        </main>
      </div>

      {/* Bottom Navigation - Mobile only */}
      {isMobile && (
        <BottomNavigation
          activeSection={activeSection}
          onSectionChange={setActiveSection}
        />
      )}

      {/* Notifications Modal */}
      {isNotificationsOpen && (
        <Dialog open={isNotificationsOpen} onOpenChange={closeNotifications}>
          <DialogContent 
            className="glassmorphism-card border-0 bg-card text-card-foreground max-w-4xl max-h-[80vh] p-0"
            aria-describedby="notifications-description"
          >
            <DialogHeader>
              <DialogTitle className="sr-only">Notifications</DialogTitle>
              <DialogDescription id="notifications-description" className="sr-only">
                View and manage your notifications, AI insights, and system updates from across Aurum Life
              </DialogDescription>
            </DialogHeader>
            <SimpleNotifications onClose={closeNotifications} />
          </DialogContent>
        </Dialog>
      )}

      {/* Mobile Navigation Modal */}
      {isMobileMenuOpen && (
        <Dialog open={isMobileMenuOpen} onOpenChange={closeMobileMenu}>
          <DialogContent 
            className="glassmorphism-card border-0 bg-card text-card-foreground max-w-sm w-full h-[80vh] p-0 left-4 translate-x-0"
            aria-describedby="mobile-navigation-description"
          >
            <DialogHeader>
              <DialogTitle className="sr-only">Navigation Menu</DialogTitle>
              <DialogDescription id="mobile-navigation-description" className="sr-only">
                Navigate between different sections of Aurum Life including Dashboard, Tasks, Projects, and more
              </DialogDescription>
            </DialogHeader>
            <div className="h-full overflow-y-auto">
              <Navigation 
                activeSection={activeSection} 
                onSectionChange={(section, settingsSection) => {
                  setActiveSection(section, settingsSection);
                  closeMobileMenu();
                }} 
              />
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Enhanced Features */}
      <SampleDataInitializer />
      <JournalSampleData />
      {!isMobile && <FloatingActionButton isMobile={false} />}
      <QuickCaptureModal />
      
      {/* Debug Component - Temporarily disabled to prevent errors */}
      {/* {process.env.NODE_ENV === 'development' && (
        <div>
          <HierarchyDebug />
        </div>
      )} */}
      
      {/* Toast Notifications */}
      <Toaster />
    </OneHandedLayout>
  );
}

function App() {
  return (
    <TimeoutErrorBoundary>
      <SimpleErrorBoundary>
        <AppContent />
      </SimpleErrorBoundary>
    </TimeoutErrorBoundary>
  );
}

export default App;