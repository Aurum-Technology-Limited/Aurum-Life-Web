import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Dialog, DialogContent } from './ui/dialog';
import { 
  HomeIcon, 
  CalendarIcon, 
  LightningBoltIcon, 
  ViewGridIcon, 
  FolderIcon, 
  DocumentTextIcon, 
  ClipboardListIcon, 
  ChartBarIcon,
  SearchIcon,
  CogIcon,
  UserIcon,
  PlusIcon,
  XIcon,
  BeakerIcon,
  SparklesIcon,
  LocationMarkerIcon
} from '@heroicons/react/outline';

// Quick Win #3: Command Palette System for Power Users

const CommandPalette = ({ isOpen, onClose, onNavigate }) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const listRef = useRef(null);

  // Navigation commands
  const navigationCommands = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      description: 'Overview & daily planning hub',
      icon: HomeIcon,
      shortcut: '⌘1',
      keywords: ['home', 'overview', 'main'],
      category: 'Navigation'
    },
    {
      id: 'today',
      name: 'Today',
      description: 'Focus tasks & daily engagement',
      icon: CalendarIcon,
      shortcut: '⌘2',
      keywords: ['daily', 'tasks', 'focus'],
      category: 'Navigation'
    },
    {
      id: 'pillars',
      name: 'Pillars',
      description: 'Core life domains & priorities',
      icon: LightningBoltIcon,
      shortcut: '⌘3',
      keywords: ['domains', 'priorities', 'structure'],
      category: 'Navigation'
    },
    {
      id: 'areas',
      name: 'Areas',
      description: 'Focus categories within pillars',
      icon: ViewGridIcon,
      shortcut: '⌘4',
      keywords: ['categories', 'organization'],
      category: 'Navigation'
    },
    {
      id: 'projects',
      name: 'Projects',
      description: 'Initiatives & deliverables',
      icon: FolderIcon,
      shortcut: '⌘5',
      keywords: ['initiatives', 'work', 'deliverables'],
      category: 'Navigation'
    },
    {
      id: 'tasks',
      name: 'Tasks',
      description: 'Individual action items',
      icon: ClipboardListIcon,
      shortcut: '⌘T',
      keywords: ['todo', 'actions', 'items'],
      category: 'Navigation'
    },
    {
      id: 'journal',
      name: 'Journal',
      description: 'Personal reflection & notes',
      icon: DocumentTextIcon,
      shortcut: '⌘J',
      keywords: ['notes', 'reflection', 'writing'],
      category: 'Navigation'
    },
    {
      id: 'analytics',
      name: 'Analytics',
      description: 'Performance insights & data',
      icon: ChartBarIcon,
      shortcut: '⌘A',
      keywords: ['data', 'insights', 'performance', 'stats'],
      category: 'Navigation'
    }
  ];

  // AI commands
  const aiCommands = [
    {
      id: 'ai-insights',
      name: 'My AI Insights',
      description: 'Browse AI observations about you',
      icon: BeakerIcon,
      shortcut: '⌘I',
      keywords: ['ai', 'insights', 'observations', 'analysis'],
      category: 'AI Features'
    },
    {
      id: 'ai-actions',
      name: 'AI Quick Actions',
      description: 'Fast AI help & overview',
      icon: SparklesIcon,
      shortcut: '⌘Q',
      keywords: ['ai', 'quick', 'help', 'actions'],
      category: 'AI Features'
    },
    {
      id: 'goal-planner',
      name: 'Goal Planner',
      description: 'Plan & achieve goals with AI',
      icon: LocationMarkerIcon,
      shortcut: '⌘G',
      keywords: ['goals', 'planning', 'ai', 'objectives'],
      category: 'AI Features'
    }
  ];

  // Action commands
  const actionCommands = [
    {
      id: 'new-task',
      name: 'New Task',
      description: 'Create a new task',
      icon: PlusIcon,
      shortcut: '⌘N',
      keywords: ['create', 'add', 'new', 'task'],
      category: 'Actions',
      action: () => console.log('Create new task')
    },
    {
      id: 'new-project',
      name: 'New Project',
      description: 'Start a new project',
      icon: PlusIcon,
      keywords: ['create', 'add', 'new', 'project'],
      category: 'Actions',
      action: () => console.log('Create new project')
    },
    {
      id: 'new-journal',
      name: 'New Journal Entry',
      description: 'Write a new journal entry',
      icon: DocumentTextIcon,
      keywords: ['write', 'journal', 'entry', 'reflection'],
      category: 'Actions',
      action: () => console.log('Create new journal entry')
    },
    {
      id: 'search',
      name: 'Semantic Search',
      description: 'Search across all your content',
      icon: SearchIcon,
      shortcut: '⌘/',
      keywords: ['search', 'find', 'semantic', 'content'],
      category: 'Actions',
      action: () => console.log('Open semantic search')
    }
  ];

  // Settings commands
  const settingsCommands = [
    {
      id: 'settings',
      name: 'Settings',
      description: 'Application preferences',
      icon: CogIcon,
      keywords: ['settings', 'preferences', 'config'],
      category: 'Settings'
    },
    {
      id: 'profile',
      name: 'Profile',
      description: 'View and edit your profile',
      icon: UserIcon,
      keywords: ['profile', 'account', 'user'],
      category: 'Settings'
    }
  ];

  // Combine all commands
  const allCommands = [
    ...navigationCommands,
    ...aiCommands,
    ...actionCommands,
    ...settingsCommands
  ];

  // Filter commands based on query
  const filteredCommands = useMemo(() => {
    if (!query.trim()) return allCommands;

    const searchQuery = query.toLowerCase().trim();
    
    return allCommands.filter(command => {
      const searchableText = [
        command.name,
        command.description,
        command.category,
        ...(command.keywords || [])
      ].join(' ').toLowerCase();
      
      return searchableText.includes(searchQuery);
    });
  }, [query]);

  // Group commands by category
  const groupedCommands = useMemo(() => {
    const groups = {};
    filteredCommands.forEach(command => {
      const category = command.category || 'Other';
      if (!groups[category]) groups[category] = [];
      groups[category].push(command);
    });
    return groups;
  }, [filteredCommands]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => 
            Math.min(prev + 1, filteredCommands.length - 1)
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          e.preventDefault();
          if (filteredCommands[selectedIndex]) {
            handleCommandSelect(filteredCommands[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands, onClose]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex];
      if (selectedElement) {
        selectedElement.scrollIntoView({
          block: 'nearest',
          behavior: 'smooth'
        });
      }
    }
  }, [selectedIndex]);

  const handleCommandSelect = (command) => {
    if (command.action) {
      command.action();
    } else if (command.id) {
      onNavigate(command.id);
    }
    onClose();
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    setSelectedIndex(0);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl p-0 overflow-hidden bg-gray-900 border border-gray-700">
        <div className="command-palette">
          {/* Header */}
          <div className="flex items-center px-4 py-3 border-b border-gray-700">
            <SearchIcon className="h-5 w-5 text-gray-400 mr-3" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Type a command or search..."
              value={query}
              onChange={handleInputChange}
              className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none text-sm"
            />
            <button
              onClick={onClose}
              className="ml-3 text-gray-400 hover:text-white transition-colors"
            >
              <XIcon className="h-4 w-4" />
            </button>
          </div>

          {/* Results */}
          <div 
            ref={listRef}
            className="max-h-96 overflow-y-auto scrollbar-enhanced"
          >
            {Object.keys(groupedCommands).length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-400">
                <SearchIcon className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                <p className="text-sm">No commands found</p>
                <p className="text-xs mt-1">Try searching for something else</p>
              </div>
            ) : (
              Object.entries(groupedCommands).map(([category, commands]) => (
                <div key={category} className="py-2">
                  {/* Category Header */}
                  <div className="px-4 py-1">
                    <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                      {category}
                    </h3>
                  </div>

                  {/* Commands */}
                  {commands.map((command, index) => {
                    const globalIndex = filteredCommands.indexOf(command);
                    const isSelected = globalIndex === selectedIndex;

                    return (
                      <button
                        key={command.id}
                        onClick={() => handleCommandSelect(command)}
                        className={`w-full px-4 py-3 flex items-center text-left transition-all ${
                          isSelected
                            ? 'bg-yellow-400 text-black'
                            : 'text-gray-300 hover:bg-gray-800'
                        }`}
                      >
                        {/* Icon */}
                        <div className={`mr-3 ${isSelected ? 'text-black' : 'text-gray-400'}`}>
                          <command.icon className="h-5 w-5" />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className={`font-medium ${isSelected ? 'text-black' : 'text-white'}`}>
                            {command.name}
                          </div>
                          {command.description && (
                            <div className={`text-sm mt-0.5 ${
                              isSelected ? 'text-gray-700' : 'text-gray-400'
                            }`}>
                              {command.description}
                            </div>
                          )}
                        </div>

                        {/* Shortcut */}
                        {command.shortcut && (
                          <div className={`ml-3 text-xs px-2 py-1 rounded border ${
                            isSelected 
                              ? 'text-gray-700 border-gray-700 bg-gray-100'
                              : 'text-gray-400 border-gray-600 bg-gray-800'
                          }`}>
                            {command.shortcut}
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-gray-700 bg-gray-800">
            <div className="flex items-center justify-between text-xs text-gray-400">
              <div className="flex items-center space-x-4">
                <span className="flex items-center">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 border border-gray-600 rounded text-xs">
                    ↑↓
                  </kbd>
                  <span className="ml-1">navigate</span>
                </span>
                <span className="flex items-center">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 border border-gray-600 rounded text-xs">
                    ⏎
                  </kbd>
                  <span className="ml-1">select</span>
                </span>
                <span className="flex items-center">
                  <kbd className="px-1.5 py-0.5 bg-gray-700 border border-gray-600 rounded text-xs">
                    esc
                  </kbd>
                  <span className="ml-1">close</span>
                </span>
              </div>
              <div className="text-gray-500">
                {filteredCommands.length} commands
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CommandPalette;