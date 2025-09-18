import { ChevronRight, Home, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { useAppStore } from '../../stores/basicAppStore';
import { motion } from 'motion/react';
import { useMemo } from 'react';
import { SectionType } from '../../types/app';

export default function HierarchyBreadcrumbs() {
  const hierarchyContext = useAppStore(state => state.hierarchyContext);
  const activeSection = useAppStore(state => state.activeSection);
  const navigateUp = useAppStore(state => state.navigateUp);
  const resetHierarchy = useAppStore(state => state.resetHierarchy);
  const navigateToBreadcrumb = useAppStore(state => state.navigateToBreadcrumb);

  // Debug hierarchy context
  console.log('🔍 Breadcrumbs - Hierarchy context:', {
    activeSection,
    pillarId: hierarchyContext.pillarId,
    pillarName: hierarchyContext.pillarName,
    areaId: hierarchyContext.areaId,
    areaName: hierarchyContext.areaName,
    projectId: hierarchyContext.projectId,
    projectName: hierarchyContext.projectName,
    timestamp: new Date().toISOString()
  });

  // Compute breadcrumbs directly from state to avoid infinite loops
  const breadcrumbs = useMemo(() => {
    const crumbs = [
      { label: 'Dashboard', section: 'dashboard' as SectionType }
    ];

    if (hierarchyContext.pillarId) {
      crumbs.push({
        label: 'Pillars',
        section: 'pillars' as SectionType
      });
      
      if (hierarchyContext.pillarName) {
        crumbs.push({
          label: hierarchyContext.pillarName,
          section: 'areas' as SectionType,
          context: { pillarId: hierarchyContext.pillarId, pillarName: hierarchyContext.pillarName }
        });
      }

      if (hierarchyContext.areaId && hierarchyContext.areaName) {
        crumbs.push({
          label: hierarchyContext.areaName,
          section: 'projects' as SectionType,
          context: hierarchyContext
        });
      }

      if (hierarchyContext.projectId && hierarchyContext.projectName) {
        crumbs.push({
          label: hierarchyContext.projectName,
          section: 'tasks' as SectionType,
          context: hierarchyContext
        });
      }
    } else {
      // Add current section if no hierarchy
      if (activeSection !== 'dashboard') {
        const sectionLabels: Record<SectionType, string> = {
          dashboard: 'Dashboard',
          pillars: 'Pillars',
          areas: 'Areas',
          projects: 'Projects',
          tasks: 'Tasks',
          today: 'Today',
          journal: 'Journal',
          settings: 'Settings',
          analytics: 'Analytics'
        };
        crumbs.push({
          label: sectionLabels[activeSection],
          section: activeSection
        });
      }
    }

    return crumbs;
  }, [hierarchyContext, activeSection]);

  // Don't show breadcrumbs on dashboard or if only dashboard in breadcrumbs
  if (breadcrumbs.length <= 1) return null;

  const handleBreadcrumbClick = (breadcrumb: typeof breadcrumbs[0], index: number) => {
    if (index === 0) {
      // Reset to dashboard
      resetHierarchy();
      return;
    }
    
    // Use the new navigateToBreadcrumb action
    navigateToBreadcrumb(breadcrumb.section, breadcrumb.context);
  };

  const showBackButton = hierarchyContext.pillarId || hierarchyContext.areaId || hierarchyContext.projectId;

  return (
    <motion.div 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between mb-6 p-4 glassmorphism-panel rounded-lg"
    >
      <div className="flex items-center space-x-2">
        {showBackButton && (
          <Button
            variant="ghost"
            size="sm"
            onClick={navigateUp}
            className="text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)] mr-2"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back
          </Button>
        )}
        
        <nav className="flex items-center space-x-1">
          {breadcrumbs.map((breadcrumb, index) => (
            <div key={index} className="flex items-center space-x-1">
              {index > 0 && (
                <ChevronRight className="w-4 h-4 text-[#6B7280] mx-1" />
              )}
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleBreadcrumbClick(breadcrumb, index)}
                className={`px-2 py-1 h-auto ${
                  index === breadcrumbs.length - 1
                    ? 'text-[#F4D03F] font-medium cursor-default'
                    : 'text-[#B8BCC8] hover:text-[#F4D03F] hover:bg-[rgba(244,208,63,0.1)]'
                }`}
                disabled={index === breadcrumbs.length - 1}
              >
                {index === 0 && <Home className="w-4 h-4 mr-1" />}
                {breadcrumb.label}
              </Button>
            </div>
          ))}
        </nav>
      </div>

      {/* Context Info */}
      {(hierarchyContext.pillarName || hierarchyContext.areaName || hierarchyContext.projectName) && (
        <div className="text-right">
          <div className="text-xs text-[#6B7280] uppercase tracking-wide mb-1">
            Current Context
          </div>
          <div className="flex items-center space-x-2 text-sm">
            {hierarchyContext.pillarName && (
              <span className="px-2 py-1 bg-[rgba(244,208,63,0.1)] text-[#F4D03F] rounded text-xs">
                {hierarchyContext.pillarName}
              </span>
            )}
            {hierarchyContext.areaName && (
              <span className="px-2 py-1 bg-[rgba(59,130,246,0.1)] text-blue-400 rounded text-xs">
                {hierarchyContext.areaName}
              </span>
            )}
            {hierarchyContext.projectName && (
              <span className="px-2 py-1 bg-[rgba(16,185,129,0.1)] text-green-400 rounded text-xs">
                {hierarchyContext.projectName}
              </span>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}