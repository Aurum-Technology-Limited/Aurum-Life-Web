import React from 'react';
import { ChevronRight, Brain, Target } from 'lucide-react';

const CrossNavigationWidget = ({ 
  currentScreen, 
  onNavigate, 
  relatedInsights = 0, 
  recentCoachActions = 0 
}) => {
  // Always show cross-navigation widgets for better user experience
  if (currentScreen === 'goal-planner' || currentScreen === 'ai-coach') {
    return (
      <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <Brain className="h-4 w-4 text-white" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-purple-300">My AI Insights</h4>
              <p className="text-xs text-purple-400">
                {relatedInsights > 0 
                  ? `View ${relatedInsights} insights from previous AI analysis`
                  : 'Browse what AI has learned about your productivity patterns'
                }
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate && onNavigate('ai-insights')}
            className="flex items-center space-x-1 px-4 py-2 bg-purple-600/20 hover:bg-purple-600/40 rounded-lg transition-colors text-purple-300 text-sm font-medium"
          >
            <span>View Insights</span>
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  }

  if (currentScreen === 'ai-insights' || currentScreen === 'ai-intelligence') {
    return (
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-yellow-600 flex items-center justify-center">
              <Target className="h-4 w-4 text-white" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-yellow-300">Goal Planner</h4>
              <p className="text-xs text-yellow-400">
                {recentCoachActions > 0
                  ? `${recentCoachActions} coaching sessions used this month`
                  : 'Get AI coaching for strategic planning and goal achievement'
                }
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate && onNavigate('goal-planner')}
            className="flex items-center space-x-1 px-4 py-2 bg-yellow-600/20 hover:bg-yellow-600/40 rounded-lg transition-colors text-yellow-300 text-sm font-medium"
          >
            <span>Plan Goals</span>
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  }

  if (currentScreen === 'ai-actions' || currentScreen === 'ai-command') {
    return (
      <div className="bg-gradient-to-r from-purple-900/20 to-yellow-900/20 border border-gray-500/30 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => onNavigate && onNavigate('ai-insights')}
            className="flex items-center space-x-2 p-3 bg-purple-600/20 hover:bg-purple-600/30 rounded-lg transition-colors"
          >
            <Brain className="h-4 w-4 text-purple-300" />
            <div className="text-left">
              <div className="text-sm font-medium text-purple-300">My AI Insights</div>
              <div className="text-xs text-purple-400">Browse past analysis</div>
            </div>
          </button>
          
          <button
            onClick={() => onNavigate && onNavigate('goal-planner')}
            className="flex items-center space-x-2 p-3 bg-yellow-600/20 hover:bg-yellow-600/30 rounded-lg transition-colors"
          >
            <Target className="h-4 w-4 text-yellow-300" />
            <div className="text-left">
              <div className="text-sm font-medium text-yellow-300">Goal Planner</div>
              <div className="text-xs text-yellow-400">Strategic coaching</div>
            </div>
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default CrossNavigationWidget;