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

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<any>;
  badge?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export function Sidebar({ activeSection, onSectionChange }: SidebarProps) {
  const navSections: NavSection[] = [
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
        { id: 'insights', label: 'AI Insights', icon: Sparkles },
        { id: 'quick', label: 'Quick Actions', icon: Wand2 },
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
    <aside className="hidden lg:flex lg:flex-col w-72 shrink-0 p-4">
      <div className="rounded-2xl border" style={{background: 'rgba(11,13,20,0.8)', backdropFilter: 'blur(16px)', borderColor: 'rgba(244,208,63,0.12)'}}>
        {/* Brand */}
        <div className="px-4 py-4 flex items-center gap-3 border-b" style={{borderColor: 'rgba(244,208,63,0.12)'}}>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{background: 'linear-gradient(135deg, #F4D03F 0%, #F7DC6F 100%)', color: '#0B0D14', fontWeight: '700'}}>
            AL
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-semibold tracking-tight">Aurum Life</span>
            <span className="text-[11px]" style={{color: '#B8BCC8'}}>Personal Operating System</span>
          </div>
        </div>

        {/* Navigation Groups */}
        <nav className="p-2">
          {navSections.map((section, sectionIndex) => (
            <div key={section.title} className="px-2 py-3">
              <h4 className="text-xs uppercase tracking-wide mb-2" style={{color: '#6B7280'}}>{section.title}</h4>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeSection === item.id;
                  
                  return (
                    <button
                      key={item.id}
                      onClick={() => onSectionChange(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition group ${
                        isActive 
                          ? 'text-white' 
                          : 'text-white hover:bg-white/5'
                      }`}
                      style={isActive ? {
                        background: 'rgba(244,208,63,0.08)', 
                        border: '1px solid rgba(244,208,63,0.22)'
                      } : {}}
                    >
                      <Icon 
                        className="w-4 h-4" 
                        style={{color: isActive ? '#F4D03F' : '#B8BCC8'}} 
                      />
                      <span className="font-medium">{item.label}</span>
                      {item.badge && (
                        <span className="ml-auto text-[11px] px-2 py-0.5 rounded-full" style={{background: 'rgba(244,208,63,0.12)', color: '#F4D03F'}}>
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Divider */}
        <div className="mx-4 my-4 h-px" style={{background: 'linear-gradient(90deg, transparent, rgba(244,208,63,0.25), transparent)'}}></div>

        {/* Footer */}
        <div className="px-4 py-4">
          <div className="flex items-center gap-3">
            <img 
              src="https://images.unsplash.com/photo-1581065178026-390bc4e78dad?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjB3b21hbiUyMHBvcnRyYWl0fGVufDF8fHx8MTc1NzIwMTY3Nnww&ixlib=rb-4.1.0&q=80&w=200" 
              alt="User" 
              className="w-8 h-8 rounded-full ring-1" 
              style={{ringColor: 'rgba(244,208,63,0.3)'}}
            />
            <div className="flex-1">
              <div className="text-sm font-medium">Dania</div>
              <div className="text-xs" style={{color: '#B8BCC8'}}>Alignment on track</div>
            </div>
            <button className="p-2 rounded-lg border hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.25)'}}>
              <LogOut className="w-4 h-4" style={{color: '#B8BCC8'}} />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}