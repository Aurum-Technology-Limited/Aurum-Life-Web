import React, { useState } from 'react';
import { LightBulbIcon, PlusIcon, CheckIcon, XIcon } from '@heroicons/react/outline';

const ProjectDecompositionHelper = ({ projectName, projectDescription, onTasksCreated, onCancel }) => {
  const [templateType, setTemplateType] = useState('general');
  const [suggestions, setSuggestions] = useState([]);
  const [selectedTasks, setSelectedTasks] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  const templateTypes = [
    { value: 'general', label: 'General Project', description: 'Basic project structure' },
    { value: 'learning', label: 'Learning & Education', description: 'Study and skill development' },
    { value: 'career', label: 'Career Development', description: 'Professional growth and advancement' },
    { value: 'health', label: 'Health & Fitness', description: 'Wellness and physical goals' },
    { value: 'work', label: 'Work Project', description: 'Business and work-related tasks' },
    { value: 'personal', label: 'Personal Development', description: 'Self-improvement and personal goals' }
  ];

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);

      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');

      if (!token) {
        setError('Authentication required');
        return;
      }

      // Use centralized API client
      try {
        const { aiCoachAPI } = await import('../services/api');
        const resp = await aiCoachAPI.decomposeProject(projectName, projectDescription, templateType);
        const data = resp?.data || {};
        setSuggestions(data.suggested_tasks || []);
        const allTaskIds = new Set((data.suggested_tasks || []).map((_, index) => index));
        setSelectedTasks(allTaskIds);
      } catch (e) {
        throw e;
      }
    } catch (err) {
      console.error('Error fetching suggestions:', err);
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleTaskToggle = (taskIndex) => {
    const newSelected = new Set(selectedTasks);
    if (newSelected.has(taskIndex)) {
      newSelected.delete(taskIndex);
    } else {
      newSelected.add(taskIndex);
    }
    setSelectedTasks(newSelected);
  };

  const handleCreateTasks = async () => {
    if (selectedTasks.size === 0) {
      setError('Please select at least one task to create');
      return;
    }

    try {
      setCreating(true);
      setError(null);

      const selectedSuggestions = suggestions.filter((_, index) => selectedTasks.has(index));
      
      // Call the parent callback with selected tasks
      if (onTasksCreated) {
        await onTasksCreated(selectedSuggestions);
      }
    } catch (err) {
      console.error('Error creating tasks:', err);
      setError('Failed to create tasks');
    } finally {
      setCreating(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={(e) => { if (e.target === e.currentTarget) onCancel(); }}
      onKeyDown={(e) => { if (e.key === 'Escape') onCancel(); }}
      tabIndex={-1}
    >
      <div className="bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <LightBulbIcon className="h-6 w-6 text-yellow-400" />
              <h2 className="text-xl font-semibold text-white">Break Down Your Project</h2>
            </div>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-white"
            >
              <XIcon className="h-6 w-6" />
            </button>
          </div>
          <p className="text-gray-300 mt-2">
            Let's help you get started with "<span className="font-medium text-white">{projectName}</span>"
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Template Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              What type of project is this?
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {templateTypes.map((type) => (
                <label
                  key={type.value}
                  className={`flex items-start p-3 rounded-lg border cursor-pointer transition-colors ${
                    templateType === type.value
                      ? 'border-yellow-500 bg-yellow-500 bg-opacity-10'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <input
                    type="radio"
                    name="templateType"
                    value={type.value}
                    checked={templateType === type.value}
                    onChange={(e) => setTemplateType(e.target.value)}
                    className="mt-1 text-yellow-500 bg-gray-700 border-gray-600 focus:ring-yellow-500"
                  />
                  <div className="ml-3">
                    <div className="text-sm font-medium text-white">{type.label}</div>
                    <div className="text-xs text-gray-400">{type.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          {suggestions.length === 0 && (
            <div className="mb-6">
              <button
                onClick={fetchSuggestions}
                disabled={loading}
                className="w-full bg-gradient-to-r from-yellow-500 to-yellow-600 text-black px-4 py-3 rounded-lg font-medium hover:from-yellow-600 hover:to-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                    <span>Generating suggestions...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <LightBulbIcon className="h-4 w-4" />
                    <span>Get Task Suggestions</span>
                  </div>
                )}
              </button>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded-lg">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <>
              <div className="mb-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-medium text-white">Suggested Tasks</h3>
                  <p className="text-sm text-gray-400">
                    {selectedTasks.size} of {suggestions.length} selected
                  </p>
                </div>
                <p className="text-sm text-gray-400 mb-4">
                  Select the tasks you'd like to add to your project:
                </p>
              </div>

              <div className="space-y-3 mb-6">
                {suggestions.map((task, index) => (
                  <label
                    key={index}
                    className={`flex items-start p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedTasks.has(index)
                        ? 'border-yellow-500 bg-yellow-500 bg-opacity-10'
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTasks.has(index)}
                      onChange={() => handleTaskToggle(index)}
                      className="mt-1 text-yellow-500 bg-gray-700 border-gray-600 rounded focus:ring-yellow-500"
                    />
                    <div className="ml-3 flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm">{getPriorityIcon(task.priority)}</span>
                        <span className="font-medium text-white">{task.name}</span>
                        <span className={`text-xs font-medium ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                      </div>
                      {task.estimated_duration && (
                        <p className="text-xs text-gray-400">
                          Estimated time: {task.estimated_duration} minutes
                        </p>
                      )}
                    </div>
                  </label>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        {suggestions.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-700 bg-gray-900">
            <div className="flex items-center justify-between">
              <button
                onClick={onCancel}
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <div className="flex space-x-3">
                <button
                  onClick={fetchSuggestions}
                  disabled={loading}
                  className="px-4 py-2 text-yellow-400 hover:text-yellow-300 transition-colors disabled:opacity-50"
                >
                  Regenerate
                </button>
                <button
                  onClick={handleCreateTasks}
                  disabled={creating || selectedTasks.size === 0}
                  className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-black px-6 py-2 rounded-lg font-medium hover:from-yellow-600 hover:to-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creating ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                      <span>Creating...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <PlusIcon className="h-4 w-4" />
                      <span>Add {selectedTasks.size} Tasks</span>
                    </div>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectDecompositionHelper;