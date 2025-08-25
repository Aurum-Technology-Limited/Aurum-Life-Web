import React, { useState, useEffect, Suspense, lazy } from 'react';
import "./App.css";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './contexts/BackendAuthContext';
import { DataProvider } from './contexts/DataContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { GoogleOAuthProvider } from '@react-oauth/google';
import ProtectedRoute from './components/ProtectedRoute';
import AppWrapper from './components/AppWrapper';
import SimpleLayout from './components/SimpleLayout';
import { Toaster } from './components/ui/toaster';
import globalErrorHandler from './utils/globalErrorHandler'; // Import global error handler
import ErrorBoundary from './components/ErrorBoundary';
import LazyComponentErrorBoundary from './components/LazyComponentErrorBoundary';
import PasswordReset from './components/PasswordReset';

// Import performance test for debugging
import './services/performanceTest';

// Lazy load components for better performance and code splitting
const OptimizedDashboard = lazy(() => import('./components/OptimizedDashboard'));
const Today = lazy(() => import('./components/Today'));
const Pillars = lazy(() => import('./components/Pillars'));
const Areas = lazy(() => import('./components/Areas'));
const Projects = lazy(() => import('./components/Projects'));
const ProjectTemplates = lazy(() => import('./components/ProjectTemplates'));
const Journal = lazy(() => import('./components/Journal'));
const Tasks = lazy(() => import('./components/Tasks'));
const Feedback = lazy(() => import('./components/Feedback'));
const AICoach = lazy(() => import('./components/AICoach'));
const Profile = lazy(() => import('./components/Profile'));
const ProfilePage = lazy(() => import('./components/ProfilePage'));
const Insights = lazy(() => import('./components/Insights'));
const Settings = lazy(() => import('./components/Settings'));
const NotificationSettings = lazy(() => import('./components/NotificationSettings'));
const NotificationCenter = lazy(() => import('./components/NotificationCenter'));

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
  const [sectionParams, setSectionParams] = useState({}); // Add state for section parameters
  const [isPasswordResetPage, setIsPasswordResetPage] = useState(false);

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
      'project-templates': 'Project Templates',
      'tasks': 'Tasks',
      'journal': 'Journal',
      'feedback': 'Feedback & Support',
      'ai-coach': 'AI Coach',
      'profile': 'Profile',
      'insights': 'Insights',
      'settings': 'Settings',
      'notification-settings': 'Notifications',
      'notifications': 'Notification Center'
    };

    const sectionTitle = sectionTitles[activeSection] || 'Dashboard';
    document.title = `${sectionTitle} | Aurum Life`;
  }, [activeSection]);

  // Check if we're on password reset page (robust with URL change detection)
  useEffect(() => {
    const checkPasswordResetPage = () => {
      const pathname = window.location.pathname;
      const hash = window.location.hash;
      
      console.log('🔍 Checking password reset page. Pathname:', pathname, 'Hash:', hash);
      
      if (pathname === '/reset-password') {
        console.log('✅ Password reset page detected');
        setIsPasswordResetPage(true);
      } else {
        console.log('❌ Not password reset page');
        setIsPasswordResetPage(false);
      }
    };
    
    // Check on mount
    checkPasswordResetPage();
    
    // Listen for URL changes (including hash changes)
    const handlePopState = () => {
      console.log('🔄 URL changed, rechecking password reset page');
      checkPasswordResetPage();
    };
    
    const handleHashChange = () => {
      console.log('🔄 Hash changed, rechecking password reset page');
      checkPasswordResetPage();
    };
    
    window.addEventListener('popstate', handlePopState);
    window.addEventListener('hashchange', handleHashChange);
    
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  const handleSectionChange = (newSection, params = {}) => {
    console.log('🔄 Navigation: Changing section from', activeSection, 'to', newSection, 'with params:', params);
    setActiveSection(newSection);
    setSectionParams(params);
  };

  const renderActiveSection = () => {
    const props = { onSectionChange: handleSectionChange, sectionParams };
    
    console.log('🎯 Rendering active section:', activeSection, 'with params:', sectionParams);
    
    return (
      <Suspense fallback={<LoadingSpinner />}>
        {(() => {
          switch (activeSection) {
            case 'today':
              console.log('📅 Rendering Today component');
              return <Today {...props} />;
            case 'insights':
              console.log('📊 Rendering Insights component');
              return <Insights {...props} />;
            case 'pillars':
              console.log('⛰️ Rendering Pillars component');
              return <Pillars {...props} />;
            case 'areas':
              console.log('🗂️ Rendering Areas component');
              return <Areas {...props} />;
            case 'projects':
              console.log('📁 Rendering Projects component');
              return <Projects {...props} />;
            case 'project-templates':
              console.log('📋 Rendering ProjectTemplates component');
              return <ProjectTemplates {...props} />;
            case 'journal':
              console.log('📖 Rendering Journal component');
              return (
                <LazyComponentErrorBoundary componentName="Journal">
                  <Journal {...props} />
                </LazyComponentErrorBoundary>
              );
            case 'tasks':
              console.log('✅ Rendering Tasks component');
              return <Tasks {...props} />;
            case 'feedback':
              console.log('💬 Rendering Feedback component');
              return <Feedback {...props} />;
            case 'ai-coach':
              console.log('🤖 Rendering AICoach component');
              return <AICoach {...props} />;
            case 'settings':
              console.log('⚙️ Rendering Settings component');
              return <Settings {...props} />;
            case 'notification-settings':
              console.log('🔔 Rendering NotificationSettings component');
              return <NotificationSettings {...props} />;
            case 'notifications':
              console.log('📋 Rendering NotificationCenter component');
              return <NotificationCenter {...props} />;
            case 'profile':
              console.log('👤 Rendering Profile component');
              // Check if this is an OAuth callback
              const hash = window.location.hash;
              if (hash.includes('session_id=')) {
                return <ProfilePage setActiveSection={setActiveSection} />;
              } else {
                return <Profile {...props} />;
              }
            case 'dashboard':
            default:
              console.log('🏠 Rendering Optimized Dashboard component');
              return <OptimizedDashboard {...props} />;
          }
        })()}
      </Suspense>
    );
  };

  // If on password reset page, show the PasswordReset component
  if (isPasswordResetPage) {
    return (
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <GoogleOAuthProvider clientId="514537887764-mgfh2g9k8ni7tanhm32o2o4mg1atrcgb.apps.googleusercontent.com">
            <AuthProvider>
              <DataProvider>
                <NotificationProvider>
                  <DndProvider backend={HTML5Backend}>
                    <div className="App">
                      <PasswordReset />
                    </div>
                  </DndProvider>
                </NotificationProvider>
              </DataProvider>
            </AuthProvider>
          </GoogleOAuthProvider>
        </QueryClientProvider>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <GoogleOAuthProvider clientId="514537887764-mgfh2g9k8ni7tanhm32o2o4mg1atrcgb.apps.googleusercontent.com">
          <AuthProvider>
            <DataProvider>
              <NotificationProvider>
                <DndProvider backend={HTML5Backend}>
                  <div className="App">
                  <AppWrapper onNavigateToSection={handleSectionChange}>
                    <SimpleLayout 
                      activeSection={activeSection} 
                      setActiveSection={setActiveSection}
                    >
                      {renderActiveSection()}
                    </SimpleLayout>
                  </AppWrapper>
                  <Toaster />
                  </div>
                </DndProvider>
              </NotificationProvider>
            </DataProvider>
          </AuthProvider>
        </GoogleOAuthProvider>
        {/* TanStack Query DevTools - temporarily disabled due to locale issue */}
        {/* process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        ) */}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;