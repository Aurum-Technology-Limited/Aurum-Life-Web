import React, { useState, useEffect } from 'react';
import { useDrag, useDrop } from 'react-dnd';
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
  X,
  GripVertical
} from 'lucide-react';
import { projectsAPI, tasksAPI } from '../services/api';

const KanbanBoard = ({ project, tasks, onBack, onTaskUpdate, loading }) => {
  const [error, setError] = useState(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState('todo');
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    priority: 'medium',
    due_date: '',
    status: 'todo'
  });

  // Drag and Drop state (UI-3.3.2)
  const [optimisticTasks, setOptimisticTasks] = useState([]);
  const [dragError, setDragError] = useState(null);

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

  // Organize tasks by status/column
  const organizeTasksByColumn = () => {
    const organizedTasks = {
      todo: [],
      'in-progress': [],
      review: [],
      completed: []
    };

    // Use optimistic tasks if available, otherwise use props tasks
    const currentTasks = optimisticTasks.length > 0 ? optimisticTasks : (tasks || []);

    currentTasks.forEach(task => {
      const status = task.status || 'todo';
      // Map status to column ID
      const columnId = status === 'in_progress' ? 'in-progress' : status;
      if (organizedTasks[columnId]) {
        organizedTasks[columnId].push(task);
      } else {
        organizedTasks.todo.push(task); // Default to todo if status not recognized
      }
    });

    return organizedTasks;
  };

  const tasksByColumn = organizeTasksByColumn();
  const totalTasks = (optimisticTasks.length > 0 ? optimisticTasks : tasks)?.length || 0;
  const completedTasks = (optimisticTasks.length > 0 ? optimisticTasks : tasks || []).filter(task => task.completed || task.status === 'completed').length;

  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      const taskData = {
        ...formData,
        project_id: project.id,
        due_date: formData.due_date || null
      };
      
      if (editingTask) {
        await tasksAPI.updateTask(editingTask.id, taskData);
      } else {
        await tasksAPI.createTask(taskData);
      }
      
      // Use shared callback to refresh data
      onTaskUpdate();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving task:', err);
      setError(editingTask ? 'Failed to update task' : 'Failed to create task');
    }
  };

  const handleMoveTask = async (taskId, newColumn) => {
    try {
      await tasksAPI.moveTaskColumn(taskId, newColumn);
      onTaskUpdate();
    } catch (err) {
      console.error('Error moving task:', err);
      setError('Failed to move task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await tasksAPI.deleteTask(taskId);
        onTaskUpdate();
      } catch (err) {
        console.error('Error deleting task:', err);
        setError('Failed to delete task');
      }
    }
  };

  // Enhanced Drag & Drop Handlers (FR-3.1.1, FR-3.1.2, UI-3.3.2)
  const handleDragStart = (task) => {
    setDraggedTask(task);
    setDragError(null);
  };

  const handleDragEnd = () => {
    setDraggedTask(null);
  };

  const handleDrop = async (task, targetColumn) => {
    if (!task || !targetColumn || task.status === targetColumn) {
      return;
    }

    // Map column IDs to status values
    const columnToStatus = {
      'todo': 'todo',
      'in-progress': 'in_progress', 
      'review': 'review',
      'completed': 'completed'
    };

    const newStatus = columnToStatus[targetColumn];
    if (!newStatus) {
      console.error('Invalid target column:', targetColumn);
      return;
    }

    // Optimistic update (UI-3.3.2)
    const originalTasks = tasks;
    const optimisticTaskUpdate = tasks.map(t => 
      t.id === task.id 
        ? { ...t, status: newStatus, kanban_column: targetColumn }
        : t
    );
    setOptimisticTasks(optimisticTaskUpdate);

    try {
      // Update task status via API (FR-3.1.2)
      await tasksAPI.updateTask(task.id, { status: newStatus });
      
      // Refresh data to get the latest state
      onTaskUpdate();
      setOptimisticTasks([]);
      setDragError(null);
      
    } catch (err) {
      console.error('Error updating task status:', err);
      
      // Revert optimistic update on error (UI-3.3.2)
      setOptimisticTasks([]);
      setDragError(`Failed to move "${task.name}" to ${targetColumn.replace('-', ' ')}`);
      
      // Clear error after 5 seconds
      setTimeout(() => setDragError(null), 5000);
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

  // Draggable Task Card Component (UI-3.3.1)
  const DraggableTaskCard = ({ task, columnId }) => {
    const [{ isDragging }, drag] = useDrag(() => ({
      type: 'task',
      item: { ...task, sourceColumn: columnId },
      collect: (monitor) => ({
        isDragging: monitor.isDragging(),
      }),
    }));

    const isBlocked = task.can_start === false;
    
    return (
      <div
        ref={drag}
        className={`bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700 cursor-move transition-all duration-200 hover:border-gray-600 group ${
          isDragging ? 'opacity-50 rotate-1 scale-105' : ''
        } ${
          draggedTask?.id === task.id ? 'shadow-lg shadow-yellow-400/20' : ''
        } ${
          isBlocked ? 'opacity-75 border-orange-400/30' : ''
        }`}
        style={{
          transform: isDragging ? 'rotate(2deg)' : 'none',
        }}
      >
        {/* Drag Handle */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <GripVertical size={16} className="text-gray-500 group-hover:text-gray-400" />
            {isBlocked && (
              <div className="text-orange-400" title="Task has unmet dependencies">
                🔒
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => handleEditTask(task)}
              className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-blue-400 transition-all"
            >
              <Edit2 size={14} />
            </button>
            <button
              onClick={() => handleDeleteTask(task.id)}
              className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-400 transition-all"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {/* Task Content */}
        <h4 className="text-white font-medium mb-2 line-clamp-2">
          {task.name || task.title || 'Unnamed Task'}
        </h4>
        
        {task.description && (
          <p className="text-gray-400 text-sm mb-3 line-clamp-2">
            {task.description}
          </p>
        )}

        {/* Task Metadata */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            {/* Priority */}
            <span className={`px-2 py-1 rounded-full border ${priorityColors[task.priority] || priorityColors.medium}`}>
              {task.priority || 'medium'}
            </span>
            
            {/* Due Date */}
            {task.due_date && (
              <div className={`flex items-center space-x-1 ${
                isOverdue(task.due_date) && !task.completed ? 'text-red-400' : 'text-gray-400'
              }`}>
                <Calendar size={12} />
                <span>{new Date(task.due_date).toLocaleDateString()}</span>
              </div>
            )}
          </div>
          
          <div className="text-gray-500">
            #{task.id?.slice(-6) || 'N/A'}
          </div>
        </div>
      </div>
    );
  };

  // Droppable Column Component (UI-3.3.1)
  const DroppableColumn = ({ column, children }) => {
    const [{ isOver, canDrop }, drop] = useDrop(() => ({
      accept: 'task',
      drop: (item, monitor) => {
        if (item.sourceColumn !== column.id) {
          handleDrop(item, column.id);
        }
      },
      collect: (monitor) => ({
        isOver: monitor.isOver(),
        canDrop: monitor.canDrop(),
      }),
    }));

    return (
      <div
        ref={drop}
        className={`bg-gray-900/50 rounded-xl p-4 border-2 transition-all duration-200 ${
          isOver && canDrop
            ? 'border-yellow-400 bg-yellow-400/5 shadow-lg' 
            : isOver
            ? 'border-red-400 bg-red-400/5'
            : 'border-gray-800 hover:border-gray-700'
        }`}
        style={{
          minHeight: '500px',
        }}
      >
        {children}
      </div>
    );
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

  if (error && !tasks) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
            <h3 className="text-lg font-medium text-red-400 mb-2">Error Loading Kanban Board</h3>
            <p className="text-red-300">{error}</p>
            <button
              onClick={onTaskUpdate}
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
              {completedTasks} / {totalTasks} Complete
            </p>
            <p className="text-sm text-gray-400">
              {Math.round((completedTasks / Math.max(totalTasks, 1)) * 100)}% Progress
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

        {/* Drag Error Display (UI-3.3.2) */}
        {dragError && (
          <div className="bg-orange-900/20 border border-orange-600 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-orange-400 mr-2" />
              <span className="text-orange-400">{dragError}</span>
            </div>
          </div>
        )}

        {/* Enhanced Kanban Board with Drag & Drop (UI-3.3.1) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {columns.map((column) => {
            const columnTasks = tasksByColumn[column.id] || [];
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
                    title={`Add task to ${column.title}`}
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>

                {/* Droppable Column with Tasks */}
                <DroppableColumn column={column}>
                  <div className="space-y-3">
                    {columnTasks.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <div className="text-4xl mb-2">📋</div>
                        <div className="text-sm">Drop tasks here</div>
                        <div className="text-xs text-gray-600">or click + to add</div>
                      </div>
                    ) : (
                      columnTasks.map((task) => (
                        <DraggableTaskCard 
                          key={task.id} 
                          task={task} 
                          columnId={column.id}
                        />
                      ))
                    )}
                  </div>
                </DroppableColumn>
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