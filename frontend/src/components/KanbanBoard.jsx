import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  MoreVertical, 
  Edit2, 
  Trash2, 
  Calendar, 
  Clock,
  Circle,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  X
} from 'lucide-react';
import { projectsAPI, tasksAPI } from '../services/api';

const KanbanBoard = ({ projectId, onBack }) => {
  const [project, setProject] = useState(null);
  const [kanbanData, setKanbanData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState('todo');
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({
    name: '',  // Changed from 'title' to 'name' to match backend
    description: '',
    priority: 'medium',
    due_date: '',
    status: 'todo'
  });

  const columns = [
    { id: 'todo', title: 'To Do', color: 'text-gray-400 bg-gray-700' },
    { id: 'in-progress', title: 'In Progress', color: 'text-blue-400 bg-blue-600' },
    { id: 'review', title: 'Review', color: 'text-yellow-400 bg-yellow-600' },
    { id: 'completed', title: 'Completed', color: 'text-green-400 bg-green-600' }
  ];

  const priorityColors = {
    low: 'text-green-400 bg-green-400/10 border-green-400/20',
    medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
    high: 'text-red-400 bg-red-400/10 border-red-400/20'
  };

  const loadKanbanData = async () => {
    try {
      setLoading(true);
      const [projectResponse, kanbanResponse] = await Promise.all([
        projectsAPI.getProject(projectId, true),
        projectsAPI.getKanbanBoard(projectId)
      ]);
      
      setProject(projectResponse.data);
      setKanbanData(kanbanResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load kanban data');
      console.error('Error loading kanban:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadKanbanData();
    }
  }, [projectId]);

  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      const taskData = {
        ...formData,
        project_id: projectId,
        due_date: formData.due_date || null
      };
      
      if (editingTask) {
        await tasksAPI.updateTask(editingTask.id, taskData);
      } else {
        await tasksAPI.createTask(taskData);
      }
      
      loadKanbanData();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving task:', err);
      setError(editingTask ? 'Failed to update task' : 'Failed to create task');
    }
  };

  const handleMoveTask = async (taskId, newColumn) => {
    try {
      await tasksAPI.moveTaskColumn(taskId, newColumn);
      loadKanbanData();
    } catch (err) {
      console.error('Error moving task:', err);
      setError('Failed to move task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await tasksAPI.deleteTask(taskId);
        loadKanbanData();
      } catch (err) {
        console.error('Error deleting task:', err);
        setError('Failed to delete task');
      }
    }
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setFormData({
      name: task.name || task.title || '', // Handle both field names for backward compatibility
      description: task.description || '',
      priority: task.priority || 'medium',
      due_date: task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : '',
      status: task.status || 'todo'
    });
    setShowTaskModal(true);
  };

  const handleCloseModal = () => {
    setShowTaskModal(false);
    setEditingTask(null);
    setSelectedColumn('todo');
    setFormData({
      name: '',
      description: '',
      priority: 'medium',
      due_date: '',
      status: 'todo'
    });
  };

  const handleAddTask = (columnId) => {
    setSelectedColumn(columnId);
    setFormData({ ...formData, status: columnId });
    setShowTaskModal(true);
  };

  const isOverdue = (dueDate) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="grid grid-cols-4 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-96 bg-gray-800 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !kanbanData) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
            <h3 className="text-lg font-medium text-red-400 mb-2">Error Loading Kanban Board</h3>
            <p className="text-red-300">{error}</p>
            <button
              onClick={loadKanbanData}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={onBack}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Projects</span>
            </button>
            <div>
              <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                {project?.name || 'Project Kanban'}
              </h1>
              <p className="text-gray-400 mt-1">
                {project?.description || 'Manage tasks with drag & drop'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-medium text-white">
              {kanbanData?.completed_tasks || 0} / {kanbanData?.total_tasks || 0} Complete
            </p>
            <p className="text-sm text-gray-400">
              {Math.round(((kanbanData?.completed_tasks || 0) / Math.max(kanbanData?.total_tasks || 1, 1)) * 100)}% Progress
            </p>
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

        {/* Kanban Board */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {columns.map((column) => {
            const columnTasks = kanbanData?.columns?.[column.id] || [];
            const taskCount = columnTasks.length;

            return (
              <div key={column.id} className="flex flex-col">
                {/* Column Header */}
                <div className="flex items-center justify-between p-4 mb-4 bg-gray-900/50 border border-gray-800 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${column.color.split(' ')[1]}`} />
                    <h3 className="font-semibold text-white">{column.title}</h3>
                    <span className="text-sm text-gray-400 bg-gray-800 px-2 py-1 rounded-full">
                      {taskCount}
                    </span>
                  </div>
                  <button
                    onClick={() => handleAddTask(column.id)}
                    className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>

                {/* Column Tasks */}
                <div className="flex-1 space-y-3 min-h-[400px]">
                  {columnTasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-4 bg-gray-900/30 border rounded-lg hover:border-gray-600 transition-all duration-200 cursor-pointer ${
                        isOverdue(task.due_date) && task.status !== 'completed'
                          ? 'border-red-600/50 bg-red-900/10'
                          : 'border-gray-800'
                      }`}
                    >
                      {/* Task Header */}
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-white text-sm leading-tight">
                          {task.title}
                        </h4>
                        <div className="relative">
                          <button
                            className="p-1 text-gray-400 hover:text-white rounded"
                            onClick={(e) => {
                              e.stopPropagation();
                              // Could implement dropdown menu here
                            }}
                          >
                            <MoreVertical className="h-4 w-4" />
                          </button>
                        </div>
                      </div>

                      {/* Task Description */}
                      {task.description && (
                        <p className="text-xs text-gray-400 mb-3 line-clamp-2">
                          {task.description}
                        </p>
                      )}

                      {/* Task Meta */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${priorityColors[task.priority] || priorityColors.medium}`}>
                            {task.priority}
                          </span>
                        </div>
                        
                        {task.due_date && (
                          <div className={`flex items-center space-x-1 text-xs ${
                            isOverdue(task.due_date) && task.status !== 'completed'
                              ? 'text-red-400'
                              : 'text-gray-400'
                          }`}>
                            <Clock className="h-3 w-3" />
                            <span>
                              {new Date(task.due_date).toLocaleDateString()}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Task Actions */}
                      <div className="flex space-x-1 mt-3 pt-3 border-t border-gray-800">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditTask(task);
                          }}
                          className="flex-1 flex items-center justify-center space-x-1 px-2 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors"
                        >
                          <Edit2 className="h-3 w-3" />
                          <span>Edit</span>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteTask(task.id);
                          }}
                          className="flex-1 flex items-center justify-center space-x-1 px-2 py-1 text-xs bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded transition-colors"
                        >
                          <Trash2 className="h-3 w-3" />
                          <span>Delete</span>
                        </button>
                      </div>

                      {/* Move Task Buttons */}
                      <div className="flex space-x-1 mt-2">
                        {columns.map((col) => {
                          if (col.id === task.status) return null;
                          return (
                            <button
                              key={col.id}
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMoveTask(task.id, col.id);
                              }}
                              className="flex-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
                            >
                              → {col.title}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}

                  {/* Empty State */}
                  {taskCount === 0 && (
                    <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                      <Circle className="h-8 w-8 mb-2" />
                      <p className="text-sm">No tasks in {column.title.toLowerCase()}</p>
                      <button
                        onClick={() => handleAddTask(column.id)}
                        className="mt-2 px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors"
                      >
                        Add Task
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Task Modal */}
        {showTaskModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md border border-gray-800">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">
                  {editingTask ? 'Edit Task' : 'Create New Task'}
                </h2>
                <button
                  onClick={handleCloseModal}
                  className="p-2 text-gray-400 hover:text-white rounded-lg"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleCreateTask} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    placeholder="Task title"
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
                    placeholder="Task description"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
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

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    >
                      {columns.map(col => (
                        <option key={col.id} value={col.id}>{col.title}</option>
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
                    className="flex-1 px-4 py-2 rounded-lg font-medium transition-colors"
                    style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                  >
                    {editingTask ? 'Update' : 'Create'}
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

export default KanbanBoard;