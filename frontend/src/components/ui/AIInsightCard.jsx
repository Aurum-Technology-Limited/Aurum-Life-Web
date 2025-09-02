import React from 'react';
import { 
  Brain, 
  Target, 
  TrendingUp, 
  Lightbulb, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Zap, 
  MessageSquare,
  Pin,
  PinOff,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react';
import ConfidenceIndicator from './ConfidenceIndicator';

const getInsightTypeIcon = (type) => {
  const icons = {
    priority_reasoning: Target,
    alignment_analysis: TrendingUp,
    pattern_recognition: Brain,
    recommendation: Lightbulb,
    goal_coherence: CheckCircle,
    obstacle_identification: AlertTriangle,
    time_allocation: Clock,
    progress_prediction: Zap
  };
  return icons[type] || MessageSquare;
};

const getInsightPriority = (insight) => {
  if (insight.confidence_score >= 0.9 && insight.impact_score >= 0.8) return 'critical';
  if (insight.confidence_score >= 0.8 || insight.impact_score >= 0.7) return 'high';
  if (insight.confidence_score >= 0.6 || insight.impact_score >= 0.5) return 'medium';
  return 'low';
};

const getPriorityColor = (priority) => {
  const colors = {
    critical: 'border-red-500 bg-red-500/10',
    high: 'border-orange-500 bg-orange-500/10',
    medium: 'border-yellow-500 bg-yellow-500/10',
    low: 'border-gray-500 bg-gray-500/10'
  };
  return colors[priority] || colors.low;
};

const getConfidenceColor = (score) => {
  if (score >= 0.8) return 'text-green-400';
  if (score >= 0.6) return 'text-yellow-400';
  return 'text-orange-400';
};

const AIInsightCard = ({ 
  insight, 
  onClick, 
  onPin, 
  onFeedback, 
  showActions = true,
  showMetrics = true,
  compact = false 
}) => {
  const IconComponent = getInsightTypeIcon(insight.insight_type);
  const priority = getInsightPriority(insight);
  
  return (
    <div
      className={`border rounded-lg p-6 transition-all hover:shadow-lg cursor-pointer ${getPriorityColor(priority)} ${
        compact ? 'p-4' : ''
      }`}
      onClick={() => onClick && onClick(insight)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600 rounded-lg">
            <IconComponent className={`${compact ? 'h-4 w-4' : 'h-5 w-5'} text-white`} />
          </div>
          <div>
            <h3 className={`font-semibold text-white ${compact ? 'text-sm' : ''}`}>
              {insight.title}
            </h3>
            <p className={`text-gray-400 capitalize ${compact ? 'text-xs' : 'text-sm'}`}>
              {insight.entity_type} • {insight.insight_type?.replace('_', ' ')}
            </p>
          </div>
        </div>

        {showActions && onPin && (
          <div className="flex items-center gap-2">
            {insight.is_pinned && (
              <Pin className="h-4 w-4 text-yellow-400" />
            )}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPin(insight.id, !insight.is_pinned);
              }}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
            >
              {insight.is_pinned ? (
                <PinOff className="h-4 w-4 text-gray-400" />
              ) : (
                <Pin className="h-4 w-4 text-gray-400" />
              )}
            </button>
          </div>
        )}
      </div>

      <p className={`text-gray-300 mb-4 ${compact ? 'text-sm' : ''}`}>
        {compact && insight.summary.length > 120 
          ? insight.summary.substring(0, 120) + '...' 
          : insight.summary
        }
      </p>

      {showMetrics && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={compact ? 'text-xs' : 'text-sm'}>
              <span className="text-gray-400">Confidence: </span>
              <span className={getConfidenceColor(insight.confidence_score)}>
                {(insight.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
            {insight.impact_score && (
              <div className={compact ? 'text-xs' : 'text-sm'}>
                <span className="text-gray-400">Impact: </span>
                <span className="text-blue-400">
                  {(insight.impact_score * 100).toFixed(0)}%
                </span>
              </div>
            )}
            {!compact && (
              <ConfidenceIndicator 
                confidence={insight.confidence_score} 
                size="sm" 
                showPercentage={false}
              />
            )}
          </div>

          {showActions && onFeedback && (
            <div className="flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onFeedback(insight.id, 'accepted');
                }}
                className="p-1 hover:bg-green-600/20 rounded transition-colors"
                title="Helpful"
              >
                <ThumbsUp className="h-4 w-4 text-green-400" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onFeedback(insight.id, 'rejected');
                }}
                className="p-1 hover:bg-red-600/20 rounded transition-colors"
                title="Not helpful"
              >
                <ThumbsDown className="h-4 w-4 text-red-400" />
              </button>
            </div>
          )}
        </div>
      )}

      {insight.tags && insight.tags.length > 0 && !compact && (
        <div className="mt-4 flex flex-wrap gap-2">
          {insight.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-700 text-xs text-gray-300 rounded"
            >
              {tag}
            </span>
          ))}
          {insight.tags.length > 3 && (
            <span className="px-2 py-1 bg-gray-700 text-xs text-gray-400 rounded">
              +{insight.tags.length - 3} more
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default AIInsightCard;