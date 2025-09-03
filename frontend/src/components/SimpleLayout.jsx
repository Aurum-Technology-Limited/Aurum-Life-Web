import React, { useState, useEffect } from 'react';
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
  BeakerIcon,
  AdjustmentsIcon,
  BellIcon,
  SearchIcon,
  XIcon,
  MenuIcon
} from '@heroicons/react/outline';
import { Brain, Zap, Target } from '@heroicons/react/solid';
import UserMenu from './UserMenu';
import { useAuth } from '../contexts/BackendAuthContext';
import { useSemanticSearch } from './SemanticSearch';
import CommandPalette from './CommandPalette';

const SimpleLayout = ({ children, activeSection, setActiveSection }) => {
  const { user } = useAuth();
  const { open: openSemanticSearch } = useSemanticSearch();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  
  // Command palette handlers
  const openCommandPalette = () => setCommandPaletteOpen(true);
  const closeCommandPalette = () => setCommandPaletteOpen(false);

  const navigation = [
    {
      name: 'Dashboard',
      section: 'dashboard',
      icon: HomeIcon,
      description: 'Overview & daily planning hub',
      shortcut: '⌘1'
    },
    {
      name: 'Today',
      section: 'today',
      icon: CalendarIcon,
      description: 'Focus tasks & daily engagement',
      shortcut: '⌘2'
    },
    {
      name: 'Pillars',
      section: 'pillars',
      icon: LightningBoltIcon,
      description: 'Core life domains & priorities',
      shortcut: '⌘3'
    },
    {
      name: 'Areas',
      section: 'areas',
      icon: ViewGridIcon,
      description: 'Focus categories within pillars',
      shortcut: '⌘4'
    },
    {
      name: 'Projects',
      section: 'projects',
      icon: FolderIcon,
      description: 'Initiatives & deliverables',
      shortcut: '⌘5'
    },
    {
      name: 'Tasks',
      section: 'tasks',
      icon: ClipboardListIcon,
      description: 'Individual action items',
      shortcut: '⌘T'
    },
    {
      name: 'Journal',
      section: 'journal',
      icon: DocumentTextIcon,
      description: 'Personal reflection & notes',
      shortcut: '⌘J'
    },
    {
      name: 'Analytics',
      section: 'analytics',
      icon: ChartBarIcon,
      description: 'Performance insights & data',
      shortcut: '⌘A'
    }
  ];

  const aiNavigation = [
    {
      name: 'My AI Insights',
      section: 'ai-insights',
      icon: Brain,
      description: 'Browse AI observations about you',
      shortcut: '⌘I'
    },
    {
      name: 'AI Quick Actions',
      section: 'ai-actions',
      icon: Zap,
      description: 'Fast AI help & overview',
      shortcut: '⌘Q'
    },
    {
      name: 'Goal Planner',
      section: 'goal-planner',
      icon: Target,
      description: 'Plan & achieve goals with AI',
      shortcut: '⌘G'
    }
  ];

  const secondaryNavigation = [
    {
      name: 'Feedback',
      section: 'feedback',
      icon: ChatIcon,
      description: 'Share suggestions & report issues'
    },
    {
      name: 'Settings',
      section: 'settings',
      icon: AdjustmentsIcon,
      description: 'Application preferences'
    },
    {
      name: 'Notifications',
      section: 'notifications',
      icon: BellIcon,
      description: 'View your notifications'
    }
  ];

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Skip if user is typing in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
        return;
      }

      const shortcuts = {
        '1': 'dashboard',
        '2': 'today',
        '3': 'pillars',
        '4': 'areas',
        '5': 'projects',
        't': 'tasks',
        'j': 'journal',
        'a': 'analytics',
        'i': 'ai-insights',
        'q': 'ai-actions',
        'g': 'goal-planner'
      };

      if ((e.metaKey || e.ctrlKey) && shortcuts[e.key.toLowerCase()]) {
        e.preventDefault();
        setActiveSection(shortcuts[e.key.toLowerCase()]);
      }

      // Open semantic search with Cmd+/
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        openSemanticSearch();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [setActiveSection, openSemanticSearch]);

  const isActive = (section) => activeSection === section;

  const NavigationGroup = ({ title, items, className = "" }) => (
    <div className={`space-y-1 ${className}`}>
      {title && (
        <div className="px-3 mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            {title}
          </h3>
        </div>
      )}
      {items.map((item) => {
        const active = isActive(item.section);
        return (
          <div key={item.section} className="relative group">
            <button
              onClick={() => setActiveSection(item.section)}
              className={`nav-item group flex items-center w-full px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                active
                  ? 'bg-gradient-to-r from-yellow-400 to-yellow-500 text-black shadow-lg'
                  : 'text-gray-300 hover:text-white hover:bg-gray-800'
              }`}
              title={sidebarCollapsed ? `${item.name} ${item.shortcut || ''}` : ''}
            >
              <item.icon
                className={`${sidebarCollapsed ? 'h-6 w-6' : 'h-5 w-5'} ${
                  active ? 'text-black' : 'text-gray-400 group-hover:text-gray-300'
                } ${sidebarCollapsed ? '' : 'mr-3'} transition-colors flex-shrink-0`}
                aria-hidden="true"
              />
              {!sidebarCollapsed && (
                <div className="flex flex-col items-start flex-1 min-w-0">
                  <div className="flex items-center justify-between w-full">
                    <span className="truncate">{item.name}</span>
                    {item.shortcut && (
                      <span className={`text-xs px-1.5 py-0.5 rounded border ml-2 ${
                        active 
                          ? 'text-gray-700 border-gray-400 bg-gray-100'
                          : 'text-gray-500 border-gray-600 bg-gray-800'
                      }`}>
                        {item.shortcut}
                      </span>
                    )}
                  </div>
                  {item.description && (
                    <span className={`text-xs font-normal mt-0.5 truncate w-full ${
                      active ? 'text-gray-700' : 'text-gray-400'
                    }`}>
                      {item.description}
                    </span>
                  )}
                </div>
              )}
            </button>
            
            {/* Enhanced Tooltip for collapsed sidebar */}
            {sidebarCollapsed && item.description && (
              <div className="absolute left-full ml-3 px-3 py-2 bg-gray-800 border border-gray-600 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-200 z-50 whitespace-nowrap shadow-xl">
                <div className="font-medium">{item.name}</div>
                <div className="text-gray-300 text-xs">{item.description}</div>
                {item.shortcut && (
                  <div className="text-gray-400 text-xs mt-1">{item.shortcut}</div>
                )}
                {/* Arrow */}
                <div className="absolute right-full top-1/2 transform -translate-y-1/2">
                  <div className="border-4 border-transparent border-r-gray-800"></div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="flex h-screen bg-[#0B0D14]">
      {/* Enhanced Sidebar */}
      <div className={`${
        sidebarCollapsed ? 'w-16' : 'w-80'
      } bg-gray-900 transition-all duration-300 ease-in-out flex flex-col border-r border-gray-700 shadow-xl`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          {!sidebarCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-sm">AL</span>
              </div>
              <div>
                <div className="text-xl font-bold text-white">Aurum Life</div>
                <div className="text-xs text-gray-400">Emotional OS</div>
              </div>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-gray-400 hover:text-white transition-colors p-1 rounded-md hover:bg-gray-800"
            title={sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {sidebarCollapsed ? (
              <MenuIcon className="h-5 w-5" />
            ) : (
              <XIcon className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Command Palette Button */}
        {!sidebarCollapsed && (
          <div className="px-4 py-3 border-b border-gray-700">
            <button
              onClick={openCommandPalette}
              className="w-full flex items-center px-3 py-2 text-sm text-gray-400 bg-gray-800 rounded-lg border border-gray-700 hover:bg-gray-750 hover:text-white transition-all"
            >
              <SearchIcon className="h-4 w-4 mr-3" />
              <span>Search commands...</span>
              <kbd className="ml-auto text-xs px-1.5 py-0.5 bg-gray-700 border border-gray-600 rounded">
                ⌘K
              </kbd>
            </button>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto scrollbar-enhanced">
          <NavigationGroup 
            title={!sidebarCollapsed ? "Core Workflow" : null}
            items={navigation} 
          />
          
          <NavigationGroup 
            title={!sidebarCollapsed ? "AI Features" : null}
            items={aiNavigation}
            className="pt-2 border-t border-gray-800"
          />
          
          <NavigationGroup 
            title={!sidebarCollapsed ? "Tools" : null}
            items={secondaryNavigation}
            className="pt-2 border-t border-gray-800"
          />
        </nav>

        {/* Enhanced Search Button */}
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={openSemanticSearch}
            className={`flex items-center w-full px-3 py-2.5 text-sm font-medium rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-all duration-200 shadow-md hover:shadow-lg ${
              sidebarCollapsed ? 'justify-center' : 'justify-start'
            }`}
            title={sidebarCollapsed ? 'Semantic Search (⌘/)' : ''}
          >
            <SearchIcon className={`h-5 w-5 ${sidebarCollapsed ? '' : 'mr-3'}`} />
            {!sidebarCollapsed && (
              <div className="flex items-center justify-between w-full">
                <span>Semantic Search</span>
                <kbd className="text-xs px-1.5 py-0.5 bg-purple-500 border border-purple-400 rounded">
                  ⌘/
                </kbd>
              </div>
            )}
          </button>
        </div>

        {/* Enhanced User Menu */}
        <div className="p-4 border-t border-gray-700">
          <UserMenu collapsed={sidebarCollapsed} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-[#0B0D14]">
          <div className="fade-in-up">
            {children}
          </div>
        </main>
      </div>

      {/* Command Palette */}
      <CommandPalette />
    </div>
  );
};

export default SimpleLayout;