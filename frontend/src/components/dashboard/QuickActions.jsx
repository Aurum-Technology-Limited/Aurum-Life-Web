import React from 'react';
import { Plus, Target, Calendar, FileText, Zap, Settings } from 'lucide-react';

/**
 * Quick Actions component for rapid task creation and strategic operations
 * Converted from TypeScript to JavaScript
 */
const QuickActions = () => {
  const actions = [
    {
      id: 1,
      title: 'Add Task',
      description: 'Create a new task',
      icon: Plus,
      color: '#10B981',
      shortcut: 'T'
    },
    {
      id: 2,
      title: 'Set Goal',
      description: 'Define a new goal',
      icon: Target,
      color: '#F4D03F',
      shortcut: 'G'
    },
    {
      id: 3,
      title: 'Schedule Focus',
      description: 'Block time for deep work',
      icon: Calendar,
      color: '#3B82F6',
      shortcut: 'F'
    },
    {
      id: 4,
      title: 'Journal Entry',
      description: 'Record thoughts and insights',
      icon: FileText,
      color: '#8B5CF6',
      shortcut: 'J'
    },
    {
      id: 5,
      title: 'AI Insight',
      description: 'Get AI recommendations',
      icon: Zap,
      color: '#EF4444',
      shortcut: 'I'
    },
    {
      id: 6,
      title: 'Settings',
      description: 'Configure preferences',
      icon: Settings,
      color: '#6B7280',
      shortcut: 'S'
    }
  ];

  return (
    <div 
      className="rounded-2xl border p-6" 
      style={{
        background: 'rgba(26,29,41,0.4)', 
        backdropFilter: 'blur(12px)', 
        borderColor: 'rgba(244,208,63,0.2)'
      }}
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold">Quick Actions</h3>
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5" style={{color: '#F4D03F'}} />
          <span className="text-sm" style={{color: '#B8BCC8'}}>Press / for more</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              className="p-4 rounded-lg border hover:opacity-90 transition group"
              style={{
                borderColor: 'rgba(244,208,63,0.15)', 
                background: 'rgba(11,13,20,0.35)'
              }}
            >
              <div className="flex flex-col items-center gap-2">
                <div 
                  className="w-10 h-10 rounded-lg flex items-center justify-center" 
                  style={{
                    background: `${action.color}20`,
                    border: `1px solid ${action.color}40`
                  }}
                >
                  <Icon className="w-5 h-5" style={{color: action.color}} />
                </div>
                <div className="text-center">
                  <div className="text-xs font-medium mb-1">{action.title}</div>
                  <div className="text-[10px]" style={{color: '#B8BCC8'}}>
                    {action.description}
                  </div>
                </div>
                <div 
                  className="text-[10px] px-2 py-1 rounded border" 
                  style={{
                    borderColor: 'rgba(244,208,63,0.25)',
                    color: '#F4D03F'
                  }}
                >
                  {action.shortcut}
                </div>
              </div>
            </button>
          );
        })}
      </div>
      
      <div className="mt-6 pt-4 border-t" style={{borderColor: 'rgba(244,208,63,0.1)'}}>
        <div className="flex items-center justify-between">
          <span className="text-sm" style={{color: '#B8BCC8'}}>Keyboard shortcuts available</span>
          <button 
            className="text-sm font-medium px-3 py-1 rounded border hover:opacity-90" 
            style={{
              borderColor: 'rgba(244,208,63,0.25)', 
              color: '#F4D03F'
            }}
          >
            View All Shortcuts
          </button>
        </div>
      </div>
    </div>
  );
};

export { QuickActions };
