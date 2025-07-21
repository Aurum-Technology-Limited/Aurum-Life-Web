import React, { useState } from 'react';
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

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');

  // Debug logging
  console.log('🔍 Current activeSection:', activeSection);

  const handleSectionChange = (newSection) => {
    console.log('🔄 Changing section from', activeSection, 'to', newSection);
    setActiveSection(newSection);
  };

  const renderActiveSection = () => {
    const props = { onSectionChange: handleSectionChange };
    
    console.log('🎯 Rendering section:', activeSection);
    
    // Temporary simple test - bypass API-dependent components
    if (activeSection === 'insights') {
      return (
        <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
          <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
            🎉 INSIGHTS COMPONENT LOADED SUCCESSFULLY!
          </h1>
          <p className="text-gray-400 mt-4">This proves component routing is working.</p>
        </div>
      );
    }
    
    if (activeSection === 'today') {
      return (
        <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
          <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
            🎉 TODAY COMPONENT LOADED SUCCESSFULLY!
          </h1>
          <p className="text-gray-400 mt-4">This proves component routing is working.</p>
        </div>
      );
    }
    
    switch (activeSection) {
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
      default:
        return <Dashboard {...props} />;
    }
  };

  return (
    <AuthProvider>
      <div className="App">
        <ProtectedRoute>
          <Layout 
            activeSection={activeSection} 
            onSectionChange={handleSectionChange}
          >
            {/* DIRECT TEST - bypass renderActiveSection entirely */}
            {activeSection === 'insights' ? (
              <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
                <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                  🎉 DIRECT INSIGHTS RENDER SUCCESS!
                </h1>
                <p className="text-gray-400 mt-4">activeSection = {activeSection}</p>
                <p className="text-gray-400 mt-2">This proves the issue is in renderActiveSection function!</p>
              </div>
            ) : activeSection === 'today' ? (
              <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
                <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                  🎉 DIRECT TODAY RENDER SUCCESS!  
                </h1>
                <p className="text-gray-400 mt-4">activeSection = {activeSection}</p>
              </div>
            ) : (
              renderActiveSection()
            )}
          </Layout>
        </ProtectedRoute>
      </div>
    </AuthProvider>
  );
}

export default App;