/**
 * Aurum Life - Main Application Component
 * ========================================
 * 
 * This is the root component of the Aurum Life Personal Operating System.
 * It handles the overall application structure, routing, authentication,
 * and global state management.
 * 
 * Key Responsibilities:
 * - Authentication flow and protected routes
 * - Global state providers (Auth, Data, Notifications)
 * - Lazy loading of components for performance
 * - Section-based navigation (not traditional routing)
 * - Error boundary implementation
 * - React Query configuration
 * 
 * Architecture Notes:
 * - Uses a single-page application (SPA) approach
 * - Section-based navigation instead of URL routing
 * - Lazy loading with Suspense for code splitting
 * - Context-based state management
 * 
 * @author Aurum Life Development Team
 * @version 1.0.0
 */

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
import globalErrorHandler from './utils/globalErrorHandler';
import ErrorBoundary from './components/ErrorBoundary';
import LazyComponentErrorBoundary from './components/LazyComponentErrorBoundary';
import PasswordReset from './components/PasswordReset';

// ========================================
// PERFORMANCE MONITORING
// ========================================
// Import performance test for debugging (disable in production)
import './services/performanceTest';

// ========================================
// LAZY LOADED COMPONENTS
// ========================================
/**
 * All major components are lazy loaded to improve initial load time.
 * This creates separate chunks for each component, loaded on demand.
 * 
 * Benefits:
 * - Faster initial page load
 * - Smaller bundle sizes
 * - Better caching
 * - Improved performance on slow connections
 */

// Core feature components
const OptimizedDashboard = lazy(() => import('./components/OptimizedDashboard'));
const Today = lazy(() => import('./components/Today'));

// PAPT hierarchy components
const Pillars = lazy(() => import('./components/Pillars'));
const Areas = lazy(() => import('./components/Areas'));
const Projects = lazy(() => import('./components/Projects'));
const Tasks = lazy(() => import('./components/Tasks'));
const ProjectTemplates = lazy(() => import('./components/ProjectTemplates'));

// User engagement features
const Journal = lazy(() => import('./components/Journal'));
const Feedback = lazy(() => import('./components/Feedback'));
const AICoach = lazy(() => import('./components/AICoach'));
const Insights = lazy(() => import('./components/Insights'));

// User account and settings
const Profile = lazy(() => import('./components/Profile'));
const ProfilePage = lazy(() => import('./components/ProfilePage'));
const Settings = lazy(() => import('./components/Settings'));
const NotificationSettings = lazy(() => import('./components/NotificationSettings'));
const NotificationCenter = lazy(() => import('./components/NotificationCenter'));

// ========================================
// LOADING COMPONENT
// ========================================
/**
 * Loading spinner shown while lazy components are being loaded.
 * Maintains the app's dark theme and visual consistency.
 */
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen bg-[#0B0D14]">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
      <p className="text-gray-400 text-sm">Loading...</p>
    </div>
  </div>
);

// ========================================
// REACT QUERY CONFIGURATION
// ========================================
/**
 * TanStack Query (formerly React Query) configuration for data fetching.
 * Optimized for performance with appropriate cache times and retry logic.
 * 
 * Key Settings:
 * - staleTime: 5 minutes - data considered fresh for this duration
 * - gcTime: 10 minutes - garbage collection time for unused data
 * - retry: 1 - only retry failed requests once
 * - refetchOnWindowFocus: false - don't refetch when tab gains focus
 * - networkMode: 'online' - only fetch when internet is available
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes - data stays fresh
      gcTime: 10 * 60 * 1000,         // 10 minutes - cache retention
      retry: 1,                       // Retry failed requests once
      refetchOnWindowFocus: false,    // Don't refetch on tab focus
      refetchOnMount: 'always',       // Always refetch on mount
      refetchOnReconnect: true,       // Refetch when internet returns
      refetchInterval: false,         // No automatic refetching
      networkMode: 'online',          // Only query when online
    },
    mutations: {
      retry: 1,                       // Retry failed mutations once
      networkMode: 'online',          // Only mutate when online
    },
  },
});

// ========================================
// MAIN APP COMPONENT
// ========================================
function App() {
  /**
   * Application State Management
   * 
   * activeSection: Current visible section/page
   * sectionParams: Parameters passed to sections (e.g., specific IDs)
   * isPasswordResetPage: Special handling for password reset flow
   */
  const [activeSection, setActiveSection] = useState('dashboard');
  const [sectionParams, setSectionParams] = useState({});
  const [isPasswordResetPage, setIsPasswordResetPage] = useState(false);

  // ========================================
  // DEBUG LOGGING
  // ========================================
  /**
   * Development helper to track navigation changes.
   * Remove or disable in production.
   */
  useEffect(() => {
    console.log('🔄 Active section updated to:', activeSection, 'with params:', sectionParams);
  }, [activeSection, sectionParams]);

  // ========================================
  // DYNAMIC PAGE TITLE
  // ========================================
  /**
   * Updates browser tab title based on current section.
   * Improves user experience when multiple tabs are open.
   */
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
    document.title = `${sectionTitle} - Aurum Life`;
  }, [activeSection]);

  // ========================================
  // PASSWORD RESET DETECTION
  // ========================================
  /**
   * Check URL for password reset flow on mount.
   * This handles the special case of email-based password reset links.
   */
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const isReset = urlParams.get('type') === 'recovery' && urlParams.get('access_token');
    setIsPasswordResetPage(isReset);
  }, []);

  // ========================================
  // SECTION COMPONENT MAPPING
  // ========================================
  /**
   * Maps section names to their corresponding components.
   * This enables the section-based navigation system.
   * 
   * Note: All components are wrapped in LazyComponentErrorBoundary
   * to handle loading errors gracefully.
   */
  const renderSection = () => {
    const sectionComponents = {
      'dashboard': <LazyComponentErrorBoundary><OptimizedDashboard /></LazyComponentErrorBoundary>,
      'today': <LazyComponentErrorBoundary><Today /></LazyComponentErrorBoundary>,
      'pillars': <LazyComponentErrorBoundary><Pillars /></LazyComponentErrorBoundary>,
      'areas': <LazyComponentErrorBoundary><Areas /></LazyComponentErrorBoundary>,
      'projects': <LazyComponentErrorBoundary><Projects {...sectionParams} /></LazyComponentErrorBoundary>,
      'project-templates': <LazyComponentErrorBoundary><ProjectTemplates /></LazyComponentErrorBoundary>,
      'tasks': <LazyComponentErrorBoundary><Tasks /></LazyComponentErrorBoundary>,
      'journal': <LazyComponentErrorBoundary><Journal /></LazyComponentErrorBoundary>,
      'feedback': <LazyComponentErrorBoundary><Feedback /></LazyComponentErrorBoundary>,
      'ai-coach': <LazyComponentErrorBoundary><AICoach /></LazyComponentErrorBoundary>,
      'profile': <LazyComponentErrorBoundary><Profile /></LazyComponentErrorBoundary>,
      'profile-page': <LazyComponentErrorBoundary><ProfilePage /></LazyComponentErrorBoundary>,
      'insights': <LazyComponentErrorBoundary><Insights /></LazyComponentErrorBoundary>,
      'settings': <LazyComponentErrorBoundary><Settings /></LazyComponentErrorBoundary>,
      'notification-settings': <LazyComponentErrorBoundary><NotificationSettings /></LazyComponentErrorBoundary>,
      'notifications': <LazyComponentErrorBoundary><NotificationCenter /></LazyComponentErrorBoundary>,
    };

    return sectionComponents[activeSection] || sectionComponents['dashboard'];
  };

  // ========================================
  // PASSWORD RESET FLOW
  // ========================================
  /**
   * Special handling for password reset pages.
   * Renders without the normal app layout.
   */
  if (isPasswordResetPage) {
    return (
      <div className="min-h-screen bg-[#0A0B0E] flex items-center justify-center">
        <PasswordReset />
      </div>
    );
  }

  // ========================================
  // GLOBAL ERROR HANDLING
  // ========================================
  /**
   * Set up global error handler for unhandled errors.
   * This catches errors that escape component boundaries.
   */
  useEffect(() => {
    globalErrorHandler.setup();
    return () => {
      globalErrorHandler.cleanup();
    };
  }, []);

  // ========================================
  // MAIN RENDER
  // ========================================
  /**
   * Application structure with nested providers:
   * 
   * 1. ErrorBoundary - Catches React errors
   * 2. GoogleOAuthProvider - Google login support
   * 3. QueryClientProvider - React Query data fetching
   * 4. AuthProvider - Authentication state
   * 5. DataProvider - Global data management
   * 6. NotificationProvider - Toast notifications
   * 7. DndProvider - Drag and drop support
   * 
   * The actual app content is rendered inside these providers
   * with proper authentication protection.
   */
  return (
    <ErrorBoundary>
      <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <DataProvider>
              <NotificationProvider>
                <DndProvider backend={HTML5Backend}>
                  <div className="min-h-screen bg-[#0A0B0E]">
                    <AppWrapper>
                      <ProtectedRoute>
                        <SimpleLayout 
                          activeSection={activeSection} 
                          setActiveSection={setActiveSection}
                          setSectionParams={setSectionParams}
                        >
                          <Suspense fallback={<LoadingSpinner />}>
                            {renderSection()}
                          </Suspense>
                        </SimpleLayout>
                      </ProtectedRoute>
                    </AppWrapper>
                    {/* Global toast notifications */}
                    <Toaster />
                  </div>
                </DndProvider>
              </NotificationProvider>
            </DataProvider>
          </AuthProvider>
          {/* React Query dev tools - only in development */}
          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} />
          )}
        </QueryClientProvider>
      </GoogleOAuthProvider>
    </ErrorBoundary>
  );
}

export default App;