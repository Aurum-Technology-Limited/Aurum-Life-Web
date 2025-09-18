import { useState, useEffect } from 'react';
import { FolderKanban, Plus, Calendar, CheckCircle2, Clock, Layers3, Paperclip } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import { Button } from '../ui/button';
import { useAppStore } from '../../stores/basicAppStore';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import HierarchyCard from '../shared/HierarchyCard';
import CreateEditModal from '../shared/CreateEditModal';
import DeleteConfirmModal from '../shared/DeleteConfirmModal';
import { Project } from '../../types/enhanced-features';

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return '#10B981';
    case 'active': return '#F4D03F';
    case 'paused': return '#F59E0B';
    case 'planning': return '#3B82F6';
    case 'cancelled': return '#EF4444';
    default: return '#6B7280';
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'completed': return 'Completed';
    case 'active': return 'Active';
    case 'paused': return 'Paused';
    case 'planning': return 'Planning';
    case 'cancelled': return 'Cancelled';
    default: return 'Unknown';
  }
};

// Get icon for project
const getIconForProject = (project: Project) => {
  if (project.icon) {
    const CustomIcon = (LucideIcons as any)[project.icon];
    if (CustomIcon) return CustomIcon;
  }
  return FolderKanban;
};

export default function Projects() {
  const hierarchyContext = useAppStore(state => state.hierarchyContext);
  const navigateToProject = useAppStore(state => state.navigateToProject);
  const { 
    getAllProjects, 
    getProjectsByAreaId, 
    getAreaById, 
    getPillarById,
    deleteProject
  } = useEnhancedFeaturesStore();

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // Add debugging for modal state changes
  useEffect(() => {
    console.log('📝 Modal states changed:', {
      createModalOpen,
      editModalOpen,
      deleteModalOpen,
      selectedProject: selectedProject?.name || 'none'
    });
  }, [createModalOpen, editModalOpen, deleteModalOpen, selectedProject]);

  // Filter projects based on hierarchy context
  const filteredProjects = hierarchyContext.areaId 
    ? getProjectsByAreaId(hierarchyContext.areaId)
    : getAllProjects();

  // Debug logging for filtering
  useEffect(() => {
    console.log('🎯 Projects filtering debug:', {
      areaId: hierarchyContext.areaId,
      areaName: hierarchyContext.areaName,
      filteredCount: filteredProjects.length,
      totalCount: getAllProjects().length
    });
  }, [hierarchyContext.areaId, filteredProjects.length, getAllProjects]);

  // Get context information
  const currentArea = hierarchyContext.areaId ? getAreaById(hierarchyContext.areaId) : null;
  const currentPillar = hierarchyContext.pillarId ? getPillarById(hierarchyContext.pillarId) : null;

  // Calculate project progress based on completed tasks
  const getProjectProgress = (project: typeof filteredProjects[0]) => {
    if (project.tasks.length === 0) return 0;
    const completedTasks = project.tasks.filter(task => task.status === 'completed').length;
    return Math.round((completedTasks / project.tasks.length) * 100);
  };

  const handleProjectClick = (project: typeof filteredProjects[0]) => {
    console.log('📁 Project clicked:', project.name, 'ID:', project.id);
    navigateToProject(project.id, project.name);
  };

  const handleTaskClick = (taskId: string, taskName: string) => {
    console.log('Task clicked:', taskName);
    // Navigate to tasks section with this specific task highlighted
    const navigateToTasks = useAppStore.getState().navigateToTasks;
    navigateToTasks();
    // Here you could add logic to highlight or focus on the specific task
  };

  const handleViewTasks = (project: Project) => {
    console.log('🎯 View Tasks clicked for project:', project.name);
    // Navigate to the project context in tasks section
    navigateToProject(project.id, project.name);
    // Then navigate to tasks section
    const setActiveSection = useAppStore.getState().setActiveSection;
    setActiveSection('tasks');
  };

  const handleEdit = (project: Project) => {
    console.log('🔧 Edit button clicked for project:', project.name);
    setSelectedProject(project);
    setEditModalOpen(true);
  };

  const handleDelete = (project: Project) => {
    console.log('🗑️ Delete button clicked for project:', project.name);
    setSelectedProject(project);
    setDeleteModalOpen(true);
  };



  const confirmDelete = () => {
    if (selectedProject) {
      deleteProject(selectedProject.id);
      setDeleteModalOpen(false);
      setSelectedProject(null);
    }
  };

  const getChildrenCount = (project: Project) => {
    return project.tasks.length;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {hierarchyContext.areaName ? `${hierarchyContext.areaName} - Projects` : 'Projects'}
          </h1>
          <p className="text-[#B8BCC8]">
            {hierarchyContext.areaName 
              ? `Projects within the ${hierarchyContext.areaName} area`
              : 'Tactical initiatives and deliverables driving your goals'
            }
          </p>
        </div>
        <Button 
          className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
          onClick={() => setCreateModalOpen(true)}
          disabled={!hierarchyContext.areaId}
        >
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Projects Grid */}
      {!hierarchyContext.areaId ? (
        <div className="space-y-6">
          <div className="glassmorphism-card p-8 text-center">
            <FolderKanban className="w-16 h-16 text-[#F4D03F] mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-3">Select an Area First</h3>
            <p className="text-[#B8BCC8] mb-6">
              To view and manage projects, you need to select a focus area first. Projects are organized within areas to help structure your strategic work.
            </p>
            <Button 
              className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
              onClick={() => {
                const setActiveSection = useAppStore.getState().setActiveSection;
                setActiveSection('areas');
              }}
            >
              Go to Areas
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredProjects.length === 0 ? (
            <div className="glassmorphism-card p-8 text-center">
              <FolderKanban className="w-16 h-16 text-[#F4D03F] mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-3">No Projects in {hierarchyContext.areaName}</h3>
              <p className="text-[#B8BCC8] mb-6">
                Start organizing your {hierarchyContext.areaName} area by creating projects that contain specific tasks and deliverables.
              </p>
              <Button 
                className="bg-[#F4D03F] text-[#0B0D14] hover:bg-[#F7DC6F]"
                onClick={() => setCreateModalOpen(true)}
              >
                Create Your First Project
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredProjects.slice(0, 10).map(project => {
          const progress = getProjectProgress(project);
          const completedTasks = project.tasks.filter(task => task.status === 'completed').length;
          const totalTasks = project.tasks.length;
          const Icon = getIconForProject(project);
          
          // Convert tasks to subItems format
          const subItems = project.tasks.map(task => ({
            id: task.id,
            name: task.name,
            progress: task.status === 'completed' ? 100 : 0,
            onClick: () => handleTaskClick(task.id, task.name)
          }));
          
          return (
            <HierarchyCard
              key={project.id}
              level="project"
              title={project.name}
              description={project.description}
              progress={progress}
              icon={<Icon className="w-6 h-6" />}
              color={project.color}
              iconBgColor={project.color}
              badge={{
                text: getStatusLabel(project.status),
                variant: 'outline'
              }}
              metrics={[
                {
                  label: 'Tasks',
                  value: `${completedTasks}/${totalTasks}`,
                  icon: <Layers3 className="w-4 h-4" />,
                  color: '#10B981',
                },
                {
                  label: 'Impact',
                  value: `${project.impactScore}/10`,
                  icon: <CheckCircle2 className="w-4 h-4" />,
                  color: '#F4D03F',
                },
                {
                  label: 'Files',
                  value: `${project.attachments.length}`,
                  icon: <Paperclip className="w-4 h-4" />,
                  color: '#3B82F6',
                },
                {
                  label: 'Due Date',
                  value: project.dueDate ? new Date(project.dueDate).toLocaleDateString() : 'No date',
                  icon: <Calendar className="w-4 h-4" />,
                  color: '#B8BCC8',
                },
              ]}
              subItems={subItems}
              onClick={() => handleProjectClick(project)}
              onEdit={() => handleEdit(project)}
              onDelete={() => handleDelete(project)}
              onViewChildren={() => handleViewTasks(project)}
              showDirectActions={true}
            >
              {/* Context badges - legacy children support */}
              <div className="flex flex-wrap gap-2 mb-3">
                {currentPillar && (
                  <span className="text-xs px-2 py-1 rounded-full bg-[rgba(244,208,63,0.1)] text-[#F4D03F]">
                    {currentPillar.name}
                  </span>
                )}
                {currentArea && (
                  <span className="text-xs px-2 py-1 rounded-full bg-[rgba(59,130,246,0.1)] text-blue-400">
                    {currentArea.name}
                  </span>
                )}
              </div>
            </HierarchyCard>
          );
        })}
          </div>
          
          {/* Overflow indicator when there are more than 10 projects */}
          {filteredProjects.length > 10 && (
            <div className="text-center pt-4 border-t border-[rgba(244,208,63,0.1)]">
              <p className="text-[#6B7280] text-sm">
                Showing 10 of {filteredProjects.length} projects
              </p>
              <p className="text-[#6B7280] text-xs mt-1">
                +{filteredProjects.length - 10} more projects not displayed
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
        type="project"
        parentId={hierarchyContext.areaId || undefined}
        onSuccess={() => setCreateModalOpen(false)}
      />

      <CreateEditModal
        isOpen={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedProject(null);
        }}
        mode="edit"
        type="project"
        item={selectedProject || undefined}
        onSuccess={() => {
          setEditModalOpen(false);
          setSelectedProject(null);
        }}
      />

      <DeleteConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => {
          setDeleteModalOpen(false);
          setSelectedProject(null);
        }}
        onConfirm={confirmDelete}
        title={`Are you sure you want to delete this project?`}
        itemName={selectedProject?.name || ''}
        type="project"
        childrenCount={selectedProject ? getChildrenCount(selectedProject) : 0}
      />
    </div>
  );
}