import React from 'react';
import { ChevronRight, Brain, Target } from 'lucide-react';

const CrossNavigationWidget = ({ 
  currentScreen, 
  onNavigate, 
  relatedInsights = 0, 
  recentCoachActions = 0 
}) => {
  if (currentScreen === 'ai-coach') {
    return (
      <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <Brain className="h-4 w-4 text-white" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-purple-300">AI Intelligence Center</h4>
              <p className="text-xs text-purple-400">
                {relatedInsights > 0 
                  ? `View ${relatedInsights} related insights from previous analysis`
                  : 'Browse your historical AI insights and patterns'
                }
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('ai-intelligence')}
            className="flex items-center space-x-1 px-3 py-1 bg-purple-600/20 hover:bg-purple-600/30 rounded-lg transition-colors text-purple-300 text-sm"
          >
            <span>View Insights</span>
            <ChevronRight className="h-3 w-3" />
          </button>
        </div>
      </div>
    );
  }

  if (currentScreen === 'ai-intelligence') {
    return (
      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-yellow-600 flex items-center justify-center">
              <Target className="h-4 w-4 text-white" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-yellow-300">AI Coach</h4>
              <p className="text-xs text-yellow-400">
                {recentCoachActions > 0
                  ? `${recentCoachActions} coaching actions used this month`
                  : 'Need help with goal planning or strategic analysis?'
                }
              </p>
            </div>
          </div>
          <button
            onClick={() => onNavigate('ai-coach')}
            className="flex items-center space-x-1 px-3 py-1 bg-yellow-600/20 hover:bg-yellow-600/30 rounded-lg transition-colors text-yellow-300 text-sm"
          >
            <span>Get Coaching</span>
            <ChevronRight className="h-3 w-3" />
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default CrossNavigationWidget;