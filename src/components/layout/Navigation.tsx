import { useState } from 'react';
import { 
  LayoutDashboard, 
  Target, 
  Layers3, 
  FolderKanban, 
  CheckSquare, 
  BookOpen,
  Calendar,
  Brain,
  Zap,
  TrendingUp,
  BarChart3,
  MessageSquare,
  Settings,
  ChevronDown,
  ChevronRight,
  User,
  Bell,
  Shield,
  Palette,
  Cloud,
  HelpCircle,
  FileText,
  Bot,
  Users,
  Puzzle,
  Workflow
} from 'lucide-react';
import { Button } from '../ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  section: string;
  hasDropdown?: boolean;
  children?: SubNavItem[];
}

interface SubNavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  settingsSection: string;
}

const settingsSubItems: SubNavItem[] = [
  { id: 'account', label: 'Account & Profile', icon: User, settingsSection: 'account' },
  { id: 'preferences', label: 'App Preferences', icon: Palette, settingsSection: 'preferences' },
  { id: 'notifications', label: 'Notifications', icon: Bell, settingsSection: 'notifications' },
  { id: 'ai', label: 'AI & Automation', icon: Brain, settingsSection: 'ai' },
  { id: 'sync', label: 'Sync & Backup', icon: Cloud, settingsSection: 'sync' },
  { id: 'privacy', label: 'Privacy & Security', icon: Shield, settingsSection: 'privacy' },
  { id: 'audit', label: 'Audit & Transparency', icon: FileText, settingsSection: 'audit' },
  { id: 'help', label: 'Help & Support', icon: HelpCircle, settingsSection: 'help' }
];

const navItems: NavItem[] = [
  // Core Workflow
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, section: 'Core Workflow' },
  { id: 'today', label: 'Today', icon: Calendar, section: 'Core Workflow' },
  { id: 'pillars', label: 'Pillars', icon: Target, section: 'Core Workflow' },
  { id: 'areas', label: 'Areas', icon: Layers3, section: 'Core Workflow' },
  { id: 'projects', label: 'Projects', icon: FolderKanban, section: 'Core Workflow' },
  { id: 'tasks', label: 'Tasks', icon: CheckSquare, section: 'Core Workflow' },
  { id: 'journal', label: 'Journal', icon: BookOpen, section: 'Core Workflow' },
  
  // AI Features
  { id: 'ai-insights', label: 'AI Insights', icon: Brain, section: 'AI Features' },
  { id: 'ai-quick-capture', label: 'Quick Capture', icon: Zap, section: 'AI Features' },
  { id: 'quick-actions', label: 'Quick Actions', icon: TrendingUp, section: 'AI Features' },
  { id: 'goal-planner', label: 'Goal Planner', icon: Target, section: 'AI Features' },
  
  // Advanced AI & Enterprise (Phase 4)
  { id: 'ai-workflows', label: 'AI Workflows', icon: Workflow, section: 'Advanced AI & Enterprise' },
  { id: 'ai-life-coach', label: 'AI Life Coach', icon: Bot, section: 'Advanced AI & Enterprise' },
  { id: 'predictive-analytics', label: 'Predictive Analytics', icon: TrendingUp, section: 'Advanced AI & Enterprise' },
  { id: 'team-collaboration', label: 'Team Collaboration', icon: Users, section: 'Advanced AI & Enterprise' },
  { id: 'enterprise-security', label: 'Enterprise Security', icon: Shield, section: 'Advanced AI & Enterprise' },
  
  // Tools
  { id: 'integrations', label: 'Calendar & Email', icon: Calendar, section: 'Tools' },
  { id: 'integration-hub', label: 'All Integrations', icon: Puzzle, section: 'Tools' },
  { id: 'analytics', label: 'Analytics', icon: BarChart3, section: 'Tools' },
  { id: 'enhanced-profile', label: 'Enhanced Profile', icon: User, section: 'Tools' },
  { id: 'privacy-controls', label: 'Privacy Controls', icon: Shield, section: 'Tools' },
  { id: 'feedback', label: 'Feedback', icon: MessageSquare, section: 'Tools' },
  { id: 'settings', label: 'Settings', icon: Settings, section: 'Tools', hasDropdown: true, children: settingsSubItems }
];

const sections = ['Core Workflow', 'AI Features', 'Advanced AI & Enterprise', 'Tools'];

interface NavigationProps {
  activeSection: string;
  onSectionChange: (section: string, settingsSection?: string) => void;
}

export default function Navigation({ activeSection, onSectionChange }: NavigationProps) {
  const [settingsExpanded, setSettingsExpanded] = useState(false);
  const [activeSettingsSection, setActiveSettingsSection] = useState('account');

  return (
    <nav className="w-full h-full flex flex-col space-y-6 pb-6 pt-6 px-4 bg-[var(--aurum-secondary-bg)]">
      {sections.map(section => (
        <div key={section} className="space-y-2">
          <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            {section}
          </h4>
          <div className="space-y-1">
            {navItems
              .filter(item => item.section === section)
              .map(item => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                
                // Handle settings dropdown
                if (item.hasDropdown && item.children) {
                  return (
                    <Collapsible 
                      key={item.id} 
                      open={settingsExpanded} 
                      onOpenChange={setSettingsExpanded}
                    >
                      <CollapsibleTrigger asChild>
                        <Button
                          variant="ghost"
                          className={`w-full justify-start px-3 py-2 h-auto transition-all duration-200 ${
                            isActive 
                              ? 'bg-primary/10 text-primary border-l-2 border-primary' 
                              : 'text-muted-foreground hover:text-foreground hover:bg-primary/5'
                          }`}
                          onClick={() => {
                            if (!settingsExpanded) {
                              onSectionChange(item.id, activeSettingsSection);
                            }
                          }}
                        >
                          <Icon className="w-4 h-4 mr-3" />
                          {item.label}
                          {settingsExpanded ? (
                            <ChevronDown className="w-4 h-4 ml-auto" />
                          ) : (
                            <ChevronRight className="w-4 h-4 ml-auto" />
                          )}
                        </Button>
                      </CollapsibleTrigger>
                      <CollapsibleContent className="space-y-1 ml-4 mt-1">
                        {item.children.map(child => {
                          const ChildIcon = child.icon;
                          const isChildActive = activeSection === 'settings' && activeSettingsSection === child.settingsSection;
                          
                          return (
                            <Button
                              key={child.id}
                              variant="ghost"
                              size="sm"
                              className={`w-full justify-start px-3 py-1.5 h-auto transition-all duration-200 ${
                                isChildActive
                                  ? 'bg-primary/15 text-primary border-l-2 border-primary' 
                                  : 'text-muted-foreground hover:text-foreground hover:bg-primary/5'
                              }`}
                              onClick={() => {
                                setActiveSettingsSection(child.settingsSection);
                                onSectionChange('settings', child.settingsSection);
                              }}
                            >
                              <ChildIcon className="w-3.5 h-3.5 mr-2" />
                              <span className="text-sm">{child.label}</span>
                            </Button>
                          );
                        })}
                      </CollapsibleContent>
                    </Collapsible>
                  );
                }
                
                // Regular navigation items
                return (
                  <Button
                    key={item.id}
                    variant="ghost"
                    className={`w-full justify-start px-3 py-2 h-auto transition-all duration-200 ${
                      isActive 
                        ? 'bg-primary/10 text-primary border-l-2 border-primary' 
                        : 'text-muted-foreground hover:text-foreground hover:bg-primary/5'
                    }`}
                    onClick={() => onSectionChange(item.id)}
                  >
                    <Icon className="w-4 h-4 mr-3" />
                    {item.label}
                  </Button>
                );
              })}
          </div>
        </div>
      ))}
    </nav>
  );
}