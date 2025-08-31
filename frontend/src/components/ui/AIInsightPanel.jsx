import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  Brain, 
  Lightbulb, 
  Target, 
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react';
import AIBadge from './AIBadge';
import ConfidenceIndicator from './ConfidenceIndicator';
import ReasoningPath from './ReasoningPath';

/**
 * AIInsightPanel Component - Expandable panel showing detailed AI insights
 * Displays reasoning, recommendations, and confidence scores
 */
const AIInsightPanel = ({ 
  insight = {}, 
  isExpanded = false, 
  onToggle = null,
  onClose = null,
  showCloseButton = false,
  className = ''
}) => {
  const [internalExpanded, setInternalExpanded] = useState(isExpanded);
  
  const expanded = onToggle ? isExpanded : internalExpanded;
  const toggleExpanded = onToggle || (() => setInternalExpanded(!internalExpanded));

  // Extract insight data with fallbacks
  const {
    title = 'AI Insight',
    summary = 'No summary available',
    reasoning = [],
    recommendations = [],
    confidence_score = 0,
    insight_type = 'general',
    priority_score = 0,
    created_at,
    metadata = {}
  } = insight;

  // Get icon for insight type
  const getInsightIcon = (type) => {
    const iconClass = "h-5 w-5";
    switch (type?.toLowerCase()) {
      case 'priority_reasoning':
        return <Target className={`${iconClass} text-blue-400`} />;
      case 'alignment_analysis':
        return <TrendingUp className={`${iconClass} text-green-400`} />;
      case 'pattern_recognition':
        return <Brain className={`${iconClass} text-purple-400`} />;
      case 'recommendation':
        return <Lightbulb className={`${iconClass} text-yellow-400`} />;
      case 'time_allocation':
        return <Clock className={`${iconClass} text-orange-400`} />;
      case 'obstacle_identification':
        return <AlertTriangle className={`${iconClass} text-red-400`} />;
      default:
        return <Brain className={`${iconClass} text-gray-400`} />;
    }
  };

  return (
    <div className={`bg-gray-900/50 border border-gray-700 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div 
        className={`flex items-center justify-between p-4 ${onToggle || !onToggle ? 'cursor-pointer hover:bg-gray-800/50' : ''} transition-colors`}
        onClick={toggleExpanded}
      >
        <div className="flex items-center space-x-3">
          {getInsightIcon(insight_type)}
          <div>
            <h3 className="text-sm font-medium text-white">{title}</h3>
            <p className="text-xs text-gray-400 mt-1">{summary}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <AIBadge 
            confidence={confidence_score} 
            variant="confidence" 
            size="xs"
          />
          {showCloseButton && onClose && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClose();
              }}
              className="p-1 text-gray-400 hover:text-white transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          {(onToggle || !onToggle) && (
            <button className="text-gray-400 hover:text-white transition-colors">
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="border-t border-gray-700 p-4 space-y-4">
          {/* Confidence Indicator */}
          <div>
            <h4 className="text-xs font-medium text-gray-400 mb-2">CONFIDENCE LEVEL</h4>
            <ConfidenceIndicator 
              confidence={confidence_score} 
              showPercentage={true}
              size="md"
            />
          </div>

          {/* Reasoning Path */}
          {reasoning && reasoning.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-400 mb-2">REASONING PATH</h4>
              <ReasoningPath 
                reasoning={reasoning} 
                orientation="vertical"
                showIcons={true}
              />
            </div>
          )}

          {/* Recommendations */}
          {recommendations && recommendations.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-400 mb-2">RECOMMENDATIONS</h4>
              <div className="space-y-2">
                {recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-2 bg-gray-800/30 rounded p-3">
                    <CheckCircle className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                    <div className="text-sm text-gray-300">
                      {typeof rec === 'string' ? rec : rec.text || rec.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Priority Score */}
          {priority_score > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-400 mb-2">PRIORITY SCORE</h4>
              <div className="flex items-center space-x-2">
                <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-2 bg-gradient-to-r from-yellow-500 to-orange-500 transition-all duration-500"
                    style={{ width: `${Math.min(priority_score * 10, 100)}%` }}
                  />
                </div>
                <span className="text-sm text-yellow-400 font-medium">
                  {priority_score.toFixed(1)}
                </span>
              </div>
            </div>
          )}

          {/* Metadata */}
          {created_at && (
            <div className="text-xs text-gray-500 pt-2 border-t border-gray-800">
              Generated {new Date(created_at).toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIInsightPanel;