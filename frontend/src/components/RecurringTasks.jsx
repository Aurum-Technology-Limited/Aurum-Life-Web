import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Save, 
  X, 
  AlertCircle, 
  Repeat, 
  Calendar, 
  Clock,
  Target,
  TrendingUp,
  Play,
  Pause
} from 'lucide-react';
import { recurringTasksAPI, projectsAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';

const RecurringTasks = () => {
  const { onDataMutation } = useDataContext();
  const [recurringTasks, setRecurringTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: 'medium',
    project_id: '',
    category: 'general',
    estimated_duration: 30,
    due_time: '09:00',
    recurrence_pattern: {
      type: 'daily',
      interval: 1,
      weekdays: [],
      month_day: null,
      end_date: null,
      max_instances: null
    }
  });

  const loadRecurringTasks = async () => {
    try {
      setLoading(true);
      const [tasksResponse, projectsResponse] = await Promise.all([
        recurringTasksAPI.getRecurringTasks(),
        projectsAPI.getProjects()
      ]);
      setRecurringTasks(tasksResponse.data);
      setProjects(projectsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load recurring tasks');
      console.error('Error loading recurring tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecurringTasks();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTask) {
        await recurringTasksAPI.updateRecurringTask(editingTask.id, formData);
        onDataMutation('recurring_task', 'update', { taskId: editingTask.id, ...formData });
      } else {
        await recurringTasksAPI.createRecurringTask(formData);
        onDataMutation('recurring_task', 'create', formData);
      }
      loadRecurringTasks();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving recurring task:', err);
      setError(editingTask ? 'Failed to update recurring task' : 'Failed to create recurring task');
    }
  };

  const handleDelete = async (taskId) => {
    if (window.confirm('Are you sure? This will delete all instances of this recurring task.')) {
      try {
        await recurringTasksAPI.deleteRecurringTask(taskId);
        loadRecurringTasks();
        onDataMutation('recurring_task', 'delete', { taskId });
      } catch (err) {
        console.error('Error deleting recurring task:', err);
        setError('Failed to delete recurring task');
      }
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setFormData({
      name: task.name,
      description: task.description,
      priority: task.priority,
      project_id: task.project_id,
      category: task.category,
      estimated_duration: task.estimated_duration || 30,
      due_time: task.due_time || '09:00',
      recurrence_pattern: task.recurrence_pattern
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingTask(null);
    setFormData({
      name: '',
      description: '',
      priority: 'medium',
      project_id: '',
      category: 'general',
      estimated_duration: 30,
      due_time: '09:00',
      recurrence_pattern: {
        type: 'daily',
        interval: 1,
        weekdays: [],
        month_day: null,
        end_date: null,
        max_instances: null
      }
    });
  };

  const handleGenerateInstances = async () => {
    try {
      await recurringTasksAPI.generateRecurringTaskInstances();
      loadRecurringTasks(); // Refresh to see updated stats
    } catch (err) {
      console.error('Error generating instances:', err);
      setError('Failed to generate task instances');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const getRecurrenceDisplay = (pattern) => {
    switch (pattern.type) {
      case 'daily':
        return pattern.interval === 1 ? 'Daily' : `Every ${pattern.interval} days`;
      case 'weekly':
        if (pattern.weekdays && pattern.weekdays.length > 0) {
          const dayNames = pattern.weekdays.map(day => 
            day.charAt(0).toUpperCase() + day.slice(1, 3)
          ).join(', ');
          return `Weekly on ${dayNames}`;
        }
        return pattern.interval === 1 ? 'Weekly' : `Every ${pattern.interval} weeks`;
      case 'monthly':
        const dayText = pattern.month_day ? ` on day ${pattern.month_day}` : '';
        return pattern.interval === 1 ? `Monthly${dayText}` : `Every ${pattern.interval} months${dayText}`;
      default:
        return 'No recurrence';
    }
  };

  const handleWeekdayChange = (weekday, checked) => {
    const newWeekdays = checked 
      ? [...formData.recurrence_pattern.weekdays, weekday]
      : formData.recurrence_pattern.weekdays.filter(day => day !== weekday);
    
    setFormData({
      ...formData,
      recurrence_pattern: {
        ...formData.recurrence_pattern,
        weekdays: newWeekdays
      }
    });
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
              Recurring Tasks
            </h1>
            <p className="text-gray-400 mt-1">
              Automate your routine with smart recurring tasks
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleGenerateInstances}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors border border-gray-700"
            >
              <Play className="h-4 w-4" />
              <span>Generate Now</span>
            </button>
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:shadow-lg"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              <Plus className="h-5 w-5" />
              <span>New Recurring Task</span>
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

        {/* Recurring Tasks Grid */}
        {recurringTasks.length === 0 ? (
          <div className="text-center py-12">
            <Repeat className="mx-auto h-16 w-16 text-gray-600 mb-4" />
            <h3 className="text-xl font-medium text-gray-400 mb-2">No recurring tasks yet</h3>
            <p className="text-gray-500 mb-6">Create your first recurring task to automate routine work</p>
            <button
              onClick={() => setShowModal(true)}
              className="px-6 py-3 rounded-lg font-medium"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              Create First Recurring Task
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recurringTasks.map((task) => (
              <div
                key={task.id}
                className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all duration-200 hover:shadow-lg"
              >
                {/* Task Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-semibold text-white text-lg">{task.name}</h3>
                      {!task.is_active && (
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-600 text-gray-300">
                          Paused
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-400/10 text-blue-400">
                        {task.category}
                      </span>
                    </div>
                    {task.project_name && (
                      <p className="text-sm text-gray-400 mb-2">{task.project_name}</p>
                    )}
                  </div>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleEdit(task)}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(task.id)}
                      className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                {task.description && (
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {task.description}
                  </p>
                )}

                {/* Recurrence Pattern */}
                <div className="bg-gray-800 rounded-lg p-3 mb-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Repeat className="h-4 w-4 text-yellow-400" />
                    <span className="text-sm font-medium text-white">
                      {getRecurrenceDisplay(task.recurrence_pattern)}
                    </span>
                  </div>
                  {task.due_time && (
                    <div className="flex items-center space-x-2">
                      <Clock className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-400">
                        at {task.due_time}
                      </span>
                    </div>
                  )}
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-white">{task.total_instances}</div>
                    <div className="text-xs text-gray-500">Created</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-400">{task.completed_instances}</div>
                    <div className="text-xs text-gray-500">Done</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-yellow-400">{Math.round(task.completion_rate)}%</div>
                    <div className="text-xs text-gray-500">Rate</div>
                  </div>
                </div>

                {/* Next Due */}
                {task.next_due && (
                  <div className="flex items-center space-x-2 text-xs text-gray-400">
                    <Target className="h-3 w-3" />
                    <span>Next: {new Date(task.next_due).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-2xl border border-gray-800 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {editingTask ? 'Edit Recurring Task' : 'Create Recurring Task'}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="p-2 text-gray-400 hover:text-white rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Task Name
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      placeholder="e.g., Daily Exercise, Weekly Planning"
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
                      placeholder="Describe this recurring task"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Project
                      </label>
                      <select
                        value={formData.project_id}
                        onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        required
                      >
                        <option value="">Select a project</option>
                        {projects.map(project => (
                          <option key={project.id} value={project.id}>
                            {project.name} ({project.area_name})
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
                        Category
                      </label>
                      <select
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      >
                        <option value="general">General</option>
                        <option value="health">Health</option>
                        <option value="work">Work</option>
                        <option value="learning">Learning</option>
                        <option value="personal">Personal</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Default Time
                      </label>
                      <input
                        type="time"
                        value={formData.due_time}
                        onChange={(e) => setFormData({ ...formData, due_time: e.target.value })}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Recurrence Pattern */}
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-white mb-4">Recurrence Pattern</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Repeat Type
                      </label>
                      <select
                        value={formData.recurrence_pattern.type}
                        onChange={(e) => setFormData({
                          ...formData,
                          recurrence_pattern: {
                            ...formData.recurrence_pattern,
                            type: e.target.value,
                            weekdays: e.target.value === 'weekly' ? formData.recurrence_pattern.weekdays : []
                          }
                        })}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Every X {formData.recurrence_pattern.type.slice(0, -2)}(s)
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={formData.recurrence_pattern.interval}
                        onChange={(e) => setFormData({
                          ...formData,
                          recurrence_pattern: {
                            ...formData.recurrence_pattern,
                            interval: parseInt(e.target.value) || 1
                          }
                        })}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      />
                    </div>

                    {/* Weekly specific options */}
                    {formData.recurrence_pattern.type === 'weekly' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Days of Week
                        </label>
                        <div className="grid grid-cols-7 gap-2">
                          {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => (
                            <label key={day} className="flex items-center justify-center">
                              <input
                                type="checkbox"
                                checked={formData.recurrence_pattern.weekdays.includes(day)}
                                onChange={(e) => handleWeekdayChange(day, e.target.checked)}
                                className="sr-only"
                              />
                              <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xs font-medium border cursor-pointer transition-colors ${
                                formData.recurrence_pattern.weekdays.includes(day)
                                  ? 'bg-yellow-500 text-gray-900 border-yellow-500'
                                  : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
                              }`}>
                                {day.slice(0, 3).toUpperCase()}
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Monthly specific options */}
                    {formData.recurrence_pattern.type === 'monthly' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Day of Month (optional)
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="31"
                          value={formData.recurrence_pattern.month_day || ''}
                          onChange={(e) => setFormData({
                            ...formData,
                            recurrence_pattern: {
                              ...formData.recurrence_pattern,
                              month_day: e.target.value ? parseInt(e.target.value) : null
                            }
                          })}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="Leave empty for same day each month"
                        />
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          End Date (optional)
                        </label>
                        <input
                          type="date"
                          value={formData.recurrence_pattern.end_date ? formData.recurrence_pattern.end_date.split('T')[0] : ''}
                          onChange={(e) => setFormData({
                            ...formData,
                            recurrence_pattern: {
                              ...formData.recurrence_pattern,
                              end_date: e.target.value ? new Date(e.target.value).toISOString() : null
                            }
                          })}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Max Instances (optional)
                        </label>
                        <input
                          type="number"
                          min="1"
                          value={formData.recurrence_pattern.max_instances || ''}
                          onChange={(e) => setFormData({
                            ...formData,
                            recurrence_pattern: {
                              ...formData.recurrence_pattern,
                              max_instances: e.target.value ? parseInt(e.target.value) : null
                            }
                          })}
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                          placeholder="Unlimited"
                        />
                      </div>
                    </div>
                  </div>
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
                    <span>{editingTask ? 'Update' : 'Create'}</span>
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

export default RecurringTasks;