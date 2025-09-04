import React, { useState, useEffect, memo, useMemo, useCallback } from 'react';
import { 
  FolderIcon, 
  PlusIcon, 
  DotsVerticalIcon, 
  CalendarIcon, 
  CheckIcon,
  XIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  DocumentTextIcon
} from '@heroicons/react/outline';
import { 
  FolderOpenIcon,
  FolderIcon as FolderIconSolid
} from '@heroicons/react/solid';
import { useAuth } from '../contexts/BackendAuthContext';
import { 
  useProjects, 
  useCreateProject, 
  useUpdateProject,
  useAreas 
} from '../hooks/useGraphQL';
import ProjectDecompositionHelper from './ProjectDecompositionHelper';
import FileAttachment from './ui/FileAttachment';
import { OptimizedProjectCard } from './optimized/OptimizedLists';

const ProjectCard = memo(({ project, onEdit, onDelete, onViewTasks, onUpdateStatus }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'NOT_STARTED': return 'text-gray-400';
      case 'IN_PROGRESS': return 'text-blue-400';
      case 'COMPLETED': return 'text-green-400';
      case 'ON_HOLD': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'HIGH': return 'text-red-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'LOW': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div 
      className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors group cursor-pointer"
      onClick={() => onViewTasks(project)}
      title="Click to view project tasks"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="p-2 rounded-lg"
            style={{ backgroundColor: project.area?.color || '#F59E0B' }}
          >
            <FolderOpenIcon className="h-5 w-5 text-black" />
          </div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-yellow-400 transition-colors">
              {project.name}
            </h3>
            {project.area && (
              <p className="text-sm text-gray-400">{project.area.name}</p>
            )}
          </div>
        </div>
        
        {/* Edit Action Icon */}
        <button 
          className="text-gray-400 hover:text-yellow-400 p-2 rounded-lg hover:bg-gray-700 transition-colors opacity-0 group-hover:opacity-100"
          onClick={(e) => {
            e.stopPropagation();
            onEdit(project);
          }}
          title="Edit project"
        >
          <PencilIcon className="h-4 w-4" />
        </button>
      </div>

      {project.description && (
        <p className="text-gray-300 text-sm mb-4 line-clamp-2">
          {project.description}
        </p>
      )}

      <div className="flex items-center justify-between mb-4">
        <span className={`text-sm font-medium ${getStatusColor(project.status)}`}>
          {project.status.replace('_', ' ')}
        </span>
        <span className={`text-sm ${getPriorityColor(project.priority)}`}>
          {project.priority}
        </span>
      </div>

      {project.deadline && (
        <div className="flex items-center text-gray-400 text-sm mb-4">
          <CalendarIcon className="h-4 w-4 mr-1" />
          <span>Due {new Date(project.deadline).toLocaleDateString()}</span>
        </div>
      )}

      {/* Progress Bar */}
      <div className="w-full bg-gray-700 rounded-full h-2 mb-4">
        <div 
          className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
          style={{ width: `${project.completionPercentage || 0}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-400">
          {project.completionPercentage || 0}% Complete
        </span>
        <div className="flex items-center space-x-2">
          {project.tasks && (
            <span className="text-gray-400">
              {project.tasks.filter(t => t.completed).length}/{project.tasks.length} tasks
            </span>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-end space-x-2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onUpdateStatus(project);
          }}
          className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
        >
          Update Status
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(project.id);
          }}
          className="px-3 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
});

ProjectCard.displayName = 'ProjectCard';

const Projects = ({ onSectionChange, viewContext = {} }) => {
  const { user } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [selectedAreaFilter, setSelectedAreaFilter] = useState(viewContext.areaId || 'all');
  const [showArchived, setShowArchived] = useState(false);
  const [showDecompositionHelper, setShowDecompositionHelper] = useState(false);
  const [decompositionProject, setDecompositionProject] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    area_id: '',
    priority: 'MEDIUM',
    deadline: '',
    status: 'NOT_STARTED',
    icon: '🚀'
  });

  // GraphQL Hooks
  const filter = {
    areaId: selectedAreaFilter !== 'all' ? selectedAreaFilter : null,
    archived: showArchived
  };
  
  const { projects, loading: projectsLoading, error: projectsError, refetch } = useProjects(filter);
  const { areas, loading: areasLoading } = useAreas();
  const { createProject, loading: creating } = useCreateProject();
  const { updateProject, loading: updating } = useUpdateProject();

  // Group projects by area
  const projectsByArea = useMemo(() => {
    const grouped = {};
    projects.forEach(project => {
      const areaId = project.area?.id || 'no-area';
      if (!grouped[areaId]) {
        grouped[areaId] = {
          area: project.area,
          projects: []
        };
      }
      grouped[areaId].projects.push(project);
    });
    return grouped;
  }, [projects]);

  // Statistics
  const stats = useMemo(() => {
    const total = projects.length;
    const completed = projects.filter(p => p.status === 'COMPLETED').length;
    const inProgress = projects.filter(p => p.status === 'IN_PROGRESS').length;
    const onHold = projects.filter(p => p.status === 'ON_HOLD').length;
    const notStarted = projects.filter(p => p.status === 'NOT_STARTED').length;
    
    return { total, completed, inProgress, onHold, notStarted };
  }, [projects]);

  // Handlers
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (editingProject) {
      const input = {
        id: editingProject.id,
        name: formData.name,
        description: formData.description,
        status: formData.status,
        priority: formData.priority,
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null,
        completionPercentage: formData.completion_percentage
      };
      
      await updateProject(input);
    } else {
      const input = {
        areaId: formData.area_id,
        name: formData.name,
        description: formData.description,
        icon: formData.icon,
        deadline: formData.deadline ? new Date(formData.deadline).toISOString() : null,
        priority: formData.priority,
        importance: 3
      };
      
      await createProject(input);
    }
    
    setShowModal(false);
    resetForm();
    refetch();
  };

  const handleDelete = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project? This will also delete all associated tasks.')) {
      // TODO: Implement delete mutation
      console.log('Delete project:', projectId);
      refetch();
    }
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      name: project.name,
      description: project.description || '',
      area_id: project.area?.id || '',
      priority: project.priority,
      deadline: project.deadline ? project.deadline.split('T')[0] : '',
      status: project.status,
      icon: project.icon || '🚀',
      completion_percentage: project.completionPercentage || 0
    });
    setShowModal(true);
  };

  const handleUpdateStatus = async (project) => {
    const statusFlow = ['NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD'];
    const currentIndex = statusFlow.indexOf(project.status);
    const nextStatus = statusFlow[(currentIndex + 1) % statusFlow.length];
    
    const input = {
      id: project.id,
      status: nextStatus
    };
    
    await updateProject(input);
    refetch();
  };

  const handleViewTasks = (project) => {
    onSectionChange('tasks', { projectId: project.id, projectName: project.name });
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      area_id: '',
      priority: 'MEDIUM',
      deadline: '',
      status: 'NOT_STARTED',
      icon: '🚀'
    });
    setEditingProject(null);
  };

  if (projectsLoading || areasLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
      </div>
    );
  }

  if (projectsError) {
    return (
      <div className="text-center text-red-400 p-8">
        <p>Error loading projects: {projectsError.message}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Projects</h1>
          <p className="text-gray-400 mt-1">
            {stats.total} projects • {stats.completed} completed • {stats.inProgress} in progress
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-yellow-400 hover:bg-yellow-500 text-black font-medium rounded-lg transition-colors"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Project</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <select
          value={selectedAreaFilter}
          onChange={(e) => setSelectedAreaFilter(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
        >
          <option value="all">All Areas</option>
          {areas.map(area => (
            <option key={area.id} value={area.id}>
              {area.name}
            </option>
          ))}
        </select>
        
        <label className="flex items-center space-x-2 text-gray-400">
          <input
            type="checkbox"
            checked={showArchived}
            onChange={(e) => setShowArchived(e.target.checked)}
            className="rounded bg-gray-700 border-gray-600 text-yellow-400"
          />
          <span>Show archived</span>
        </label>
      </div>

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="text-center py-12">
          <FolderIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No projects yet. Create your first project to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onViewTasks={handleViewTasks}
              onUpdateStatus={handleUpdateStatus}
            />
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-semibold text-white mb-4">
              {editingProject ? 'Edit Project' : 'Create New Project'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Project Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Area
                </label>
                <select
                  value={formData.area_id}
                  onChange={(e) => setFormData({ ...formData, area_id: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  required={!editingProject}
                >
                  <option value="">Select an area</option>
                  {areas.map(area => (
                    <option key={area.id} value={area.id}>
                      {area.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Priority
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Deadline
                  </label>
                  <input
                    type="date"
                    value={formData.deadline}
                    onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  />
                </div>
              </div>

              {editingProject && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                  >
                    <option value="NOT_STARTED">Not Started</option>
                    <option value="IN_PROGRESS">In Progress</option>
                    <option value="COMPLETED">Completed</option>
                    <option value="ON_HOLD">On Hold</option>
                  </select>
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || updating}
                  className="px-4 py-2 bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-600 text-black font-medium rounded-lg"
                >
                  {creating || updating ? 'Saving...' : (editingProject ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Project Decomposition Helper */}
      {showDecompositionHelper && decompositionProject && (
        <ProjectDecompositionHelper
          project={decompositionProject}
          onClose={() => {
            setShowDecompositionHelper(false);
            setDecompositionProject(null);
          }}
          onTasksCreated={() => {
            refetch();
          }}
        />
      )}
    </div>
  );
};

export default Projects;