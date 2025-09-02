import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Line,
  Bar,
  Doughnut
} from 'react-chartjs-2';
import {
  Brain,
  TrendingUp,
  Heart,
  Zap,
  Target,
  RefreshCw,
  Calendar,
  Smile,
  Activity,
  AlertTriangle,
  CheckCircle,
  Star,
  Play
} from 'lucide-react';
import { useAuth } from '../contexts/BackendAuthContext';
import { useAnalytics } from '../hooks/useAnalytics';
import SentimentIndicator, { SentimentCard } from './ui/SentimentIndicator';

const EmotionalInsightsDashboard = () => {
  const { user, token } = useAuth();
  const analytics = useAnalytics();
  const [timeRange, setTimeRange] = useState(30);
  const [selectedInsight, setSelectedInsight] = useState(null);
  const queryClient = useQueryClient();
  
  // Backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Track emotional insights dashboard usage
  useEffect(() => {
    analytics.trackPageView('/emotional-insights');
    analytics.trackFeatureUsage('emotional_insights_dashboard', { time_range: timeRange });
  }, [analytics, timeRange]);

  // Fetch sentiment trends
  const { data: trendsData, isLoading: trendsLoading, error: trendsError } = useQuery({
    queryKey: ['sentiment-trends', timeRange],
    queryFn: async () => {
      const response = await fetch(`${backendUrl}/api/sentiment/trends?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sentiment trends');
      }

      return response.json();
    },
    enabled: !!user && !!token,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch emotional wellness score
  const { data: wellnessData, isLoading: wellnessLoading } = useQuery({
    queryKey: ['emotional-wellness', timeRange],
    queryFn: async () => {
      const response = await fetch(`${backendUrl}/api/sentiment/wellness-score?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch wellness score');
      }

      return response.json();
    },
    enabled: !!user && !!token,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch activity correlations
  const { data: correlationsData, isLoading: correlationsLoading } = useQuery({
    queryKey: ['activity-sentiment-correlations', timeRange],
    queryFn: async () => {
      const response = await fetch(`${backendUrl}/api/sentiment/correlations?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch activity correlations');
      }

      return response.json();
    },
    enabled: !!user && !!token,
    staleTime: 5 * 60 * 1000,
  });

  // Fetch emotional insights
  const { data: insightsData, isLoading: insightsLoading } = useQuery({
    queryKey: ['emotional-insights', timeRange],
    queryFn: async () => {
      const response = await fetch(`${backendUrl}/api/sentiment/insights?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch emotional insights');
      }

      return response.json();
    },
    enabled: !!user && !!token,
    staleTime: 5 * 60 * 1000,
  });

  // Bulk analyze mutation
  const bulkAnalyzeMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${backendUrl}/api/sentiment/bulk-analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Bulk analysis failed');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['sentiment-trends']);
      queryClient.invalidateQueries(['emotional-wellness']);
      queryClient.invalidateQueries(['activity-sentiment-correlations']);
      queryClient.invalidateQueries(['emotional-insights']);
    }
  });

  // Handle time range change
  const handleTimeRangeChange = (newRange) => {
    analytics.trackFeatureUsage('emotional_insights_time_range', { 
      old_range: timeRange, 
      new_range: newRange 
    });
    setTimeRange(newRange);
  };

  // Prepare chart data for sentiment trends
  const sentimentChartData = trendsData?.trends ? {
    labels: trendsData.trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Daily Sentiment',
        data: trendsData.trends.map(t => t.average_sentiment),
        borderColor: '#8B5CF6',
        backgroundColor: '#8B5CF620',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: trendsData.trends.map(t => {
          const colorMap = {
            'very_positive': '#10B981',
            'positive': '#34D399',
            'neutral': '#6B7280',
            'negative': '#F59E0B', 
            'very_negative': '#EF4444'
          };
          return colorMap[t.dominant_category] || '#6B7280';
        }),
        pointBorderColor: '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 6
      }
    ]
  } : null;

  const isLoading = trendsLoading || wellnessLoading || correlationsLoading || insightsLoading;

  if (trendsError) {
    return (
      <div className="min-h-screen bg-[#0B0D14] text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-400 mb-2">Failed to Load Emotional Insights</h2>
            <p className="text-red-300 mb-4">{trendsError.message}</p>
            <button
              onClick={() => queryClient.invalidateQueries()}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0D14] text-white p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-600 rounded-lg">
              <Heart className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Emotional Intelligence Dashboard</h1>
              <p className="text-gray-400">Understand your emotional patterns and optimize for well-being</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => handleTimeRangeChange(parseInt(e.target.value))}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>

            <button
              onClick={() => queryClient.invalidateQueries()}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>

            <button
              onClick={() => bulkAnalyzeMutation.mutate()}
              disabled={bulkAnalyzeMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <Brain className="h-4 w-4" />
              {bulkAnalyzeMutation.isPending ? 'Analyzing...' : 'Analyze Past Entries'}
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <Heart className="h-8 w-8 text-purple-400 animate-pulse mx-auto mb-4" />
            <p className="text-gray-400">Loading emotional insights...</p>
          </div>
        ) : (
          <>
            {/* Emotional Wellness Score */}
            {wellnessData && (
              <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-6xl">{wellnessData.wellness_emoji}</div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">Emotional Wellness Score</h3>
                      <p className="text-gray-300">{wellnessData.interpretation}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-4xl font-bold text-purple-400">{wellnessData.wellness_score.toFixed(1)}</div>
                    <div className="text-sm text-gray-400">out of 100</div>
                  </div>
                </div>
              </div>
            )}

            {/* Sentiment Trends Chart */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-400" />
                Emotional Journey Over Time
              </h3>
              
              {sentimentChartData ? (
                <div style={{ height: '300px' }}>
                  <Line
                    data={sentimentChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: false,
                        },
                        tooltip: {
                          backgroundColor: '#1F2937',
                          titleColor: '#FFFFFF',
                          bodyColor: '#FFFFFF',
                          borderColor: '#374151',
                          borderWidth: 1,
                          callbacks: {
                            label: function(context) {
                              const score = context.parsed.y;
                              const category = score >= 0.6 ? 'Very Positive' :
                                             score >= 0.2 ? 'Positive' :
                                             score >= -0.2 ? 'Neutral' :
                                             score >= -0.6 ? 'Negative' : 'Very Negative';
                              return `${category}: ${score.toFixed(2)}`;
                            }
                          }
                        }
                      },
                      scales: {
                        y: {
                          min: -1,
                          max: 1,
                          grid: {
                            color: '#374151',
                          },
                          ticks: {
                            color: '#9CA3AF',
                            callback: function(value) {
                              return value > 0 ? `+${value}` : value.toString();
                            }
                          },
                        },
                        x: {
                          grid: {
                            color: '#374151',
                          },
                          ticks: {
                            color: '#9CA3AF',
                          },
                        },
                      },
                    }}
                  />
                </div>
              ) : (
                <div className="text-center py-8">
                  <Heart className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-gray-400">No sentiment data available yet</p>
                  <p className="text-sm text-gray-500">Write journal entries to see your emotional trends</p>
                </div>
              )}
            </div>

            {/* Activity Emotional Correlations */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-400" />
                Activity-Emotion Correlations
              </h3>
              
              {correlationsData?.correlations && correlationsData.correlations.length > 0 ? (
                <div className="space-y-4">
                  {correlationsData.correlations.slice(0, 5).map((correlation, index) => (
                    <div key={index} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className="w-3 h-3 rounded-full" style={{ 
                            backgroundColor: correlation.average_sentiment >= 0.2 ? '#10B981' : 
                                            correlation.average_sentiment <= -0.2 ? '#EF4444' : '#6B7280' 
                          }}></div>
                          <div>
                            <h4 className="text-white font-medium">{correlation.activity_name}</h4>
                            <p className="text-xs text-gray-400 capitalize">{correlation.activity_type}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <SentimentIndicator
                            sentimentScore={correlation.average_sentiment}
                            sentimentCategory={
                              correlation.average_sentiment >= 0.6 ? 'very_positive' :
                              correlation.average_sentiment >= 0.2 ? 'positive' :
                              correlation.average_sentiment >= -0.2 ? 'neutral' :
                              correlation.average_sentiment >= -0.6 ? 'negative' : 'very_negative'
                            }
                            size="small"
                          />
                          <p className="text-xs text-gray-400">{correlation.entry_count} entries</p>
                        </div>
                      </div>
                      
                      {correlation.insights && correlation.insights.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-gray-300">{correlation.insights[0]}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Target className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-gray-400">No activity correlations available</p>
                  <p className="text-sm text-gray-500">Complete tasks and write journal entries to see patterns</p>
                </div>
              )}
            </div>

            {/* Emotional Insights Grid */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-400" />
                AI Emotional Insights
              </h3>
              
              {insightsData?.insights && insightsData.insights.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {insightsData.insights.map((insight, index) => (
                    <div key={index} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 hover:bg-gray-800/70 transition-colors cursor-pointer"
                         onClick={() => setSelectedInsight(insight)}>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-purple-600 rounded-lg">
                          {insight.insight_type === 'trend_analysis' && <TrendingUp className="h-4 w-4 text-white" />}
                          {insight.insight_type === 'activity_correlation' && <Target className="h-4 w-4 text-white" />}
                          {insight.insight_type === 'emotional_pattern' && <Brain className="h-4 w-4 text-white" />}
                          {insight.insight_type === 'wellness_alert' && <AlertTriangle className="h-4 w-4 text-white" />}
                          {insight.insight_type === 'mood_prediction' && <Star className="h-4 w-4 text-white" />}
                        </div>
                        <div>
                          <h4 className="text-white font-medium">{insight.title}</h4>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-400 capitalize">
                              {insight.insight_type.replace('_', ' ')}
                            </span>
                            <div className="flex items-center gap-1">
                              <Star className="h-3 w-3 text-yellow-400" />
                              <span className="text-xs text-gray-400">
                                {(insight.confidence_score * 100).toFixed(0)}% confident
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-300 mb-3">{insight.description}</p>
                      
                      {insight.actionable_suggestions && insight.actionable_suggestions.length > 0 && (
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-400" />
                          <span className="text-xs text-green-400">
                            {insight.actionable_suggestions.length} suggestion(s)
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Brain className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-gray-400">No emotional insights available</p>
                  <p className="text-sm text-gray-500">AI will generate insights as you add more journal entries</p>
                </div>
              )}
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Entries Analyzed</p>
                    <p className="text-2xl font-bold text-white">
                      {trendsData?.summary?.total_entries_analyzed || 0}
                    </p>
                  </div>
                  <Activity className="h-8 w-8 text-blue-400" />
                </div>
              </div>
              
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Trend Direction</p>
                    <p className="text-2xl font-bold text-white capitalize">
                      {trendsData?.summary?.trend_direction?.replace('_', ' ') || 'Stable'}
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-400" />
                </div>
              </div>
              
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Activity Correlations</p>
                    <p className="text-2xl font-bold text-white">
                      {correlationsData?.total_correlations || 0}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-purple-400" />
                </div>
              </div>
              
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">AI Insights</p>
                    <p className="text-2xl font-bold text-white">
                      {insightsData?.insight_count || 0}
                    </p>
                  </div>
                  <Brain className="h-8 w-8 text-pink-400" />
                </div>
              </div>
            </div>
          </>
        )}

        {/* Insight Detail Modal */}
        {selectedInsight && (
          <InsightDetailModal
            insight={selectedInsight}
            onClose={() => setSelectedInsight(null)}
          />
        )}
      </div>
    </div>
  );
};

// Insight Detail Modal Component
const InsightDetailModal = ({ insight, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-600 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">{insight.title}</h2>
              <p className="text-gray-400 capitalize">
                {insight.insight_type.replace('_', ' ')} • {(insight.confidence_score * 100).toFixed(0)}% confident
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="h-6 w-6 text-gray-400" />
          </button>
        </div>

        {/* Description */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">Analysis</h3>
          <p className="text-gray-300">{insight.description}</p>
        </div>

        {/* Actionable Suggestions */}
        {insight.actionable_suggestions && insight.actionable_suggestions.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3">Recommendations</h3>
            <div className="space-y-2">
              {insight.actionable_suggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-green-600/10 border border-green-600/30 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <p className="text-green-200 text-sm">{suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Insight Data */}
        {insight.insight_data && Object.keys(insight.insight_data).length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3">Additional Data</h3>
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                {JSON.stringify(insight.insight_data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmotionalInsightsDashboard;