import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Save,
  X,
  AlertCircle,
  FileText,
  Clock,
  Target,
  ArrowRight,
  Copy
} from 'lucide-react';
import { projectTemplatesAPI, areasAPI, projectsAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';

const ProjectTemplates = ({ onSectionChange }) => {
  const { onDataMutation } = useDataContext();
  const [templates, setTemplates] = useState([]);
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showUseModal, setShowUseModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    tasks: []
  });

  const [useFormData, setUseFormData] = useState({
    area_id: '',
    name: '',
    description: '',
    status: 'Not Started',
    priority: 'medium'
  });

  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    priority: 'medium',
    estimated_duration: 60
  });

  const priorityOptions = [
    { value: 'low', label: 'Low', color: 'text-green-400 bg-green-400/10' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-400 bg-yellow-400/10' },
    { value: 'high', label: 'High', color: 'text-red-400 bg-red-400/10' }
  ];

  const statusOptions = [
    { value: 'Not Started', label: 'Not Started', color: 'text-blue-400 bg-blue-400/10' },
    { value: 'In Progress', label: 'In Progress', color: 'text-green-400 bg-green-400/10' },
    { value: 'On Hold', label: 'On Hold', color: 'text-yellow-400 bg-yellow-400/10' },
    { value: 'Completed', label: 'Completed', color: 'text-gray-400 bg-gray-400/10' }
  ];

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await projectTemplatesAPI.getTemplates();
      setTemplates(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load templates');
      console.error('Error loading templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAreas = async () => {
    try {
      const response = await areasAPI.getAreas(false);
      setAreas(response.data);
    } catch (err) {
      console.error('Error loading areas:', err);
      setError('Failed to load areas. Please refresh the page.');
    }
  };

  useEffect(() => {
    loadTemplates();
    loadAreas();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTemplate) {
        await projectTemplatesAPI.updateTemplate(editingTemplate.id, formData);
        onDataMutation('template', 'update', { templateId: editingTemplate.id, ...formData });
      } else {
        const response = await projectTemplatesAPI.createTemplate(formData);
        onDataMutation('template', 'create', response.data || formData);
      }
      loadTemplates();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving template:', err);
      setError(editingTemplate ? 'Failed to update template' : 'Failed to create template');
    }
  };

  const handleUseTemplate = async (e) => {
    e.preventDefault();
    try {
      const response = await projectTemplatesAPI.useTemplate(selectedTemplate.id, useFormData);
      onDataMutation('project', 'create', response.data || useFormData);
      handleCloseUseModal();
      // Optionally navigate to the created project or projects list
      if (onSectionChange) {
        onSectionChange('projects');
      }
    } catch (err) {
      console.error('Error using template:', err);
      setError('Failed to create project from template');
    }
  };

  const handleDelete = async (templateId) => {
    if (window.confirm('Are you sure? This will delete the template permanently.')) {
      try {
        await projectTemplatesAPI.deleteTemplate(templateId);
        loadTemplates();
        onDataMutation('template', 'delete', { templateId });
      } catch (err) {
        console.error('Error deleting template:', err);
        setError('Failed to delete template');
      }
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingTemplate(null);
    setFormData({
      name: '',
      description: '',
      category: '',
      tasks: []
    });
    setNewTask({
      name: '',
      description: '',
      priority: 'medium',
      estimated_duration: 60
    });
  };

  const handleCloseUseModal = () => {
    setShowUseModal(false);
    setSelectedTemplate(null);
    setUseFormData({
      area_id: '',
      name: '',
      description: '',
      status: 'Not Started',
      priority: 'medium'
    });
  };

  const handleEdit = (template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      category: template.category || '',
      tasks: template.tasks || []
    });
    setShowModal(true);
  };

  const handleUse = (template) => {
    setSelectedTemplate(template);
    setUseFormData({
      area_id: '',
      name: template.name.replace('Template', 'Project'),
      description: template.description || '',
      status: 'Not Started',
      priority: 'medium'
    });
    setShowUseModal(true);
  };

  const addTask = () => {
    if (newTask.name.trim()) {
      setFormData({
        ...formData,
        tasks: [...formData.tasks, { ...newTask }]
      });
      setNewTask({
        name: '',
        description: '',
        priority: 'medium',
        estimated_duration: 60
      });
    }
  };

  const removeTask = (index) => {
    setFormData({
      ...formData,
      tasks: formData.tasks.filter((_, i) => i !== index)
    });
  };

  const getPriorityColor = (priority) => {
    const priorityOption = priorityOptions.find(opt => opt.value === priority);
    return priorityOption ? priorityOption.color : 'text-gray-400 bg-gray-400/10';
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => (
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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
              Project Templates
            </h1>
            <p className="text-gray-400 mt-1">
              Reusable project templates to speed up project creation
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
          >
            <Plus className="h-5 w-5" />
            <span>New Template</span>
          </button>
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

        {/* Templates Grid */}
        {templates.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="mx-auto h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No templates yet</h3>
            <p className="text-gray-500 mb-6">Create your first project template to get started</p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 rounded-lg font-medium"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              Create First Template
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all duration-200 hover:shadow-lg"
              >
                {/* Template Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-white text-lg mb-2">{template.name}</h3>
                    {template.category && (
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-400/10 text-blue-400">
                        {template.category}
                      </span>
                    )}
                  </div>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleEdit(template)}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(template.id)}
                      className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                {template.description && (
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {template.description}
                  </p>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-lg font-bold text-white">
                      {template.task_count || 0}
                    </p>
                    <p className="text-xs text-gray-500">Tasks</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-white">
                      {template.usage_count || 0}
                    </p>
                    <p className="text-xs text-gray-500">Times Used</p>
                  </div>
                </div>

                {/* Action Button */}
                <button 
                  onClick={() => handleUse(template)}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm font-medium"
                  style={{ color: '#F4B400' }}
                >
                  <Copy className="h-4 w-4" />
                  <span>Use Template</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Create/Edit Template Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-2xl border border-gray-800 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {editingTemplate ? 'Edit Template' : 'Create New Template'}
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
                    Template Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="e.g., Marathon Training Template"
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
                    placeholder="Describe what this template is for"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Category
                  </label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="e.g., fitness, business, learning"
                  />
                </div>

                {/* Tasks Section */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Tasks
                  </label>
                  
                  {/* Add New Task */}
                  <div className="bg-gray-800 rounded-lg p-4 mb-4">
                    <h4 className="text-sm font-medium text-white mb-3">Add New Task</h4>
                    <div className="space-y-3">
                      <input
                        type="text"
                        value={newTask.name}
                        onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        placeholder="Task name"
                      />
                      <textarea
                        value={newTask.description}
                        onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        placeholder="Task description"
                        rows={2}
                      />
                      <div className="flex space-x-3">
                        <select
                          value={newTask.priority}
                          onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                          className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        >
                          {priorityOptions.map(priority => (
                            <option key={priority.value} value={priority.value}>{priority.label}</option>
                          ))}
                        </select>
                        <input
                          type="number"
                          value={newTask.estimated_duration}
                          onChange={(e) => setNewTask({ ...newTask, estimated_duration: parseInt(e.target.value) })}
                          className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="Duration (min)"
                          min="1"
                        />
                      </div>
                      <button
                        type="button"
                        onClick={addTask}
                        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                      >
                        Add Task
                      </button>
                    </div>
                  </div>

                  {/* Task List */}
                  {formData.tasks.length > 0 && (
                    <div className="space-y-2">
                      {formData.tasks.map((task, index) => (
                        <div key={index} className="bg-gray-800 rounded-lg p-3 flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h5 className="font-medium text-white">{task.name}</h5>
                              <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(task.priority)}`}>
                                {task.priority}
                              </span>
                              {task.estimated_duration && (
                                <div className="flex items-center space-x-1 text-xs text-gray-400">
                                  <Clock className="h-3 w-3" />
                                  <span>{task.estimated_duration}m</span>
                                </div>
                              )}
                            </div>
                            {task.description && (
                              <p className="text-sm text-gray-400 mt-1">{task.description}</p>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => removeTask(index)}
                            className="p-1 text-gray-400 hover:text-red-400 rounded"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
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
                    <span>{editingTemplate ? 'Update' : 'Create'}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Use Template Modal */}
        {showUseModal && selectedTemplate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md border border-gray-800">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  Use Template: {selectedTemplate.name}
                </h2>
                <button
                  onClick={handleCloseUseModal}
                  className="p-2 text-gray-400 hover:text-white rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleUseTemplate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={useFormData.name}
                    onChange={(e) => setUseFormData({ ...useFormData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="Enter project name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Area
                  </label>
                  <select
                    value={useFormData.area_id}
                    onChange={(e) => setUseFormData({ ...useFormData, area_id: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  >
                    <option value="">Select an area</option>
                    {areas.map(area => (
                      <option key={area.id} value={area.id}>{area.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={useFormData.description}
                    onChange={(e) => setUseFormData({ ...useFormData, description: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="Project description"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Status
                    </label>
                    <select
                      value={useFormData.status}
                      onChange={(e) => setUseFormData({ ...useFormData, status: e.target.value })}
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
                      value={useFormData.priority}
                      onChange={(e) => setUseFormData({ ...useFormData, priority: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    >
                      {priorityOptions.map(priority => (
                        <option key={priority.value} value={priority.value}>{priority.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-3">
                  <h4 className="text-sm font-medium text-white mb-2">
                    This will create {selectedTemplate.task_count || 0} tasks:
                  </h4>
                  {selectedTemplate.tasks && selectedTemplate.tasks.length > 0 ? (
                    <ul className="text-xs text-gray-400 space-y-1">
                      {selectedTemplate.tasks.map((task, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <Target className="h-3 w-3" />
                          <span>{task.name}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-xs text-gray-500">No tasks defined in template</p>
                  )}
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseUseModal}
                    className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors"
                    style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                  >
                    <Copy className="h-4 w-4" />
                    <span>Create Project</span>
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

export default ProjectTemplates;