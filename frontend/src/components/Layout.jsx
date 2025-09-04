import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {HomeIcon, CalendarIcon, LightningBoltIcon, ViewGridIcon, FolderIcon, DocumentTextIcon, ClipboardListIcon, ChatIcon, ChartBarIcon, BeakerIcon, AdjustmentsIcon, BellIcon, SearchIcon, Brain, Zap, Target} from '@heroicons/react/outline';
import UserMenu from './UserMenu';
import { useAuth } from '../contexts/BackendAuthContext';
import { useSemanticSearch } from './SemanticSearch';
import { CDNImage } from './ui/CDNImage';

const Layout = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { open: openSemanticSearch } = useSemanticSearch();
  
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const navigation = [
    { 
      name: 'Dashboard', 
      href: '/dashboard', 
      icon: HomeIcon, 
      description: 'Overview & daily planning hub',
      purpose: 'main_entry'
    },
    { 
      name: 'Today', 
      href: '/today', 
      icon: CalendarIcon, 
      description: 'Focus tasks & daily engagement',
      purpose: 'daily_productivity'
    },
    { 
      name: 'Pillars', 
      href: '/pillars', 
      icon: LightningBoltIcon, 
      description: 'Core life domains & priorities',
      purpose: 'strategic_structure'
    },
    { 
      name: 'Areas', 
      href: '/areas', 
      icon: ViewGridIcon, 
      description: 'Focus categories within pillars',
      purpose: 'strategic_structure'
    },
    { 
      name: 'Projects', 
      href: '/projects', 
      icon: FolderIcon, 
      description: 'Initiatives & deliverables',
      purpose: 'tactical_execution'
    },
    { 
      name: 'Tasks', 
      href: '/tasks', 
      icon: ClipboardListIcon, 
      description: 'Individual action items',
      purpose: 'tactical_execution'
    },
    { 
      name: 'Journal', 
      href: '/journal', 
      icon: DocumentTextIcon, 
      description: 'Personal reflection & notes',
      purpose: 'self_reflection'
    },
    { 
      name: 'Intelligence Hub', 
      href: '/insights', 
      icon: ChartBarIcon, 
      description: 'Analytics & AI insights dashboard',
      purpose: 'intelligence_analysis'
    },
    { 
      name: 'Feedback', 
      href: '/feedback', 
      icon: ChatIcon, 
      description: 'Share suggestions & report issues',
      purpose: 'system_improvement'
    },
    { name: 'My AI Insights', href: '/ai-insights', icon: Brain, description: 'Browse AI observations about you' },
    { name: 'AI Quick Actions', href: '/ai-actions', icon: Zap, description: 'Fast AI help & overview' },
    { name: 'Goal Planner', href: '/goal-planner', icon: Target, description: 'Plan & achieve goals with AI' },
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
              <CDNImage
                bucket="assets"
                path="logos/aurum-brain-logo.svg"
                alt="Aurum Life Logo"
                className="w-8 h-8 object-contain"
                size="thumbnail"
                priority={true}
                placeholder="/aurum-brain-logo.svg"
              />
              <div 
                className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg items-center justify-center text-black font-bold text-sm hidden"
                style={{ display: 'none' }}
              >
                AL
              </div>
            </div>
              <span className="text-xl font-bold text-white">Aurum Life</span>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <div key={item.name} className="relative group">
                <button
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
                  {!sidebarCollapsed && (
                    <div className="flex flex-col items-start">
                      <span>{item.name}</span>
                      {item.description && (
                        <span className="text-xs text-gray-400 font-normal mt-0.5">
                          {item.description}
                        </span>
                      )}
                    </div>
                  )}
                </button>
                
                {/* Tooltip for collapsed sidebar */}
                {sidebarCollapsed && item.description && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap">
                    <div className="font-medium">{item.name}</div>
                    <div className="text-gray-400">{item.description}</div>
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        {/* Search button */}
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={openSemanticSearch}
            className={`flex items-center w-full px-3 py-2 text-sm font-medium rounded-md bg-purple-600 hover:bg-purple-700 text-white transition-colors ${
              sidebarCollapsed ? 'justify-center' : 'justify-start'
            }`}
            title={sidebarCollapsed ? 'Semantic Search' : ''}
          >
            <SearchIcon className={`h-5 w-5 ${sidebarCollapsed ? '' : 'mr-3'}`} />
            {!sidebarCollapsed && 'Semantic Search'}
          </button>
        </div>

        {/* User menu */}
        <div className="p-4 border-t border-gray-700">
          <UserMenu collapsed={sidebarCollapsed} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;