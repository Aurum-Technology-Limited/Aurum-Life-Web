import React, { useState } from 'react';
import "./App.css";
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

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');

  const renderActiveSection = () => {
    const props = { onSectionChange: setActiveSection };
    
    switch (activeSection) {
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
      default:
        return <Dashboard {...props} />;
    }
  };

  return (
    <div className="App">
      <Layout 
        activeSection={activeSection} 
        onSectionChange={setActiveSection}
      >
        {renderActiveSection()}
      </Layout>
    </div>
  );
}

export default App;