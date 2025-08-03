import React, { useState, useEffect } from 'react';
import { Bot, Target, TrendingUp, AlertTriangle, Loader2, AlertCircle, Brain, ChevronRight, Clock, Zap } from 'lucide-react';
import { api, aiCoachAPI } from '../services/api';

const FeatureCard = ({ icon: Icon, title, description, buttonText, onClick, disabled = false, isLoading = false }) => (
  <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group">
    <div className="flex items-center space-x-3 mb-4">
      <div className="w-12 h-12 rounded-lg bg-yellow-400 flex items-center justify-center group-hover:scale-110 transition-transform">
        <Icon size={24} style={{ color: '#0B0D14' }} />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
    </div>
    <p className="text-gray-400 mb-6 leading-relaxed">{description}</p>
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className="w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
    >
      {isLoading ? (
        <Loader2 size={18} className="animate-spin" />
      ) : (
        <>
          <span>{buttonText}</span>
          <ChevronRight size={16} />
        </>
      )}
    </button>
  </div>
);

const QuotaDisplay = ({ remaining, total }) => (
  <div className="flex items-center space-x-3 p-4 rounded-lg bg-gray-800/50 border border-gray-700">
    <div className="w-10 h-10 rounded-lg bg-yellow-400/20 flex items-center justify-center">
      <Zap size={20} className="text-yellow-400" />
    </div>
    <div className="flex-1">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-400">AI Interactions This Month</span>
        <span className="text-sm font-semibold text-white">{remaining}/{total}</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div 
          className="bg-yellow-400 h-2 rounded-full transition-all duration-500"
          style={{ width: `${(remaining / total) * 100}%` }}
        />
      </div>
    </div>
  </div>
);

const RateLimitWarning = ({ show }) => {
  if (!show) return null;
  
  return (
    <div className="p-3 rounded-lg bg-orange-900/20 border border-orange-500/30 flex items-center space-x-2 mb-4">
      <Clock size={16} className="text-orange-400" />
      <span className="text-orange-400 text-sm">Please wait a moment before making another request</span>
    </div>
  );
};

const GoalDecompositionModal = ({ isOpen, onClose, onSubmit, isLoading }) => {
  const [goalText, setGoalText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (goalText.trim()) {
      onSubmit(goalText.trim());
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md mx-4">
        <h3 className="text-xl font-semibold text-white mb-4">Goal Decomposition</h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Describe your goal:
            </label>
            <textarea
              value={goalText}
              onChange={(e) => setGoalText(e.target.value)}
              placeholder="e.g., Learn Spanish, Launch my business, Get fit, Plan a trip to Japan..."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 transition-colors resize-none"
              rows="3"
              disabled={isLoading}
            />
          </div>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!goalText.trim() || isLoading}
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : 'Generate Breakdown'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const InteractiveProjectEditor = ({ isOpen, onClose, aiResponse, onSave, isLoading }) => {
  const [projectData, setProjectData] = useState({
    title: '',
    description: '',
    area_id: null,
    priority: 'medium',
    status: 'Planning'
  });
  
  const [tasks, setTasks] = useState([]);
  const [availableAreas, setAvailableAreas] = useState([]);

  useEffect(() => {
    if (isOpen && aiResponse) {
      // Initialize form with AI suggestions
      const suggested = aiResponse.suggested_project || {};
      setProjectData({
        title: suggested.title || '',
        description: suggested.description || '',
        area_id: suggested.area_id || null,
        priority: suggested.priority || 'medium',
        status: suggested.status || 'Planning'
      });
      
      setTasks(aiResponse.suggested_tasks || []);
      setAvailableAreas(aiResponse.available_areas || []);
    }
  }, [isOpen, aiResponse]);

  const addNewTask = () => {
    setTasks([...tasks, { 
      title: '', 
      priority: 'medium', 
      estimated_duration: 30 
    }]);
  };

  const updateTask = (index, field, value) => {
    const updatedTasks = [...tasks];
    updatedTasks[index] = { ...updatedTasks[index], [field]: value };
    setTasks(updatedTasks);
  };

  const removeTask = (index) => {
    setTasks(tasks.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    // Filter out empty tasks
    const validTasks = tasks.filter(task => task.title && task.title.trim());
    onSave(projectData, validTasks);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-700 sticky top-0 bg-gray-900 z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
                <Target size={20} style={{ color: '#0B0D14' }} />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">Edit & Save Your Project</h3>
                <p className="text-sm text-gray-400">Review, edit, and save to add this project to your system</p>
              </div>
            </div>
            <button
              onClick={onClose}
              disabled={isLoading}
              className="text-gray-400 hover:text-white p-2 disabled:opacity-50"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Project Details */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white">Project Details</h4>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Project Title*</label>
              <input
                type="text"
                value={projectData.title}
                onChange={(e) => setProjectData({...projectData, title: e.target.value})}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors"
                placeholder="Enter project title..."
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea
                value={projectData.description}
                onChange={(e) => setProjectData({...projectData, description: e.target.value})}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors resize-none"
                rows="2"
                placeholder="Brief description of the project..."
                disabled={isLoading}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Life Area</label>
                <select
                  value={projectData.area_id || ''}
                  onChange={(e) => setProjectData({...projectData, area_id: e.target.value || null})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors"
                  disabled={isLoading}
                >
                  <option value="">Select an area...</option>
                  {availableAreas.map(area => (
                    <option key={area.id} value={area.id}>{area.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
                <select
                  value={projectData.priority}
                  onChange={(e) => setProjectData({...projectData, priority: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors"
                  disabled={isLoading}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
                <select
                  value={projectData.status}
                  onChange={(e) => setProjectData({...projectData, status: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors"
                  disabled={isLoading}
                >
                  <option value="Planning">Planning</option>
                  <option value="In Progress">In Progress</option>
                  <option value="On Hold">On Hold</option>
                </select>
              </div>
            </div>
          </div>

          {/* Tasks */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-white">Project Tasks</h4>
              <button
                onClick={addNewTask}
                disabled={isLoading}
                className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
              >
                <span>+</span>
                <span>Add Task</span>
              </button>
            </div>

            <div className="space-y-3">
              {tasks.map((task, index) => (
                <div key={index} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-start">
                    <div className="md:col-span-6">
                      <input
                        type="text"
                        value={task.title}
                        onChange={(e) => updateTask(index, 'title', e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors text-sm"
                        placeholder="Task title..."
                        disabled={isLoading}
                      />
                    </div>
                    
                    <div className="md:col-span-2">
                      <select
                        value={task.priority}
                        onChange={(e) => updateTask(index, 'priority', e.target.value)}
                        className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors text-sm"
                        disabled={isLoading}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>

                    <div className="md:col-span-3">
                      <div className="flex items-center space-x-2">
                        <input
                          type="number"
                          value={task.estimated_duration}
                          onChange={(e) => updateTask(index, 'estimated_duration', parseInt(e.target.value) || 30)}
                          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors text-sm"
                          min="5"
                          max="480"
                          disabled={isLoading}
                        />
                        <span className="text-xs text-gray-400 whitespace-nowrap">min</span>
                      </div>
                    </div>

                    <div className="md:col-span-1 flex justify-center">
                      <button
                        onClick={() => removeTask(index)}
                        disabled={isLoading}
                        className="p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <span className="text-sm">×</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {tasks.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <p>No tasks added yet. Click "Add Task" to create some!</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 bg-gray-900/50 sticky bottom-0">
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!projectData.title?.trim() || isLoading}
              className="flex-2 py-2 px-6 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <span>💾</span>
                  <span>Save Project & Tasks</span>
                </>
              )}
            </button>
          </div>
          
          {projectData.title && (
            <div className="mt-3 text-center">
              <p className="text-sm text-gray-400">
                This will create: <span className="text-yellow-400 font-medium">"{projectData.title}"</span> 
                {tasks.filter(t => t.title?.trim()).length > 0 && (
                  <span> with {tasks.filter(t => t.title?.trim()).length} task{tasks.filter(t => t.title?.trim()).length !== 1 ? 's' : ''}</span>
                )}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ObstacleAnalysisModal = ({ isOpen, onClose, onSubmit, projects, isLoading }) => {
  const [selectedProject, setSelectedProject] = useState('');
  const [problemDescription, setProblemDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedProject && problemDescription.trim()) {
      onSubmit(selectedProject, problemDescription.trim());
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md mx-4">
        <h3 className="text-xl font-semibold text-white mb-4">Obstacle Analysis</h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select Project:
            </label>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-yellow-400 transition-colors"
              disabled={isLoading}
            >
              <option value="">Choose a project...</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              What's the problem?
            </label>
            <textarea
              value={problemDescription}
              onChange={(e) => setProblemDescription(e.target.value)}
              placeholder="e.g., I'm stuck on the planning phase, Can't find motivation to continue..."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 transition-colors resize-none"
              rows="3"
              disabled={isLoading}
            />
          </div>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedProject || !problemDescription.trim() || isLoading}
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            >
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : 'Get Help'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const ResponseModal = ({ isOpen, onClose, response, title }) => {
  if (!isOpen || !response) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
            <Brain size={20} style={{ color: '#0B0D14' }} />
          </div>
          <h3 className="text-xl font-semibold text-white">{title}</h3>
        </div>
        
        <div className="space-y-4 mb-6">
          {response.suggested_project_title && (
            <div>
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">Suggested Project Title:</h4>
              <p className="text-white font-medium">{response.suggested_project_title}</p>
            </div>
          )}
          
          {response.suggested_tasks && response.suggested_tasks.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">Action Steps:</h4>
              <ul className="space-y-2">
                {response.suggested_tasks.map((task, index) => (
                  <li key={index} className="flex items-start space-x-3 p-3 bg-gray-800/50 rounded-lg">
                    <span className="text-yellow-400 font-semibold text-sm mt-0.5">{index + 1}.</span>
                    <div className="flex-1">
                      <p className="text-white">{task.name}</p>
                      {task.priority && (
                        <span className={`inline-block px-2 py-1 text-xs rounded mt-1 ${
                          task.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                          task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-green-500/20 text-green-400'
                        }`}>
                          {task.priority} priority
                        </span>
                      )}
                      {task.estimated_duration && (
                        <span className="inline-block ml-2 px-2 py-1 text-xs rounded mt-1 bg-blue-500/20 text-blue-400">
                          ~{task.estimated_duration}min
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {response.weekly_summary && (
            <div>
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">Weekly Review:</h4>
              <p className="text-gray-300 leading-relaxed">{response.weekly_summary}</p>
            </div>
          )}
          
          {response.suggestions && response.suggestions.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">Next Actions:</h4>
              <ul className="space-y-2">
                {response.suggestions.map((suggestion, index) => (
                  <li key={index} className="p-3 bg-gray-800/50 rounded-lg">
                    <p className="text-white">{suggestion}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <button
          onClick={onClose}
          className="w-full py-2 px-4 rounded-lg font-medium transition-all duration-200"
          style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
        >
          Close
        </button>
      </div>
    </div>
  );
};

const AICoach = () => {
  // State management for the MVP AI Coach
  const [quota, setQuota] = useState({ remaining: 10, total: 10 });
  const [rateLimited, setRateLimited] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Modal states
  const [goalModalOpen, setGoalModalOpen] = useState(false);
  const [obstacleModalOpen, setObstacleModalOpen] = useState(false);
  const [responseModalOpen, setResponseModalOpen] = useState(false);
  
  // Loading states for each feature
  const [goalLoading, setGoalLoading] = useState(false);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [obstacleLoading, setObstacleLoading] = useState(false);
  
  // Response data
  const [currentResponse, setCurrentResponse] = useState(null);
  const [responseTitle, setResponseTitle] = useState('');
  
  // Projects data for obstacle analysis
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    initializeCoach();
  }, []);

  const initializeCoach = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load user's AI interaction quota
      await loadQuota();
      
      // Load user's projects for obstacle analysis
      await loadProjects();
      
    } catch (err) {
      setError('Failed to initialize AI Coach');
      console.error('AI Coach initialization error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadQuota = async () => {
    try {
      const response = await aiCoachAPI.getQuota();
      setQuota(response.data);
    } catch (err) {
      console.error('Error loading quota:', err);
      // Use mock data if API fails
      setQuota({ remaining: 10, total: 10 });
    }
  };

  const loadProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data.filter(project => project.status !== 'Completed'));
    } catch (err) {
      console.error('Error loading projects:', err);
      setProjects([]);
    }
  };

  const checkRateLimit = async () => {
    // Simple client-side rate limiting
    const lastRequest = localStorage.getItem('aiCoachLastRequest');
    const now = Date.now();
    
    if (lastRequest && now - parseInt(lastRequest) < 20000) { // 20 seconds
      setRateLimited(true);
      setTimeout(() => setRateLimited(false), 20000 - (now - parseInt(lastRequest)));
      return false;
    }
    
    localStorage.setItem('aiCoachLastRequest', now.toString());
    return true;
  };

  // Feature 1: Goal Decomposition
  const handleGoalDecomposition = async (goalText) => {
    if (!await checkRateLimit()) return;
    if (quota.remaining <= 0) {
      setError('You have reached your monthly AI interaction limit.');
      return;
    }

    try {
      setGoalLoading(true);
      setError(null);
      
      const response = await aiCoachAPI.decomposeGoal(goalText);
      
      // Update quota after successful request
      await loadQuota();
      
      setCurrentResponse({
        suggested_project_title: goalText,
        suggested_tasks: response.data.suggested_tasks
      });
      setResponseTitle('Goal Breakdown');
      setGoalModalOpen(false);
      setResponseModalOpen(true);
      
    } catch (err) {
      if (err.response?.status === 429) {
        setError('Too many requests. Please wait a moment before trying again.');
      } else if (err.response?.status === 402) {
        setError('Monthly AI interaction limit reached.');
      } else {
        setError('Failed to decompose goal. Please try again.');
      }
      console.error('Goal decomposition error:', err);
    } finally {
      setGoalLoading(false);
    }
  };

  // Feature 2: Weekly Strategic Review
  const handleWeeklyReview = async () => {
    if (!await checkRateLimit()) return;
    if (quota.remaining <= 0) {
      setError('You have reached your monthly AI interaction limit.');
      return;
    }

    try {
      setReviewLoading(true);
      setError(null);
      
      const response = await aiCoachAPI.getWeeklyReview();
      
      // Update quota after successful request
      await loadQuota();
      
      setCurrentResponse({
        weekly_summary: response.data.weekly_summary
      });
      setResponseTitle('Weekly Strategic Review');
      setResponseModalOpen(true);
      
    } catch (err) {
      if (err.response?.status === 429) {
        setError('Too many requests. Please wait a moment before trying again.');
      } else if (err.response?.status === 402) {
        setError('Monthly AI interaction limit reached.');
      } else {
        setError('Failed to generate weekly review. Please try again.');
      }
      console.error('Weekly review error:', err);
    } finally {
      setReviewLoading(false);
    }
  };

  // Feature 3: Obstacle Analysis
  const handleObstacleAnalysis = async (projectId, problemDescription) => {
    if (!await checkRateLimit()) return;
    if (quota.remaining <= 0) {
      setError('You have reached your monthly AI interaction limit.');
      return;
    }

    try {
      setObstacleLoading(true);
      setError(null);
      
      const response = await aiCoachAPI.analyzeObstacle(projectId, problemDescription);
      
      // Update quota after successful request
      await loadQuota();
      
      setCurrentResponse({
        suggestions: response.data.suggestions
      });
      setResponseTitle(`Obstacle Analysis: ${response.data.project_name}`);
      setObstacleModalOpen(false);
      setResponseModalOpen(true);
      
    } catch (err) {
      if (err.response?.status === 429) {
        setError('Too many requests. Please wait a moment before trying again.');
      } else if (err.response?.status === 402) {
        setError('Monthly AI interaction limit reached.');
      } else if (err.response?.status === 404) {
        setError('Project not found. Please select a valid project.');
      } else {
        setError('Failed to analyze obstacle. Please try again.');
      }
      console.error('Obstacle analysis error:', err);
    } finally {
      setObstacleLoading(false);
    }
  };



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
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="w-16 h-16 rounded-2xl bg-yellow-400 flex items-center justify-center">
            <Brain size={32} style={{ color: '#0B0D14' }} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">AI Growth Coach</h1>
            <p className="text-gray-400">Strategic guidance for your personal OS</p>
          </div>
        </div>
      </div>

      {/* AI Interaction Quota */}
      <QuotaDisplay remaining={quota.remaining} total={quota.total} />
      
      {/* Rate Limit Warning */}
      <RateLimitWarning show={rateLimited} />

      {/* Error Display */}
      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            ✕
          </button>
        </div>
      )}

      {/* MVP Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Feature 1: Goal Decomposition */}
        <FeatureCard
          icon={Target}
          title="Goal Decomposition"
          description="Break down a large goal into a structured project with actionable tasks to get started."
          buttonText="Break Down Goal"
          onClick={() => setGoalModalOpen(true)}
          disabled={quota.remaining === 0 || rateLimited}
          isLoading={goalLoading}
        />

        {/* Feature 2: Weekly Strategic Review */}
        <FeatureCard
          icon={TrendingUp}
          title="Weekly Strategic Review"
          description="Get insights on how well your completed projects aligned with your stated priorities."
          buttonText="Generate Review"
          onClick={handleWeeklyReview}
          disabled={quota.remaining === 0 || rateLimited}
          isLoading={reviewLoading}
        />

        {/* Feature 3: Obstacle Analysis */}
        <FeatureCard
          icon={AlertTriangle}
          title="Obstacle Analysis"
          description="Get concrete suggestions for the next action when you're stuck on a specific project."
          buttonText="Get Unstuck"
          onClick={() => setObstacleModalOpen(true)}
          disabled={quota.remaining === 0 || rateLimited || projects.length === 0}
          isLoading={obstacleLoading}
        />
      </div>

      {/* Usage Guidelines */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h3 className="text-lg font-semibold text-white mb-4">How to Get the Most from Your AI Coach</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="p-4 bg-gray-800/50 rounded-lg">
            <h4 className="font-semibold text-yellow-400 mb-2">🎯 Goal Decomposition</h4>
            <p className="text-gray-300">Best for: New goals, unclear next steps, blank slate syndrome. Be specific about what you want to achieve.</p>
          </div>
          <div className="p-4 bg-gray-800/50 rounded-lg">
            <h4 className="font-semibold text-yellow-400 mb-2">📊 Weekly Review</h4>
            <p className="text-gray-300">Best used once per week to reflect on completed projects and alignment with your priorities.</p>
          </div>
          <div className="p-4 bg-gray-800/50 rounded-lg">
            <h4 className="font-semibold text-yellow-400 mb-2">🚧 Obstacle Analysis</h4>
            <p className="text-gray-300">Best for: When you're stuck, procrastinating, or unsure of the next action on an existing project.</p>
          </div>
        </div>
      </div>

      {/* Modals */}
      <GoalDecompositionModal
        isOpen={goalModalOpen}
        onClose={() => setGoalModalOpen(false)}
        onSubmit={handleGoalDecomposition}
        isLoading={goalLoading}
      />

      <ObstacleAnalysisModal
        isOpen={obstacleModalOpen}
        onClose={() => setObstacleModalOpen(false)}
        onSubmit={handleObstacleAnalysis}
        projects={projects}
        isLoading={obstacleLoading}
      />

      <ResponseModal
        isOpen={responseModalOpen}
        onClose={() => setResponseModalOpen(false)}
        response={currentResponse}
        title={responseTitle}
      />
    </div>
  );
};

export default AICoach;