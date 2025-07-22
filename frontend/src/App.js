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
        console.log('📅 Rendering Today component');
        return <Today {...props} />;
      case 'insights':
        console.log('📊 Rendering Insights component');
        return <Insights {...props} />;
      case 'areas':
        console.log('🗂️ Rendering Areas component');
        return <Areas {...props} />;
      case 'projects':
        console.log('📁 Rendering Projects component');
        return <Projects {...props} />;
      case 'habits':
        console.log('🎯 Rendering Habits component');
        return <Habits {...props} />;
      case 'journal':
        console.log('📖 Rendering Journal component');
        return <Journal {...props} />;
      case 'mindfulness':
        console.log('🧘 Rendering Mindfulness component');
        return <Mindfulness {...props} />;
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