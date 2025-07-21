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
          {/* MINIMAL TEST - no Layout component */}
          <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
            <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
              MINIMAL TEST - No Layout Component
            </h1>
            <p className="text-white mt-4">Current activeSection: <strong>{activeSection}</strong></p>
            
            <div className="flex space-x-4 mt-8">
              <button 
                onClick={() => handleSectionChange('today')}
                className="px-4 py-2 bg-blue-600 text-white rounded"
              >
                Set to Today
              </button>
              <button 
                onClick={() => handleSectionChange('insights')}
                className="px-4 py-2 bg-green-600 text-white rounded"
              >
                Set to Insights
              </button>
              <button 
                onClick={() => handleSectionChange('dashboard')}
                className="px-4 py-2 bg-red-600 text-white rounded"
              >
                Set to Dashboard
              </button>
            </div>
          </div>
        </ProtectedRoute>
      </div>
    </AuthProvider>
  );
}

export default App;