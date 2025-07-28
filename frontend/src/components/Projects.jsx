import React, { useState, useEffect } from 'react';
import { 
  FolderIcon, 
  PlusIcon, 
  DotsVerticalIcon, 
  CalendarIcon, 
  CheckIcon,
  XIcon
} from '@heroicons/react/outline';
import { 
  FolderOpenIcon,
  FolderIcon as FolderIconSolid
} from '@heroicons/react/solid';
import { useAuth } from '../contexts/SupabaseAuthContext';

const Projects = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState([]);
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [error, setError] = useState('');
  
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

  // Load projects and areas
  useEffect(() => {
    if (user) {
      loadProjects();
      loadAreas();
    }
  }, [user]);

  const loadProjects = async () => {
    try {
      const backendURL = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendURL}/api/projects?include_tasks=true`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data || []);
      } else {
        setError('Failed to load projects');
      }
    } catch (error) {
      console.error('Error loading projects:', error);
      setError('Network error loading projects');
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
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create project');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      setError('Network error creating project');
    }
  };

  const updateProjectStatus = async (projectId, newStatus) => {
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
  };

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
          <h1 className="text-2xl font-bold text-white">Projects</h1>
          <p className="text-gray-400 mt-1">Manage your life projects and track progress</p>
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
        {projects.map((project) => (
          <div
            key={project.id}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
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
                  <h3 className="font-semibold text-white">{project.name}</h3>
                  {project.area_name && (
                    <p className="text-sm text-gray-400">{project.area_name}</p>
                  )}
                </div>
              </div>
              <button className="text-gray-400 hover:text-white">
                <DotsVerticalIcon className="h-5 w-5" />
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
                {project.tasks ? `${project.tasks.length} tasks` : '0 tasks'}
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => updateProjectStatus(project.id, 'in_progress')}
                  className="p-1 text-blue-400 hover:text-blue-300"
                  title="Mark In Progress"
                >
                  <FolderIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => updateProjectStatus(project.id, 'completed')}
                  className="p-1 text-green-400 hover:text-green-300"
                  title="Mark Complete"
                >
                  <CheckIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {projects.length === 0 && !showCreateForm && (
          <div className="col-span-full text-center py-12">
            <FolderIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No projects yet</h3>
            <p className="text-gray-400 mb-4">Create your first project to get started</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-yellow-500 text-black px-4 py-2 rounded-lg font-medium hover:bg-yellow-600 transition-colors"
            >
              Create Project
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;