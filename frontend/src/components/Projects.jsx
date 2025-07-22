import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Calendar, 
  Target, 
  CheckCircle2,
  Circle,
  AlertCircle,
  X,
  Save,
  FolderOpen,
  Clock,
  BarChart3,
  ArrowRight,
  Archive,
  ArchiveRestore,
  Eye,
  EyeOff,
  List,
  ArrowLeft
} from 'lucide-react';
import { projectsAPI, areasAPI, tasksAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import KanbanBoard from './KanbanBoard';
import DonutChart from './ui/DonutChart';

const Projects = ({ onSectionChange, filterAreaId }) => {
  const { onDataMutation } = useDataContext();
  const [projects, setProjects] = useState([]);
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [selectedArea, setSelectedArea] = useState(filterAreaId || '');
  const [showKanban, setShowKanban] = useState(false);
  const [showListView, setShowListView] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectTasks, setProjectTasks] = useState([]);
  const [projectTasksLoading, setProjectTasksLoading] = useState(false);
  const [showArchived, setShowArchived] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    area_id: '',
    status: 'Not Started',
    priority: 'medium',
    due_date: '',
    target_completion: ''
  });

  const statusOptions = [
    { value: 'Not Started', label: 'Not Started', color: 'text-blue-400 bg-blue-400/10' },
    { value: 'In Progress', label: 'In Progress', color: 'text-green-400 bg-green-400/10' },
    { value: 'On Hold', label: 'On Hold', color: 'text-yellow-400 bg-yellow-400/10' },
    { value: 'Completed', label: 'Completed', color: 'text-gray-400 bg-gray-400/10' }
  ];

  const priorityOptions = [
    { value: 'low', label: 'Low', color: 'text-green-400 bg-green-400/10' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400 bg-yellow-400/10' },
    { value: 'high', label: 'High', color: 'text-red-400 bg-red-400/10' }
  ];

  const handleAreaChange = (e) => {
    const selectedAreaId = e.target.value;
    console.log('🔍 Area dropdown changed:', { selectedAreaId, formDataBefore: formData.area_id });
    
    // Ensure immutable state update
    setFormData(prevData => ({ 
      ...prevData, 
      area_id: selectedAreaId 
    }));
    
    console.log('✅ Area state should be updated to:', selectedAreaId);
  };

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectsAPI.getProjects(selectedArea || null, showArchived);
      setProjects(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load projects');
      console.error('Error loading projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAreas = async () => {
    try {
      console.log('Loading areas...'); // Debug log
      const response = await areasAPI.getAreas(false);
      console.log('Areas loaded:', response.data); // Debug log
      setAreas(response.data);
    } catch (err) {
      console.error('Error loading areas:', err);
      setError('Failed to load areas. Please refresh the page.');
    }
  };

  useEffect(() => {
    loadAreas();
  }, []);

  useEffect(() => {
    loadProjects();
  }, [selectedArea, showArchived]); // Reload when selectedArea or showArchived changes

  // Debug: Watch for formData changes
  useEffect(() => {
    console.log('📝 FormData updated:', formData);
  }, [formData]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Form Data:', formData); // Debug log
    
    try {
      const submitData = {
        area_id: formData.area_id,
        name: formData.name,
        description: formData.description,
        status: formData.status,
        priority: formData.priority,
        deadline: formData.due_date || null,
        // Note: target_completion removed as it's not in the backend model
      };
      
      console.log('Submit Data:', submitData); // Debug log
      
      if (editingProject) {
        await projectsAPI.updateProject(editingProject.id, submitData);
        // Notify data context of the mutation
        onDataMutation('project', 'update', { projectId: editingProject.id, ...submitData });
      } else {
        const response = await projectsAPI.createProject(submitData);
        // Notify data context of the mutation
        onDataMutation('project', 'create', response.data || submitData);
      }
      loadProjects();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving project:', err);
      setError(editingProject ? 'Failed to update project' : 'Failed to create project');
    }
  };

  const handleArchive = async (projectId, isArchived) => {
    try {
      if (isArchived) {
        await projectsAPI.unarchiveProject(projectId);
        // Notify data context of the mutation
        onDataMutation('project', 'unarchive', { projectId });
      } else {
        await projectsAPI.archiveProject(projectId);
        // Notify data context of the mutation  
        onDataMutation('project', 'archive', { projectId });
      }
      loadProjects();
    } catch (err) {
      console.error('Error archiving/unarchiving project:', err);
      setError(`Failed to ${isArchived ? 'unarchive' : 'archive'} project`);
    }
  };

  const handleDelete = async (projectId) => {
    if (window.confirm('Are you sure? This will delete all tasks in this project.')) {
      try {
        await projectsAPI.deleteProject(projectId);
        loadProjects();
        // Notify data context of the mutation
        onDataMutation('project', 'delete', { projectId });
      } catch (err) {
        console.error('Error deleting project:', err);
        setError('Failed to delete project');
      }
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingProject(null);
    setFormData({
      name: '',
      description: '',
      area_id: selectedArea || '',
      status: 'Not Started',
      priority: 'medium',
      due_date: '',
      target_completion: ''
    });
  };

  const handleEdit = (project) => {
    setEditingProject(project);
    setFormData({
      name: project.name,
      description: project.description || '',
      area_id: project.area_id || '',
      status: project.status || 'Not Started',
      priority: project.priority || 'medium',
      due_date: project.deadline ? new Date(project.deadline).toISOString().split('T')[0] : '',
      target_completion: project.target_completion ? new Date(project.target_completion).toISOString().split('T')[0] : ''
    });
    setShowModal(true);
  };

  const getStatusColor = (status) => {
    const statusOption = statusOptions.find(opt => opt.value === status);
    return statusOption ? statusOption.color : 'text-gray-400 bg-gray-400/10';
  };

  const getPriorityColor = (priority) => {
    const priorityOption = priorityOptions.find(opt => opt.value === priority);
    return priorityOption ? priorityOption.color : 'text-gray-400 bg-gray-400/10';
  };

  const getProgressPercentage = (project) => {
    if (!project.total_tasks || project.total_tasks === 0) return 0;
    return Math.round((project.completed_tasks / project.total_tasks) * 100);
  };

  const handleKanban = (projectId) => {
    setSelectedProjectId(projectId);
    setShowKanban(true);
  };

  const handleBackFromKanban = () => {
    setShowKanban(false);
    setSelectedProjectId(null);
  };

  const isOverdue = (dueDate) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  if (showKanban && selectedProjectId) {
    return <KanbanBoard projectId={selectedProjectId} onBack={handleBackFromKanban} />;
  }

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-64 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
              Projects
            </h1>
            <p className="text-gray-400 mt-1">
              Manage your active projects and goals
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {/* Archive Toggle */}
            <button
              onClick={() => setShowArchived(!showArchived)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                showArchived 
                  ? 'bg-gray-700 text-white border border-gray-600' 
                  : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700'
              }`}
            >
              {showArchived ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              <span>{showArchived ? 'Hide Archived' : 'Show Archived'}</span>
            </button>
            {/* Area Filter */}
            <select
              value={selectedArea}
              onChange={(e) => setSelectedArea(e.target.value)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              <option value="">All Areas</option>
              {areas.map(area => (
                <option key={area.id} value={area.id}>{area.name}</option>
              ))}
            </select>
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              <Plus className="h-5 w-5" />
              <span>New Project</span>
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <span className="text-red-400">{error}</span>
            </div>
          </div>
        )}

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen className="mx-auto h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No projects yet</h3>
            <p className="text-gray-500 mb-6">Create your first project to get started</p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 rounded-lg font-medium"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              Create First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className={`bg-gray-900/50 border rounded-xl p-6 hover:border-gray-700 transition-all duration-200 hover:shadow-lg ${
                  project.archived ? 'border-gray-700 opacity-75' : 'border-gray-800'
                }`}
              >
                {/* Project Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-white text-lg">{project.name}</h3>
                      <div className="flex space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(project.status)}`}>
                          {project.status}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(project.priority)}`}>
                          {project.priority}
                        </span>
                        {project.archived && (
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-600 text-gray-300">
                            Archived
                          </span>
                        )}
                      </div>
                    </div>
                    {project.area_name && (
                      <p className="text-sm text-gray-400">{project.area_name}</p>
                    )}
                  </div>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleArchive(project.id, project.archived)}
                      className={`p-2 rounded-lg transition-colors ${
                        project.archived
                          ? 'text-blue-400 hover:text-blue-300 hover:bg-gray-800'
                          : 'text-gray-400 hover:text-yellow-400 hover:bg-gray-800'
                      }`}
                      title={project.archived ? 'Unarchive Project' : 'Archive Project'}
                    >
                      {project.archived ? <ArchiveRestore className="h-4 w-4" /> : <Archive className="h-4 w-4" />}
                    </button>
                    <button
                      onClick={() => handleEdit(project)}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(project.id)}
                      className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                {project.description && (
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {project.description}
                  </p>
                )}

                {/* Enhanced Progress Visualization */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Progress</span>
                    <span className="text-sm font-medium text-white">
                      {getProgressPercentage(project)}%
                    </span>
                  </div>
                  
                  {/* Traditional Progress Bar */}
                  <div className="w-full bg-gray-800 rounded-full h-2 mb-3">
                    <div
                      className="h-2 rounded-full transition-all duration-300"
                      style={{
                        backgroundColor: '#F4B400',
                        width: `${getProgressPercentage(project)}%`
                      }}
                    />
                  </div>
                  
                  <p className="text-xs text-gray-500 mb-3">
                    {project.completed_tasks || 0} of {project.total_tasks || 0} tasks complete
                  </p>

                  {/* Enhanced Donut Chart Visualization */}
                  {(project.total_tasks || 0) > 0 && (
                    <div className="flex justify-center">
                      <DonutChart
                        data={{
                          labels: ['Completed', 'In Progress', 'To Do'],
                          values: [
                            project.completed_tasks || 0,
                            project.active_tasks || 0,
                            Math.max(0, (project.total_tasks || 0) - (project.completed_tasks || 0) - (project.active_tasks || 0))
                          ],
                          colors: [
                            '#10B981', // Green for completed
                            '#F4B400', // Aurum gold for in progress  
                            '#6B7280', // Gray for to do
                          ]
                        }}
                        size="sm"
                        showLegend={false}
                      />
                    </div>
                  )}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-lg font-bold text-white">
                      {project.total_tasks || 0}
                    </p>
                    <p className="text-xs text-gray-500">Total Tasks</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-white">
                      {project.active_tasks || 0}
                    </p>
                    <p className="text-xs text-gray-500">Active Tasks</p>
                  </div>
                </div>

                {/* Due Date */}
                {project.due_date && (
                  <div className={`flex items-center space-x-2 text-sm mb-4 ${
                    isOverdue(project.due_date) ? 'text-red-400' : 'text-gray-400'
                  }`}>
                    <Clock className="h-4 w-4" />
                    <span>
                      Due: {new Date(project.due_date).toLocaleDateString()}
                      {isOverdue(project.due_date) && ' (Overdue)'}
                    </span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-2">
                  <button 
                    onClick={() => handleKanban(project.id)}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                  >
                    <BarChart3 className="h-4 w-4" />
                    <span>Kanban View</span>
                  </button>
                  <button 
                    onClick={() => onSectionChange && onSectionChange('tasks', { projectId: project.id })}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    <span>List View</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md border border-gray-800 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {editingProject ? 'Edit Project' : 'Create New Project'}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="p-2 text-gray-400 hover:text-white rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="e.g., Build Personal Website"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="What is this project about?"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Area
                  </label>
                  <select
                    value={formData.area_id}
                    onChange={(e) => {
                      console.log('🚨 DIRECT onChange fired with value:', e.target.value);
                      setFormData({ ...formData, area_id: e.target.value });
                      console.log('🔧 Updated formData with area_id:', e.target.value);
                    }}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  >
                    <option value="">Select an area</option>
                    {areas.map(area => (
                      <option key={area.id} value={area.id}>{area.name}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    >
                      {statusOptions.map(status => (
                        <option key={status.value} value={status.value}>{status.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Priority
                    </label>
                    <select
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    >
                      {priorityOptions.map(priority => (
                        <option key={priority.value} value={priority.value}>{priority.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Due Date
                  </label>
                  <input
                    type="date"
                    value={formData.due_date}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors"
                    style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                  >
                    <Save className="h-4 w-4" />
                    <span>{editingProject ? 'Update' : 'Create'}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;