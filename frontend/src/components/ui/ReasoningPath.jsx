import React from 'react';
import { ChevronRight, Target, Brain, Lightbulb, CheckCircle } from 'lucide-react';

/**
 * ReasoningPath Component - Visualizes AI reasoning hierarchy and decision paths
 * Shows the step-by-step reasoning process from goals to specific recommendations
 */
const ReasoningPath = ({ 
  reasoning = [], 
  showIcons = true, 
  orientation = 'horizontal',
  className = ''
}) => {
  if (!reasoning || reasoning.length === 0) {
    return (
      <div className={`text-gray-400 text-sm italic ${className}`}>
        No reasoning path available
      </div>
    );
  }

  // Icon mapping for different reasoning types
  const getReasoningIcon = (type, index) => {
    const iconClass = "h-4 w-4";
    
    switch (type?.toLowerCase()) {
      case 'goal':
      case 'objective':
        return <Target className={`${iconClass} text-blue-400`} />;
      case 'analysis':
      case 'evaluation':
        return <Brain className={`${iconClass} text-purple-400`} />;
      case 'insight':
      case 'observation':
        return <Lightbulb className={`${iconClass} text-yellow-400`} />;
      case 'conclusion':
      case 'recommendation':
        return <CheckCircle className={`${iconClass} text-green-400`} />;
      default:
        return (
          <div className={`${iconClass} rounded-full bg-gray-600 text-gray-300 flex items-center justify-center text-xs font-bold`}>
            {index + 1}
          </div>
        );
    }
  };

  // Horizontal layout
  if (orientation === 'horizontal') {
    return (
      <div className={`flex items-center space-x-2 overflow-x-auto ${className}`}>
        {reasoning.map((step, index) => (
          <React.Fragment key={index}>
            <div className="flex items-center space-x-2 bg-gray-800/50 rounded-lg px-3 py-2 min-w-0 flex-shrink-0">
              {showIcons && getReasoningIcon(step.type, index)}
              <div className="min-w-0">
                {step.title && (
                  <div className="text-sm font-medium text-white truncate">
                    {step.title}
                  </div>
                )}
                <div className="text-xs text-gray-400 truncate">
                  {step.description || step.text || step.content}
                </div>
              </div>
            </div>
            {index < reasoning.length - 1 && (
              <ChevronRight className="h-4 w-4 text-gray-500 flex-shrink-0" />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  // Vertical layout
  return (
    <div className={`space-y-3 ${className}`}>
      {reasoning.map((step, index) => (
        <div key={index} className="flex items-start space-x-3">
          <div className="flex flex-col items-center">
            {showIcons && getReasoningIcon(step.type, index)}
            {index < reasoning.length - 1 && (
              <div className="w-px h-8 bg-gray-600 mt-2" />
            )}
          </div>
          <div className="flex-1 bg-gray-800/50 rounded-lg p-3">
            {step.title && (
              <div className="text-sm font-medium text-white mb-1">
                {step.title}
              </div>
            )}
            <div className="text-sm text-gray-300">
              {step.description || step.text || step.content}
            </div>
            {step.confidence && (
              <div className="mt-2 text-xs text-gray-400">
                Confidence: {Math.round(step.confidence * 100)}%
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ReasoningPath;