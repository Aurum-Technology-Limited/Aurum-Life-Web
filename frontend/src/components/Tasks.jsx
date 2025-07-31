import React, { useState, useEffect, memo } from 'react';
import { CheckSquare, Plus, Calendar, Flag, Clock, Check, X, Loader2, AlertCircle, Lock, Repeat, ChevronDown, ChevronUp, FolderIcon } from 'lucide-react';
import { tasksAPI, projectsAPI, handleApiError } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import FileAttachment from './FileAttachment';

// Memoized TaskCard component to prevent unnecessary re-renders
const TaskCard = memo(({ task, onToggle, onEdit, onDelete, loading = false }) => {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-400';
      case 'medium': return 'bg-yellow-400';
      case 'low': return 'bg-green-400';
      default: return 'bg-gray-400';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const isOverdue = task.is_overdue;
  const isBlocked = task.can_start === false; // Task has unmet dependencies (UI-1.3.2)

  return (
    <div className={`p-6 rounded-xl border transition-all duration-300 group hover:scale-105 ${
      task.completed 
        ? 'border-green-400/30 bg-gradient-to-br from-green-900/20 to-gray-800/30' 
        : isBlocked
        ? 'border-orange-400/30 bg-gradient-to-br from-orange-900/20 to-gray-800/30 opacity-75' // Blocked tasks styling
        : isOverdue
        ? 'border-red-400/30 bg-gradient-to-br from-red-900/20 to-gray-800/30'
        : 'border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30'
    } ${loading ? 'opacity-50' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3 flex-1">
          {/* Blocked task indicator (UI-1.3.2) */}
          {isBlocked && !task.completed && (
            <div className="mt-1 mr-2" title={`Blocked: ${task.dependency_tasks?.map(d => d.name).join(', ') || 'Prerequisites required'}`}>
              <Lock size={16} className="text-orange-400" />
            </div>
          )}
          
          <div 
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-200 mt-1 ${
              task.completed 
                ? 'bg-green-400 border-green-400' 
                : isBlocked
                ? 'border-orange-400/50 cursor-not-allowed' // Blocked styling
                : 'border-gray-500 hover:border-yellow-400'
            } ${loading ? 'cursor-not-allowed' : ''}`}
            onClick={() => !loading && !isBlocked && onToggle(task.id, !task.completed)}
          >
            {loading ? (
              <Loader2 size={12} className="animate-spin text-gray-400" />
            ) : task.completed ? (
              <Check size={14} style={{ color: '#0B0D14' }} />
            ) : null}
          </div>
          
          <div className="flex-1">
            <h3 className={`text-lg font-semibold mb-2 ${
              task.completed ? 'text-gray-400 line-through' : 'text-white'
            }`}>
              {task.name || task.title || 'Unnamed Task'}
            </h3>
            <p className="text-sm text-gray-400 mb-3">{task.description}</p>
            
            {/* Blocked status indicator (UI-1.3.2 & UI-1.3.3) */}
            {isBlocked && !task.completed && (
              <div className="bg-orange-900/20 border border-orange-400/30 rounded-lg p-2 mb-3">
                <div className="flex items-center space-x-2">
                  <Lock size={14} className="text-orange-400 flex-shrink-0" />
                  <div className="text-xs">
                    <div className="text-orange-400 font-medium">Prerequisites required</div>
                    {task.dependency_tasks && task.dependency_tasks.length > 0 && (
                      <div className="text-gray-400 mt-1">
                        Complete: {task.dependency_tasks.map(dep => dep.name).join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <Calendar size={14} className="text-gray-400" />
                <span className={`${isOverdue && !task.completed ? 'text-red-400' : 'text-gray-400'}`}>
                  {formatDate(task.due_date)}
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <Flag size={14} className="text-gray-400" />
                <span className="text-gray-400 capitalize">{task.priority}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-gray-500 capitalize">{task.category}</span>
              </div>
              {task.date_created && (
                <div className="flex items-center space-x-1">
                  <span className="text-xs text-gray-500">
                    Created: {new Date(task.date_created).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-8 rounded-full ${getPriorityColor(task.priority)}`} />
          <button
            onClick={() => onEdit(task)}
            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors opacity-0 group-hover:opacity-100"
            disabled={loading}
          >
            <Clock size={14} className="text-gray-400" />
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="p-2 rounded-lg bg-gray-800 hover:bg-red-700 transition-colors opacity-0 group-hover:opacity-100"
            disabled={loading}
          >
            <X size={14} className="text-gray-400 hover:text-red-400" />
          </button>
        </div>
      </div>
    </div>
  );
});

TaskCard.displayName = 'TaskCard';

// Memoized TaskModal component to prevent unnecessary re-renders
const TaskModal = memo(({ task, isOpen, onClose, onSave, loading = false, defaultProjectId = null }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: 'medium',
    due_date: '',
    due_time: '',  // New field for time
    category: 'personal',
    project_id: '',
    sub_task_completion_required: false  // New field for sub-task completion requirement
  });
  
  // Recurrence configuration state
  const [recurrenceEnabled, setRecurrenceEnabled] = useState(false);
  const [recurrenceConfig, setRecurrenceConfig] = useState({
    type: 'none',
    interval: 1,
    weekdays: [],
    month_day: null,
    end_date: '',
    max_instances: null
  });
  const [showRecurrenceDetails, setShowRecurrenceDetails] = useState(false);
  
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [subtasks, setSubtasks] = useState([]);  // For managing sub-tasks
  const [newSubtask, setNewSubtask] = useState({ name: '', description: '' });  // For adding new sub-tasks
  
  // Task Dependencies state (UI-1.3.1)
  const [dependencies, setDependencies] = useState([]);
  const [availableDependencies, setAvailableDependencies] = useState([]);
  const [loadingDependencies, setLoadingDependencies] = useState(false);
  const [selectedDependencyIds, setSelectedDependencyIds] = useState([]);

  const loadSubtasks = async (taskId) => {
    try {
      const response = await tasksAPI.getSubtasks(taskId);
      setSubtasks(response.data || []);
    } catch (err) {
      console.error('Error loading subtasks:', err);
      setSubtasks([]);
    }
  };

  const addSubtask = () => {
    if (newSubtask.name.trim()) {
      const subtask = {
        id: `temp_${Date.now()}`, // Temporary ID for UI
        name: newSubtask.name,
        description: newSubtask.description,
        completed: false,
        isNew: true // Mark as new for backend creation
      };
      setSubtasks(prev => [...prev, subtask]);
      setNewSubtask({ name: '', description: '' });
    }
  };

  const removeSubtask = (subtaskId) => {
    setSubtasks(prev => prev.filter(st => st.id !== subtaskId));
  };

  const toggleSubtaskComplete = (subtaskId) => {
    setSubtasks(prev => prev.map(st => 
      st.id === subtaskId ? { ...st, completed: !st.completed } : st
    ));
  };

  // Load available dependency tasks
  const loadAvailableDependencies = async (projectId) => {
    if (!projectId) return;
    
    try {
      setLoadingDependencies(true);
      const response = await tasksAPI.getAvailableDependencyTasks(projectId, task?.id);
      setAvailableDependencies(response.data || []);
    } catch (err) {
      console.error('Error loading available dependencies:', err);
      setAvailableDependencies([]);
    } finally {
      setLoadingDependencies(false);
    }
  };

  // Load current task dependencies
  const loadTaskDependencies = async (taskId) => {
    if (!taskId) return;
    
    try {
      const response = await tasksAPI.getTaskDependencies(taskId);
      const depData = response.data || {};
      setSelectedDependencyIds(depData.dependency_task_ids || []);
      setDependencies(depData.dependency_tasks || []);
    } catch (err) {
      console.error('Error loading task dependencies:', err);
      setSelectedDependencyIds([]);
      setDependencies([]);
    }
  };

  const handleDependencyToggle = (dependencyId) => {
    setSelectedDependencyIds(prev => {
      if (prev.includes(dependencyId)) {
        return prev.filter(id => id !== dependencyId);
      } else {
        return [...prev, dependencyId];
      }
    });
  };

  // Load projects when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchProjects();
    }
  }, [isOpen]);

  const fetchProjects = async () => {
    try {
      setLoadingProjects(true);
      const response = await projectsAPI.getProjects();
      setProjects(response.data);
      
      // Set default project if none is selected and we're creating a new task
      if (!task && !formData.project_id) {
        const projectId = defaultProjectId || (response.data.length > 0 ? response.data[0].id : '');
        setFormData(prev => ({
          ...prev,
          project_id: projectId
        }));
      }
    } catch (err) {
      console.error('Error loading projects:', err);
      // Set a default project if loading fails
      setProjects([]);
    } finally {
      setLoadingProjects(false);
    }
  };

  useEffect(() => {
    if (task) {
      setFormData({
        name: task.name || task.title || '', // Handle both old and new field names
        description: task.description,
        priority: task.priority,
        due_date: task.due_date ? task.due_date.split('T')[0] : '',
        due_time: task.due_time || '', // New field
        category: task.category,
        project_id: task.project_id || '',
        sub_task_completion_required: task.sub_task_completion_required || false // New field
      });
      
      // Handle recurrence data if editing a recurring task
      if (task.recurrence_pattern) {
        setRecurrenceEnabled(true);
        setRecurrenceConfig({
          type: task.recurrence_pattern.type || 'none',
          interval: task.recurrence_pattern.interval || 1,
          weekdays: task.recurrence_pattern.weekdays || [],
          month_day: task.recurrence_pattern.month_day || null,
          end_date: task.recurrence_pattern.end_date ? task.recurrence_pattern.end_date.split('T')[0] : '',
          max_instances: task.recurrence_pattern.max_instances || null
        });
        setShowRecurrenceDetails(true);
      } else {
        setRecurrenceEnabled(false);
        setRecurrenceConfig({
          type: 'none',
          interval: 1,
          weekdays: [],
          month_day: null,
          end_date: '',
          max_instances: null
        });
        setShowRecurrenceDetails(false);
      }
      
      // Load existing subtasks if editing
      if (task.id) {
        loadSubtasks(task.id);
        loadTaskDependencies(task.id);
      }
      
      // Load available dependencies for the project
      if (task.project_id) {
        loadAvailableDependencies(task.project_id);
      }
    } else {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      setFormData({
        name: '',
        description: '',
        priority: 'medium',
        due_date: tomorrow.toISOString().split('T')[0],
        due_time: '', // New field
        category: 'personal',
        project_id: '', // Will be set after projects load
        sub_task_completion_required: false // New field
      });
      
      // Reset recurrence for new tasks
      setRecurrenceEnabled(false);
      setRecurrenceConfig({
        type: 'none',
        interval: 1,
        weekdays: [],
        month_day: null,
        end_date: '',
        max_instances: null
      });
      setShowRecurrenceDetails(false);
      
      // Clear subtasks when creating new task
      setSubtasks([]);
      setNewSubtask({ name: '', description: '' });
    }
  }, [task, isOpen, projects]);

  // Set default project when defaultProjectId changes
  useEffect(() => {
    if (defaultProjectId && !task && !formData.project_id) {
      setFormData(prev => ({
        ...prev,
        project_id: defaultProjectId
      }));
    }
  }, [defaultProjectId, task, formData.project_id]);

  // Load dependencies when project changes
  useEffect(() => {
    if (formData.project_id) {
      loadAvailableDependencies(formData.project_id);
    }
  }, [formData.project_id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null
    };
    
    // Add recurrence data if enabled
    if (recurrenceEnabled && recurrenceConfig.type !== 'none') {
      submitData.recurrence_pattern = {
        ...recurrenceConfig,
        end_date: recurrenceConfig.end_date ? new Date(recurrenceConfig.end_date).toISOString() : null
      };
    }
    
    try {
      // Save the main task first
      const savedTask = await onSave(submitData);
      const taskId = savedTask?.id || task?.id;
      
      // Save dependencies if they've changed
      if (taskId && selectedDependencyIds.length >= 0) { // >= 0 to handle empty array (removing all dependencies)
        try {
          await tasksAPI.updateTaskDependencies(taskId, selectedDependencyIds);
        } catch (err) {
          console.error('Error saving task dependencies:', err);
          // Don't throw here - task was saved successfully, just dependencies failed
        }
      }
      
      // If creating a new task and we have subtasks, create them
      if (!task && subtasks.length > 0) {
        // We'll need the created task ID to create subtasks
        // For now, we'll handle this in the parent component
        // Pass subtasks data to be handled after task creation
        if (onSave.subtasks) {
          onSave.subtasks(subtasks);
        }
      } else if (task && subtasks.length > 0) {
        // Handle subtask updates for existing tasks
        for (const subtask of subtasks) {
          if (subtask.isNew) {
            // Create new subtask
            const subtaskData = {
              name: subtask.name,
              description: subtask.description || '',
              priority: 'medium',
              category: formData.category
            };
            await tasksAPI.createSubtask(task.id, subtaskData);
          } else if (subtask.completed !== subtask.originalCompleted) {
            // Update existing subtask completion status
            await tasksAPI.updateTask(subtask.id, { completed: subtask.completed });
          }
        }
      }
    } catch (err) {
      console.error('Error saving task with subtasks:', err);
      throw err; // Re-throw to let parent handle the error
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4 z-50">
      <div className="bg-gray-900 rounded-xl p-4 sm:p-6 w-full max-w-4xl max-h-[95vh] sm:max-h-[90vh] overflow-y-auto border border-gray-800">
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-xl font-bold text-white">
            {task ? 'Edit Task' : 'Create New Task'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
            disabled={loading}
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
          {/* Task Name and Description - Full Width */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Task Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                placeholder="Enter task name..."
                disabled={loading}
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
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                placeholder="Add more details..."
                rows="3"
                disabled={loading}
              />
            </div>
          </div>
          {/* Project, Priority, Due Date Grid - Mobile Responsive */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Project
              </label>
              <select
                value={formData.project_id}
                onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                disabled={loading || loadingProjects}
                required
              >
                <option value="">Select Project</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
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
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                disabled={loading}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                disabled={loading}
              />
            </div>
          </div>

          {/* Due Time and Category - 2 Columns */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Due Time (Optional)
              </label>
              <input
                type="time"
                value={formData.due_time}
                onChange={(e) => setFormData({ ...formData, due_time: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                disabled={loading}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none"
                disabled={loading}
              >
                <option value="personal">Personal</option>
                <option value="work">Work</option>
                <option value="health">Health</option>
                <option value="finance">Finance</option>
                <option value="learning">Learning</option>
                <option value="family">Family</option>
                <option value="social">Social</option>
                <option value="creative">Creative</option>
                <option value="maintenance">Maintenance</option>
                <option value="spiritual">Spiritual</option>
                <option value="travel">Travel</option>
                <option value="goals">Goals</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>
          
          {/* Recurrence Configuration Section */}
          <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <label className="flex items-center space-x-2 text-sm font-medium text-gray-300">
                <input
                  type="checkbox"
                  checked={recurrenceEnabled}
                  onChange={(e) => {
                    setRecurrenceEnabled(e.target.checked);
                    if (!e.target.checked) {
                      setRecurrenceConfig({
                        type: 'none',
                        interval: 1,
                        weekdays: [],
                        month_day: null,
                        end_date: '',
                        max_instances: null
                      });
                      setShowRecurrenceDetails(false);
                    } else {
                      setShowRecurrenceDetails(true);
                    }
                  }}
                  className="rounded bg-gray-800 border-gray-700 text-yellow-400 focus:ring-yellow-400 focus:ring-2"
                  disabled={loading}
                />
                <Repeat className="h-4 w-4 text-gray-400" />
                <span>Make this a recurring task</span>
              </label>
              
              {recurrenceEnabled && (
                <button
                  type="button"
                  onClick={() => setShowRecurrenceDetails(!showRecurrenceDetails)}
                  className="flex items-center space-x-1 text-xs text-gray-400 hover:text-white transition-colors"
                >
                  {showRecurrenceDetails ? (
                    <>
                      <ChevronUp className="h-3 w-3" />
                      <span>Hide Options</span>
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-3 w-3" />
                      <span>More Options</span>
                    </>
                  )}
                </button>
              )}
            </div>
            
            {/* Recurrence Configuration */}
            {recurrenceEnabled && (
              <div className="space-y-4">
                {/* Recurrence Type and Interval Grid - Mobile Responsive */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Repeat Pattern
                    </label>
                    <select
                      value={recurrenceConfig.type}
                      onChange={(e) => setRecurrenceConfig({ 
                        ...recurrenceConfig, 
                        type: e.target.value,
                        // Reset specific configurations when changing type
                        weekdays: e.target.value === 'weekly' ? recurrenceConfig.weekdays : [],
                        month_day: e.target.value === 'monthly' ? recurrenceConfig.month_day : null
                      })}
                      className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                      disabled={loading}
                    >
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Every
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        min="1"
                        max="30"
                        value={recurrenceConfig.interval}
                        onChange={(e) => setRecurrenceConfig({ 
                          ...recurrenceConfig, 
                          interval: parseInt(e.target.value) || 1 
                        })}
                        className="flex-1 px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                        disabled={loading}
                      />
                      <span className="text-sm text-gray-400 w-16">
                        {recurrenceConfig.type === 'daily' ? 'day(s)' :
                         recurrenceConfig.type === 'weekly' ? 'week(s)' :
                         'month(s)'}
                      </span>
                    </div>
                  </div>
                </div>
                
                {/* Weekly specific options */}
                {recurrenceConfig.type === 'weekly' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      On these days
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
                        <button
                          key={day}
                          type="button"
                          onClick={() => {
                            const updatedWeekdays = recurrenceConfig.weekdays.includes(day)
                              ? recurrenceConfig.weekdays.filter(d => d !== day)
                              : [...recurrenceConfig.weekdays, day];
                            setRecurrenceConfig({ ...recurrenceConfig, weekdays: updatedWeekdays });
                          }}
                          className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                            recurrenceConfig.weekdays.includes(day)
                              ? 'bg-yellow-600 text-black'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                          disabled={loading}
                        >
                          {day.substring(0, 3).toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Monthly specific options */}
                {recurrenceConfig.type === 'monthly' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      On day of month
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="31"
                      value={recurrenceConfig.month_day || ''}
                      onChange={(e) => setRecurrenceConfig({ 
                        ...recurrenceConfig, 
                        month_day: parseInt(e.target.value) || null 
                      })}
                      placeholder="e.g., 15 for 15th of each month"
                      className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                      disabled={loading}
                    />
                  </div>
                )}
                
                {/* Advanced options - Better Grid Layout */}
                {showRecurrenceDetails && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-600">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        End Date (Optional)
                      </label>
                      <input
                        type="date"
                        value={recurrenceConfig.end_date}
                        onChange={(e) => setRecurrenceConfig({ 
                          ...recurrenceConfig, 
                          end_date: e.target.value 
                        })}
                        className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                        disabled={loading}
                      />
                      <p className="text-xs text-gray-400 mt-1">When to stop repeating</p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Max Occurrences (Optional)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="365"
                        value={recurrenceConfig.max_instances || ''}
                        onChange={(e) => setRecurrenceConfig({ 
                          ...recurrenceConfig, 
                          max_instances: parseInt(e.target.value) || null 
                        })}
                        placeholder="e.g., 10"
                        className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                        disabled={loading}
                      />
                      <p className="text-xs text-gray-400 mt-1">How many times to repeat</p>
                    </div>
                  </div>
                )}
                
                {/* Recurrence Preview */}
                {recurrenceConfig.type !== 'none' && (
                  <div className="bg-blue-900/20 border border-blue-600/30 rounded-lg p-3">
                    <div className="flex items-start space-x-2">
                      <Repeat className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm text-blue-300 font-medium">Preview:</p>
                        <p className="text-xs text-blue-400 mt-1">
                          {recurrenceConfig.type === 'daily' && 
                            `Repeats every ${recurrenceConfig.interval} day${recurrenceConfig.interval > 1 ? 's' : ''}`
                          }
                          {recurrenceConfig.type === 'weekly' && 
                            `Repeats every ${recurrenceConfig.interval} week${recurrenceConfig.interval > 1 ? 's' : ''} on ${
                              recurrenceConfig.weekdays.length > 0 
                                ? recurrenceConfig.weekdays.map(d => d.substring(0, 3).toUpperCase()).join(', ')
                                : 'selected days'
                            }`
                          }
                          {recurrenceConfig.type === 'monthly' && 
                            `Repeats every ${recurrenceConfig.interval} month${recurrenceConfig.interval > 1 ? 's' : ''}${
                              recurrenceConfig.month_day ? ` on day ${recurrenceConfig.month_day}` : ''
                            }`
                          }
                          {recurrenceConfig.end_date && ` until ${new Date(recurrenceConfig.end_date).toLocaleDateString()}`}
                          {recurrenceConfig.max_instances && ` (max ${recurrenceConfig.max_instances} times)`}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Sub-task completion requirement */}
          <div className="flex items-center">
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-300">
              <input
                type="checkbox"
                checked={formData.sub_task_completion_required}
                onChange={(e) => setFormData({ ...formData, sub_task_completion_required: e.target.checked })}
                className="rounded bg-gray-800 border-gray-700 text-yellow-400 focus:ring-yellow-400 focus:ring-2"
                disabled={loading}
              />
              <span>Require all sub-tasks to complete</span>
            </label>
          </div>
          
          {/* Sub-tasks Section */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-gray-300">Sub-tasks</h4>
              <span className="text-xs text-gray-500">{subtasks.length} sub-tasks</span>
            </div>
            
            {/* Add new sub-task */}
            <div className="bg-gray-800 rounded-lg p-3 mb-3">
              <div className="space-y-2">
                <input
                  type="text"
                  value={newSubtask.name}
                  onChange={(e) => setNewSubtask({ ...newSubtask, name: e.target.value })}
                  placeholder="Sub-task name"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-gray-700 border border-gray-600 text-white focus:border-yellow-400 focus:outline-none"
                />
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newSubtask.description}
                    onChange={(e) => setNewSubtask({ ...newSubtask, description: e.target.value })}
                    placeholder="Description (optional)"
                    className="flex-1 px-3 py-2 text-sm rounded-lg bg-gray-700 border border-gray-600 text-white focus:border-yellow-400 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={addSubtask}
                    className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
                    disabled={!newSubtask.name.trim()}
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
            
            {/* Sub-tasks list */}
            {subtasks.length > 0 && (
              <div className="space-y-2 mb-4">
                {subtasks.map((subtask) => (
                  <div key={subtask.id} className="bg-gray-800 rounded-lg p-3 flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <input
                        type="checkbox"
                        checked={subtask.completed}
                        onChange={() => toggleSubtaskComplete(subtask.id)}
                        className="rounded bg-gray-700 border-gray-600 text-yellow-400 focus:ring-yellow-400 focus:ring-2"
                      />
                      <div className="flex-1">
                        <div className={`text-sm font-medium ${subtask.completed ? 'line-through text-gray-500' : 'text-white'}`}>
                          {subtask.name}
                          {subtask.isNew && <span className="ml-2 text-xs text-blue-400">(New)</span>}
                        </div>
                        {subtask.description && (
                          <div className={`text-xs mt-1 ${subtask.completed ? 'text-gray-600' : 'text-gray-400'}`}>
                            {subtask.description}
                          </div>
                        )}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSubtask(subtask.id)}
                      className="p-1 text-gray-400 hover:text-red-400 rounded transition-colors"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Task Dependencies Section (UI-1.3.1) */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-gray-300">Prerequisites</h4>
              <span className="text-xs text-gray-500">{selectedDependencyIds.length} dependencies</span>
            </div>
            
            {loadingDependencies ? (
              <div className="bg-gray-800 rounded-lg p-4 flex items-center justify-center">
                <Loader2 size={16} className="animate-spin text-gray-400 mr-2" />
                <span className="text-sm text-gray-400">Loading available tasks...</span>
              </div>
            ) : availableDependencies.length > 0 ? (
              <div className="bg-gray-800 rounded-lg p-3 max-h-32 overflow-y-auto">
                <div className="text-xs text-gray-500 mb-2">
                  Select tasks that must be completed before this task can start:
                </div>
                <div className="space-y-2">
                  {availableDependencies.map((depTask) => (
                    <label key={depTask.id} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedDependencyIds.includes(depTask.id)}
                        onChange={() => handleDependencyToggle(depTask.id)}
                        className="rounded bg-gray-700 border-gray-600 text-yellow-400 focus:ring-yellow-400 focus:ring-2"
                      />
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium truncate ${
                          depTask.completed ? 'line-through text-gray-500' : 'text-white'
                        }`}>
                          {depTask.name}
                        </div>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`inline-block w-2 h-2 rounded-full ${
                            depTask.completed ? 'bg-green-400' :
                            depTask.priority === 'high' ? 'bg-red-400' :
                            depTask.priority === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
                          }`}></span>
                          <span className="text-xs text-gray-500 capitalize">
                            {depTask.status?.replace('_', ' ') || 'todo'}
                          </span>
                          {depTask.completed && (
                            <span className="text-xs text-green-400">✓ Complete</span>
                          )}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <span className="text-sm text-gray-500">
                  No other tasks available as prerequisites
                </span>
              </div>
            )}
            
            {/* Show current dependencies */}
            {selectedDependencyIds.length > 0 && (
              <div className="mt-3">
                <div className="text-xs text-gray-500 mb-2">Selected prerequisites:</div>
                <div className="bg-gray-700 rounded-lg p-2 text-xs">
                  {selectedDependencyIds.map((depId, index) => {
                    const depTask = availableDependencies.find(t => t.id === depId);
                    return (
                      <span key={depId} className="text-yellow-400">
                        {depTask?.name || 'Unknown Task'}
                        {index < selectedDependencyIds.length - 1 && ', '}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
          
          {/* File Attachment - Only show for existing tasks */}
          {task && (
            <div>
              <FileAttachment 
                parentType="task"
                parentId={task.id}
                parentName={task.name}
              />
            </div>
          )}
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-700 text-gray-300 hover:bg-gray-800 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105 flex items-center justify-center space-x-2"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
              disabled={loading}
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <span>{task ? 'Update' : 'Create'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
});

TaskModal.displayName = 'TaskModal';

const Tasks = memo(({ onSectionChange, sectionParams }) => {
  const { onDataMutation } = useDataContext();
  const [tasks, setTasks] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState('all'); // all, active, completed
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [error, setError] = useState(null);

  // Extract project filter from section params
  const activeProjectId = sectionParams?.projectId || null;
  const activeProjectName = sectionParams?.projectName || null;

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await tasksAPI.getTasks();
      setTasks(response.data);
    } catch (err) {
      setError(handleApiError(err, 'Failed to load tasks'));
    } finally {
      setLoading(false);
    }
  };

  // Filter tasks by project if projectId is provided
  const filteredTasksByProject = activeProjectId 
    ? tasks.filter(task => task.project_id === activeProjectId)
    : tasks;

  const handleToggleTask = async (taskId, completed) => {
    try {
      setActionLoading(taskId);
      
      await tasksAPI.updateTask(taskId, { completed });
      
      // Update local state optimistically
      setTasks(prev => prev.map(task => 
        task.id === taskId 
          ? { ...task, completed, completed_at: completed ? new Date().toISOString() : null }
          : task
      ));
      
      // Notify data context of the mutation
      onDataMutation('task', completed ? 'complete' : 'uncomplete', { taskId, completed });
    } catch (err) {
      setError(handleApiError(err, 'Failed to update task'));
    } finally {
      setActionLoading(null);
    }
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setModalOpen(true);
  };

  const handleCreateTask = () => {
    setEditingTask(null);
    setModalOpen(true);
    
    // If we're viewing tasks for a specific project, pre-populate the project_id
    if (activeProjectId) {
      // We'll need to modify the modal to handle this pre-population
      // For now, this will be handled in the modal's useEffect
    }
  };

  const handleSaveTask = async (formData) => {
    try {
      setModalLoading(true);
      
      if (editingTask) {
        await tasksAPI.updateTask(editingTask.id, formData);
        // Update local state
        setTasks(prev => prev.map(task =>
          task.id === editingTask.id
            ? { ...task, ...formData }
            : task
        ));
        
        // Notify data context of the mutation
        onDataMutation('task', 'update', { taskId: editingTask.id, ...formData });
      } else {
        const response = await tasksAPI.createTask(formData);
        // Add to local state
        setTasks(prev => [...prev, response.data]);
        
        // Notify data context of the mutation
        onDataMutation('task', 'create', response.data);
      }
      
      setModalOpen(false);
      setEditingTask(null);
    } catch (err) {
      setError(handleApiError(err, editingTask ? 'Failed to update task' : 'Failed to create task'));
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await tasksAPI.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      
      // Notify data context of the mutation
      onDataMutation('task', 'delete', { taskId });
    } catch (err) {
      setError(handleApiError(err, 'Failed to delete task'));
    }
  };

  const filteredTasks = filteredTasksByProject.filter(task => {
    switch (filter) {
      case 'active': return !task.completed;
      case 'completed': return task.completed;
      default: return true;
    }
  });

  const completedCount = filteredTasksByProject.filter(t => t.completed).length;
  const activeCount = filteredTasksByProject.filter(t => !t.completed).length;
  const overdueCount = filteredTasksByProject.filter(t => !t.completed && t.is_overdue).length;

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 size={48} className="animate-spin text-yellow-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold text-white mb-2">
              Task Management
            </h1>
            {activeProjectName && (
              <>
                <span className="text-2xl text-gray-500">›</span>
                <div className="flex items-center space-x-2">
                  <FolderIcon className="h-5 w-5 text-yellow-400" />
                  <span className="text-xl font-medium text-yellow-400">{activeProjectName}</span>
                </div>
              </>
            )}
          </div>
          <p className="text-gray-400">
            {activeProjectName 
              ? `Manage tasks for ${activeProjectName} project`
              : 'Organize your goals and track your productivity'
            }
          </p>
          {activeProjectName && onSectionChange && (
            <button
              onClick={() => onSectionChange('projects')}
              className="mt-2 text-sm text-yellow-400 hover:text-yellow-300 transition-colors"
            >
              ← Back to all projects
            </button>
          )}
        </div>
        <button
          onClick={handleCreateTask}
          className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
          style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
        >
          <Plus size={20} />
          <span>Add Task</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={fetchTasks}
            className="ml-auto px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <CheckSquare size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{filteredTasksByProject.length}</h3>
              <p className="text-sm text-gray-400">
                {activeProjectName ? `${activeProjectName} Tasks` : 'Total Tasks'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-blue-400 flex items-center justify-center">
              <Clock size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{activeCount}</h3>
              <p className="text-sm text-gray-400">Active Tasks</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-green-400 flex items-center justify-center">
              <Check size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{completedCount}</h3>
              <p className="text-sm text-gray-400">Completed</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-red-400 flex items-center justify-center">
              <Flag size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{overdueCount}</h3>
              <p className="text-sm text-gray-400">Overdue</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {[
          { key: 'all', label: 'All Tasks' },
          { key: 'active', label: 'Active' },
          { key: 'completed', label: 'Completed' }
        ].map((filterOption) => (
          <button
            key={filterOption.key}
            onClick={() => setFilter(filterOption.key)}
            className={`px-4 py-2 rounded-lg transition-all duration-200 ${
              filter === filterOption.key
                ? 'text-gray-900 font-medium'
                : 'text-gray-400 hover:text-white'
            }`}
            style={{
              backgroundColor: filter === filterOption.key ? '#F4B400' : 'transparent',
              border: filter === filterOption.key ? 'none' : '1px solid #374151'
            }}
          >
            {filterOption.label}
          </button>
        ))}
      </div>

      {/* Tasks Grid */}
      {filteredTasks.length > 0 ? (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggle={handleToggleTask}
              onEdit={handleEditTask}
              onDelete={handleDeleteTask}
              loading={actionLoading === task.id}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-lg bg-yellow-400/20 flex items-center justify-center mx-auto mb-4">
            <CheckSquare size={32} className="text-yellow-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">
            {filter === 'completed' ? 'No completed tasks' : 
             filter === 'active' ? 'No active tasks' : 'No tasks yet'}
          </h3>
          <p className="text-gray-400 mb-6">
            {filter === 'all' ? 'Create your first task to get started' : 
             `Switch to ${filter === 'completed' ? 'active' : 'all'} tasks to see more`}
          </p>
          {filter === 'all' && (
            <button
              onClick={handleCreateTask}
              className="px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              Create Your First Task
            </button>
          )}
        </div>
      )}

      <TaskModal
        task={editingTask}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingTask(null);
        }}
        onSave={handleSaveTask}
        loading={modalLoading}
        defaultProjectId={activeProjectId}
      />
    </div>
  );
});

Tasks.displayName = 'Tasks';

export default Tasks;