import React, { useState, useEffect, memo } from 'react';
import {
  Loader2,
  CheckSquare,
  AlertCircle,
  Clock,
  Check,
  Flag,
  Plus,
  ChevronDown,
  ChevronUp,
  Repeat,
  X,
  FolderOpen
} from 'lucide-react';
import { useDataContext } from '../contexts/DataContext';
import { tasksAPI, handleApiError } from '../services/api';
import FileAttachment from './ui/FileAttachment';
import TaskWhyStatements from './TaskWhyStatements';

// ... rest of imports remain

const TaskCard = memo(({ task, onToggle, onEdit, onDelete, loading }) => {
  const priorityColor =
    task.priority === 'high' ? 'text-red-400' :
    task.priority === 'medium' ? 'text-yellow-400' : 'text-green-400';

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => onToggle(task.id, !task.completed)}
              className="rounded bg-gray-700 border-gray-600 text-yellow-400 focus:ring-yellow-400 focus:ring-2"
            />
            <span className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>{task.name}</span>
          </div>
          {task.description && (
            <p className="text-sm text-gray-400 mt-1">{task.description}</p>
          )}
        </div>
        <div className="text-right text-xs text-gray-500">
          <div className={priorityColor}>{(task.priority || 'medium').toUpperCase()}</div>
          {task.due_date && (
            <div>{new Date(task.due_date).toLocaleDateString()}</div>
          )}
        </div>
      </div>
      <div className="flex items-center justify-end space-x-2 mt-3">
        <button
          onClick={() => onEdit(task)}
          className="px-2 py-1 text-xs rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="px-2 py-1 text-xs rounded bg-gray-700 hover:bg-gray-600 text-red-400"
        >
          Delete
        </button>
      </div>
    </div>
  );
});

TaskCard.displayName = 'TaskCard';

const TaskModal = memo(({ task, isOpen, onClose, onSave, loading, defaultProjectId }) => {
  const [name, setName] = useState(task?.name || '');
  const [description, setDescription] = useState(task?.description || '');

  useEffect(() => {
    setName(task?.name || '');
    setDescription(task?.description || '');
  }, [task]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 w-full max-w-lg" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <div className="text-white font-semibold">{task ? 'Edit Task' : 'Create Task'}</div>
          <button className="text-gray-400 hover:text-white" onClick={onClose}>✕</button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-400">Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-700 rounded p-2 text-white text-sm" placeholder="Task name" />
          </div>
          <div>
            <label className="text-xs text-gray-400">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-700 rounded p-2 text-white text-sm" rows={3} placeholder="Optional details" />
          </div>
          {/* Visible FileAttachment placeholder */}
          <FileAttachment parentType="task" parentId={task?.id} parentName={task?.name || name} />
          <div className="flex justify-end gap-2 pt-2">
            <button className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded" onClick={onClose}>Cancel</button>
            <button className="px-3 py-1.5 text-sm bg-yellow-600 hover:bg-yellow-700 rounded text-black font-semibold" disabled={loading || !name.trim()} onClick={() => onSave({ name: name.trim(), description: description.trim() })}>
              {loading ? 'Saving…' : 'Save'}
            </button>
          </div>
        </div>
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
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [priorityChip, setPriorityChip] = useState('all'); // all, high, medium, low
  const [dueChip, setDueChip] = useState('all'); // all, overdue, today, week
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(20);
  const [total, setTotal] = useState(null);
  const [hasMore, setHasMore] = useState(false);

  // URL query sync for search
  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const q = params.get('tasks_q');
      if (q && !search) setSearch(q);
    } catch {}
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    try {
      const url = new URL(window.location.href);
      if (debouncedSearch) {
        url.searchParams.set('tasks_q', debouncedSearch);
      } else {
        url.searchParams.delete('tasks_q');
      }
      window.history.replaceState({}, '', url);
    } catch {}
  }, [debouncedSearch]);

  // Extract project filter from section params
  const activeProjectId = sectionParams?.projectId || null;
  const activeProjectName = sectionParams?.projectName || null;

  useEffect(() => {
    fetchTasks();
  }, [debouncedSearch, priorityChip, dueChip, filter, activeProjectId, page, limit]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await tasksAPI.getTasks({
        // Initial load: no filters, but keep API flexible for future
        returnMeta: false,
      });
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
        
        // Consistency window for tasks after update
        try { localStorage.setItem('TASKS_FORCE_STANDARD_UNTIL', String(Date.now() + 2000)); } catch {}
      } else {
        const response = await tasksAPI.createTask(formData);
        // Add to local state
        setTasks(prev => [...prev, response.data]);
        
        // Notify data context of the mutation
        onDataMutation('task', 'create', response.data);
        
        // Consistency window for tasks after create
        try { localStorage.setItem('TASKS_FORCE_STANDARD_UNTIL', String(Date.now() + 2500)); } catch {}
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

  // Quick chips for tasks (move above filters to avoid reference errors)
  const [priorityChip, setPriorityChip] = useState('all'); // all, high, medium, low
  const [dueChip, setDueChip] = useState('all'); // all, overdue, today, week
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(20);
  const [total, setTotal] = useState(null);
  const [hasMore, setHasMore] = useState(false);

  const filteredTasks = filteredTasksByProject
    .filter(task => {
      switch (filter) {
        case 'active': return !task.completed;
        case 'completed': return task.completed;
        default: return true;
      }
    })
    .filter(task => {
      // Priority chip
      if (priorityChip !== 'all') {
        if ((task.priority || 'medium') !== priorityChip) return false;
      }
      // Due chip
      if (dueChip !== 'all') {
        const due = task.due_date ? new Date(task.due_date) : null;
        const now = new Date();
        const endOfToday = new Date(); endOfToday.setHours(23,59,59,999);
        const endOfWeek = new Date(); const d = endOfWeek.getDate(); endOfWeek.setDate(d + (7 - endOfWeek.getDay())); endOfWeek.setHours(23,59,59,999);
        if (dueChip === 'overdue' && !(due && due < now && !task.completed)) return false;
        if (dueChip === 'today' && !(due && due <= endOfToday)) return false;
        if (dueChip === 'week' && !(due && due <= endOfWeek)) return false;
      }
      return true;
    })
    .filter(task => {
      const q = (debouncedSearch || search).trim().toLowerCase();
      if (!q) return true;
      const fields = [task.name, task.description, task.category, activeProjectName]
        .map(v => (v || '').toLowerCase());
      return fields.some(f => f.includes(q));
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
                  <FolderOpen className="h-5 w-5 text-yellow-400" />
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
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tasks..."
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
          <button
            data-testid="task-new"
            onClick={handleCreateTask}
            className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
          >
            <Plus size={20} />
            <span>Add Task</span>
          </button>
        </div>
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
      <div className="flex flex-wrap gap-2 items-center">
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
        {/* Quick chips */}
        <div className="flex items-center gap-2 ml-2">
          {['all','high','medium','low'].map(p => (
            <button key={p} onClick={() => setPriorityChip(p)} className={`px-2 py-1 rounded text-xs ${priorityChip===p? 'bg-yellow-600 text-black':'bg-gray-800 text-gray-300 border border-gray-700'}`}>prio:{p}</button>
          ))}
          {['all','overdue','today','week'].map(d => (
            <button key={d} onClick={() => setDueChip(d)} className={`px-2 py-1 rounded text-xs ${dueChip===d? 'bg-yellow-600 text-black':'bg-gray-800 text-gray-300 border border-gray-700'}`}>due:{d}</button>
          ))}
        </div>
      </div>

      {/* Tasks Grid */}
      {filteredTasks.length > 0 ? (
        <div className="space-y-8">
          {/* Task Why Statements - Show insights for active tasks */}
          {filteredTasks.filter(task => !task.completed).length > 0 && (
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <TaskWhyStatements 
                taskIds={filteredTasks.filter(task => !task.completed).slice(0, 5).map(task => task.id)}
                showAll={false}
              />
            </div>
          )}
          
          {/* Tasks List */}
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
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-lg bg-yellow-400/20 flex items-center justify-center mx-auto mb-4">
            <CheckSquare size={32} className="text-yellow-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">
            {filter === 'completed' ? 'No completed tasks' : 
             filter === 'active' ? 'No active tasks' : (search ? 'No tasks match your search' : 'No tasks yet')}
          </h3>
          <p className="text-gray-400 mb-6">
            {filter === 'all' ? (search ? 'Try a different search term' : 'Create your first task to get started') : 
             `Switch to ${filter === 'completed' ? 'active' : 'all'} tasks to see more`}
          </p>
          {filter === 'all' && !search && (
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

export { TaskModal };
export default Tasks;