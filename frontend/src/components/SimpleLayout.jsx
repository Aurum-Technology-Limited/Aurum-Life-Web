import React, { memo, useMemo } from 'react';
import {HomeIcon, CalendarIcon, LightningBoltIcon, ViewGridIcon, FolderIcon, DocumentTextIcon, ClipboardListIcon, ChatIcon, ChartBarIcon, BeakerIcon, BellIcon} from '@heroicons/react/outline';
import UserMenu from './UserMenu';
import { useAuth } from '../contexts/BackendAuthContext';

const SimpleLayout = memo(({ children, activeSection, setActiveSection }) => {
  const { user } = useAuth();

  const navigation = useMemo(() => [
    { name: 'Dashboard', key: 'dashboard', icon: HomeIcon },
    { name: 'Today', key: 'today', icon: CalendarIcon },
    { name: 'Pillars', key: 'pillars', icon: LightningBoltIcon },
    { name: 'Areas', key: 'areas', icon: ViewGridIcon },
    { name: 'Projects', key: 'projects', icon: FolderIcon },
    { name: 'Tasks', key: 'tasks', icon: ClipboardListIcon },
    { name: 'Templates', key: 'project-templates', icon: DocumentTextIcon },
    { name: 'Journal', key: 'journal', icon: DocumentTextIcon },
    { name: 'Insights', key: 'insights', icon: ChartBarIcon },
    { name: 'Feedback', key: 'feedback', icon: ChatIcon },
    { name: 'AI Coach', key: 'ai-coach', icon: BeakerIcon },
  ], []);

  const currentPageName = useMemo(() => {
    return navigation.find(item => activeSection === item.key)?.name || 'Aurum Life';
  }, [navigation, activeSection]);

  const isActive = (key) => {
    return activeSection === key;
  };

  const handleNavClick = (key) => {
    setActiveSection(key);
  };

  return (
    <div className="flex h-screen bg-[#0B0D14]">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 transition-all duration-300 ease-in-out flex flex-col border-r border-gray-700">
        {/* Logo */}
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 flex items-center justify-center">
              <img 
                src="/aurum-brain-logo.svg" 
                alt="Aurum Life Logo" 
                className="w-8 h-8 object-contain"
                onError={(e) => {
                  // Fallback to text logo if image fails to load
                  e.target.style.display = 'none';
                  e.target.nextElementSibling.style.display = 'flex';
                }}
              />
              <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center" style={{display: 'none'}}>
                <span className="text-black font-bold text-sm">AL</span>
              </div>
            </div>
            <span className="text-white font-semibold">Aurum Life</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const active = isActive(item.key);
            return (
              <button
                key={item.key}
                onClick={() => handleNavClick(item.key)}
                className={`group flex items-center w-full px-2 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  active
                    ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-black'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <item.icon
                  className={`h-5 w-5 ${
                    active ? 'text-black' : 'text-gray-400 group-hover:text-gray-300'
                  } mr-3 transition-colors`}
                  aria-hidden="true"
                />
                {item.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="bg-gray-900 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-white">
              {currentPageName}
            </h1>
            {user && (
              <div className="flex items-center space-x-4">
                <UserMenu onSectionChange={setActiveSection} />
              </div>
            )}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-[#0B0D14] p-6">
          {children}
        </main>
      </div>
    </div>
  );
});

SimpleLayout.displayName = 'SimpleLayout';

export default SimpleLayout;