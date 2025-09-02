import React, { useMemo, memo } from 'react';
import {HomeIcon, CalendarIcon, LightningBoltIcon, ViewGridIcon, FolderIcon, DocumentTextIcon, ClipboardListIcon, ChatIcon, ChartBarIcon, BeakerIcon, BellIcon, SearchIcon} from '@heroicons/react/outline';
import { Brain, Zap, Target } from 'lucide-react';
import UserMenu from './UserMenu';
import { useAuth } from '../contexts/BackendAuthContext';
import { useSemanticSearch } from './SemanticSearch';

const SimpleLayout = memo(({ children, activeSection, setActiveSection }) => {
  const { user } = useAuth();
  const { open: openSemanticSearch } = useSemanticSearch();

  const navigation = useMemo(() => [
    { 
      name: 'Dashboard', 
      key: 'dashboard', 
      icon: HomeIcon, 
      description: 'Overview & daily planning hub',
      purpose: 'main_entry'
    },
    { 
      name: 'Today', 
      key: 'today', 
      icon: CalendarIcon, 
      description: 'Focus tasks & daily engagement',
      purpose: 'daily_productivity'
    },
    { 
      name: 'Pillars', 
      key: 'pillars', 
      icon: LightningBoltIcon, 
      description: 'Core life domains & priorities',
      purpose: 'strategic_structure'
    },
    { 
      name: 'Areas', 
      key: 'areas', 
      icon: ViewGridIcon, 
      description: 'Focus categories within pillars',
      purpose: 'strategic_structure'
    },
    { 
      name: 'Projects', 
      key: 'projects', 
      icon: FolderIcon, 
      description: 'Initiatives & deliverables',
      purpose: 'tactical_execution'
    },
    { 
      name: 'Tasks', 
      key: 'tasks', 
      icon: ClipboardListIcon, 
      description: 'Individual action items',
      purpose: 'tactical_execution'
    },
    { 
      name: 'Journal', 
      key: 'journal', 
      icon: DocumentTextIcon, 
      description: 'Personal reflection & notes',
      purpose: 'self_reflection'
    },
    { 
      name: 'Insights', 
      key: 'insights', 
      icon: ChartBarIcon, 
      description: 'Analytics & alignment tracking',
      purpose: 'performance_analysis'
    },
    { 
      name: 'My AI Insights', 
      key: 'ai-insights', 
      icon: Brain, 
      description: 'Browse AI observations about you',
      whenToUse: 'See what AI has learned from your productivity patterns',
      purpose: 'ai_intelligence'
    },
    { 
      name: 'Feedback', 
      key: 'feedback', 
      icon: ChatIcon, 
      description: 'Share suggestions & report issues',
      purpose: 'system_improvement'
    },
    { 
      name: 'AI Quick Actions', 
      key: 'ai-actions', 
      icon: Zap, 
      description: 'Fast AI help & overview',
      whenToUse: 'Quick AI assistance or check your AI usage',
      purpose: 'ai_productivity'
    },
    { 
      name: 'Goal Planner', 
      key: 'goal-planner', 
      icon: Target, 
      description: 'Plan & achieve goals with AI',
      whenToUse: 'Strategic planning, goal breakdown, overcome obstacles',
      purpose: 'ai_strategy'
    },
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

  // Robust image fallback handler (prevents errors if logo asset is missing)
  const handleLogoError = (e) => {
    try {
      if (!e || !e.target) return;
      const imgEl = e.target;
      // Hide broken image element
      imgEl.style.display = 'none';
      // Prefer an explicitly marked fallback sibling for resilience
      const fallback = imgEl.parentElement?.querySelector('[data-fallback-logo]');
      if (fallback) {
        fallback.style.display = 'flex';
        return;
      }
      // Secondary fallback logic
      const parentEl = imgEl.parentElement;
      if (parentEl) {
        const fallbackElement = parentEl.querySelector('.logo-fallback');
        if (fallbackElement) {
          fallbackElement.style.display = 'flex';
        } else {
          console.warn('No fallback element found for logo');
        }
      }
    } catch (error) {
      console.warn('Error in logo fallback handler:', error);
    }
  };

  return (
    <div className="flex h-screen bg-[#0B0D14]">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 flex flex-col border-r border-gray-700">
        {/* Logo */}
        <div className="flex items-center space-x-2 p-4">
          <div className="w-8 h-8 flex items-center justify-center">
            <img 
              src="/aurum-brain-logo.svg" 
              alt="Aurum Life Logo" 
              className="w-8 h-8 object-contain"
              onError={handleLogoError}
            />
            <div 
              data-fallback-logo
              className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-lg items-center justify-center text-black font-bold text-sm logo-fallback"
              style={{ display: 'none' }}
            >
              AL
            </div>
          </div>
          <span className="text-xl font-bold text-white">Aurum Life</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-2 py-4 space-y-2 overflow-y-auto">
          {navigation.map((item) => {
            const active = isActive(item.key);
            const IconComponent = item.icon;
            
            return (
              <div key={item.key} className="relative">
                <button
                  onClick={() => handleNavClick(item.key)}
                  className={`group flex items-start w-full px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                    active
                      ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-black shadow-lg'
                      : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
                  }`}
                >
                  <IconComponent
                    className={`h-5 w-5 mt-0.5 mr-3 flex-shrink-0 ${
                      active ? 'text-black' : 'text-gray-400 group-hover:text-gray-300'
                    } transition-colors`}
                    aria-hidden="true"
                  />
                  <div className="flex flex-col items-start text-left min-w-0 flex-1">
                    <span className="font-medium truncate w-full">{item.name}</span>
                    {item.description && (
                      <span className={`text-xs mt-1 font-normal leading-tight ${
                        active ? 'text-black/70' : 'text-gray-500 group-hover:text-gray-400'
                      }`}>
                        {item.description}
                      </span>
                    )}
                  </div>
                </button>
              </div>
            );
          })}
        </nav>

        {/* AI Section Decision Helper (when hovering over AI items) */}
        <div className="px-4 py-3 border-t border-gray-700">
          <div className="bg-gray-800/50 rounded-lg p-3 text-xs text-gray-400">
            <div className="font-medium text-gray-300 mb-2">🤔 Choose Your Tool:</div>
            <div className="space-y-1">
              <div>📊 <span className="text-purple-300">My AI Insights</span> - Review past analysis</div>
              <div>⚡ <span className="text-yellow-300">AI Quick Actions</span> - Fast AI help</div>
              <div>🎯 <span className="text-green-300">Goal Planner</span> - Strategic coaching</div>
            </div>
          </div>
        </div>

        {/* Screen Grouping Guide */}
        <div className="px-4 py-3 border-t border-gray-700">
          <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg p-3 text-xs">
            <div className="font-medium text-blue-300 mb-2">📱 Quick Guide:</div>
            <div className="space-y-1 text-gray-400">
              <div><span className="text-blue-300">📊 Structure:</span> Pillars → Areas → Projects → Tasks</div>
              <div><span className="text-green-300">🎯 Daily:</span> Today, Journal for daily work</div>
              <div><span className="text-purple-300">🤖 AI:</span> Quick Actions, Insights, Goal Planner</div>
              <div><span className="text-yellow-300">📈 Analysis:</span> Insights for performance tracking</div>
            </div>
          </div>
        </div>

        {/* Search button */}
        <div className="px-4 pb-2">
          <button
            onClick={openSemanticSearch}
            className="flex items-center w-full px-3 py-2 text-sm font-medium rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-colors"
          >
            <SearchIcon className="h-5 w-5 mr-3" />
            Semantic Search
          </button>
        </div>

        {/* User menu */}
        <div className="p-4 border-t border-gray-700">
          <UserMenu onSectionChange={setActiveSection} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">{currentPageName}</h1>
            {user && (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-400">
                  Welcome, {user.first_name || user.username || 'User'}
                </span>
              </div>
            )}
          </div>
        </header>
        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
});

SimpleLayout.displayName = 'SimpleLayout';

export default SimpleLayout;