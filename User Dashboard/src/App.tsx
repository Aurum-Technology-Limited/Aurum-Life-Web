import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { TodaySection } from './components/TodaySection';
import { PillarsSection } from './components/PillarsSection';
import { AreasSection } from './components/AreasSection';
import { TasksSection } from './components/TasksSection';
import { AdvancedAIInsights } from './components/dashboard/AdvancedAIInsights';
import { StrategicProjectAssessment } from './components/dashboard/StrategicProjectAssessment';

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'today':
        return <TodaySection />;
      case 'pillars':
        return <PillarsSection />;
      case 'areas':
        return <AreasSection />;
      case 'projects':
        return <StrategicProjectAssessment />;
      case 'tasks':
        return <TasksSection />;
      case 'journal':
        return <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Journal</h2>
          <p className="text-muted-foreground">Reflection and strategic thinking workspace.</p>
        </div>;
      case 'insights':
        return <AdvancedAIInsights />;
      case 'quick':
        return <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Quick Actions</h2>
          <p className="text-muted-foreground">Rapid task creation and strategic operations.</p>
        </div>;
      case 'goals':
        return <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Goal Planner</h2>
          <p className="text-muted-foreground">Strategic goal setting and achievement tracking.</p>
        </div>;
      case 'analytics':
        return <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Analytics</h2>
          <p className="text-muted-foreground">Deep insights into your productivity and strategic alignment patterns.</p>
        </div>;
      case 'feedback':
        return <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Feedback</h2>
          <p className="text-muted-foreground">Share your experience and help improve Aurum Life.</p>
        </div>;
      case 'settings':
        return <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Settings</h2>
          <p className="text-muted-foreground">Configure your personal operating system preferences.</p>
        </div>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen flex" style={{backgroundColor: '#0B0D14', color: 'white'}}>
      <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />
      
      <div className="flex-1 flex flex-col">
        <Header />
        
        <main className="px-4 lg:px-6 py-6">
          <div className="max-w-[1400px] mx-auto space-y-8">
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
            {renderActiveSection()}
          </div>
        </main>
      </div>
    </div>
  );
}