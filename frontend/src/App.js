import React, { useState, useEffect } from 'react';
import "./App.css";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './contexts/AuthContext';
import { DataProvider } from './contexts/DataContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { GoogleOAuthProvider } from '@react-oauth/google';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import OptimizedDashboard from './components/OptimizedDashboard';
import Today from './components/Today';
import Pillars from './components/Pillars';
import Areas from './components/Areas';
import Projects from './components/Projects';
import ProjectTemplates from './components/ProjectTemplates';
import Journal from './components/Journal';
import Tasks from './components/Tasks';
import Feedback from './components/Feedback';
import AICoach from './components/AICoach';
import globalErrorHandler from './utils/globalErrorHandler'; // Import global error handler
import Achievements from './components/Achievements';
import Profile from './components/Profile';
import Insights from './components/Insights';
import PasswordReset from './components/PasswordReset';
import NotificationSettings from './components/NotificationSettings';
import NotificationCenter from './components/NotificationCenter';
import ErrorBoundary from './components/ErrorBoundary';

// Import performance test for debugging
import './services/performanceTest';

// Create TanStack Query client with optimized configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes - data stays fresh
      gcTime: 10 * 60 * 1000, // 10 minutes - cache time (renamed from cacheTime in v5)
      retry: 1, // Only retry once on failure
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
      refetchOnMount: true, // Refetch when component mounts
      refetchOnReconnect: true, // Refetch when reconnecting to internet
    },
    mutations: {
      retry: 1,
    },
  },
});

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [isPasswordResetPage, setIsPasswordResetPage] = useState(false);

  // Debug effect to track activeSection changes
  useEffect(() => {
    console.log('🔄 Active section updated to:', activeSection);
  }, [activeSection]);

  // Update document title based on active section
  useEffect(() => {
    const sectionTitles = {
      'dashboard': 'Dashboard',
      'today': 'Today',
      'pillars': 'Pillars',
      'areas': 'Areas', 
      'projects': 'Projects',
      'project-templates': 'Project Templates',
      'tasks': 'Tasks',
      'journal': 'Journal',
      'feedback': 'Feedback & Support',
      'ai-coach': 'AI Coach',
      'achievements': 'Achievements',
      'profile': 'Profile',
      'insights': 'Insights',
      'notification-settings': 'Notifications',
      'notifications': 'Notification Center'
    };

    const sectionTitle = sectionTitles[activeSection] || 'Dashboard';
    document.title = `${sectionTitle} | Aurum Life`;
  }, [activeSection]);

  // Check if we're on password reset page
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const pathname = window.location.pathname;
    
    if (token && (pathname === '/reset-password' || pathname === '/')) {
      setIsPasswordResetPage(true);
    } else {
      setIsPasswordResetPage(false);
    }
  }, []);

  const handleSectionChange = (newSection) => {
    console.log('🔄 Navigation: Changing section from', activeSection, 'to', newSection);
    setActiveSection(newSection);
  };

  const renderActiveSection = () => {
    const props = { onSectionChange: handleSectionChange };
    
    console.log('🎯 Rendering active section:', activeSection);
    
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
        return <Journal {...props} />;
      case 'tasks':
        console.log('✅ Rendering Tasks component');
        return <Tasks {...props} />;
      case 'feedback':
        console.log('💬 Rendering Feedback component');
        return <Feedback {...props} />;
      case 'ai-coach':
        console.log('🤖 Rendering AICoach component');
        return <AICoach {...props} />;
      case 'achievements':
        console.log('🏆 Rendering Achievements component');
        return <Achievements {...props} />;
      case 'notification-settings':
        console.log('🔔 Rendering NotificationSettings component');
        return <NotificationSettings {...props} />;
      case 'notifications':
        console.log('📋 Rendering NotificationCenter component');
        return <NotificationCenter {...props} />;
      case 'profile':
        console.log('👤 Rendering Profile component');
        return <Profile {...props} />;
      case 'dashboard':
      default:
        console.log('🏠 Rendering Optimized Dashboard component');
        return <OptimizedDashboard {...props} />;
    }
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
                  <ProtectedRoute>
                    <Layout 
                      activeSection={activeSection} 
                      onSectionChange={handleSectionChange}
                    >
                      {renderActiveSection()}
                    </Layout>
                  </ProtectedRoute>
                  </div>
                </DndProvider>
              </NotificationProvider>
            </DataProvider>
          </AuthProvider>
        </GoogleOAuthProvider>
        {/* TanStack Query DevTools - only in development */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;