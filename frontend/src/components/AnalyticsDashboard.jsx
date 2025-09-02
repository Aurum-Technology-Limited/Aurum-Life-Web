import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import {
  Brain,
  TrendingUp,
  Clock,
  Target,
  Eye,
  Settings,
  Shield,
  Download,
  RefreshCw,
  Filter,
  Calendar,
  Zap,
  Users,
  Activity
} from 'lucide-react';
import { useAuth } from '../contexts/BackendAuthContext';
import { useAnalytics } from '../hooks/useAnalytics';
import { analyticsAPI } from '../services/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AnalyticsDashboard = () => {
  const { user, token } = useAuth();
  const analytics = useAnalytics();
  const [timeRange, setTimeRange] = useState(30);
  const [showPrivacySettings, setShowPrivacySettings] = useState(false);

  // Track analytics dashboard usage
  useEffect(() => {
    analytics.trackPageView('/analytics-dashboard');
    analytics.trackFeatureUsage('analytics_dashboard', { time_range: timeRange });
  }, [analytics, timeRange]);

  // Fetch analytics dashboard data using API service
  const { data: dashboardData, isLoading, error, refetch } = useQuery({
    queryKey: ['analytics-dashboard', timeRange],
    queryFn: () => analyticsAPI.getDashboard(timeRange),
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: !!user && !!token,
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Fetch user preferences using API service
  const { data: preferences } = useQuery({
    queryKey: ['analytics-preferences'],
    queryFn: () => analyticsAPI.getPreferences(),
    enabled: !!user && !!token,
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Colors for charts
  const COLORS = ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5A2B'];

  // Handle time range change
  const handleTimeRangeChange = (newRange) => {
    analytics.trackFeatureUsage('analytics_time_range_change', { 
      old_range: timeRange, 
      new_range: newRange 
    });
    setTimeRange(newRange);
  };

  // Handle data export
  const handleExportData = async () => {
    try {
      analytics.trackFeatureUsage('analytics_export_data', { time_range: timeRange });
      
      const data = await analyticsAPI.getDashboard(timeRange);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `aurum-analytics-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-[#0B0D14] text-white p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
            <Brain className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-400 mb-2">Failed to Load Analytics</h2>
            <p className="text-red-300 mb-4">{error.message}</p>
            <button
              onClick={() => refetch()}
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
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-600 rounded-lg">
              <Activity className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
              <p className="text-gray-400">Track your AI section usage patterns and productivity insights</p>
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
              onClick={() => refetch()}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>

            <button
              onClick={handleExportData}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
            >
              <Download className="h-4 w-4" />
              Export
            </button>

            <button
              onClick={() => setShowPrivacySettings(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <Shield className="h-4 w-4" />
              Privacy
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <Activity className="h-8 w-8 text-purple-400 animate-pulse mx-auto mb-4" />
            <p className="text-gray-400">Loading analytics data...</p>
          </div>
        ) : (
          <>
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Total Sessions"
                value={dashboardData?.user_engagement?.total_sessions || 0}
                icon={Users}
                color="text-blue-400"
                bgColor="bg-blue-500/10"
              />
              
              <MetricCard
                title="AI Interactions"
                value={dashboardData?.user_engagement?.total_ai_interactions || 0}
                icon={Brain}
                color="text-purple-400"
                bgColor="bg-purple-500/10"
              />
              
              <MetricCard
                title="Time Spent"
                value={formatDuration(dashboardData?.user_engagement?.total_time_spent_ms || 0)}
                icon={Clock}
                color="text-green-400"
                bgColor="bg-green-500/10"
              />
              
              <MetricCard
                title="Avg Session"
                value={formatDuration(dashboardData?.user_engagement?.average_session_duration_ms || 0)}
                icon={TrendingUp}
                color="text-yellow-400"
                bgColor="bg-yellow-500/10"
              />
            </div>

            {/* AI Features Usage Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-400" />
                  AI Features Usage
                </h3>
                
                {dashboardData?.ai_feature_usage?.length > 0 ? (
                  <div style={{ height: '300px' }}>
                    <Bar
                      data={{
                        labels: dashboardData.ai_feature_usage.map(f => f.feature_name),
                        datasets: [
                          {
                            label: 'Interactions',
                            data: dashboardData.ai_feature_usage.map(f => f.total_interactions),
                            backgroundColor: '#8B5CF6',
                            borderColor: '#7C3AED',
                            borderWidth: 1,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            grid: {
                              color: '#374151',
                            },
                            ticks: {
                              color: '#9CA3AF',
                            },
                          },
                          x: {
                            grid: {
                              color: '#374151',
                            },
                            ticks: {
                              color: '#9CA3AF',
                              maxRotation: 45,
                            },
                          },
                        },
                      }}
                    />
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-400">No AI feature usage data available</p>
                  </div>
                )}
              </div>

              {/* Daily Usage Trend */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-400" />
                  Daily Usage Trend
                </h3>
                
                {dashboardData?.daily_stats?.length > 0 ? (
                  <div style={{ height: '300px' }}>
                    <Line
                      data={{
                        labels: dashboardData.daily_stats.map(d => d.date),
                        datasets: [
                          {
                            label: 'AI Interactions',
                            data: dashboardData.daily_stats.map(d => d.ai_interactions),
                            borderColor: '#10B981',
                            backgroundColor: '#10B98120',
                            tension: 0.1,
                            fill: true,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            grid: {
                              color: '#374151',
                            },
                            ticks: {
                              color: '#9CA3AF',
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
                    <TrendingUp className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-400">No daily usage data available</p>
                  </div>
                )}
              </div>
            </div>

            {/* Top Features and Success Rates */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Top Features */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-400" />
                  Most Used Features
                </h3>
                
                <div className="space-y-3">
                  {dashboardData?.top_features?.slice(0, 5).map((feature, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center text-xs font-bold">
                          {index + 1}
                        </div>
                        <span className="text-white">{feature.feature_name}</span>
                      </div>
                      <div className="text-gray-400">
                        {feature.usage_count} uses
                      </div>
                    </div>
                  )) || (
                    <div className="text-center py-4">
                      <p className="text-gray-400">No feature usage data available</p>
                    </div>
                  )}
                </div>
              </div>

              {/* AI Feature Success Rates */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-400" />
                  AI Feature Success Rates
                </h3>
                
                <div className="space-y-3">
                  {dashboardData?.ai_feature_usage?.slice(0, 5).map((feature, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-white text-sm">{feature.feature_name}</span>
                        <span className="text-green-400 text-sm">
                          {(feature.success_rate * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-green-400 h-2 rounded-full"
                          style={{ width: `${feature.success_rate * 100}%` }}
                        />
                      </div>
                    </div>
                  )) || (
                    <div className="text-center py-4">
                      <p className="text-gray-400">No success rate data available</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Engagement Insights */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Eye className="h-5 w-5 text-cyan-400" />
                Engagement Insights
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-cyan-400 mb-1">
                    {dashboardData?.user_engagement?.bounce_rate ? 
                      (dashboardData.user_engagement.bounce_rate * 100).toFixed(1) + '%' : 
                      '0%'
                    }
                  </div>
                  <div className="text-gray-400 text-sm">Bounce Rate</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400 mb-1">
                    {dashboardData?.user_engagement?.return_user_rate ? 
                      (dashboardData.user_engagement.return_user_rate * 100).toFixed(1) + '%' : 
                      '0%'
                    }
                  </div>
                  <div className="text-gray-400 text-sm">Return Rate</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-400 mb-1">
                    {dashboardData?.user_engagement?.total_page_views || 0}
                  </div>
                  <div className="text-gray-400 text-sm">Page Views</div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Privacy Settings Modal */}
        {showPrivacySettings && (
          <PrivacySettingsModal
            preferences={preferences}
            onClose={() => setShowPrivacySettings(false)}
            onUpdate={() => refetch()}
          />
        )}
      </div>
    </div>
  );
};

// Utility Components
const MetricCard = ({ title, value, icon: Icon, color, bgColor }) => (
  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm">{title}</p>
        <p className="text-2xl font-bold text-white mt-1">{value}</p>
      </div>
      <div className={`p-3 ${bgColor} rounded-lg`}>
        <Icon className={`h-6 w-6 ${color}`} />
      </div>
    </div>
  </div>
);

// Privacy Settings Modal
const PrivacySettingsModal = ({ preferences, onClose, onUpdate }) => {
  const { user } = useAuth();
  const [settings, setSettings] = useState(preferences || {});
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdateSettings = async () => {
    if (!user) return;

    setIsUpdating(true);
    try {
      await analyticsAPI.updatePreferences(settings);
      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to update privacy settings:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-400" />
            Privacy & Analytics Settings
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            ×
          </button>
        </div>

        <div className="space-y-6">
          {/* General Analytics */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">General Analytics</h3>
            <div className="space-y-3">
              {[
                { key: 'analytics_consent', label: 'Allow Analytics Tracking' },
                { key: 'ai_behavior_tracking', label: 'Track AI Feature Usage' },
                { key: 'performance_tracking', label: 'Performance & Error Tracking' },
                { key: 'error_reporting', label: 'Automatic Error Reporting' }
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings[key] || false}
                    onChange={(e) => setSettings({ ...settings, [key]: e.target.checked })}
                    className="rounded border-gray-600 bg-gray-800 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-white">{label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Feature-Specific Tracking */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Feature-Specific Tracking</h3>
            <div className="space-y-3">
              {[
                { key: 'track_ai_insights_usage', label: 'Track My AI Insights usage' },
                { key: 'track_ai_actions_usage', label: 'Track AI Quick Actions usage' },
                { key: 'track_goal_planner_usage', label: 'Track Goal Planner usage' },
                { key: 'track_navigation_patterns', label: 'Track navigation patterns' },
                { key: 'track_search_queries', label: 'Track search behavior (sensitive)' }
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings[key] || false}
                    onChange={(e) => setSettings({ ...settings, [key]: e.target.checked })}
                    className="rounded border-gray-600 bg-gray-800 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-white">{label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Data Retention */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Data Retention</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Data Retention (days)</label>
                <select
                  value={settings.data_retention_days || 365}
                  onChange={(e) => setSettings({ ...settings, data_retention_days: parseInt(e.target.value) })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value={90}>90 days</option>
                  <option value={180}>6 months</option>
                  <option value={365}>1 year</option>
                  <option value={730}>2 years</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Anonymize After (days)</label>
                <select
                  value={settings.anonymize_after_days || 90}
                  onChange={(e) => setSettings({ ...settings, anonymize_after_days: parseInt(e.target.value) })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value={30}>30 days</option>
                  <option value={90}>90 days</option>
                  <option value={180}>6 months</option>
                  <option value={365}>1 year</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4 mt-8">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpdateSettings}
            disabled={isUpdating}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {isUpdating ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Utility functions
const formatDuration = (milliseconds) => {
  if (!milliseconds) return '0m';
  
  const minutes = Math.floor(milliseconds / 60000);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  return `${minutes}m`;
};

export default AnalyticsDashboard;