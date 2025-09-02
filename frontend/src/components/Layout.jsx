import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {HomeIcon, CalendarIcon, LightningBoltIcon, ViewGridIcon, FolderIcon, DocumentTextIcon, ClipboardListIcon, ChatIcon, ChartBarIcon, BeakerIcon, AdjustmentsIcon, BellIcon, SearchIcon} from '@heroicons/react/outline';
import UserMenu from './UserMenu';
import { useAuth } from '../contexts/BackendAuthContext';
import { useSemanticSearch } from './SemanticSearch';

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { open: openSemanticSearch } = useSemanticSearch();
  
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Today', href: '/today', icon: CalendarIcon },
    { name: 'Pillars', href: '/pillars', icon: LightningBoltIcon },
    { name: 'Areas', href: '/areas', icon: ViewGridIcon },
    { name: 'Projects', href: '/projects', icon: FolderIcon },
    { name: 'Tasks', href: '/tasks', icon: ClipboardListIcon },
    { name: 'Templates', href: '/templates', icon: DocumentTextIcon },
    { name: 'Journal', href: '/journal', icon: DocumentTextIcon },
    { name: 'Insights', href: '/insights', icon: ChartBarIcon },
    { name: 'Feedback', href: '/feedback', icon: ChatIcon },
    { name: 'AI Coach', href: '/ai-coach', icon: BeakerIcon },
    { name: 'Notifications', href: '/notifications', icon: BellIcon },
  ];

  const isActive = (href) => {
    if (href === '/dashboard' && (location.pathname === '/' || location.pathname === '/dashboard')) {
      return true;
    }
    return location.pathname === href;
  };

  const handleNavClick = (href) => {
    navigate(href);
  };

  return (
    <div className="flex h-screen bg-[#0B0D14]">
      {/* Sidebar */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-gray-900 transition-all duration-300 ease-in-out flex flex-col border-r border-gray-700`}>
        {/* Logo and collapse button */}
        <div className="flex items-center justify-between p-4">
          {!sidebarCollapsed && (
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
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <AdjustmentsIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <button
                key={item.name}
                onClick={() => handleNavClick(item.href)}
                className={`group flex items-center w-full px-2 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                  active
                    ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-black'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
                title={sidebarCollapsed ? item.name : ''}
              >
                <item.icon
                  className={`${sidebarCollapsed ? 'h-6 w-6' : 'h-5 w-5'} ${
                    active ? 'text-black' : 'text-gray-400 group-hover:text-gray-300'
                  } ${sidebarCollapsed ? '' : 'mr-3'} transition-colors`}
                  aria-hidden="true"
                />
                {!sidebarCollapsed && item.name}
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
              {navigation.find(item => isActive(item.href))?.name || 'Aurum Life'}
            </h1>
            {user && (
              <div className="flex items-center space-x-4">
                <button
                  onClick={openSemanticSearch}
                  className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                  title="Semantic Search (Ctrl+Shift+F)"
                >
                  <SearchIcon className="h-5 w-5" />
                </button>
                <UserMenu />
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

export default Layout;