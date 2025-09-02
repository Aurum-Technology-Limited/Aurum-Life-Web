import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Brain, 
  Lightbulb, 
  TrendingUp, 
  Filter, 
  Search, 
  Pin,
  PinOff,
  ThumbsUp,
  ThumbsDown,
  MoreHorizontal,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Target,
  Eye,
  MessageSquare
} from 'lucide-react';
import { hrmAPI, aiCoachAPI } from '../services/api';
import CrossNavigationWidget from './ui/CrossNavigationWidget';
import AIQuotaWidget from './ui/AIQuotaWidget';
import AIInsightCard from './ui/AIInsightCard';
import { useAnalytics } from '../hooks/useAnalytics';

const AIIntelligenceCenter = ({ onSectionChange }) => {
  // Analytics tracking
  const analytics = useAnalytics();
  
  // State management
  const [filters, setFilters] = useState({
    entity_type: '',
    insight_type: '',
    is_active: true,
    min_confidence: 0,
    tags: ''
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  const queryClient = useQueryClient();

  // Track page view when component mounts
  useEffect(() => {
    analytics.trackPageView('/ai-insights');
    analytics.trackAIInteraction('my_ai_insights', 'page_load', {
      filters_active: showFilters,
      search_active: !!searchTerm
    });
  }, [analytics]);

  // Fetch AI quota for cross-navigation
  const { data: quota } = useQuery({
    queryKey: ['ai-quota'],
    queryFn: async () => {
      try {
        const response = await aiCoachAPI.getQuota();
        return response.data;
      } catch (error) {
        console.error('Error loading quota:', error);
        return { remaining: 10, total: 10 };
      }
    },
    staleTime: 2 * 60 * 1000,
  });

  // Fetch insights with filters
  const { data: insightsData, isLoading, error } = useQuery({
    queryKey: ['hrm-insights', filters, searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          params.append(key, value.toString());
        }
      });
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      return await hrmAPI.getInsights(params);
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000 // Refresh every 5 minutes
  });

  // Fetch statistics for dashboard overview
  const { data: statistics } = useQuery({
    queryKey: ['hrm-statistics'],
    queryFn: () => hrmAPI.getStatistics(),
    staleTime: 5 * 60 * 1000
  });

  // Feedback mutation
  const feedbackMutation = useMutation({
    mutationFn: ({ insightId, feedback, details }) => 
      hrmAPI.provideFeedback(insightId, feedback, details),
    onSuccess: () => {
      queryClient.invalidateQueries(['hrm-insights']);
      queryClient.invalidateQueries(['hrm-statistics']);
    }
  });

  // Pin/unpin mutation
  const pinMutation = useMutation({
    mutationFn: ({ insightId, pinned }) => hrmAPI.pinInsight(insightId, pinned),
    onSuccess: () => {
      queryClient.invalidateQueries(['hrm-insights']);
    }
  });

  // Deactivate mutation
  const deactivateMutation = useMutation({
    mutationFn: (insightId) => hrmAPI.deactivateInsight(insightId),
    onSuccess: () => {
      queryClient.invalidateQueries(['hrm-insights']);
      setSelectedInsight(null);
    }
  });

  const insights = insightsData?.insights || [];

  // Helper functions (defined before useMemo hooks)
  const getInsightPriority = (insight) => {
    if (insight.confidence_score >= 0.9 && insight.impact_score >= 0.8) return 'critical';
    if (insight.confidence_score >= 0.8 || insight.impact_score >= 0.7) return 'high';
    if (insight.confidence_score >= 0.6 || insight.impact_score >= 0.5) return 'medium';
    return 'low';
  };

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

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-yellow-400';
    return 'text-orange-400';
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

  // Filter insights by search term
  const filteredInsights = useMemo(() => {
    if (!searchTerm) return insights;
    
    const term = searchTerm.toLowerCase();
    return insights.filter(insight => 
      insight.title.toLowerCase().includes(term) ||
      insight.summary.toLowerCase().includes(term) ||
      insight.tags?.some(tag => tag.toLowerCase().includes(term))
    );
  }, [insights, searchTerm]);

  // Group insights by priority
  const groupedInsights = useMemo(() => {
    const groups = {
      critical: [],
      high: [],
      medium: [],
      low: []
    };

    filteredInsights.forEach(insight => {
      const priority = getInsightPriority(insight);
      groups[priority].push(insight);
    });

    return groups;
  }, [filteredInsights]);

  const handleFeedback = (insightId, feedback) => {
    // Track feedback event
    analytics.trackInsightFeedback(insightId, feedback, selectedInsight?.insight_type);
    feedbackMutation.mutate({ insightId, feedback });
  };

  const handlePin = (insightId, pinned) => {
    // Track pin/unpin action
    analytics.trackAIInteraction('my_ai_insights', pinned ? 'pin_insight' : 'unpin_insight', {
      insight_id: insightId
    });
    pinMutation.mutate({ insightId, pinned });
  };

  const handleDeactivate = (insightId) => {
    if (window.confirm('Are you sure you want to deactivate this insight?')) {
      // Track deactivation
      analytics.trackAIInteraction('my_ai_insights', 'deactivate_insight', {
        insight_id: insightId
      });
      deactivateMutation.mutate(insightId);
    }
  };

  // Track filter changes
  const handleFiltersChange = useCallback((newFilters) => {
    analytics.trackAIInteraction('my_ai_insights', 'apply_filters', {
      filters_applied: Object.keys(newFilters).filter(key => newFilters[key] !== '' && newFilters[key] !== null),
      filter_count: Object.values(newFilters).filter(val => val !== '' && val !== null).length
    });
    setFilters(newFilters);
  }, [analytics]);

  // Track search
  const handleSearchChange = useCallback((term) => {
    if (term.length >= 3) {
      analytics.trackSearch(term, 'ai_insights', filteredInsights.length);
    }
    setSearchTerm(term);
  }, [analytics, filteredInsights.length]);

  // Track insight selection
  const handleInsightSelection = useCallback((insight) => {
    analytics.trackAIInteraction('my_ai_insights', 'view_insight_details', {
      insight_id: insight.id,
      insight_type: insight.insight_type,
      confidence_score: insight.confidence_score,
      is_pinned: insight.is_pinned
    });
    setSelectedInsight(insight);
  }, [analytics]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#0B0D14] text-white p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 text-center">
            <XCircle className="h-8 w-8 text-red-400 mx-auto mb-2" />
            <h2 className="text-lg font-semibold text-red-400">Failed to Load AI Insights</h2>
            <p className="text-red-300 mt-1">Please try refreshing the page</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0D14] text-white p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Cross-Navigation Widget */}
        <CrossNavigationWidget 
          currentScreen="ai-insights"
          onNavigate={(screen) => onSectionChange && onSectionChange(screen)}
          recentCoachActions={quota ? quota.total - quota.remaining : 0}
        />

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-600 rounded-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">My AI Insights</h1>
                <p className="text-gray-400">Review what AI has learned about your productivity patterns</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* AI Quota Display */}
              {quota && (
                <AIQuotaWidget 
                  remaining={quota.remaining} 
                  total={quota.total}
                  showDetails={false}
                  size="small"
                />
              )}
              
              <button
                onClick={() => {
                  analytics.trackAIInteraction('my_ai_insights', 'toggle_filters', { 
                    filters_shown: !showFilters 
                  });
                  setShowFilters(!showFilters);
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                  showFilters 
                    ? 'bg-purple-600 border-purple-600 text-white' 
                    : 'border-gray-600 text-gray-300 hover:border-purple-600'
                }`}
              >
                <Filter className="h-4 w-4" />
                Filters
              </button>
            </div>
          </div>

          {/* Statistics Overview */}
          {statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Insights</p>
                    <p className="text-2xl font-bold text-white">{statistics.total_insights}</p>
                  </div>
                  <Brain className="h-8 w-8 text-purple-400" />
                </div>
              </div>
              
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Avg Confidence</p>
                    <p className="text-2xl font-bold text-white">
                      {(statistics.avg_confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-400" />
                </div>
              </div>
              
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Feedback Rate</p>
                    <p className="text-2xl font-bold text-white">
                      {(statistics.feedback_rate * 100).toFixed(0)}%
                    </p>
                  </div>
                  <MessageSquare className="h-8 w-8 text-blue-400" />
                </div>
              </div>
              
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Acceptance Rate</p>
                    <p className="text-2xl font-bold text-white">
                      {(statistics.acceptance_rate * 100).toFixed(0)}%
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-400" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Entity Type
                </label>
                <select
                  value={filters.entity_type}
                  onChange={(e) => {
                    const newFilters = { ...filters, entity_type: e.target.value };
                    handleFiltersChange(newFilters);
                  }}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value="">All Types</option>
                  <option value="global">Global</option>
                  <option value="pillar">Pillars</option>
                  <option value="area">Areas</option>
                  <option value="project">Projects</option>
                  <option value="task">Tasks</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Insight Type
                </label>
                <select
                  value={filters.insight_type}
                  onChange={(e) => {
                    const newFilters = { ...filters, insight_type: e.target.value };
                    handleFiltersChange(newFilters);
                  }}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value="">All Insights</option>
                  <option value="priority_reasoning">Priority Reasoning</option>
                  <option value="alignment_analysis">Alignment Analysis</option>
                  <option value="pattern_recognition">Pattern Recognition</option>
                  <option value="recommendation">Recommendations</option>
                  <option value="obstacle_identification">Obstacles</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Min Confidence
                </label>
                <select
                  value={filters.min_confidence}
                  onChange={(e) => setFilters(prev => ({ ...prev, min_confidence: parseFloat(e.target.value) }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value={0}>Any Confidence</option>
                  <option value={0.5}>50%+</option>
                  <option value={0.7}>70%+</option>
                  <option value={0.8}>80%+</option>
                  <option value={0.9}>90%+</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={filters.is_active}
                  onChange={(e) => setFilters(prev => ({ ...prev, is_active: e.target.value === 'true' }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value={true}>Active Only</option>
                  <option value={false}>Inactive Only</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Search
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search insights..."
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-3 py-2 text-white placeholder-gray-500"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end mt-4 gap-2">
              <button
                onClick={() => {
                  setFilters({
                    entity_type: '',
                    insight_type: '',
                    is_active: true,
                    min_confidence: 0,
                    tags: ''
                  });
                  setSearchTerm('');
                }}
                className="px-4 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              >
                Clear All
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <Brain className="h-8 w-8 text-purple-400 animate-pulse mx-auto mb-4" />
            <p className="text-gray-400">Loading AI insights...</p>
          </div>
        )}

        {/* Insights Grid */}
        {!isLoading && (
          <div className="space-y-6">
            {Object.entries(groupedInsights).map(([priority, priorityInsights]) => {
              if (priorityInsights.length === 0) return null;

              return (
                <div key={priority}>
                  <h2 className="text-xl font-semibold text-white mb-4 capitalize flex items-center gap-2">
                    {priority === 'critical' && <AlertTriangle className="h-5 w-5 text-red-400" />}
                    {priority === 'high' && <Zap className="h-5 w-5 text-orange-400" />}
                    {priority === 'medium' && <Eye className="h-5 w-5 text-yellow-400" />}
                    {priority === 'low' && <MessageSquare className="h-5 w-5 text-gray-400" />}
                    {priority} Priority Insights ({priorityInsights.length})
                  </h2>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {priorityInsights.map((insight) => (
                      <AIInsightCard
                        key={insight.id}
                        insight={insight}
                        onClick={setSelectedInsight}
                        onPin={handlePin}
                        onFeedback={handleFeedback}
                        showActions={true}
                        showMetrics={true}
                        compact={false}
                      />
                    ))}
                  </div>
                </div>
              );
            })}

            {filteredInsights.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <Brain className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-400 mb-2">No insights found</h3>
                <p className="text-gray-500">
                  {searchTerm || Object.values(filters).some(f => f !== '' && f !== true && f !== 0)
                    ? 'Try adjusting your filters or search term'
                    : 'AI insights will appear here as you use the system'
                  }
                </p>
              </div>
            )}
          </div>
        )}

        {/* Insight Detail Modal */}
        {selectedInsight && (
          <InsightDetailModal
            insight={selectedInsight}
            onClose={() => setSelectedInsight(null)}
            onFeedback={handleFeedback}
            onPin={handlePin}
            onDeactivate={handleDeactivate}
          />
        )}
      </div>
    </div>
  );
};

// Insight Detail Modal Component
const InsightDetailModal = ({ insight, onClose, onFeedback, onPin, onDeactivate }) => {
  const IconComponent = insight.insight_type ? {
    priority_reasoning: Target,
    alignment_analysis: TrendingUp,
    pattern_recognition: Brain,
    recommendation: Lightbulb,
    goal_coherence: CheckCircle,
    obstacle_identification: AlertTriangle,
    time_allocation: Clock,
    progress_prediction: Zap
  }[insight.insight_type] || MessageSquare : MessageSquare;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-600 rounded-lg">
              <IconComponent className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">{insight.title}</h2>
              <p className="text-gray-400 capitalize">
                {insight.entity_type} • {insight.insight_type?.replace('_', ' ')}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <XCircle className="h-6 w-6 text-gray-400" />
          </button>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <p className="text-sm text-gray-400">Confidence Score</p>
            <p className="text-2xl font-bold text-green-400">
              {(insight.confidence_score * 100).toFixed(0)}%
            </p>
          </div>
          
          {insight.impact_score && (
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <p className="text-sm text-gray-400">Impact Score</p>
              <p className="text-2xl font-bold text-blue-400">
                {(insight.impact_score * 100).toFixed(0)}%
              </p>
            </div>
          )}
          
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <p className="text-sm text-gray-400">Created</p>
            <p className="text-lg font-semibold text-white">
              {new Date(insight.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Summary */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">Summary</h3>
          <p className="text-gray-300">{insight.summary}</p>
        </div>

        {/* Reasoning Path */}
        {insight.reasoning_path && insight.reasoning_path.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3">Reasoning Path</h3>
            <div className="space-y-3">
              {insight.reasoning_path.map((step, index) => (
                <div key={index} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-purple-400 font-semibold capitalize">
                      {step.level}
                    </span>
                    {step.confidence && (
                      <span className="text-sm text-gray-400">
                        ({(step.confidence * 100).toFixed(0)}% confidence)
                      </span>
                    )}
                  </div>
                  <p className="text-gray-300">{step.reasoning}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Detailed Reasoning */}
        {insight.detailed_reasoning && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3">Detailed Analysis</h3>
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                {JSON.stringify(insight.detailed_reasoning, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-6 border-t border-gray-700">
          <div className="flex items-center gap-4">
            <button
              onClick={() => onFeedback(insight.id, 'accepted')}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
            >
              <ThumbsUp className="h-4 w-4" />
              Helpful
            </button>
            
            <button
              onClick={() => onFeedback(insight.id, 'rejected')}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              <ThumbsDown className="h-4 w-4" />
              Not Helpful
            </button>
            
            <button
              onClick={() => onPin(insight.id, !insight.is_pinned)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                insight.is_pinned 
                  ? 'bg-yellow-600 hover:bg-yellow-700' 
                  : 'bg-gray-600 hover:bg-gray-700'
              }`}
            >
              <Pin className="h-4 w-4" />
              {insight.is_pinned ? 'Unpin' : 'Pin'}
            </button>
          </div>

          <button
            onClick={() => onDeactivate(insight.id)}
            className="px-4 py-2 text-red-400 hover:bg-red-600/20 rounded-lg transition-colors"
          >
            Deactivate
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIIntelligenceCenter;