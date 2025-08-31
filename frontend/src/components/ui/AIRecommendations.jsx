import React, { useState } from 'react';
import { 
  Lightbulb, 
  CheckCircle, 
  Clock, 
  Target, 
  TrendingUp,
  AlertTriangle,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import AIBadge from './AIBadge';

/**
 * AIRecommendations Component - Displays AI-generated recommendations
 * Shows actionable suggestions with priority levels and confidence scores
 */
const AIRecommendations = ({ 
  recommendations = [], 
  title = "AI Recommendations",
  showPriority = true,
  showConfidence = true,
  onRecommendationClick = null,
  maxVisible = 5,
  className = ''
}) => {
  const [showAll, setShowAll] = useState(false);

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className={`bg-gray-900/50 border border-gray-700 rounded-lg p-4 ${className}`}>
        <div className="flex items-center space-x-2 text-gray-400">
          <Lightbulb className="h-5 w-5" />
          <span className="text-sm">No recommendations available</span>
        </div>
      </div>
    );
  }

  // Get icon for recommendation type
  const getRecommendationIcon = (type, priority) => {
    const iconClass = "h-4 w-4";
    
    switch (type?.toLowerCase()) {
      case 'urgent':
      case 'critical':
        return <AlertTriangle className={`${iconClass} text-red-400`} />;
      case 'optimization':
      case 'improvement':
        return <TrendingUp className={`${iconClass} text-green-400`} />;
      case 'focus':
      case 'priority':
        return <Target className={`${iconClass} text-blue-400`} />;
      case 'time':
      case 'scheduling':
        return <Clock className={`${iconClass} text-orange-400`} />;
      default:
        // Use priority-based coloring if no specific type
        if (priority >= 0.8) return <AlertTriangle className={`${iconClass} text-red-400`} />;
        if (priority >= 0.6) return <Target className={`${iconClass} text-yellow-400`} />;
        return <Lightbulb className={`${iconClass} text-blue-400`} />;
    }
  };

  // Get priority styling
  const getPriorityStyle = (priority) => {
    if (priority >= 0.8) return { bg: 'bg-red-500/20', border: 'border-red-500/30', text: 'text-red-400' };
    if (priority >= 0.6) return { bg: 'bg-yellow-500/20', border: 'border-yellow-500/30', text: 'text-yellow-400' };
    if (priority >= 0.4) return { bg: 'bg-blue-500/20', border: 'border-blue-500/30', text: 'text-blue-400' };
    return { bg: 'bg-gray-500/20', border: 'border-gray-500/30', text: 'text-gray-400' };
  };

  const visibleRecommendations = showAll ? recommendations : recommendations.slice(0, maxVisible);
  const hasMore = recommendations.length > maxVisible;

  return (
    <div className={`bg-gray-900/50 border border-gray-700 rounded-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-yellow-400" />
          <h3 className="text-sm font-medium text-white">{title}</h3>
          <span className="text-xs text-gray-400">({recommendations.length})</span>
        </div>
        {hasMore && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="text-xs text-yellow-400 hover:text-yellow-300 transition-colors"
          >
            {showAll ? 'Show Less' : `Show All (${recommendations.length})`}
          </button>
        )}
      </div>

      {/* Recommendations List */}
      <div className="divide-y divide-gray-700">
        {visibleRecommendations.map((rec, index) => {
          const priority = rec.priority || rec.priority_score || 0.5;
          const confidence = rec.confidence || rec.confidence_score || 0.5;
          const priorityStyle = getPriorityStyle(priority);

          return (
            <div
              key={index}
              className={`p-4 transition-colors ${
                onRecommendationClick ? 'hover:bg-gray-800/50 cursor-pointer' : ''
              }`}
              onClick={() => onRecommendationClick && onRecommendationClick(rec, index)}
            >
              <div className="flex items-start space-x-3">
                {/* Icon */}
                <div className="flex-shrink-0 mt-0.5">
                  {getRecommendationIcon(rec.type, priority)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Title */}
                  {rec.title && (
                    <h4 className="text-sm font-medium text-white mb-1">
                      {rec.title}
                    </h4>
                  )}

                  {/* Description */}
                  <p className="text-sm text-gray-300 leading-relaxed">
                    {rec.description || rec.text || rec.recommendation}
                  </p>

                  {/* Action */}
                  {rec.action && (
                    <div className="mt-2 text-xs text-yellow-400 font-medium">
                      → {rec.action}
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="flex items-center justify-between mt-3">
                    <div className="flex items-center space-x-2">
                      {/* Priority Badge */}
                      {showPriority && (
                        <span className={`
                          inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                          ${priorityStyle.bg} ${priorityStyle.border} ${priorityStyle.text} border
                        `}>
                          Priority: {Math.round(priority * 100)}%
                        </span>
                      )}

                      {/* Type Badge */}
                      {rec.type && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-700 text-gray-300">
                          {rec.type}
                        </span>
                      )}
                    </div>

                    {/* Confidence & Action */}
                    <div className="flex items-center space-x-2">
                      {showConfidence && (
                        <AIBadge 
                          confidence={confidence} 
                          variant="confidence" 
                          size="xs"
                        />
                      )}
                      {onRecommendationClick && (
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      {hasMore && !showAll && (
        <div className="p-3 bg-gray-800/30 text-center">
          <button
            onClick={() => setShowAll(true)}
            className="text-xs text-yellow-400 hover:text-yellow-300 transition-colors"
          >
            View {recommendations.length - maxVisible} more recommendations
          </button>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;