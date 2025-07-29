import React, { memo } from 'react';
import { 
  HomeIcon, 
  CalendarIcon, 
  LightningBoltIcon, 
  ViewGridIcon, 
  FolderIcon, 
  DocumentTextIcon, 
  ClipboardListIcon, 
  ChatIcon, 
  ChartBarIcon, 
  CogIcon, 
  BadgeCheckIcon, 
  UserIcon,
  BeakerIcon,
  AdjustmentsIcon,
  BellIcon
} from '@heroicons/react/outline';
import UserMenu from './UserMenu';
import { useAuth } from '../contexts/BackendAuthContext';

const SimpleLayout = memo(({ children, activeSection, setActiveSection }) => {
  const { user } = useAuth();

  const navigation = [
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
    { name: 'Achievements', key: 'achievements', icon: BadgeCheckIcon },
    { name: 'Notifications', key: 'notifications', icon: BellIcon },
  ];

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
            <div className="bg-yellow-500 text-black px-2 py-1 rounded font-bold">AL</div>
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

        {/* User menu */}
        <div className="p-4 border-t border-gray-700">
          <UserMenu />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="bg-gray-900 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-white">
              {navigation.find(item => isActive(item.key))?.name || 'Aurum Life'}
            </h1>
            {user && (
              <div className="flex items-center space-x-4">
                <div className="text-gray-300 text-sm">
                  Level {user.level || 1} • {user.total_points || 0} pts
                </div>
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
};

export default SimpleLayout;