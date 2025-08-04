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
  EyeIcon
} from '@heroicons/react/outline';
import { 
  FolderOpenIcon,
  FolderIcon as FolderIconSolid
} from '@heroicons/react/solid';
import { useAuth } from '../contexts/BackendAuthContext';
import { projectsAPI } from '../services/api';
import ProjectDecompositionHelper from './ProjectDecompositionHelper';

// Memoized ProjectCard component to prevent unnecessary re-renders
const ProjectCard = memo(({ project, onEdit, onDelete, onViewTasks, onUpdateStatus }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'not_started': return 'text-gray-400';
      case 'in_progress': return 'text-blue-400';
      case 'completed': return 'text-green-400';
      case 'on_hold': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
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
            style={{ backgroundColor: project.color || '#F59E0B' }}
          >
            <FolderOpenIcon className="h-5 w-5 text-black" />
          </div>
          <div>
            <h3 className="font-semibold text-white group-hover:text-yellow-400 transition-colors">
              {project.name}
            </h3>
            {project.area_name && (
              <p className="text-sm text-gray-400">{project.area_name}</p>
            )}
          </div>
        </div>
        
        {/* Edit Action Icon */}
        <button 
          className="text-gray-400 hover:text-yellow-400 p-2 rounded-lg hover:bg-gray-700 transition-colors opacity-0 group-hover:opacity-100"
          onClick={(e) => {
            e.stopPropagation(); // Prevent triggering the card click
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
          {project.status?.replace('_', ' ').toUpperCase() || 'NOT STARTED'}
        </span>
        <span className={`text-sm ${getPriorityColor(project.priority)}`}>
          {project.priority?.toUpperCase() || 'MEDIUM'}
        </span>
      </div>

      {project.due_date && (
        <div className="flex items-center text-gray-400 text-sm mb-4">
          <CalendarIcon className="h-4 w-4 mr-1" />
          <span>{new Date(project.due_date).toLocaleDateString()}</span>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          <span className="hover:text-yellow-400 transition-colors">
            {project.task_count ? `${project.task_count} tasks` : '0 tasks'}
          </span>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => onViewTasks(project)}
            className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
            title="View Tasks"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onEdit(project)}
            className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
            title="Edit Project"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => onUpdateStatus(project.id, project.status === 'completed' ? 'in_progress' : 'completed')}
            className="p-1 text-green-400 hover:text-green-300 transition-colors"
            title={project.status === 'completed' ? 'Mark In Progress' : 'Mark Complete'}
          >
            <CheckIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
});

ProjectCard.displayName = 'ProjectCard';

const Projects = memo(({ onSectionChange, sectionParams }) => {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [showDecompositionHelper, setShowDecompositionHelper] = useState(false);
  const [newProjectForDecomposition, setNewProjectForDecomposition] = useState(null);
  const [error, setError] = useState('');
  
  // Extract area filter from section params
  const activeAreaId = sectionParams?.areaId || null;
  const activeAreaName = sectionParams?.areaName || null;
  
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    area_id: '',
    status: 'not_started',
    priority: 'medium',
    color: '#F59E0B',
    icon: 'FolderOpen',
    due_date: ''
  });

  // Memoize filtered projects to prevent recalculation on every render
  const filteredProjects = useMemo(() => {
    return activeAreaId 
      ? projects.filter(project => project.area_id === activeAreaId)
      : projects;
  }, [projects, activeAreaId]);

  // Memoize callbacks to prevent unnecessary re-renders of child components
  const handleViewProjectTasks = useCallback((project) => {
    if (onSectionChange) {
      onSectionChange('tasks', { projectId: project.id, projectName: project.name });
    }
  }, [onSectionChange]);

  const handleEditProject = useCallback((project) => {
    setEditingProject({
      ...project,
      due_date: project.due_date ? new Date(project.due_date).toISOString().split('T')[0] : ''
    });
    setShowEditForm(true);
  }, []);

  const handleDeleteProject = useCallback(async (projectId, projectName) => {
    if (!window.confirm(`Are you sure you want to delete the project "${projectName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendURL}/api/projects/${projectId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      if (response.ok) {
        setProjects(prev => prev.filter(p => p.id !== projectId));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete project');
      }
    } catch (error) {
      console.error('Error deleting project:', error);
      setError('Network error deleting project');
    }
  }, []);

  const updateProjectStatus = useCallback(async (projectId, newStatus) => {
    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendURL}/api/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        const updatedProject = await response.json();
        setProjects(prev => prev.map(p => p.id === projectId ? updatedProject : p));
      }
    } catch (error) {
      console.error('Error updating project status:', error);
    }
  }, []);

  // Update form when activeAreaId changes (for pre-populating area)
  useEffect(() => {
    if (activeAreaId) {
      setNewProject(prev => ({ ...prev, area_id: activeAreaId }));
    }
  }, [activeAreaId]);

  // Load projects and areas
  useEffect(() => {
    if (user) {
      loadProjects();
      loadAreas();
    }
  }, [user]);

  // Set area name when activeAreaId changes
  useEffect(() => {
    if (activeAreaId && areas.length > 0) {
      const area = areas.find(a => a.id === activeAreaId);
      if (area) {
        // Update the sectionParams to include area name for display
        const updatedParams = { ...sectionParams, areaName: area.name };
        // Note: We don't call onSectionChange here to avoid infinite loop
      }
    }
  }, [activeAreaId, areas, sectionParams]);

  const loadProjects = async () => {
    try {
      console.log('🚀 Projects component: Using projectsAPI service with ultra-performance...');
      
      // Use the projectsAPI service which includes ultra-performance optimization
      const response = await projectsAPI.getProjects(null, false); // null for areaId, false for includeArchived
      
      console.log('✅ Projects component: Successfully fetched via projectsAPI service');
      setProjects(response.data || []);
      setError(null);
    } catch (error) {
      console.error('❌ Projects component: Failed to fetch projects:', error);
      setError('Network error loading projects');
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAreas = async () => {
    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendURL}/api/areas`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAreas(data || []);
      }
    } catch (error) {
      console.error('Error loading areas:', error);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const projectData = {
        ...newProject,
        due_date: newProject.due_date ? new Date(newProject.due_date).toISOString() : null
      };

      const response = await fetch(`${backendURL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify(projectData),
      });

      if (response.ok) {
        const createdProject = await response.json();
        setProjects(prev => [...prev, createdProject]);
        
        // Store the created project for potential decomposition
        setNewProjectForDecomposition(createdProject);
        
        // Reset form
        setNewProject({
          name: '',
          description: '',
          area_id: '',
          status: 'not_started',
          priority: 'medium',
          color: '#F59E0B',
          icon: 'FolderOpen',
          due_date: ''
        });
        setShowCreateForm(false);
        
        // Ask user if they want to break down the project
        if (window.confirm('Project created successfully! Would you like to break it down into tasks using AI suggestions?')) {
          setShowDecompositionHelper(true);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create project');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      setError('Network error creating project');
    }
  };

  const handleTasksCreated = async (suggestedTasks) => {
    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const createdTasks = [];
      
      // Create each suggested task using the tasks API
      for (const taskSuggestion of suggestedTasks) {
        const taskData = {
          name: taskSuggestion.name,
          description: '',
          project_id: newProjectForDecomposition.id,
          priority: taskSuggestion.priority,
          estimated_duration: taskSuggestion.estimated_duration,
          status: 'todo',
          completed: false
        };

        const response = await fetch(`${backendURL}/api/tasks`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
          },
          body: JSON.stringify(taskData),
        });

        if (response.ok) {
          const createdTask = await response.json();
          createdTasks.push(createdTask);
        }
      }
      
      // Close decomposition helper
      setShowDecompositionHelper(false);
      setNewProjectForDecomposition(null);
      
      // Show success message
      alert(`Successfully created ${createdTasks.length} tasks for your project!`);
      
      // Refresh projects to show updated task counts
      loadProjects();
      
    } catch (error) {
      console.error('Error creating tasks:', error);
      setError('Failed to create tasks from suggestions');
    }
  };

  const handleCancelDecomposition = () => {
    setShowDecompositionHelper(false);
    setNewProjectForDecomposition(null);
  };

  const handleUpdateProject = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const projectData = {
        ...editingProject,
        due_date: editingProject.due_date ? new Date(editingProject.due_date).toISOString() : null
      };

      const response = await fetch(`${backendURL}/api/projects/${editingProject.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify(projectData),
      });

      if (response.ok) {
        const updatedProject = await response.json();
        setProjects(prev => prev.map(p => p.id === updatedProject.id ? updatedProject : p));
        setShowEditForm(false);
        setEditingProject(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update project');
      }
    } catch (error) {
      console.error('Error updating project:', error);
      setError('Network error updating project');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-400">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white">Projects</h1>
            {activeAreaId && sectionParams?.areaName && (
              <>
                <span className="text-2xl text-gray-500">›</span>
                <div className="flex items-center space-x-2">
                  <FolderIcon className="h-5 w-5 text-yellow-400" />
                  <span className="text-xl font-medium text-yellow-400">{sectionParams.areaName}</span>
                </div>
              </>
            )}
          </div>
          <p className="text-gray-400 mt-1">
            {activeAreaId && sectionParams?.areaName
              ? `Projects within the ${sectionParams.areaName} area`
              : 'Manage your life projects and track progress'
            }
          </p>
          {activeAreaId && (
            <button
              onClick={() => onSectionChange('areas')}
              className="mt-2 text-sm text-yellow-400 hover:text-yellow-300 transition-colors"
            >
              ← Back to all areas
            </button>
          )}
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-medium hover:bg-yellow-600 transition-colors flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Project</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 text-red-300 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Edit Project Form */}
      {showEditForm && editingProject && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <form onSubmit={handleUpdateProject} className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">Edit Project</h3>
              <button
                type="button"
                onClick={() => {
                  setShowEditForm(false);
                  setEditingProject(null);
                }}
                className="text-gray-400 hover:text-white"
              >
                <XIcon className="h-5 w-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  value={editingProject.name}
                  onChange={(e) => setEditingProject({...editingProject, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                  placeholder="Enter project name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Area
                </label>
                <select
                  value={editingProject.area_id || ''}
                  onChange={(e) => setEditingProject({...editingProject, area_id: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="">Select an area (optional)</option>
                  {areas.map((area) => (
                    <option key={area.id} value={area.id}>{area.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={editingProject.status || 'not_started'}
                  onChange={(e) => setEditingProject({...editingProject, status: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="not_started">Not Started</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="on_hold">On Hold</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Priority
                </label>
                <select
                  value={editingProject.priority || 'medium'}
                  onChange={(e) => setEditingProject({...editingProject, priority: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Due Date
                </label>
                <input
                  type="date"
                  value={editingProject.due_date || ''}
                  onChange={(e) => setEditingProject({...editingProject, due_date: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={editingProject.description || ''}
                onChange={(e) => setEditingProject({...editingProject, description: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                rows="3"
                placeholder="Project description (optional)"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                className="bg-yellow-500 text-black px-4 py-2 rounded-md font-medium hover:bg-yellow-600 transition-colors"
              >
                Update Project
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowEditForm(false);
                  setEditingProject(null);
                }}
                className="bg-gray-600 text-white px-4 py-2 rounded-md font-medium hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Create Project Form */}
      {showCreateForm && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <form onSubmit={handleCreateProject} className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-white">Create New Project</h3>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="text-gray-400 hover:text-white"
              >
                <XIcon className="h-5 w-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                  placeholder="Enter project name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Area
                </label>
                <select
                  value={newProject.area_id}
                  onChange={(e) => setNewProject({...newProject, area_id: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="">Select an area (optional)</option>
                  {areas.map((area) => (
                    <option key={area.id} value={area.id}>{area.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Priority
                </label>
                <select
                  value={newProject.priority}
                  onChange={(e) => setNewProject({...newProject, priority: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Due Date
                </label>
                <input
                  type="date"
                  value={newProject.due_date}
                  onChange={(e) => setNewProject({...newProject, due_date: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={newProject.description}
                onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-yellow-500"
                rows="3"
                placeholder="Project description (optional)"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                className="bg-yellow-500 text-black px-4 py-2 rounded-md font-medium hover:bg-yellow-600 transition-colors"
              >
                Create Project
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="bg-gray-600 text-white px-4 py-2 rounded-md font-medium hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onEdit={handleEditProject}
            onDelete={handleDeleteProject}
            onViewTasks={handleViewProjectTasks}
            onUpdateStatus={updateProjectStatus}
          />
        ))}

        {filteredProjects.length === 0 && !showCreateForm && (
          <div className="col-span-full text-center py-12">
            <FolderIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">
              {activeAreaId && sectionParams?.areaName 
                ? `No projects in ${sectionParams.areaName} yet`
                : 'No projects yet'
              }
            </h3>
            <p className="text-gray-400 mb-4">
              {activeAreaId && sectionParams?.areaName
                ? `Create your first project in the ${sectionParams.areaName} area`
                : 'Create your first project to get started'
              }
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-medium hover:bg-yellow-600 transition-colors"
            >
              Create Project
            </button>
          </div>
        )}
      </div>
      
      {/* Project Decomposition Helper */}
      {showDecompositionHelper && newProjectForDecomposition && (
        <ProjectDecompositionHelper
          projectName={newProjectForDecomposition.name}
          projectDescription={newProjectForDecomposition.description}
          onTasksCreated={handleTasksCreated}
          onCancel={handleCancelDecomposition}
        />
      )}
    </div>
  );
});

Projects.displayName = 'Projects';

export default Projects;