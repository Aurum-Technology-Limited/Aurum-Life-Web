import { useState, useEffect, useMemo } from 'react';
import { Layers3, Plus, Target, FolderKanban } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import { Button } from '../ui/button';
import { useAppStore } from '../../stores/basicAppStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import HierarchyCard from '../shared/HierarchyCard';
import CreateEditModal from '../shared/CreateEditModal';
import DeleteConfirmModal from '../shared/DeleteConfirmModal';
import EmptyState from '../shared/EmptyState';
import { Area } from '../../types/enhanced-features';

export default function Areas() {
  const hierarchyContext = useAppStore(state => state.hierarchyContext);
  const navigateToArea = useAppStore(state => state.navigateToArea);
  // Get enhanced features store state and functions
  const enhancedStore = useEnhancedFeaturesStore();
  const { 
    pillars, 
    getAllAreas, 
    getAllProjects, 
    getAllTasks, 
    getPillarById, 
    getAreasByPillarId,
    deleteArea
  } = enhancedStore;

  // Force re-render when pillar context changes
  const [, forceUpdate] = useState({});

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedArea, setSelectedArea] = useState<Area | null>(null);

  // Filter areas based on hierarchy context with enhanced reactivity
  const filteredAreas = useMemo(() => {
    console.log('🔄 Recalculating filtered areas...', {
      pillarId: hierarchyContext.pillarId,
      pillarName: hierarchyContext.pillarName,
      pillarsCount: pillars.length,
      timestamp: new Date().toISOString()
    });
    
    // If no pillar context, show all areas
    if (!hierarchyContext.pillarId) {
      const allAreas = getAllAreas();
      console.log('🎯 No pillar context - returning all areas:', {
        count: allAreas.length,
        areaNames: allAreas.map(a => a.name)
      });
      return allAreas;
    }
    
    // Find the target pillar directly from the pillars array
    console.log('🔍 Looking for pillar with ID:', hierarchyContext.pillarId);
    console.log('🔍 Available pillars:', pillars.map(p => ({ id: p.id, name: p.name, areasCount: p.areas?.length || 0 })));
    
    const targetPillar = pillars.find(p => p.id === hierarchyContext.pillarId);
    
    if (!targetPillar) {
      console.log('❌ Target pillar not found!');
      return [];
    }
    
    console.log('✅ Target pillar found:', {
      id: targetPillar.id,
      name: targetPillar.name,
      areasCount: targetPillar.areas?.length || 0
    });
    
    const result = targetPillar.areas || [];
    
    console.log('🎯 Final filtering result:', {
      pillarId: hierarchyContext.pillarId,
      pillarName: hierarchyContext.pillarName,
      filteredCount: result.length,
      filteredNames: result.map(a => a.name),
      totalAreasInSystem: getAllAreas().length
    });
    
    return result;
  }, [
    hierarchyContext.pillarId, 
    hierarchyContext.pillarName, 
    pillars, 
    getAllAreas
  ]);

  // Force component refresh when hierarchy context changes
  const [refreshKey, setRefreshKey] = useState(0);
  
  useEffect(() => {
    console.log('🔄 [AREAS] Hierarchy context changed:', {
      pillarId: hierarchyContext.pillarId,
      pillarName: hierarchyContext.pillarName,
      filteredCount: filteredAreas.length,
      totalCount: getAllAreas().length,
      refreshKey
    });
    
    // Force refresh when context changes
    setRefreshKey(prev => prev + 1);
  }, [hierarchyContext.pillarId, hierarchyContext.pillarName]);
  
  // Listen for custom navigation events
  useEffect(() => {
    const handleHierarchyChange = (event: CustomEvent) => {
      console.log('🔄 [AREAS] Custom hierarchy change event received:', event.detail);
      setRefreshKey(prev => prev + 1);
    };
    
    window.addEventListener('aurumHierarchyChanged', handleHierarchyChange);
    return () => window.removeEventListener('aurumHierarchyChanged', handleHierarchyChange);
  }, []);

  // Get icon for area
  const getIconForArea = (area: Area) => {
    if (area.icon) {
      const CustomIcon = (LucideIcons as any)[area.icon];
      if (CustomIcon) return CustomIcon;
    }
    return Target;
  };

  // Get the current pillar for context
  const currentPillar = hierarchyContext.pillarId ? getPillarById(hierarchyContext.pillarId) : null;

  // Calculate metrics for each area
  const getAreaMetrics = (areaId: string) => {
    const allProjects = getAllProjects();
    const allTasks = getAllTasks();
    
    // Get projects for this area
    const areaProjects = allProjects.filter(project => project.areaId === areaId);
    
    // Get tasks for this area
    const areaTasks = allTasks.filter(task => {
      return areaProjects.some(project => project.id === task.projectId);
    });
    
    return {
      projects: areaProjects.length,
      tasks: areaTasks.length
    };
  };

  const handleAreaClick = (area: typeof filteredAreas[0]) => {
    console.log('🎯 Area clicked:', area.name, 'ID:', area.id);
    navigateToArea(area.id, area.name);
  };

  const handleProjectClick = (projectId: string, projectName: string, area: Area) => {
    console.log('📁 Project clicked from area:', projectName, 'Area:', area.name);
    if (hierarchyContext.pillarId && hierarchyContext.pillarName) {
      // We have full context - use it
      const navigateToProjectWithFullContext = useAppStore.getState().navigateToProjectWithFullContext;
      navigateToProjectWithFullContext(
        hierarchyContext.pillarId, 
        hierarchyContext.pillarName, 
        area.id, 
        area.name, 
        projectId, 
        projectName
      );
    } else {
      // Fallback to regular navigation
      const navigateToProject = useAppStore.getState().navigateToProject;
      navigateToProject(projectId, projectName);
    }
  };

  const handleEdit = (area: Area) => {
    console.log('🔧 Edit button clicked for area:', area.name);
    setSelectedArea(area);
    setEditModalOpen(true);
  };

  const handleDelete = (area: Area) => {
    console.log('🗑️ Delete button clicked for area:', area.name);
    setSelectedArea(area);
    setDeleteModalOpen(true);
  };

  const handleViewProjects = (area: Area) => {
    console.log('🎯 View Projects clicked for area:', area.name);
    // Navigate to the area context in projects section
    navigateToArea(area.id, area.name);
    // Then navigate to projects section
    const setActiveSection = useAppStore.getState().setActiveSection;
    setActiveSection('projects');
  };



  const confirmDelete = () => {
    if (selectedArea) {
      deleteArea(selectedArea.id);
      setDeleteModalOpen(false);
      setSelectedArea(null);
    }
  };

  const getChildrenCount = (area: Area) => {
    return area.projects.length;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {hierarchyContext.pillarName ? `${hierarchyContext.pillarName} - Focus Areas` : 'Focus Areas'}
          </h1>
          <p className="text-[#B8BCC8]">
            {hierarchyContext.pillarName 
              ? `Focus areas within the ${hierarchyContext.pillarName} pillar`
              : 'Specific focus categories within your strategic pillars'
            }
          </p>
        </div>
        <Button 
          className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          onClick={() => setCreateModalOpen(true)}
          disabled={!hierarchyContext.pillarId}
        >
          <Plus className="w-4 h-4 mr-2" />
          New Area
        </Button>
      </div>

      {/* Areas Grid */}
      {!hierarchyContext.pillarId ? (
        <EmptyState
          icon={<Target className="w-12 h-12" />}
          title="Select a Pillar First"
          description="To view and manage focus areas, you need to select a strategic pillar first. Areas are organized within pillars to help structure your life framework."
          actionLabel="Go to Pillars"
          onAction={() => {
            const setActiveSection = useAppStore.getState().setActiveSection;
            setActiveSection('pillars');
          }}
        />
      ) : filteredAreas.length === 0 ? (
        <EmptyState
          icon={<Target className="w-12 h-12" />}
          title={`No Areas in ${hierarchyContext.pillarName}`}
          description={`Start organizing your ${hierarchyContext.pillarName} pillar by creating focus areas that group related projects.`}
          actionLabel="Create Your First Area"
          onAction={() => setCreateModalOpen(true)}
        />
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAreas.slice(0, 10).map(area => {
          const metrics = getAreaMetrics(area.id);
          const Icon = getIconForArea(area);
          
          // Convert projects to subItems format
          const subItems = area.projects.map(project => {
            const projectProgress = project.tasks.length > 0 
              ? Math.round((project.tasks.filter(t => t.status === 'completed').length / project.tasks.length) * 100) 
              : 0;
            
            return {
              id: project.id,
              name: project.name,
              progress: projectProgress,
              onClick: () => handleProjectClick(project.id, project.name, area)
            };
          });
          
          return (
            <HierarchyCard
              key={area.id}
              level="area"
              title={area.name}
              description={area.description}
              healthScore={area.healthScore}
              icon={<Icon className="w-6 h-6" />}
              color={area.color}
              iconBgColor={area.color}
              badge={{
                text: currentPillar?.name || 'Unknown Pillar',
                variant: 'outline'
              }}
              metrics={[
                {
                  label: 'Projects',
                  value: metrics.projects,
                  icon: <FolderKanban className="w-4 h-4" />,
                  color: '#3B82F6',
                },
                {
                  label: 'Tasks',
                  value: metrics.tasks,
                  icon: <Layers3 className="w-4 h-4" />,
                  color: '#10B981',
                },
              ]}
              subItems={subItems}
              onClick={() => handleAreaClick(area)}
              onEdit={() => handleEdit(area)}
              onDelete={() => handleDelete(area)}
              onViewChildren={() => handleViewProjects(area)}
              showDirectActions={true}
            />
          );
        })}
          </div>
          
          {/* Overflow indicator when there are more than 10 areas */}
          {filteredAreas.length > 10 && (
            <div className="text-center pt-4 border-t border-[rgba(244,208,63,0.1)]">
              <p className="text-[#6B7280] text-sm">
                Showing 10 of {filteredAreas.length} areas
              </p>
              <p className="text-[#6B7280] text-xs mt-1">
                +{filteredAreas.length - 10} more areas not displayed
              </p>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      <CreateEditModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        mode="create"
        type="area"
        parentId={hierarchyContext.pillarId || undefined}
        onSuccess={() => setCreateModalOpen(false)}
      />

      <CreateEditModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedArea(null);
        }}
        mode="edit"
        type="area"
        item={selectedArea || undefined}
        onSuccess={() => {
          setEditModalOpen(false);
          setSelectedArea(null);
        }}
      />

      <DeleteConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setSelectedArea(null);
        }}
        onConfirm={confirmDelete}
        title={`Are you sure you want to delete this area?`}
        itemName={selectedArea?.name || ''}
        type="area"
        childrenCount={selectedArea ? getChildrenCount(selectedArea) : 0}
      />
    </div>
  );
}