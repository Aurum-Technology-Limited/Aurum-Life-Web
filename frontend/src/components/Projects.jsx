import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Grid, 
  List, 
  Calendar,
  Users,
  Clock,
  CheckCircle,
  Circle,
  MoreHorizontal,
  Edit,
  Trash2,
  Archive,
  FolderOpen,
  Target,
  TrendingUp,
  AlertCircle,
  FileText,
  Tag,
  Star,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  BarChart3,
  Settings,
  Copy,
  ExternalLink,
  Download,
  Upload,
  X
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useDataContext } from '../contexts/DataContext';
import { useNotification } from '../contexts/NotificationContext';
import { projectsAPI, areasAPI, projectTemplatesAPI } from '../services/api';
import FileAttachment from './FileAttachment';

const Projects = ({ onSectionChange }) => {
  const { user } = useAuth();
  const { areas, refreshAreas } = useDataContext();
  const { addNotification } = useNotification();
  
  const [projects, setProjects] = useState([]);
  const [filteredProjects, setFilteredProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // UI State
  const [viewMode, setViewMode] = useState('grid'); // 'grid', 'list', 'kanban'
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'active', 'completed', 'archived'
  const [filterArea, setFilterArea] = useState('all');
  const [sortBy, setSortBy] = useState('updated_at'); // 'name', 'created_at', 'updated_at', 'progress'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc', 'desc'
  
  // Modal States
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedProjectForView, setSelectedProjectForView] = useState(null);
  
  // Form States
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    area_id: '',
    status: 'active',
    priority: 'medium',
    start_date: '',
    end_date: '',
    tags: []
  });
  
  // Template States
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  
  // Kanban States
  const [kanbanData, setKanbanData] = useState({
    planning: [],
    active: [],
    review: [],
    completed: []
  });

  // Load projects on component mount
  useEffect(() => {
    loadProjects();
    loadTemplates();
  }, []);

  // Filter and sort projects when dependencies change
  useEffect(() => {
    filterAndSortProjects();
  }, [projects, searchTerm, filterStatus, filterArea, sortBy, sortOrder]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectsAPI.getProjects();
      setProjects(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Error loading projects:', err);
      setError('Failed to load projects');
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to load projects'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await projectTemplatesAPI.getTemplates();
      setTemplates(response.data || []);
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const filterAndSortProjects = () => {
    let filtered = [...projects];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(project => {
        switch (filterStatus) {
          case 'active':
            return project.status === 'active' && !project.archived;
          case 'completed':
            return project.status === 'completed';
          case 'archived':
            return project.archived;
          default:
            return true;
        }
      });
    }

    // Apply area filter
    if (filterArea !== 'all') {
      filtered = filtered.filter(project => project.area_id === filterArea);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      // Handle special cases
      if (sortBy === 'progress') {
        aValue = calculateProgress(a);
        bValue = calculateProgress(b);
      } else if (sortBy === 'area_name') {
        aValue = getAreaName(a.area_id);
        bValue = getAreaName(b.area_id);
      }

      // Handle null/undefined values
      if (aValue == null) aValue = '';
      if (bValue == null) bValue = '';

      // Sort
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredProjects(filtered);
    
    // Update kanban data if in kanban view
    if (viewMode === 'kanban') {
      updateKanbanData(filtered);
    }
  };

  const updateKanbanData = (projectList) => {
    const kanban = {
      planning: projectList.filter(p => p.status === 'planning'),
      active: projectList.filter(p => p.status === 'active' && !p.archived),
      review: projectList.filter(p => p.status === 'review'),
      completed: projectList.filter(p => p.status === 'completed')
    };
    setKanbanData(kanban);
  };

  const calculateProgress = (project) => {
    if (!project.task_count || project.task_count === 0) return 0;
    return Math.round((project.completed_task_count / project.task_count) * 100);
  };

  const getAreaName = (areaId) => {
    const area = areas.find(a => a.id === areaId);
    return area ? area.name : 'No Area';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'planning': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-green-100 text-green-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    
    try {
      let projectData = { ...formData };
      
      // If creating from template
      if (selectedTemplate) {
        const response = await projectTemplatesAPI.createFromTemplate(selectedTemplate, {
          name: formData.name,
          area_id: formData.area_id,
          description: formData.description
        });
        
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Project created from template successfully'
        });
      } else {
        // Regular project creation
        const response = await projectsAPI.create(projectData);
        
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Project created successfully'
        });
      }
      
      await loadProjects();
      await refreshAreas();
      resetForm();
      setShowCreateModal(false);
      setShowTemplateModal(false);
      
    } catch (err) {
      console.error('Error creating project:', err);
      addNotification({
        type: 'error',
        title: 'Error',
        message: err.response?.data?.detail || 'Failed to create project'
      });
    }
  };

  const handleUpdateProject = async (e) => {
    e.preventDefault();
    
    try {
      await projectsAPI.update(selectedProject.id, formData);
      
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Project updated successfully'
      });
      
      await loadProjects();
      await refreshAreas();
      resetForm();
      setShowEditModal(false);
      setSelectedProject(null);
      
    } catch (err) {
      console.error('Error updating project:', err);
      addNotification({
        type: 'error',
        title: 'Error',
        message: err.response?.data?.detail || 'Failed to update project'
      });
    }
  };

  const handleDeleteProject = async () => {
    try {
      await projectsAPI.delete(selectedProject.id);
      
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Project deleted successfully'
      });
      
      await loadProjects();
      await refreshAreas();
      setShowDeleteModal(false);
      setSelectedProject(null);
      
    } catch (err) {
      console.error('Error deleting project:', err);
      addNotification({
        type: 'error',
        title: 'Error',
        message: err.response?.data?.detail || 'Failed to delete project'
      });
    }
  };

  const handleArchiveProject = async (project) => {
    try {
      if (project.archived) {
        await projectsAPI.unarchive(project.id);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Project unarchived successfully'
        });
      } else {
        await projectsAPI.archive(project.id);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Project archived successfully'
        });
      }
      
      await loadProjects();
      await refreshAreas();
      
    } catch (err) {
      console.error('Error archiving project:', err);
      addNotification({
        type: 'error',
        title: 'Error',
        message: err.response?.data?.detail || 'Failed to archive project'
      });
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      area_id: '',
      status: 'active',
      priority: 'medium',
      start_date: '',
      end_date: '',
      tags: []
    });
    setSelectedTemplate('');
  };

  const openEditModal = (project) => {
    setSelectedProject(project);
    setFormData({
      name: project.name,
      description: project.description || '',
      area_id: project.area_id || '',
      status: project.status,
      priority: project.priority || 'medium',
      start_date: project.start_date || '',
      end_date: project.end_date || '',
      tags: project.tags || []
    });
    setShowEditModal(true);
  };

  const openDeleteModal = (project) => {
    setSelectedProject(project);
    setShowDeleteModal(true);
  };

  const openProjectView = (project) => {
    setSelectedProjectForView(project);
  };

  const closeProjectView = () => {
    setSelectedProjectForView(null);
  };

  // Project List View Component
  const ProjectListView = ({ projects }) => (
    <div className="space-y-4">
      {projects.map((project) => (
        <div key={project.id} className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 
                  className="text-lg font-semibold text-white cursor-pointer hover:text-yellow-400"
                  onClick={() => openProjectView(project)}
                >
                  {project.name}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                  {project.status}
                </span>
                {project.priority && (
                  <span className={`text-sm font-medium ${getPriorityColor(project.priority)}`}>
                    {project.priority}
                  </span>
                )}
                {project.archived && (
                  <span className="px-2 py-1 bg-gray-600 text-gray-300 rounded-full text-xs">
                    Archived
                  </span>
                )}
              </div>
              
              {project.description && (
                <p className="text-gray-400 mb-3">{project.description}</p>
              )}
              
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <FolderOpen className="h-4 w-4" />
                  {getAreaName(project.area_id)}
                </span>
                <span className="flex items-center gap-1">
                  <CheckCircle className="h-4 w-4" />
                  {project.completed_task_count || 0}/{project.task_count || 0} tasks
                </span>
                <span className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  {calculateProgress(project)}% complete
                </span>
                {project.end_date && (
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Due {new Date(project.end_date).toLocaleDateString()}
                  </span>
                )}
              </div>
              
              {project.tags && project.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {project.tags.map((tag, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-800 text-gray-300 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-2 ml-4">
              <div className="w-24 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${calculateProgress(project)}%` }}
                />
              </div>
              <span className="text-sm text-gray-400 w-12 text-right">
                {calculateProgress(project)}%
              </span>
              
              <div className="relative">
                <button className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800">
                  <MoreHorizontal className="h-4 w-4" />
                </button>
                {/* Dropdown menu would go here */}
              </div>
            </div>
          </div>
          
          {/* File Attachments Section */}
          <div className="mt-4 pt-4 border-t border-gray-700">
            <FileAttachment 
              parentType="project"
              parentId={project.id}
              parentName={project.name}
            />
          </div>
        </div>
      ))}
    </div>
  );

  // Project Grid View Component
  const ProjectGridView = ({ projects }) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <div key={project.id} className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 
                className="text-lg font-semibold text-white cursor-pointer hover:text-yellow-400 mb-2"
                onClick={() => openProjectView(project)}
              >
                {project.name}
              </h3>
              <div className="flex items-center gap-2 mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                  {project.status}
                </span>
                {project.archived && (
                  <span className="px-2 py-1 bg-gray-600 text-gray-300 rounded-full text-xs">
                    Archived
                  </span>
                )}
              </div>
            </div>
            
            <div className="relative">
              <button className="p-1 text-gray-400 hover:text-white rounded">
                <MoreHorizontal className="h-4 w-4" />
              </button>
            </div>
          </div>
          
          {project.description && (
            <p className="text-gray-400 text-sm mb-4 line-clamp-2">{project.description}</p>
          )}
          
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Area</span>
              <span className="text-gray-300">{getAreaName(project.area_id)}</span>
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Progress</span>
              <span className="text-gray-300">{calculateProgress(project)}%</span>
            </div>
            
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${calculateProgress(project)}%` }}
              />
            </div>
            
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Tasks</span>
              <span className="text-gray-300">
                {project.completed_task_count || 0}/{project.task_count || 0}
              </span>
            </div>
            
            {project.end_date && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Due Date</span>
                <span className="text-gray-300">
                  {new Date(project.end_date).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
          
          {project.tags && project.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-4">
              {project.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="px-2 py-1 bg-gray-800 text-gray-300 rounded text-xs">
                  {tag}
                </span>
              ))}
              {project.tags.length > 3 && (
                <span className="px-2 py-1 bg-gray-800 text-gray-300 rounded text-xs">
                  +{project.tags.length - 3}
                </span>
              )}
            </div>
          )}
          
          {/* File Attachments Section */}
          <div className="mt-4 pt-4 border-t border-gray-700">
            <FileAttachment 
              parentType="project"
              parentId={project.id}
              parentName={project.name}
            />
          </div>
        </div>
      ))}
    </div>
  );

  // Project Kanban View Component
  const ProjectKanbanView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Object.entries(kanbanData).map(([status, projects]) => (
        <div key={status} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white capitalize">{status}</h3>
            <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded-full text-sm">
              {projects.length}
            </span>
          </div>
          
          <div className="space-y-3">
            {projects.map((project) => (
              <div key={project.id} className="bg-gray-800 border border-gray-600 rounded-lg p-3 cursor-pointer hover:border-gray-500">
                <h4 
                  className="font-medium text-white mb-2 hover:text-yellow-400"
                  onClick={() => openProjectView(project)}
                >
                  {project.name}
                </h4>
                
                {project.description && (
                  <p className="text-gray-400 text-sm mb-2 line-clamp-2">{project.description}</p>
                )}
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{getAreaName(project.area_id)}</span>
                  <span>{calculateProgress(project)}%</span>
                </div>
                
                <div className="w-full bg-gray-700 rounded-full h-1 mt-2">
                  <div 
                    className="bg-yellow-500 h-1 rounded-full"
                    style={{ width: `${calculateProgress(project)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading projects...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <p className="text-red-400 mb-4">{error}</p>
          <button 
            onClick={loadProjects}
            className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Projects</h1>
          <p className="text-gray-400 mt-1">Manage your projects and track progress</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowTemplateModal(true)}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center gap-2"
          >
            <Copy className="h-4 w-4" />
            From Template
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            New Project
          </button>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
            </div>
          </div>
          
          {/* Filters */}
          <div className="flex gap-3">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
            
            <select
              value={filterArea}
              onChange={(e) => setFilterArea(e.target.value)}
              className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              <option value="all">All Areas</option>
              {areas && areas.map((area) => (
                <option key={area.id} value={area.id}>{area.name}</option>
              ))}
            </select>
            
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field);
                setSortOrder(order);
              }}
              className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
            >
              <option value="updated_at-desc">Recently Updated</option>
              <option value="created_at-desc">Recently Created</option>
              <option value="name-asc">Name A-Z</option>
              <option value="name-desc">Name Z-A</option>
              <option value="progress-desc">Progress High-Low</option>
              <option value="progress-asc">Progress Low-High</option>
            </select>
          </div>
          
          {/* View Mode */}
          <div className="flex bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-yellow-500 text-gray-900' : 'text-gray-400 hover:text-white'}`}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-yellow-500 text-gray-900' : 'text-gray-400 hover:text-white'}`}
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('kanban')}
              className={`p-2 rounded ${viewMode === 'kanban' ? 'bg-yellow-500 text-gray-900' : 'text-gray-400 hover:text-white'}`}
            >
              <Grid className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Projects Display */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <FolderOpen className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">No projects found</h3>
          <p className="text-gray-500 mb-6">
            {searchTerm || filterStatus !== 'all' || filterArea !== 'all' 
              ? 'Try adjusting your filters or search terms'
              : 'Create your first project to get started'
            }
          </p>
          {!searchTerm && filterStatus === 'all' && filterArea === 'all' && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 font-medium"
            >
              Create Your First Project
            </button>
          )}
        </div>
      ) : (
        <>
          {viewMode === 'grid' && <ProjectGridView projects={filteredProjects} />}
          {viewMode === 'list' && <ProjectListView projects={filteredProjects} />}
          {viewMode === 'kanban' && <ProjectKanbanView />}
        </>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Create New Project</h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
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
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Area
                </label>
                <select
                  value={formData.area_id}
                  onChange={(e) => setFormData({ ...formData, area_id: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="">Select an area</option>
                  {areas && areas.map((area) => (
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
                    <option value="planning">Planning</option>
                    <option value="active">Active</option>
                    <option value="review">Review</option>
                    <option value="completed">Completed</option>
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
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                </div>
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600"
                >
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Template Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Create from Template</h2>
              <button
                onClick={() => {
                  setShowTemplateModal(false);
                  resetForm();
                }}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Select Template *
                </label>
                <select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  required
                >
                  <option value="">Choose a template</option>
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name} ({template.task_count} tasks)
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Area
                </label>
                <select
                  value={formData.area_id}
                  onChange={(e) => setFormData({ ...formData, area_id: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="">Select an area</option>
                  {areas && areas.map((area) => (
                    <option key={area.id} value={area.id}>{area.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowTemplateModal(false);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600"
                >
                  Create from Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Project Modal */}
      {showEditModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Edit Project</h2>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setSelectedProject(null);
                  resetForm();
                }}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <form onSubmit={handleUpdateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
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
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Area
                </label>
                <select
                  value={formData.area_id}
                  onChange={(e) => setFormData({ ...formData, area_id: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                >
                  <option value="">Select an area</option>
                  {areas && areas.map((area) => (
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
                    <option value="planning">Planning</option>
                    <option value="active">Active</option>
                    <option value="review">Review</option>
                    <option value="completed">Completed</option>
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
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  />
                </div>
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedProject(null);
                    resetForm();
                  }}
                  className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600"
                >
                  Update Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">Delete Project</h2>
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedProject(null);
                }}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-4">
                <AlertCircle className="h-8 w-8 text-red-500" />
                <div>
                  <h3 className="font-medium text-white">Are you sure?</h3>
                  <p className="text-gray-400 text-sm">This action cannot be undone.</p>
                </div>
              </div>
              
              <p className="text-gray-300">
                You are about to delete the project <strong>"{selectedProject.name}"</strong>. 
                All associated tasks and data will be permanently removed.
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedProject(null);
                }}
                className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteProject}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Delete Project
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Project Detail View Modal */}
      {selectedProjectForView && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div>
                <h2 className="text-2xl font-semibold text-white">{selectedProjectForView.name}</h2>
                <div className="flex items-center gap-3 mt-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedProjectForView.status)}`}>
                    {selectedProjectForView.status}
                  </span>
                  {selectedProjectForView.priority && (
                    <span className={`text-sm font-medium ${getPriorityColor(selectedProjectForView.priority)}`}>
                      {selectedProjectForView.priority} priority
                    </span>
                  )}
                  {selectedProjectForView.archived && (
                    <span className="px-2 py-1 bg-gray-600 text-gray-300 rounded-full text-xs">
                      Archived
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => openEditModal(selectedProjectForView)}
                  className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleArchiveProject(selectedProjectForView)}
                  className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
                >
                  <Archive className="h-4 w-4" />
                </button>
                <button
                  onClick={() => openDeleteModal(selectedProjectForView)}
                  className="p-2 text-red-400 hover:text-red-300 rounded-lg hover:bg-gray-800"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                <button
                  onClick={closeProjectView}
                  className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Project Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Project Details</h3>
                  <div className="space-y-3">
                    <div>
                      <span className="text-gray-400 text-sm">Area:</span>
                      <p className="text-white">{getAreaName(selectedProjectForView.area_id)}</p>
                    </div>
                    {selectedProjectForView.description && (
                      <div>
                        <span className="text-gray-400 text-sm">Description:</span>
                        <p className="text-white">{selectedProjectForView.description}</p>
                      </div>
                    )}
                    {selectedProjectForView.start_date && (
                      <div>
                        <span className="text-gray-400 text-sm">Start Date:</span>
                        <p className="text-white">{new Date(selectedProjectForView.start_date).toLocaleDateString()}</p>
                      </div>
                    )}
                    {selectedProjectForView.end_date && (
                      <div>
                        <span className="text-gray-400 text-sm">End Date:</span>
                        <p className="text-white">{new Date(selectedProjectForView.end_date).toLocaleDateString()}</p>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4">Progress</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-400 text-sm">Overall Progress</span>
                        <span className="text-white font-medium">{calculateProgress(selectedProjectForView)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-3">
                        <div 
                          className="bg-yellow-500 h-3 rounded-full transition-all duration-300"
                          style={{ width: `${calculateProgress(selectedProjectForView)}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-gray-800 rounded-lg">
                        <div className="text-2xl font-bold text-white">{selectedProjectForView.task_count || 0}</div>
                        <div className="text-gray-400 text-sm">Total Tasks</div>
                      </div>
                      <div className="text-center p-3 bg-gray-800 rounded-lg">
                        <div className="text-2xl font-bold text-green-400">{selectedProjectForView.completed_task_count || 0}</div>
                        <div className="text-gray-400 text-sm">Completed</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Tags */}
              {selectedProjectForView.tags && selectedProjectForView.tags.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedProjectForView.tags.map((tag, index) => (
                      <span key={index} className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* File Attachments */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">File Attachments</h3>
                <FileAttachment 
                  parentType="project"
                  parentId={selectedProjectForView.id}
                  parentName={selectedProjectForView.name}
                />
              </div>
              
              {/* Quick Actions */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Quick Actions</h3>
                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => {
                      closeProjectView();
                      onSectionChange('tasks');
                    }}
                    className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-600 flex items-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    View Tasks
                  </button>
                  <button
                    onClick={() => openEditModal(selectedProjectForView)}
                    className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center gap-2"
                  >
                    <Edit className="h-4 w-4" />
                    Edit Project
                  </button>
                  <button
                    onClick={() => handleArchiveProject(selectedProjectForView)}
                    className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center gap-2"
                  >
                    <Archive className="h-4 w-4" />
                    {selectedProjectForView.archived ? 'Unarchive' : 'Archive'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;