import React, { useState, useEffect } from 'react';
import { CheckSquare, Plus, Calendar, Flag, Clock, Check, X, Loader2, AlertCircle } from 'lucide-react';
import { tasksAPI, projectsAPI, handleApiError } from '../services/api';
import { useDataContext } from '../contexts/DataContext';

const TaskCard = ({ task, onToggle, onEdit, onDelete, loading = false }) => {
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

  return (
    <div className={`p-6 rounded-xl border transition-all duration-300 group hover:scale-105 ${
      task.completed 
        ? 'border-green-400/30 bg-gradient-to-br from-green-900/20 to-gray-800/30' 
        : isOverdue
        ? 'border-red-400/30 bg-gradient-to-br from-red-900/20 to-gray-800/30'
        : 'border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30'
    } ${loading ? 'opacity-50' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3 flex-1">
          <div 
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-200 mt-1 ${
              task.completed 
                ? 'bg-green-400 border-green-400' 
                : 'border-gray-500 hover:border-yellow-400'
            } ${loading ? 'cursor-not-allowed' : ''}`}
            onClick={() => !loading && onToggle(task.id, !task.completed)}
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
};

const TaskModal = ({ task, isOpen, onClose, onSave, loading = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: 'medium',
    due_date: '',
    category: 'personal',
    project_id: ''
  });
  
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(false);

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
        category: task.category,
        project_id: task.project_id || ''
      });
    } else {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      setFormData({
        name: '',
        description: '',
        priority: 'medium',
        due_date: tomorrow.toISOString().split('T')[0],
        category: 'personal',
        project_id: projects.length > 0 ? projects[0].id : '' // Default to first project
      });
    }
  }, [task, isOpen, projects]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null
    };
    onSave(submitData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md border border-gray-800">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">
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
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Task Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              placeholder="What needs to be done?"
              required
              disabled={loading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Project
            </label>
            <select
              value={formData.project_id}
              onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              required
              disabled={loading || loadingProjects}
            >
              {loadingProjects ? (
                <option value="">Loading projects...</option>
              ) : projects.length > 0 ? (
                projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name} ({project.area_name})
                  </option>
                ))
              ) : (
                <option value="">No projects available</option>
              )}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              rows="3"
              placeholder="Add more details..."
              disabled={loading}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Project *
              </label>
              <select
                value={formData.project_id}
                onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                disabled={loading || loadingProjects}
                required
              >
                <option value="">Select a project</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>
                    {project.name} ({project.area_name})
                  </option>
                ))}
              </select>
              {loadingProjects && (
                <p className="text-xs text-gray-400 mt-1">Loading projects...</p>
              )}
              {!loadingProjects && projects.length === 0 && (
                <p className="text-xs text-red-400 mt-1">
                  No projects available. Please create a project first.
                </p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                disabled={loading}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
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
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                disabled={loading}
              >
                <option value="personal">Personal</option>
                <option value="learning">Learning</option>
                <option value="health">Health</option>
                <option value="work">Work</option>
                <option value="mindfulness">Mindfulness</option>
                <option value="coaching">Coaching</option>
                <option value="planning">Planning</option>
              </select>
            </div>
          </div>
          
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
};

const Tasks = () => {
  const { onDataMutation } = useDataContext();
  const [tasks, setTasks] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState('all'); // all, active, completed
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const filteredTasks = tasks.filter(task => {
    switch (filter) {
      case 'active': return !task.completed;
      case 'completed': return task.completed;
      default: return true;
    }
  });

  const completedCount = tasks.filter(t => t.completed).length;
  const activeCount = tasks.filter(t => !t.completed).length;
  const overdueCount = tasks.filter(t => !t.completed && t.is_overdue).length;

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
          <h1 className="text-3xl font-bold text-white mb-2">Task Management</h1>
          <p className="text-gray-400">Organize your goals and track your productivity</p>
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
              <h3 className="text-2xl font-bold text-white">{tasks.length}</h3>
              <p className="text-sm text-gray-400">Total Tasks</p>
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
      />
    </div>
  );
};

export default Tasks;