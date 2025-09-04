import React, { memo, useCallback, useMemo } from 'react';
import { arePropsEqualIgnoreFunctions } from '../../hooks/useMemorization';

/**
 * Optimized TaskItem component with React.memo
 * Only re-renders when task data changes, ignores callback functions
 */
export const TaskItem = memo(({ 
  task, 
  onToggleComplete, 
  onEdit, 
  onDelete,
  onViewDetails,
  isSelected 
}) => {
  const handleToggle = useCallback((e) => {
    e.stopPropagation();
    onToggleComplete(task.id);
  }, [task.id, onToggleComplete]);

  const handleEdit = useCallback((e) => {
    e.stopPropagation();
    onEdit(task);
  }, [task, onEdit]);

  const handleDelete = useCallback((e) => {
    e.stopPropagation();
    onDelete(task.id);
  }, [task.id, onDelete]);

  const priorityClass = useMemo(() => {
    switch (task.priority) {
      case 'high': return 'border-red-500 bg-red-500/10';
      case 'medium': return 'border-yellow-500 bg-yellow-500/10';
      case 'low': return 'border-green-500 bg-green-500/10';
      default: return 'border-gray-600';
    }
  }, [task.priority]);

  return (
    <div 
      className={`
        p-4 rounded-lg border transition-all cursor-pointer
        ${isSelected ? 'ring-2 ring-blue-500' : ''}
        ${task.completed ? 'opacity-50' : ''}
        ${priorityClass}
      `}
      onClick={() => onViewDetails(task)}
    >
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          className="mt-1 rounded border-gray-600"
          onClick={(e) => e.stopPropagation()}
        />
        
        <div className="flex-1 min-w-0">
          <h4 className={`font-medium ${task.completed ? 'line-through' : ''}`}>
            {task.name}
          </h4>
          {task.description && (
            <p className="text-sm text-gray-400 mt-1">{task.description}</p>
          )}
          
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            {task.due_date && (
              <span className="flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
            <span className={`
              px-2 py-1 rounded-full text-xs
              ${task.priority === 'high' ? 'bg-red-500/20 text-red-400' : ''}
              ${task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : ''}
              ${task.priority === 'low' ? 'bg-green-500/20 text-green-400' : ''}
            `}>
              {task.priority}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleEdit}
            className="p-1 hover:bg-gray-700 rounded transition-colors"
            title="Edit task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={handleDelete}
            className="p-1 hover:bg-red-500/20 rounded transition-colors"
            title="Delete task"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}, arePropsEqualIgnoreFunctions);

/**
 * Optimized TaskList component
 * Memoizes the task list to prevent unnecessary re-renders
 */
export const TaskList = memo(({ 
  tasks, 
  onToggleComplete, 
  onEdit, 
  onDelete,
  onViewDetails,
  selectedTaskId,
  emptyMessage = "No tasks found" 
}) => {
  // Memoize filtered/sorted tasks if needed
  const sortedTasks = useMemo(() => {
    return [...tasks].sort((a, b) => {
      // Sort by completion status first
      if (a.completed !== b.completed) {
        return a.completed ? 1 : -1;
      }
      // Then by priority
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }, [tasks]);

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <svg className="w-12 h-12 mx-auto mb-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {sortedTasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onEdit={onEdit}
          onDelete={onDelete}
          onViewDetails={onViewDetails}
          isSelected={task.id === selectedTaskId}
        />
      ))}
    </div>
  );
});

/**
 * Optimized TaskFilters component
 * Only re-renders when filter values change
 */
export const TaskFilters = memo(({ 
  filters, 
  onFilterChange,
  projects = [] 
}) => {
  const handleFilterChange = useCallback((filterType, value) => {
    onFilterChange({ ...filters, [filterType]: value });
  }, [filters, onFilterChange]);

  return (
    <div className="flex flex-wrap gap-4 mb-6">
      <select
        value={filters.status || 'all'}
        onChange={(e) => handleFilterChange('status', e.target.value)}
        className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
      >
        <option value="all">All Status</option>
        <option value="todo">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
      </select>

      <select
        value={filters.priority || 'all'}
        onChange={(e) => handleFilterChange('priority', e.target.value)}
        className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
      >
        <option value="all">All Priorities</option>
        <option value="high">High Priority</option>
        <option value="medium">Medium Priority</option>
        <option value="low">Low Priority</option>
      </select>

      <select
        value={filters.projectId || 'all'}
        onChange={(e) => handleFilterChange('projectId', e.target.value)}
        className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
      >
        <option value="all">All Projects</option>
        {projects.map(project => (
          <option key={project.id} value={project.id}>
            {project.name}
          </option>
        ))}
      </select>

      <input
        type="date"
        value={filters.dueDate || ''}
        onChange={(e) => handleFilterChange('dueDate', e.target.value)}
        className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
        placeholder="Due date"
      />

      {Object.keys(filters).some(key => filters[key] && filters[key] !== 'all') && (
        <button
          onClick={() => onFilterChange({})}
          className="px-3 py-2 text-sm text-red-400 hover:text-red-300 transition-colors"
        >
          Clear Filters
        </button>
      )}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if filters or projects change
  return JSON.stringify(prevProps.filters) === JSON.stringify(nextProps.filters) &&
         JSON.stringify(prevProps.projects) === JSON.stringify(nextProps.projects);
});