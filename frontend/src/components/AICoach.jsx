import React, { useState, useEffect } from 'react';
import { Bot, Target, TrendingUp, AlertTriangle, Loader2, AlertCircle, Brain, ChevronRight, Clock, Zap } from 'lucide-react';
import { api } from '../services/api';

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
              placeholder="e.g., Learn Spanish, Launch my business, Get fit..."
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
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : 'Get Breakdown'}
            </button>
          </div>
        </form>
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

export default AICoach;