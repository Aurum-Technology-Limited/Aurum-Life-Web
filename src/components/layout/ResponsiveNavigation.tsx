import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
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
  Menu,
  X,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { Button } from '../ui/button';
import { useUI } from '../../stores/appStore';
import { SectionType } from '../../types/app';
import { cn } from '../ui/utils';

interface NavItem {
  id: SectionType;
  label: string;
  icon: React.ElementType;
  section: string;
  badge?: number;
}

const navItems: NavItem[] = [
  // Core Workflow
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, section: 'Core Workflow' },
  { id: 'today', label: 'Today', icon: Calendar, section: 'Core Workflow', badge: 3 },
  { id: 'pillars', label: 'Pillars', icon: Target, section: 'Core Workflow' },
  { id: 'areas', label: 'Areas', icon: Layers3, section: 'Core Workflow' },
  { id: 'projects', label: 'Projects', icon: FolderKanban, section: 'Core Workflow' },
  { id: 'tasks', label: 'Tasks', icon: CheckSquare, section: 'Core Workflow', badge: 5 },
  { id: 'journal', label: 'Journal', icon: BookOpen, section: 'Core Workflow' },
  
  // AI & Intelligence
  { id: 'ai-insights', label: 'AI Insights', icon: Brain, section: 'AI & Intelligence' },
  { id: 'quick-actions', label: 'Quick Actions', icon: Zap, section: 'AI & Intelligence' },
  { id: 'goal-planner', label: 'Goal Planner', icon: TrendingUp, section: 'AI & Intelligence' },
  
  // Analytics & Feedback
  { id: 'analytics', label: 'Analytics', icon: BarChart3, section: 'Analytics & Feedback' },
  { id: 'feedback', label: 'Feedback', icon: MessageSquare, section: 'Analytics & Feedback' },
  { id: 'settings', label: 'Settings', icon: Settings, section: 'Analytics & Feedback' },
];

interface NavigationProps {
  activeSection: SectionType;
  onSectionChange: (section: SectionType) => void;
}

const sidebarVariants = {
  expanded: { width: '280px' },
  collapsed: { width: '80px' },
};

const itemVariants = {
  expanded: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.2, delay: 0.1 }
  },
  collapsed: { 
    opacity: 0, 
    x: -10,
    transition: { duration: 0.1 }
  },
};

export default function ResponsiveNavigation({ activeSection, onSectionChange }: NavigationProps) {
  const { isSidebarCollapsed, toggleSidebar, setSidebarCollapsed } = useUI();
  const [collapsedSections, setCollapsedSections] = useState<string[]>([]);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [setSidebarCollapsed]);

  const groupedItems = navItems.reduce((acc, item) => {
    if (!acc[item.section]) {
      acc[item.section] = [];
    }
    acc[item.section].push(item);
    return acc;
  }, {} as Record<string, NavItem[]>);

  const toggleSection = (section: string) => {
    setCollapsedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const handleItemClick = (sectionId: SectionType) => {
    onSectionChange(sectionId);
    if (isMobile) {
      setSidebarCollapsed(true);
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobile && !isSidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarCollapsed(true)}
          />
        )}
      </AnimatePresence>

      {/* Navigation Sidebar */}
      <motion.nav
        variants={sidebarVariants}
        animate={isSidebarCollapsed ? 'collapsed' : 'expanded'}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className={cn(
          "glassmorphism-header fixed left-0 top-16 bottom-0 z-50 lg:relative lg:top-0",
          "flex flex-col border-r border-[rgba(244,208,63,0.1)]",
          isMobile && isSidebarCollapsed && "translate-x-[-100%]",
          !isMobile && "translate-x-0"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4">
          <AnimatePresence>
            {!isSidebarCollapsed && (
              <motion.h2
                variants={itemVariants}
                initial="collapsed"
                animate="expanded"
                exit="collapsed"
                className="aurum-text-gradient font-medium"
              >
                Navigation
              </motion.h2>
            )}
          </AnimatePresence>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] p-2"
          >
            {isSidebarCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
          </Button>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto px-2 pb-4">
          {Object.entries(groupedItems).map(([sectionName, items]) => (
            <div key={sectionName} className="mb-6">
              {/* Section Header */}
              {!isSidebarCollapsed ? (
                <motion.button
                  onClick={() => toggleSection(sectionName)}
                  className="flex items-center justify-between w-full px-3 py-2 mb-2 text-sm text-[#B8BCC8] hover:text-[#F4D03F] transition-colors"
                  whileHover={{ x: 2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span>{sectionName}</span>
                  {collapsedSections.includes(sectionName) ? (
                    <ChevronRight className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </motion.button>
              ) : (
                <div className="h-1 bg-gradient-to-r from-transparent via-[rgba(244,208,63,0.3)] to-transparent mb-2" />
              )}

              {/* Navigation Items */}
              <AnimatePresence>
                {(!collapsedSections.includes(sectionName) || isSidebarCollapsed) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="space-y-1"
                  >
                    {items.map((item) => {
                      const Icon = item.icon;
                      const isActive = activeSection === item.id;
                      
                      return (
                        <motion.button
                          key={item.id}
                          onClick={() => handleItemClick(item.id)}
                          className={cn(
                            "relative flex items-center w-full p-3 rounded-lg transition-all duration-200",
                            "hover:bg-[rgba(244,208,63,0.1)] hover:translate-x-1",
                            isActive && "bg-[rgba(244,208,63,0.15)] text-[#F4D03F] shadow-lg shadow-[rgba(244,208,63,0.1)]",
                            !isActive && "text-[#B8BCC8] hover:text-[#F4D03F]",
                            isSidebarCollapsed && "justify-center"
                          )}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          {/* Active indicator */}
                          {isActive && (
                            <motion.div
                              layoutId="activeIndicator"
                              className="absolute left-0 w-1 h-8 bg-[#F4D03F] rounded-r"
                              transition={{ duration: 0.3 }}
                            />
                          )}
                          
                          <Icon className={cn(
                            "w-5 h-5 flex-shrink-0",
                            isSidebarCollapsed ? "mx-auto" : "mr-3"
                          )} />
                          
                          <AnimatePresence>
                            {!isSidebarCollapsed && (
                              <motion.div
                                variants={itemVariants}
                                initial="collapsed"
                                animate="expanded"
                                exit="collapsed"
                                className="flex items-center justify-between flex-1 min-w-0"
                              >
                                <span className="truncate">{item.label}</span>
                                {item.badge && (
                                  <motion.span
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="ml-2 px-2 py-1 text-xs rounded-full bg-[#F4D03F] text-[#0B0D14] font-medium"
                                  >
                                    {item.badge}
                                  </motion.span>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>
                          
                          {/* Collapsed badge */}
                          {isSidebarCollapsed && item.badge && (
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              className="absolute -top-1 -right-1 w-5 h-5 bg-[#F4D03F] text-[#0B0D14] text-xs rounded-full flex items-center justify-center font-medium"
                            >
                              {item.badge > 9 ? '9+' : item.badge}
                            </motion.div>
                          )}
                        </motion.button>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[rgba(244,208,63,0.1)]">
          <AnimatePresence>
            {!isSidebarCollapsed && (
              <motion.div
                variants={itemVariants}
                initial="collapsed"
                animate="expanded"
                exit="collapsed"
                className="text-xs text-[#6B7280] text-center"
              >
                <p>Aurum Life v1.0</p>
                <p className="mt-1">Your Personal OS</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.nav>
    </>
  );
}