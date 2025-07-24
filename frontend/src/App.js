import React, { useState, useEffect } from 'react';
import "./App.css";
import { AuthProvider } from './contexts/AuthContext';
import { DataProvider } from './contexts/DataContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { GoogleOAuthProvider } from '@react-oauth/google';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import Today from './components/Today';
import Pillars from './components/Pillars';
import Areas from './components/Areas';
import Projects from './components/Projects';
import ProjectTemplates from './components/ProjectTemplates';
import RecurringTasks from './components/RecurringTasks';
import Journal from './components/Journal';
import Tasks from './components/Tasks';
import Learning from './components/Learning';
import AICoach from './components/AICoach';
import Achievements from './components/Achievements';
import Profile from './components/Profile';
import Insights from './components/Insights';
import PasswordReset from './components/PasswordReset';

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [isPasswordResetPage, setIsPasswordResetPage] = useState(false);

  // Debug effect to track activeSection changes
  useEffect(() => {
    console.log('🔄 Active section updated to:', activeSection);
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
      case 'recurring-tasks':
        console.log('🔄 Rendering RecurringTasks component');
        return <RecurringTasks {...props} />;
      case 'journal':
        console.log('📖 Rendering Journal component');
        return <Journal {...props} />;
      case 'tasks':
        console.log('✅ Rendering Tasks component');
        return <Tasks {...props} />;
      case 'learning':
        console.log('📚 Rendering Learning component');
        return <Learning {...props} />;
      case 'ai-coach':
        console.log('🤖 Rendering AICoach component');
        return <AICoach {...props} />;
      case 'achievements':
        console.log('🏆 Rendering Achievements component');
        return <Achievements {...props} />;
      case 'profile':
        console.log('👤 Rendering Profile component');
        return <Profile {...props} />;
      case 'dashboard':
      default:
        console.log('🏠 Rendering Dashboard component');
        return <Dashboard {...props} />;
    }
  };

  // If on password reset page, show the PasswordReset component
  if (isPasswordResetPage) {
    return (
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
    );
  }

  return (
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
  );
}

export default App;