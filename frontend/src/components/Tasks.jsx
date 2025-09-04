import React, { useState, useEffect, memo, useCallback } from 'react';
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
  FolderOpen,
  Brain,
  Sparkles
} from 'lucide-react';
import { 
  useTasks, 
  useCreateTask, 
  useUpdateTask, 
  useDeleteTask, 
  useToggleTaskCompletion,
  useProjects 
} from '../hooks/useGraphQL';
import FileAttachment from './ui/FileAttachment';
import TaskWhyStatements from './TaskWhyStatements';
import AIBadge from './ui/AIBadge';
import AIInsightPanel from './ui/AIInsightPanel';
import { TaskItem } from './optimized/OptimizedTasks';

const TaskCard = memo(({ task, onToggle, onEdit, onDelete, loading, onAnalyzeWithAI, hrmInsight }) => {
  const [showInsightPanel, setShowInsightPanel] = useState(false);
  const priorityColor =
    task.priority === 'HIGH' ? 'text-red-400' :
    task.priority === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400';

  return (
    <div className="space-y-2">
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => onToggle(task.id)}
                className="rounded bg-gray-700 border-gray-600 text-yellow-400 focus:ring-yellow-400 focus:ring-2"
              />
              <span className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>{task.name}</span>
              {task.hrmPriorityScore && (
                <AIBadge 
                  confidence={task.hrmPriorityScore / 10} 
                  variant="confidence" 
                  size="xs"
                  onClick={() => setShowInsightPanel(!showInsightPanel)}
                />
              )}
            </div>
            {task.description && (
              <p className="text-sm text-gray-400 mt-1">{task.description}</p>
            )}
            {task.hrmPriorityScore && (
              <div className="text-xs text-yellow-400 mt-1">
                AI Priority Score: {task.hrmPriorityScore.toFixed(1)}
              </div>
            )}
          </div>
          <div className="text-right text-xs text-gray-500">
            <div className={priorityColor}>{task.priority}</div>
            {task.dueDate && (
              <div>{new Date(task.dueDate).toLocaleDateString()}</div>
            )}
          </div>
        </div>
        <div className="flex items-center justify-end space-x-2 mt-3">
          {onAnalyzeWithAI && (
            <button
              onClick={() => onAnalyzeWithAI(task)}
              className="px-2 py-1 text-xs rounded bg-gray-700 hover:bg-gray-600 text-purple-400 flex items-center space-x-1"
              title="Analyze with AI"
            >
              <Brain className="h-3 w-3" />
              <span>AI</span>
            </button>
          )}
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
      
      {/* AI Insight Panel */}
      {showInsightPanel && task.hrmReasoningSummary && (
        <AIInsightPanel 
          insight={{
            summary: task.hrmReasoningSummary,
            confidence_score: task.hrmPriorityScore / 10
          }}
          onClose={() => setShowInsightPanel(false)}
        />
      )}
    </div>
  );
});

TaskCard.displayName = 'TaskCard';

const Tasks = ({ onSectionChange, defaultProjectId }) => {
  const [selectedProjectId, setSelectedProjectId] = useState(defaultProjectId || null);
  const [newTaskName, setNewTaskName] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('MEDIUM');
  const [newTaskDueDate, setNewTaskDueDate] = useState('');
  const [editingTask, setEditingTask] = useState(null);
  const [showCompleted, setShowCompleted] = useState(false);
  const [isWhyStatementsOpen, setIsWhyStatementsOpen] = useState(false);
  const [selectedTaskForWhy, setSelectedTaskForWhy] = useState(null);

  // GraphQL Hooks
  const filter = {
    projectId: selectedProjectId,
    completed: showCompleted ? null : false
  };
  
  const { tasks, loading: tasksLoading, error: tasksError, refetch } = useTasks(filter);
  const { projects, loading: projectsLoading } = useProjects();
  const { createTask, loading: creating } = useCreateTask();
  const { updateTask, loading: updating } = useUpdateTask();
  const { deleteTask, loading: deleting } = useDeleteTask();
  const { toggleTask, loading: toggling } = useToggleTaskCompletion();

  // Group tasks by project
  const tasksByProject = tasks.reduce((acc, task) => {
    const projectId = task.project?.id || 'no-project';
    if (!acc[projectId]) {
      acc[projectId] = [];
    }
    acc[projectId].push(task);
    return acc;
  }, {});

  // Handlers
  const handleCreateTask = useCallback(async () => {
    if (!newTaskName.trim() || !selectedProjectId) return;

    const input = {
      projectId: selectedProjectId,
      name: newTaskName,
      description: newTaskDescription,
      priority: newTaskPriority,
      dueDate: newTaskDueDate ? new Date(newTaskDueDate).toISOString() : null
    };

    const result = await createTask(input);
    
    if (result.data?.createTask?.success) {
      setNewTaskName('');
      setNewTaskDescription('');
      setNewTaskPriority('MEDIUM');
      setNewTaskDueDate('');
      refetch();
    }
  }, [newTaskName, newTaskDescription, newTaskPriority, newTaskDueDate, selectedProjectId, createTask, refetch]);

  const handleToggleTask = useCallback(async (taskId) => {
    await toggleTask(taskId);
    refetch();
  }, [toggleTask, refetch]);

  const handleUpdateTask = useCallback(async () => {
    if (!editingTask) return;

    const input = {
      id: editingTask.id,
      name: editingTask.name,
      description: editingTask.description,
      priority: editingTask.priority,
      dueDate: editingTask.dueDate
    };

    const result = await updateTask(input);
    
    if (result.data?.updateTask?.success) {
      setEditingTask(null);
      refetch();
    }
  }, [editingTask, updateTask, refetch]);

  const handleDeleteTask = useCallback(async (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await deleteTask(taskId);
      refetch();
    }
  }, [deleteTask, refetch]);

  const handleAnalyzeWithAI = useCallback((task) => {
    setSelectedTaskForWhy(task);
    setIsWhyStatementsOpen(true);
  }, []);

  if (tasksLoading || projectsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="animate-spin h-8 w-8 text-gray-400" />
      </div>
    );
  }

  if (tasksError) {
    return (
      <div className="text-center text-red-400 p-8">
        <AlertCircle className="h-12 w-12 mx-auto mb-4" />
        <p>Error loading tasks: {tasksError.message}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Tasks</h1>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2 text-gray-400">
            <input
              type="checkbox"
              checked={showCompleted}
              onChange={(e) => setShowCompleted(e.target.checked)}
              className="rounded bg-gray-700 border-gray-600 text-yellow-400"
            />
            <span>Show completed</span>
          </label>
        </div>
      </div>

      {/* Project Filter */}
      <div className="flex items-center space-x-4">
        <select
          value={selectedProjectId || ''}
          onChange={(e) => setSelectedProjectId(e.target.value || null)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-yellow-400"
        >
          <option value="">All Projects</option>
          {projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>

      {/* New Task Form */}
      {selectedProjectId && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Add New Task</h2>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Task name"
              value={newTaskName}
              onChange={(e) => setNewTaskName(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-400"
            />
            <textarea
              placeholder="Description (optional)"
              value={newTaskDescription}
              onChange={(e) => setNewTaskDescription(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-yellow-400"
              rows={2}
            />
            <div className="flex items-center space-x-4">
              <select
                value={newTaskPriority}
                onChange={(e) => setNewTaskPriority(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-yellow-400"
              >
                <option value="LOW">Low Priority</option>
                <option value="MEDIUM">Medium Priority</option>
                <option value="HIGH">High Priority</option>
              </select>
              <input
                type="date"
                value={newTaskDueDate}
                onChange={(e) => setNewTaskDueDate(e.target.value)}
                className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-yellow-400"
              />
              <button
                onClick={handleCreateTask}
                disabled={!newTaskName.trim() || creating}
                className="px-6 py-2 bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-600 text-black font-medium rounded-lg transition-colors flex items-center space-x-2"
              >
                {creating ? (
                  <Loader2 className="animate-spin h-4 w-4" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                <span>{creating ? 'Creating...' : 'Add Task'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tasks List */}
      {tasks.length === 0 ? (
        <div className="text-center py-12">
          <CheckSquare className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No tasks yet. Select a project and create your first task!</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(tasksByProject).map(([projectId, projectTasks]) => {
            const project = projects.find(p => p.id === projectId);
            return (
              <div key={projectId} className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <FolderOpen className="h-5 w-5 text-gray-400" />
                  <span>{project?.name || 'No Project'}</span>
                  <span className="text-sm text-gray-500">({projectTasks.length})</span>
                </h3>
                {projectTasks.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onToggle={handleToggleTask}
                    onEdit={setEditingTask}
                    onDelete={handleDeleteTask}
                    loading={toggling || updating || deleting}
                    onAnalyzeWithAI={handleAnalyzeWithAI}
                    hrmInsight={task.hrmPriorityScore ? task : null}
                  />
                ))}
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-semibold text-white mb-4">Edit Task</h2>
            <div className="space-y-4">
              <input
                type="text"
                value={editingTask.name}
                onChange={(e) => setEditingTask({ ...editingTask, name: e.target.value })}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              />
              <textarea
                value={editingTask.description || ''}
                onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                rows={3}
              />
              <select
                value={editingTask.priority}
                onChange={(e) => setEditingTask({ ...editingTask, priority: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              >
                <option value="LOW">Low Priority</option>
                <option value="MEDIUM">Medium Priority</option>
                <option value="HIGH">High Priority</option>
              </select>
              <input
                type="date"
                value={editingTask.dueDate ? editingTask.dueDate.split('T')[0] : ''}
                onChange={(e) => setEditingTask({ ...editingTask, dueDate: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              />
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setEditingTask(null)}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateTask}
                  disabled={updating}
                  className="px-4 py-2 bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-600 text-black font-medium rounded-lg"
                >
                  {updating ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Task Why Statements Modal */}
      {isWhyStatementsOpen && selectedTaskForWhy && (
        <TaskWhyStatements
          task={selectedTaskForWhy}
          onClose={() => {
            setIsWhyStatementsOpen(false);
            setSelectedTaskForWhy(null);
          }}
        />
      )}
    </div>
  );
};

export default Tasks;