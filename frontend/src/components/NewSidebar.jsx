import React from 'react';
import { 
  LayoutDashboard, 
  Sun, 
  Columns2, 
  Grid2X2, 
  FolderKanban, 
  CheckSquare, 
  BookOpenText,
  Sparkles,
  Wand2,
  Goal,
  BarChart3,
  MessageSquareMore,
  Settings,
  LogOut
} from 'lucide-react';

/**
 * New Sidebar component with modern design
 * Converted from TypeScript to JavaScript
 */
const NewSidebar = ({ activeSection, onSectionChange }) => {
  const navSections = [
    {
      title: "Core Workflow",
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: 'Home' },
        { id: 'today', label: 'Today', icon: Sun },
        { id: 'pillars', label: 'Pillars', icon: Columns2 },
        { id: 'areas', label: 'Areas', icon: Grid2X2 },
        { id: 'projects', label: 'Projects', icon: FolderKanban },
        { id: 'tasks', label: 'Tasks', icon: CheckSquare },
        { id: 'journal', label: 'Journal', icon: BookOpenText },
      ]
    },
    {
      title: "AI Features",
      items: [
        { id: 'insights', label: 'My AI Insights', icon: Sparkles },
        { id: 'quick', label: 'AI Quick Actions', icon: Wand2 },
        { id: 'goals', label: 'Goal Planner', icon: Goal },
      ]
    },
    {
      title: "Tools",
      items: [
        { id: 'analytics', label: 'Analytics', icon: BarChart3 },
        { id: 'feedback', label: 'Feedback', icon: MessageSquareMore },
        { id: 'settings', label: 'Settings', icon: Settings },
      ]
    }
  ];

  return (
    <aside className="w-64 border-r" style={{background: 'rgba(11,13,20,0.95)', borderColor: 'rgba(244,208,63,0.12)'}}>
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="p-6 border-b" style={{borderColor: 'rgba(244,208,63,0.12)'}}>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{background: 'linear-gradient(135deg,#F4D03F,#F7DC6F)'}}>
              <span className="text-black font-bold text-sm">AL</span>
            </div>
            <div>
              <h1 className="font-semibold tracking-tight">Aurum Life</h1>
              <p className="text-xs" style={{color: '#B8BCC8'}}>Personal Operating System</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-6">
          {navSections.map((section) => (
            <div key={section.title}>
              <h3 className="text-xs font-medium mb-3" style={{color: '#6B7280'}}>
                {section.title}
              </h3>
              <ul className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeSection === item.id;
                  
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => onSectionChange(item.id)}
                        className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                          isActive 
                            ? 'text-black font-medium' 
                            : 'text-white hover:text-white'
                        }`}
                        style={{
                          background: isActive 
                            ? 'linear-gradient(135deg,#F4D03F,#F7DC6F)' 
                            : 'transparent'
                        }}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="flex-1 text-left">{item.label}</span>
                        {item.badge && (
                          <span className="text-xs px-2 py-1 rounded-md" style={{background: 'rgba(0,0,0,0.1)'}}>
                            {item.badge}
                          </span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t" style={{borderColor: 'rgba(244,208,63,0.12)'}}>
          <div className="flex items-center gap-3">
            <img 
              src="https://images.unsplash.com/photo-1581065178026-390bc4e78dad?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjB3b21hbiUyMHBvcnRyYWl0fGVufDF8fHx8MTc1NzIwMTY3Nnww&ixlib=rb-4.1.0&q=80&w=64" 
              alt="Avatar" 
              className="w-8 h-8 rounded-full ring-1" 
              style={{ringColor: 'rgba(244,208,63,0.25)'}}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">Test User</p>
              <p className="text-xs" style={{color: '#B8BCC8'}}>Alignment on track</p>
            </div>
            <button className="p-1 rounded hover:opacity-80">
              <LogOut className="w-4 h-4" style={{color: '#6B7280'}} />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default NewSidebar;
