import React, { useState } from 'react';
import { Brain, Zap, Target, HelpCircle, X } from 'lucide-react';

const AIDecisionHelper = ({ onNavigate, onClose, showInitially = false }) => {
  const [isVisible, setIsVisible] = useState(showInitially);

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-6 right-6 w-12 h-12 bg-gradient-to-br from-purple-600 to-yellow-400 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-all duration-200 z-50"
        title="Need help choosing an AI tool?"
      >
        <HelpCircle className="h-6 w-6 text-white" />
      </button>
    );
  }

  const aiOptions = [
    {
      key: 'ai-insights',
      name: 'My AI Insights',
      icon: Brain,
      color: 'purple',
      description: 'Browse what AI has learned about you',
      examples: [
        'See why AI prioritized certain tasks',
        'Review confidence scores and reasoning',
        'Browse historical analysis patterns'
      ],
      whenToUse: 'When you want to understand AI\'s observations about your productivity'
    },
    {
      key: 'ai-actions', 
      name: 'AI Quick Actions',
      icon: Zap,
      color: 'yellow',
      description: 'Fast AI assistance and overview',
      examples: [
        'Quick goal setup and analysis',
        'Check your AI usage quota',
        'Navigate to specialized tools'
      ],
      whenToUse: 'When you need quick AI help or want to see your AI overview'
    },
    {
      key: 'goal-planner',
      name: 'Goal Planner', 
      icon: Target,
      color: 'green',
      description: 'Strategic planning with AI coaching',
      examples: [
        'Break down big goals into actionable steps',
        'Get weekly strategic reviews',
        'Overcome obstacles and get unstuck'
      ],
      whenToUse: 'When you want to plan new goals or get strategic guidance'
    }
  ];

  const colorClasses = {
    purple: {
      bg: 'from-purple-900/50 to-purple-800/30',
      border: 'border-purple-500/30 hover:border-purple-400/50',
      button: 'bg-purple-600 hover:bg-purple-700',
      text: 'text-purple-300'
    },
    yellow: {
      bg: 'from-yellow-900/50 to-yellow-800/30', 
      border: 'border-yellow-500/30 hover:border-yellow-400/50',
      button: 'bg-yellow-600 hover:bg-yellow-700',
      text: 'text-yellow-300'
    },
    green: {
      bg: 'from-green-900/50 to-green-800/30',
      border: 'border-green-500/30 hover:border-green-400/50', 
      button: 'bg-green-600 hover:bg-green-700',
      text: 'text-green-300'
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        
        {/* Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-600 to-yellow-400 flex items-center justify-center">
                <HelpCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Choose Your AI Tool</h2>
                <p className="text-gray-400 text-sm">What would you like to do?</p>
              </div>
            </div>
            <button
              onClick={() => {
                setIsVisible(false);
                onClose && onClose();
              }}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* AI Options */}
        <div className="p-6 space-y-6">
          {aiOptions.map((option) => {
            const colors = colorClasses[option.color];
            const IconComponent = option.icon;
            
            return (
              <div 
                key={option.key}
                className={`bg-gradient-to-br ${colors.bg} border ${colors.border} rounded-xl p-6 cursor-pointer transition-all duration-200 hover:scale-[1.02]`}
                onClick={() => {
                  setIsVisible(false);
                  onNavigate(option.key);
                }}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-lg ${colors.button} flex items-center justify-center`}>
                      <IconComponent className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white">{option.name}</h3>
                      <p className={`${colors.text} text-sm`}>{option.description}</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Perfect for:</h4>
                    <p className="text-gray-400 text-sm">{option.whenToUse}</p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Examples:</h4>
                    <ul className="space-y-1">
                      {option.examples.map((example, index) => (
                        <li key={index} className="text-gray-400 text-sm flex items-start">
                          <span className={`${colors.text} mr-2`}>•</span>
                          {example}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="mt-6 pt-4 border-t border-gray-700/50">
                  <button
                    className={`w-full py-2 px-4 rounded-lg ${colors.button} text-white font-medium transition-colors flex items-center justify-center gap-2`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsVisible(false);
                      onNavigate(option.key);
                    }}
                  >
                    <IconComponent className="h-4 w-4" />
                    Go to {option.name}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Footer */}
        <div className="p-6 border-t border-gray-700 bg-gray-800/50">
          <div className="text-center">
            <p className="text-gray-400 text-sm">
              💡 <strong>Pro tip:</strong> You can access any AI tool directly from the sidebar navigation
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIDecisionHelper;