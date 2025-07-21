import React, { useState, useEffect } from 'react';
import "./App.css";
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import Today from './components/Today';
import Areas from './components/Areas';
import Projects from './components/Projects';
import Habits from './components/Habits';
import Journal from './components/Journal';
import Mindfulness from './components/Mindfulness';
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
        return <Today {...props} />;
      case 'insights':
        return <Insights {...props} />;
      case 'areas':
        return <Areas {...props} />;
      case 'projects':
        return <Projects {...props} />;
      case 'habits':
        return <Habits {...props} />;
      case 'journal':
        return <Journal {...props} />;
      case 'mindfulness':
        return <Mindfulness {...props} />;
      case 'tasks':
        return <Tasks {...props} />;
      case 'learning':
        return <Learning {...props} />;
      case 'ai-coach':
        return <AICoach {...props} />;
      case 'achievements':
        return <Achievements {...props} />;
      case 'profile':
        return <Profile {...props} />;
      case 'dashboard':
      default:
        return <Dashboard {...props} />;
    }
  };

  // If on password reset page, show the PasswordReset component
  if (isPasswordResetPage) {
    return (
      <AuthProvider>
        <div className="App">
          <PasswordReset />
        </div>
      </AuthProvider>
    );
  }

  return (
    <AuthProvider>
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
    </AuthProvider>
  );
}

export default App;