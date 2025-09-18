import { Suspense, lazy, useState, useEffect, useRef } from "react";
import { Skeleton } from "../ui/skeleton";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "../ui/button";
import CircuitBreaker from "../../utils/circuitBreaker";

// Import all sections directly to prevent dynamic import timeout issues
import Dashboard from "../sections/Dashboard";
import SimpleDashboard from "../sections/SimpleDashboard";
import Tasks from "../sections/Tasks";
import Pillars from "../sections/Pillars";
import Analytics from "../sections/Analytics";
import GoalPlanner from "../sections/GoalPlanner";
import AIQuickActions from "../sections/AIQuickActions";
import AIQuickCapture from "../sections/AIQuickCapture";
import SimpleTodayFallback from "../sections/SimpleTodayFallback";
import SimpleAreasFallback from "../sections/SimpleAreasFallback";
import SimpleProjectsFallback from "../sections/SimpleProjectsFallback";
import SimplePillarsFallback from "../sections/SimplePillarsFallback";
import Settings from "../sections/Settings";

// Import potentially problematic sections directly to avoid lazy loading timeouts
import Journal from "../sections/Journal";
import AIInsights from "../sections/AIInsights";
import Feedback from "../sections/Feedback";
import EnhancedProfile from "../sections/EnhancedProfile";
import PrivacyControls from "../sections/PrivacyControls";

// Import Phase 4 Enhanced Features
import IntelligentLifeCoachAI from "../enhanced/IntelligentLifeCoachAI";
import PredictiveLifeAnalytics from "../enhanced/PredictiveLifeAnalytics";
import TeamCollaborationHub from "../enhanced/TeamCollaborationHub";
import ThirdPartyIntegrationHub from "../enhanced/ThirdPartyIntegrationHub";
import EnterpriseSecuritySuite from "../enhanced/EnterpriseSecuritySuite";
import AdvancedAIWorkflows from "../enhanced/AdvancedAIWorkflows";
import Integrations from "../sections/Integrations";

interface LazySectionProps {
  section: string;
}

const LoadingSkeleton = () => {
  return (
    <div className="space-y-6">
      {/* Header Skeleton */}
      <div className="mb-8">
        <Skeleton className="h-8 w-1/3 mb-2 bg-[rgba(244,208,63,0.1)] shimmer" />
        <Skeleton className="h-4 w-2/3 bg-[rgba(244,208,63,0.1)] shimmer" />
      </div>
      
      {/* Content Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="glassmorphism-card p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Skeleton className="w-10 h-10 rounded-lg bg-[rgba(244,208,63,0.1)] shimmer" />
              <div className="flex-1">
                <Skeleton className="h-5 w-3/4 mb-2 bg-[rgba(244,208,63,0.1)] shimmer" />
                <Skeleton className="h-3 w-1/2 bg-[rgba(244,208,63,0.1)] shimmer" />
              </div>
            </div>
            <Skeleton className="h-2 w-full mb-3 bg-[rgba(244,208,63,0.1)] shimmer" />
            <div className="space-y-2">
              <Skeleton className="h-3 w-full bg-[rgba(244,208,63,0.1)] shimmer" />
              <Skeleton className="h-3 w-4/5 bg-[rgba(244,208,63,0.1)] shimmer" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Improved timeout wrapper with better error handling and adaptive timeouts
function RobustComponentWrapper({
  children,
  section,
}: {
  children: React.ReactNode;
  section: string;
}) {
  const [renderError, setRenderError] = useState<Error | null>(null);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const mountedRef = useRef(true);

  // Define timeout durations based on component complexity
  const getTimeoutDuration = (sectionName: string): number => {
    const complexSections = [
      'dashboard', 'enterprise-security', 'pillars', 'analytics', 
      'ai-life-coach', 'team-collaboration', 'predictive-analytics',
      'ai-workflows', 'integration-hub'
    ];
    
    const moderateSections = [
      'tasks', 'projects', 'journal', 'ai-insights', 
      'goal-planner', 'enhanced-profile', 'privacy-controls', 'integrations'
    ];
    
    if (complexSections.includes(sectionName)) {
      return 8000; // 8 seconds for complex components
    } else if (moderateSections.includes(sectionName)) {
      return 5000; // 5 seconds for moderate components  
    } else {
      return 3000; // 3 seconds for simple components
    }
  };

  useEffect(() => {
    mountedRef.current = true;
    setIsLoading(true);
    
    const timeoutDuration = getTimeoutDuration(section);
    
    // Set timeout based on component complexity
    timeoutRef.current = setTimeout(() => {
      if (mountedRef.current) {
        console.warn(`Section ${section} render timeout after ${timeoutDuration}ms - showing fallback`);
        setHasTimedOut(true);
        setIsLoading(false);
      }
    }, timeoutDuration);

    // Clear timeout if component mounts successfully
    const clearTimeoutOnMount = setTimeout(() => {
      if (mountedRef.current) {
        setIsLoading(false);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
      }
    }, 100); // Give component 100ms to initialize

    return () => {
      mountedRef.current = false;
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      clearTimeout(clearTimeoutOnMount);
    };
  }, [section]);

  // Handle render errors
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      if (error.message?.includes('getPage') || 
          error.message?.includes('timeout') ||
          error.message?.toLowerCase().includes(section)) {
        console.error(`Render error in ${section}:`, error.error);
        setRenderError(error.error || new Error(error.message));
      }
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, [section]);

  if (renderError || hasTimedOut) {
    // Return appropriate fallbacks for each section
    switch (section) {
      case "dashboard":
        return (
          <div className="flex flex-col items-center justify-center min-h-[300px] space-y-4">
            <div className="glassmorphism-card p-6 text-center max-w-lg">
              <AlertCircle className="w-10 h-10 text-[#F59E0B] mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">
                Dashboard Initializing
              </h3>
              <p className="text-[#B8BCC8] mb-4 text-sm">
                Your Personal Operating System dashboard is loading enhanced features...
              </p>
              <div className="space-y-3">
                <Button
                  onClick={() => {
                    CircuitBreaker.reset();
                    setRenderError(null);
                    setHasTimedOut(false);
                    setIsLoading(true);
                  }}
                  className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] text-sm py-2"
                >
                  <RefreshCw className="w-3 h-3 mr-2" />
                  Reload Dashboard
                </Button>
                <Button
                  onClick={() => window.location.reload()}
                  variant="outline"
                  className="w-full border-[rgba(244,208,63,0.2)] text-[#F4D03F] text-sm py-2"
                >
                  Refresh Page
                </Button>
              </div>
            </div>
          </div>
        );
        
      case "pillars":
        return (
          <div className="space-y-6">
            <div className="glassmorphism-card p-6 text-center">
              <h2 className="text-xl font-semibold text-white mb-4">Loading Pillars</h2>
              <p className="text-[#B8BCC8] mb-4">
                Setting up your PAPT Framework pillars...
              </p>
              <Button
                onClick={() => {
                  CircuitBreaker.reset();
                  setRenderError(null);
                  setHasTimedOut(false);
                  setIsLoading(true);
                }}
                className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry Loading
              </Button>
            </div>
            <SimplePillarsFallback />
          </div>
        );
        
      case "enterprise-security":
        return (
          <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
            <div className="glassmorphism-card p-8 text-center max-w-lg">
              <AlertCircle className="w-12 h-12 text-[#F59E0B] mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                Enterprise Security Loading
              </h3>
              <p className="text-[#B8BCC8] mb-6">
                Initializing enterprise security features and compliance tools...
              </p>
              <div className="space-y-3">
                <Button
                  onClick={() => {
                    CircuitBreaker.reset();
                    setRenderError(null);
                    setHasTimedOut(false);
                    setIsLoading(true);
                  }}
                  className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Retry Security Suite
                </Button>
                <Button
                  onClick={() => window.location.reload()}
                  variant="outline"
                  className="w-full border-[rgba(244,208,63,0.2)] text-[#F4D03F]"
                >
                  Refresh Page
                </Button>
              </div>
            </div>
          </div>
        );
        
      case "areas":
        return <SimpleAreasFallback />;
      case "projects":
        return <SimpleProjectsFallback />;
      case "today":
        return <SimpleTodayFallback />;
        
      default:
        return (
          <div className="flex flex-col items-center justify-center min-h-[300px] space-y-4">
            <div className="glassmorphism-card p-6 text-center max-w-md">
              <AlertCircle className="w-10 h-10 text-[#F59E0B] mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">
                {renderError ? 'Component Error' : 'Loading Timeout'}
              </h3>
              <p className="text-[#B8BCC8] mb-4 text-sm">
                {renderError 
                  ? `Error in ${section.replace("-", " ")} section: ${renderError.message}`
                  : `The ${section.replace("-", " ")} section is taking longer than expected to load.`
                }
              </p>
              <div className="space-y-2">
                <Button
                  onClick={() => {
                    CircuitBreaker.reset();
                    setRenderError(null);
                    setHasTimedOut(false);
                    setIsLoading(true);
                  }}
                  className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F] text-sm py-2"
                >
                  <RefreshCw className="w-3 h-3 mr-2" />
                  Try Again
                </Button>
                <Button
                  onClick={() => window.location.reload()}
                  variant="outline"
                  className="w-full border-[rgba(244,208,63,0.2)] text-[#F4D03F] text-sm py-2"
                >
                  Refresh Page
                </Button>
              </div>
            </div>
          </div>
        );
    }
  }

  return <>{children}</>;
}

export default function LazySection({
  section,
}: LazySectionProps) {
  const [hasError, setHasError] = useState(false);
  
  // Error boundary effect for catching getPage and similar errors
  useEffect(() => {
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const reason = String(event.reason);
      if (reason.includes('getPage') || reason.includes('timeout') || reason.includes('timed out')) {
        console.error('LazySection promise rejection:', event.reason);
        setHasError(true);
        event.preventDefault(); // Prevent the error from propagating
      }
    };

    const handleError = (event: ErrorEvent) => {
      if (event.message?.includes('getPage') || 
          event.message?.includes('timeout') ||
          event.message?.includes('timed out')) {
        console.error('LazySection error:', event.error);
        setHasError(true);
      }
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, []);

  const renderSection = () => {
    try {
      switch (section) {
        case "dashboard":
          return <Dashboard />;
        case "tasks":
          return <Tasks />;
        case "today":
          return <SimpleTodayFallback />;
        case "pillars":
          return <Pillars />;
        case "areas":
          return <SimpleAreasFallback />;
        case "projects":
          return <SimpleProjectsFallback />;
        case "journal":
          return <Journal />;
        case "ai-insights":
          return <AIInsights />;
        case "quick-actions":
          return <AIQuickActions />;
        case "ai-quick-capture":
          return <AIQuickCapture />;
        case "goal-planner":
          return <GoalPlanner />;
        case "analytics":
          return <Analytics />;
        case "enhanced-profile":
          return <EnhancedProfile />;
        case "privacy-controls":
          return <PrivacyControls />;
        case "feedback":
          return <Feedback />;
        case "settings":
          return <Settings />;
        // Phase 4 Enhanced Features
        case "ai-workflows":
          return <AdvancedAIWorkflows />;
        case "ai-life-coach":
          return <IntelligentLifeCoachAI />;
        case "predictive-analytics":
          return <PredictiveLifeAnalytics />;
        case "team-collaboration":
          return <TeamCollaborationHub />;
        case "integrations":
          return <Integrations />;
        case "integration-hub":
          return <ThirdPartyIntegrationHub />;
        case "enterprise-security":
          return <EnterpriseSecuritySuite />;
        default:
          return (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <h2 className="text-2xl text-white mb-2">
                  Coming Soon
                </h2>
                <p className="text-[#B8BCC8]">
                  The {section.replace("-", " ")} section is under
                  development
                </p>
              </div>
            </div>
          );
      }
    } catch (error) {
      console.error(`Error rendering section ${section}:`, error);
      setHasError(true);
      return null;
    }
  };

  if (hasError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="glassmorphism-card p-8 text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-[#F59E0B] mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            Section Loading Error
          </h3>
          <p className="text-[#B8BCC8] mb-6">
            There was an error loading the {section.replace("-", " ")} section. 
            This might be due to a network timeout or connection issue.
          </p>
          <div className="space-y-3">
            <Button
              onClick={() => {
                setHasError(false);
                CircuitBreaker.reset();
              }}
              className="w-full bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
            <Button
              onClick={() => window.location.reload()}
              variant="outline"
              className="w-full border-[rgba(244,208,63,0.2)] text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]"
            >
              Refresh Page
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Critical sections that need timeout protection (only Phase 4 advanced features)
  const timeoutProtectedSections = [
    'enterprise-security', 'ai-life-coach', 'team-collaboration', 
    'predictive-analytics', 'integration-hub', 'ai-workflows'
  ];
  
  // Simple sections render directly without timeout wrapper
  const simpleSections = [
    'dashboard', 'pillars', 'tasks', 'today', 'settings', 'feedback',
    'ai-quick-capture', 'quick-actions', 'journal', 'analytics', 'integrations'
  ];

  if (simpleSections.includes(section)) {
    // Render simple sections directly without timeout wrapper
    return (
      <Suspense fallback={<LoadingSkeleton />}>
        {renderSection()}
      </Suspense>
    );
  }

  if (timeoutProtectedSections.includes(section)) {
    // Use timeout protection for complex Phase 4 features
    return (
      <RobustComponentWrapper section={section}>
        {renderSection()}
      </RobustComponentWrapper>
    );
  }

  // Default behavior for other sections
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      {renderSection()}
    </Suspense>
  );
}