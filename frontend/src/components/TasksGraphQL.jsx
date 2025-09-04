/**
 * Tasks Component using GraphQL
 * Demonstrates efficient data fetching with Apollo Client
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Plus,
  Filter,
  CheckCircle,
  Circle,
  Calendar,
  Clock,
  AlertCircle,
  ChevronDown,
  Search,
} from 'lucide-react';
import {
  useTasks,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  useToggleTaskCompletion,
} from '../hooks/useGraphQL';
import { TaskItem, TaskFilters } from './optimized/OptimizedTasks';
import { Button } from './ui/button';
import { Input } from './ui/input';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

const TasksGraphQL = ({ projectId = null }) => {
  // State
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState({
    status: null,
    priority: null,
    projectId: projectId,
    completed: null,
  });
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    priority: 'MEDIUM',
    dueDate: null,
    projectId: projectId || '',
  });

  // GraphQL Hooks
  const { tasks, totalCount, hasNextPage, loading, error, refetch, loadMore } = useTasks(filter);
  const { createTask, loading: creating } = useCreateTask();
  const { updateTask, loading: updating } = useUpdateTask();
  const { deleteTask, loading: deleting } = useDeleteTask();
  const { toggleTask, loading: toggling } = useToggleTaskCompletion();

  // Filter tasks by search term
  const filteredTasks = useMemo(() => {
    if (!searchTerm) return tasks;
    
    const search = searchTerm.toLowerCase();
    return tasks.filter(
      task =>
        task.name.toLowerCase().includes(search) ||
        task.description?.toLowerCase().includes(search)
    );
  }, [tasks, searchTerm]);

  // Handlers
  const handleCreateTask = useCallback(async () => {
    if (!newTask.name.trim()) return;

    const input = {
      projectId: newTask.projectId,
      name: newTask.name,
      description: newTask.description,
      priority: newTask.priority,
      dueDate: newTask.dueDate ? new Date(newTask.dueDate).toISOString() : null,
    };

    const result = await createTask(input);
    
    if (result.data?.createTask?.success) {
      setShowCreateDialog(false);
      setNewTask({
        name: '',
        description: '',
        priority: 'MEDIUM',
        dueDate: null,
        projectId: projectId || '',
      });
    }
  }, [newTask, createTask, projectId]);

  const handleToggleTask = useCallback(async (taskId) => {
    await toggleTask(taskId);
  }, [toggleTask]);

  const handleUpdateTask = useCallback(async (taskId, updates) => {
    await updateTask({ id: taskId, ...updates });
  }, [updateTask]);

  const handleDeleteTask = useCallback(async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await deleteTask(taskId);
    }
  }, [deleteTask]);

  const handleFilterChange = useCallback((newFilter) => {
    setFilter(prevFilter => ({ ...prevFilter, ...newFilter }));
  }, []);

  // Loading state
  if (loading && !tasks.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading tasks...</div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Error loading tasks: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Tasks</h2>
          <p className="text-gray-400 mt-1">
            {totalCount} tasks • {filteredTasks.filter(t => !t.completed).length} active
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>

          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                New Task
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Create New Task</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="text-sm font-medium">Task Name</label>
                  <Input
                    value={newTask.name}
                    onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                    placeholder="Enter task name..."
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Description</label>
                  <textarea
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                    placeholder="Enter description..."
                    className="mt-1 w-full p-2 bg-gray-800 border border-gray-700 rounded-md"
                    rows={3}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Priority</label>
                    <Select
                      value={newTask.priority}
                      onValueChange={(value) => setNewTask({ ...newTask, priority: value })}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="LOW">Low</SelectItem>
                        <SelectItem value="MEDIUM">Medium</SelectItem>
                        <SelectItem value="HIGH">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Due Date</label>
                    <Input
                      type="date"
                      value={newTask.dueDate || ''}
                      onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                </div>
                
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowCreateDialog(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateTask}
                    disabled={creating || !newTask.name.trim()}
                  >
                    {creating ? 'Creating...' : 'Create Task'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search tasks..."
          className="pl-10"
        />
      </div>

      {/* Filters */}
      {showFilters && (
        <TaskFilters
          filters={filter}
          onFilterChange={handleFilterChange}
          projects={[]} // TODO: Load projects for filter
        />
      )}

      {/* Task List */}
      <div className="space-y-2">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-gray-600" />
            <p>No tasks found</p>
          </div>
        ) : (
          filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onToggleComplete={handleToggleTask}
              onEdit={(task) => {
                // TODO: Implement edit dialog
                console.log('Edit task:', task);
              }}
              onDelete={handleDeleteTask}
              onViewDetails={(task) => {
                // TODO: Implement task details view
                console.log('View task:', task);
              }}
            />
          ))
        )}
      </div>

      {/* Load More */}
      {hasNextPage && (
        <div className="flex justify-center mt-4">
          <Button
            variant="outline"
            onClick={loadMore}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Load More'}
          </Button>
        </div>
      )}

      {/* Loading States */}
      {(creating || updating || deleting || toggling) && (
        <div className="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg">
          Processing...
        </div>
      )}
    </div>
  );
};

export default TasksGraphQL;