import React, { useState, useEffect } from 'react';
import { CheckSquare, Plus, Calendar, Flag, Clock, Check } from 'lucide-react';
import { mockTasks, getStoredData, setStoredData } from '../data/mock';

const TaskCard = ({ task, onToggle, onEdit }) => {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-400';
      case 'medium': return 'bg-yellow-400';
      case 'low': return 'bg-green-400';
      default: return 'bg-gray-400';
    }
  };

  const isOverdue = new Date(task.dueDate) < new Date() && !task.completed;

  return (
    <div className={`p-6 rounded-xl border transition-all duration-300 group hover:scale-105 ${
      task.completed 
        ? 'border-green-400/30 bg-gradient-to-br from-green-900/20 to-gray-800/30' 
        : isOverdue
        ? 'border-red-400/30 bg-gradient-to-br from-red-900/20 to-gray-800/30'
        : 'border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30'
    }`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3 flex-1">
          <div 
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-200 mt-1 ${
              task.completed 
                ? 'bg-green-400 border-green-400' 
                : 'border-gray-500 hover:border-yellow-400'
            }`}
            onClick={() => onToggle(task.id)}
          >
            {task.completed && <Check size={14} style={{ color: '#0B0D14' }} />}
          </div>
          <div className="flex-1">
            <h3 className={`text-lg font-semibold mb-2 ${
              task.completed ? 'text-gray-400 line-through' : 'text-white'
            }`}>
              {task.title}
            </h3>
            <p className="text-sm text-gray-400 mb-3">{task.description}</p>
            
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <Calendar size={14} className="text-gray-400" />
                <span className={`${isOverdue && !task.completed ? 'text-red-400' : 'text-gray-400'}`}>
                  {task.dueDate}
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
          >
            <Clock size={14} className="text-gray-400" />
          </button>
        </div>
      </div>
    </div>
  );
};

const TaskModal = ({ task, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    category: 'personal'
  });

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description,
        priority: task.priority,
        dueDate: task.dueDate,
        category: task.category
      });
    } else {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        dueDate: tomorrow.toISOString().split('T')[0],
        category: 'personal'
      });
    }
  }, [task, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
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
          >
            <Plus size={20} className="text-gray-400 rotate-45" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Task Title
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              placeholder="What needs to be done?"
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
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              rows="3"
              placeholder="Add more details..."
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
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
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
                value={formData.dueDate}
                onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
                className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
                required
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
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
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-700 text-gray-300 hover:bg-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              {task ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Tasks = () => {
  const [tasks, setTasks] = useState(() => getStoredData('tasks', mockTasks));
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState('all'); // all, active, completed

  useEffect(() => {
    setStoredData('tasks', tasks);
  }, [tasks]);

  const handleToggleTask = (taskId) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId 
        ? { ...task, completed: !task.completed }
        : task
    ));
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setModalOpen(true);
  };

  const handleCreateTask = () => {
    setEditingTask(null);
    setModalOpen(true);
  };

  const handleSaveTask = (formData) => {
    if (editingTask) {
      setTasks(prev => prev.map(task =>
        task.id === editingTask.id
          ? { ...task, ...formData }
          : task
      ));
    } else {
      const newTask = {
        id: Date.now().toString(),
        ...formData,
        completed: false
      };
      setTasks(prev => [...prev, newTask]);
    }
    setModalOpen(false);
    setEditingTask(null);
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
  const overdueCount = tasks.filter(t => !t.completed && new Date(t.dueDate) < new Date()).length;

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
      <div className="space-y-4">
        {filteredTasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onToggle={handleToggleTask}
            onEdit={handleEditTask}
          />
        ))}
      </div>

      <TaskModal
        task={editingTask}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingTask(null);
        }}
        onSave={handleSaveTask}
      />
    </div>
  );
};

export default Tasks;