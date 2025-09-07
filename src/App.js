import React, { useState, useEffect, Suspense, lazy } from 'react';
import "./App.css";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ApolloProvider } from '@apollo/client';
import { apolloClient } from './services/apolloClient';
import { AuthProvider } from './contexts/SupabaseAuthContext';
import { DataProvider } from './contexts/DataContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { GoogleOAuthProvider } from '@react-oauth/google';
import ProtectedRoute from './components/ProtectedRoute';
import AppWrapper from './components/AppWrapper';
import NewSidebar from './components/NewSidebar';
import NewHeader from './components/NewHeader';
import NewDashboard from './components/NewDashboard';
import { Toaster } from './components/ui/toaster';
import globalErrorHandler from './utils/globalErrorHandler';
import ErrorBoundary from './components/ErrorBoundary';
import LazyComponentErrorBoundary from './components/LazyComponentErrorBoundary';
import PasswordReset from './components/PasswordReset';
import AIDecisionHelper from './components/ui/AIDecisionHelper';
import AuthDebugPanel from './components/AuthDebugPanel';
import { StrategicProjectAssessment } from './components/StrategicProjectAssessment';
import { AreasSection } from './components/AreasSection';
import { TasksSection } from './components/TasksSection';
import { AdvancedAIInsights } from './components/AdvancedAIInsights';

// Import performance test for debugging
import './services/performanceTest';

// Lazy load components for better performance and code splitting
const Today = lazy(() => import('./components/Today'));
const Pillars = lazy(() => import('./components/Pillars'));
const Journal = lazy(() => import('./components/Journal'));
const Feedback = lazy(() => import('./components/Feedback'));
const AICoach = lazy(() => import('./components/AICoach'));
const AICommandCenter = lazy(() => import('./components/AICommandCenter'));
const Profile = lazy(() => import('./components/Profile'));
const ProfilePage = lazy(() => import('./components/ProfilePage'));
const EnhancedInsights = lazy(() => import('./components/EnhancedInsights'));
const AnalyticsDashboard = lazy(() => import('./components/AnalyticsDashboard'));
const Settings = lazy(() => import('./components/Settings'));
const NotificationSettings = lazy(() => import('./components/NotificationSettings'));
const NotificationCenter = lazy(() => import('./components/NotificationCenter'));
const AIIntelligenceCenter = lazy(() => import('./components/AIIntelligenceCenter'));

// Import AI Command Center hook
import SemanticSearch, { useSemanticSearch } from './components/SemanticSearch';

// Loading component for suspense fallback
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen bg-[#0B0D14]">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
      <p className="text-gray-400 text-sm">Loading...</p>
    </div>
  </div>
);

// Create TanStack Query client with optimized configuration for better performance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes - increased for better performance
      gcTime: 10 * 60 * 1000, // 10 minutes - increased for better caching
      retry: 1, // Only retry once on failure for faster error feedback
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
      refetchOnMount: 'always', // Always refetch when component mounts for fresh data
      refetchOnReconnect: true, // Refetch when reconnecting to internet
      refetchInterval: false, // Disable automatic refetching
      networkMode: 'online', // Only run queries when online
    },
    mutations: {
      retry: 1, // Faster error feedback for mutations
      networkMode: 'online', // Only run mutations when online
    },
  },
});

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [sectionParams, setSectionParams] = useState({});
  const [isPasswordResetPage, setIsPasswordResetPage] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Initialize Semantic Search
  const { isOpen: isSemanticSearchOpen, close: closeSemanticSearch } = useSemanticSearch();

  // Debug effect to track activeSection changes
  useEffect(() => {
    console.log('🔄 Active section updated to:', activeSection, 'with params:', sectionParams);
  }, [activeSection, sectionParams]);

  // Update document title based on active section
  useEffect(() => {
    const sectionTitles = {
      'today': 'Today',
      'pillars': 'Pillars', 
      'areas': 'Areas', 
      'projects': 'Projects',
      'tasks': 'Tasks',
      'journal': 'Journal',
      'insights': 'AI Insights',
      'analytics': 'Analytics',
      'feedback': 'Feedback',
      'settings': 'Settings',
      'dashboard': 'Dashboard',
      'goal-planner': 'Goal Planner',
      'ai-insights': 'AI Insights',
      'ai-actions': 'AI Actions'
    };
    
    const title = sectionTitles[activeSection] || 'Aurum Life';
    document.title = `${title} - Aurum Life`;
  }, [activeSection]);

  // Handle URL hash changes for deep linking
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash && hash !== activeSection) {
        console.log('🔗 Hash change detected:', hash);
        setActiveSection(hash);
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    
    // Check initial hash
    const initialHash = window.location.hash.slice(1);
    if (initialHash && initialHash !== activeSection) {
      setActiveSection(initialHash);
    }

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [activeSection]);

  // Update URL hash when section changes (debounced to prevent throttling)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (activeSection && activeSection !== 'dashboard') {
        window.location.hash = activeSection;
      } else if (activeSection === 'dashboard') {
        window.location.hash = '';
      }
    }, 100); // 100ms debounce

    return () => clearTimeout(timeoutId);
  }, [activeSection]);

  // Handle password reset page
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('mode') === 'resetPassword') {
      setIsPasswordResetPage(true);
    }
  }, []);

  // Global error handler setup
  useEffect(() => {
    // Global error handler is already set up in its constructor
    // No additional setup needed
    return () => {
      // Cleanup if needed
    };
  }, []);

  const handleNavigateToSection = (section, params = {}) => {
    console.log('🧭 Navigating to section:', section, 'with params:', params);
    setActiveSection(section);
    setSectionParams(params);
    // Close mobile menu when navigating
    setIsMobileMenuOpen(false);
  };

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Props to pass to components
  const props = {
    onSectionChange: handleNavigateToSection,
    sectionParams,
    setSectionParams
  };

  // Render active section with new layout
  const renderActiveSection = () => {
    switch (activeSection) {
      case 'dashboard':
        console.log('🏠 Rendering Dashboard component');
        return <NewDashboard />;
      case 'today':
        console.log('📅 Rendering Today component');
        return <Today {...props} />;
      case 'insights':
        console.log('📊 Rendering Advanced AI Insights component');
        return <AdvancedAIInsights />;
      case 'analytics':
        console.log('📈 Rendering Analytics Dashboard component');
        return <AnalyticsDashboard {...props} onSectionChange={setActiveSection} />;
      case 'pillars':
        console.log('⛰️ Rendering Pillars component');
        return <Pillars {...props} />;
      case 'areas':
        console.log('🗂️ Rendering Areas Section component');
        return <AreasSection />;
      case 'projects':
        console.log('📁 Rendering Strategic Project Assessment component');
        return <StrategicProjectAssessment />;
      case 'journal':
        console.log('📖 Rendering Journal component');
        return (
          <LazyComponentErrorBoundary componentName="Journal">
            <Journal {...props} />
          </LazyComponentErrorBoundary>
        );
      case 'tasks':
        console.log('✅ Rendering Tasks Section component');
        return <TasksSection />;
      case 'feedback':
        console.log('💬 Rendering Feedback component');
        return <Feedback {...props} />;
      case 'goal-planner':
        console.log('🎯 Rendering Goal Planner (AI Coach) component');
        return <AICoach {...props} onSectionChange={setActiveSection} />;
      case 'ai-insights':
        console.log('🧠 Rendering My AI Insights (Intelligence Center) component');
        return <AIIntelligenceCenter {...props} onSectionChange={setActiveSection} />;
      case 'ai-actions':
        console.log('⚡ Rendering AI Quick Actions (Command Center) component');
        return <AICommandCenter {...props} onSectionChange={setActiveSection} />;
      case 'settings':
        console.log('⚙️ Rendering Settings component');
        return <Settings {...props} />;
      case 'profile':
        console.log('👤 Rendering Profile component');
        return <Profile {...props} />;
      case 'notifications':
        console.log('🔔 Rendering Notification Center component');
        return <NotificationCenter {...props} />;
      case 'notification-settings':
        console.log('🔔 Rendering Notification Settings component');
        return <NotificationSettings {...props} />;
      default:
        console.log('🏠 Rendering default Dashboard component');
        return <NewDashboard />;
    }
  };

  // Password reset page
  if (isPasswordResetPage) {
    return (
      <ErrorBoundary>
        <PasswordReset onBack={() => setIsPasswordResetPage(false)} />
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ApolloProvider client={apolloClient}>
          <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID || ''}>
            <AuthProvider>
              <DataProvider>
                <NotificationProvider>
                  <DndProvider backend={HTML5Backend}>
                    <AppWrapper onNavigateToSection={handleNavigateToSection}>
                      <div className="min-h-screen flex flex-col lg:flex-row" style={{backgroundColor: '#0B0D14', color: 'white'}}>
                        {/* Mobile Header */}
                        <div className="lg:hidden">
                          <NewHeader 
                            onMobileMenuToggle={handleMobileMenuToggle}
                            isMobileMenuOpen={isMobileMenuOpen}
                          />
                        </div>
                        
                        {/* Mobile Sidebar Overlay */}
                        {isMobileMenuOpen && (
                          <div className="lg:hidden fixed inset-0 z-50">
                            <div 
                              className="absolute inset-0" 
                              style={{background: 'rgba(0,0,0,0.5)'}}
                              onClick={handleMobileMenuToggle}
                            ></div>
                            <div className="relative h-full w-80 max-w-[80vw]">
                              <NewSidebar activeSection={activeSection} onSectionChange={handleNavigateToSection} />
                            </div>
                          </div>
                        )}

                        {/* Desktop Sidebar */}
                        <div className="hidden lg:block">
                          <NewSidebar activeSection={activeSection} onSectionChange={setActiveSection} />
                        </div>
                        
                        {/* Main Content Area */}
                        <div className="flex-1 flex flex-col min-w-0">
                          {/* Desktop Header */}
                          <div className="hidden lg:block">
                            <NewHeader 
                              onMobileMenuToggle={handleMobileMenuToggle}
                              isMobileMenuOpen={isMobileMenuOpen}
                            />
                          </div>
                          
                          <main className="flex-1 px-4 lg:px-6 py-4 lg:py-6 overflow-x-hidden">
                            <div className="w-full max-w-none lg:max-w-[1400px] mx-auto space-y-6 lg:space-y-8">
                              {/* Page Title / Breadcrumb */}
                              <div className="flex items-center justify-between gap-4">
                                <div>
                                  <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">Live with Intention</h1>
                                  <p className="text-sm" style={{color: '#B8BCC8'}}>Align daily actions to your life vision. Every task traces up to its purpose.</p>
                                </div>
                                <div className="hidden sm:flex items-center gap-2">
                                  <span className="text-xs" style={{color: '#B8BCC8'}}>Alignment</span>
                                  <div className="h-2 w-36 rounded-full overflow-hidden border" style={{borderColor: 'rgba(244,208,63,0.2)', background: 'rgba(26,29,41,0.6)'}}>
                                    <div className="h-full" style={{width: '72%', background: 'linear-gradient(90deg,#F4D03F,#F7DC6F)'}}></div>
                                  </div>
                                  <span className="text-xs font-medium" style={{color: '#F4D03F'}}>72%</span>
                                </div>
                              </div>

                              {/* Strategic Hierarchy Breadcrumb */}
                              <div className="strategic-breadcrumb mb-2">
                                <div className="flex items-center gap-2 text-sm" style={{color: '#B8BCC8'}}>
                                  <span>Strategic View:</span>
                                  <div className="flex items-center gap-1">
                                    <span className="px-2 py-1 rounded border" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>Health</span>
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="px-2 py-1 rounded border" style={{borderColor: 'rgba(244,208,63,0.15)'}}>Training</span>
                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                    <span className="px-2 py-1 rounded border" style={{borderColor: 'rgba(244,208,63,0.15)'}}>Strength Cycle</span>
                                  </div>
                                </div>
                              </div>

                              {/* Render Active Section */}
                              <Suspense fallback={<LoadingSpinner />}>
                                {renderActiveSection()}
                              </Suspense>
                            </div>
                          </main>
                        </div>
                      </div>

                      {/* Semantic Search Modal */}
                      <SemanticSearch 
                        isOpen={isSemanticSearchOpen}
                        onClose={closeSemanticSearch}
                        onNavigate={handleNavigateToSection}
                      />

                      {/* AI Decision Helper */}
                      <AIDecisionHelper />

                      {/* Auth Debug Panel (development only) */}
                      {process.env.NODE_ENV === 'development' && <AuthDebugPanel />}

                      {/* Toast Notifications */}
                      <Toaster />
                    </AppWrapper>
                  </DndProvider>
                </NotificationProvider>
              </DataProvider>
            </AuthProvider>
          </GoogleOAuthProvider>
        </ApolloProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;