import React, { useState, useEffect } from 'react';
import { Sun, ArrowRight, Target, CheckCircle, TrendingUp, X } from 'lucide-react';
import { api } from '../services/api';

const MorningPlanningPrompt = ({ onClose, onComplete }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get AI-curated task recommendations
      const response = await api.get('/api/ai/task-why-statements');
      if (response.data && response.data.why_statements) {
        setRecommendations(response.data.why_statements.slice(0, 5)); // Top 5 recommendations
      }
    } catch (err) {
      console.error('Failed to load morning recommendations:', err);
      setError('Unable to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleTaskSelect = (taskId) => {
    setSelectedTasks(prev => 
      prev.includes(taskId) 
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    );
  };

  const handlePlanDay = () => {
    // For MVP, we'll just track the completion
    console.log('🌅 Morning planning completed with tasks:', selectedTasks);
    onComplete(selectedTasks);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-gray-900 rounded-xl p-6 max-w-md w-full border border-gray-800">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400 mx-auto mb-4"></div>
            <p className="text-gray-400">Loading your morning plan...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl max-w-2xl w-full border border-gray-800">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
              <Sun className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Good Morning!</h2>
              <p className="text-gray-400 text-sm">Let's plan your day for maximum impact</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {error ? (
            <div className="text-center py-8">
              <div className="text-red-400 text-4xl mb-4">⚠️</div>
              <p className="text-red-400 mb-4">{error}</p>
              <button
                onClick={loadRecommendations}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-white mb-2">
                  🎯 Focus on These High-Impact Tasks Today
                </h3>
                <p className="text-gray-400 text-sm">
                  AI-curated recommendations based on your goals and priorities
                </p>
              </div>

              <div className="space-y-3 mb-6">
                {recommendations.map((item, index) => (
                  <div
                    key={item.task_id}
                    onClick={() => handleTaskSelect(item.task_id)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                      selectedTasks.includes(item.task_id)
                        ? 'border-yellow-400 bg-yellow-400/10'
                        : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                        selectedTasks.includes(item.task_id)
                          ? 'border-yellow-400 bg-yellow-400'
                          : 'border-gray-600'
                      }`}>
                        {selectedTasks.includes(item.task_id) && (
                          <CheckCircle className="w-4 h-4 text-black" />
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-yellow-400 font-bold text-sm">#{index + 1}</span>
                          <h4 className="text-white font-medium">{item.task_name}</h4>
                        </div>
                        
                        <p className="text-gray-400 text-sm mb-2 leading-relaxed">
                          {item.why_statement}
                        </p>
                        
                        {item.pillar_connection && (
                          <div className="flex items-center space-x-2 text-xs">
                            <Target className="w-3 h-3 text-blue-400" />
                            <span className="text-blue-400">{item.pillar_connection}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {recommendations.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-gray-500 text-4xl mb-4">📋</div>
                  <p className="text-gray-400 mb-4">No specific recommendations available today</p>
                  <p className="text-gray-500 text-sm">
                    Create some tasks and projects to get AI-powered guidance!
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                <div className="text-sm text-gray-400">
                  {selectedTasks.length > 0 && (
                    <span>✨ {selectedTasks.length} task{selectedTasks.length !== 1 ? 's' : ''} selected for today</span>
                  )}
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={onClose}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    Skip for Now
                  </button>
                  <button
                    onClick={handlePlanDay}
                    className="flex items-center space-x-2 px-6 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded-lg transition-colors"
                  >
                    <span>Plan My Day</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default MorningPlanningPrompt;