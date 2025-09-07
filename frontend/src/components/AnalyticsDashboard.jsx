import React, { useState, useEffect, useCallback } from 'react';
import { useAnalyticsDashboard, useAnalyticsPreferences, useUpdateAnalyticsPreferences } from '../hooks/useGraphQL';
// import { OptimizedBarChart, OptimizedLineChart } from './optimized/OptimizedCharts'; // Removed - using placeholders
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
  Activity,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../contexts/BackendAuthContext';
import { useAnalytics } from '../hooks/useAnalytics';

// Lazy load and register Chart.js components when needed
const registerChartComponents = async () => {
  const {
    Chart: ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
  } = await import('chart.js');
  
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
};

const AnalyticsDashboard = () => {
  const { user } = useAuth();
  const analytics = useAnalytics();
  const [timeRange, setTimeRange] = useState(30);
  const [showPrivacySettings, setShowPrivacySettings] = useState(false);

  // GraphQL hooks
  const { dashboard: dashboardData, loading, error, refetch } = useAnalyticsDashboard(timeRange);
  const { preferences, loading: prefsLoading } = useAnalyticsPreferences();
  const { updatePreferences, loading: updateLoading } = useUpdateAnalyticsPreferences();

  // Register chart components on mount
  useEffect(() => {
    registerChartComponents();
  }, []);

  // Track analytics dashboard usage
  useEffect(() => {
    analytics.trackPageView('/analytics-dashboard');
    analytics.trackFeatureUsage('analytics_dashboard', { time_range: timeRange });
  }, [analytics, timeRange]);

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
      
      const blob = new Blob([JSON.stringify(dashboardData, null, 2)], { type: 'application/json' });
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

  // Handle preference update
  const handlePreferenceUpdate = async (key, value) => {
    try {
      await updatePreferences({ [key]: value });
      analytics.trackFeatureUsage('analytics_preference_change', { preference: key, value });
    } catch (error) {
      console.error('Failed to update preference:', error);
    }
  };

  // Format duration helper
  const formatDuration = (ms) => {
    if (!ms || ms === 0) return '0m';
    const minutes = Math.floor(ms / 60000);
    const hours = Math.floor(minutes / 60);
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    }
    return `${minutes}m`;
  };

  // MetricCard component
  const MetricCard = ({ title, value, icon: Icon, color, bgColor }) => (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <div className={`p-2 rounded-lg ${bgColor}`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </div>
  );

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
              <h1 className="text-2xl font-bold text-white">Analytics Dashboard</h1>
              <p className="text-gray-400">Track your usage patterns and insights</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => handleTimeRangeChange(Number(e.target.value))}
              className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            
            {/* Refresh Button */}
            <button
              onClick={() => refetch()}
              disabled={loading}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
            
            {/* Export Button */}
            <button
              onClick={handleExportData}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Download className="h-5 w-5" />
            </button>
            
            {/* Privacy Settings */}
            <button
              onClick={() => setShowPrivacySettings(!showPrivacySettings)}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Shield className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
          </div>
        ) : (
          <>
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Total Sessions"
                value={dashboardData?.userEngagement?.totalSessions || 0}
                icon={Users}
                color="text-blue-400"
                bgColor="bg-blue-500/10"
              />
              
              <MetricCard
                title="AI Interactions"
                value={dashboardData?.userEngagement?.totalAiInteractions || 0}
                icon={Brain}
                color="text-purple-400"
                bgColor="bg-purple-500/10"
              />
              
              <MetricCard
                title="Time Spent"
                value={formatDuration(dashboardData?.userEngagement?.totalTimeSpentMs || 0)}
                icon={Clock}
                color="text-green-400"
                bgColor="bg-green-500/10"
              />
              
              <MetricCard
                title="Avg Session"
                value={formatDuration(dashboardData?.userEngagement?.averageSessionDurationMs || 0)}
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
                
                {dashboardData?.aiFeatureUsage?.length > 0 ? (
                  <div className="h-[300px]">
                    <OptimizedBarChart
                      data={dashboardData.aiFeatureUsage.map(f => ({
                        label: f.featureName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                        value: f.totalInteractions
                      }))}
                      color="#8B5CF6"
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
                
                {dashboardData?.dailyStats?.length > 0 ? (
                  <div className="h-[300px]">
                    <OptimizedLineChart
                      data={dashboardData.dailyStats.map(d => ({
                        x: new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                        y: d.aiInteractions
                      }))}
                      color="#10B981"
                    />
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <TrendingUp className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-400">No usage trend data available</p>
                  </div>
                )}
              </div>
            </div>

            {/* Feature Adoption */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Target className="h-5 w-5 text-orange-400" />
                Feature Adoption
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {dashboardData?.featureAdoption?.map((feature, index) => (
                  <div key={index} className="bg-gray-800/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-300">
                        {feature.featureName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        feature.usageFrequency === 'high' ? 'bg-green-500/20 text-green-400' :
                        feature.usageFrequency === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {feature.usageFrequency}
                      </span>
                    </div>
                    <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full"
                        style={{ width: `${feature.adoptionRate * 100}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {Math.round(feature.adoptionRate * 100)}% adoption
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Privacy Settings Modal */}
            {showPrivacySettings && preferences && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-md w-full">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                      <Shield className="h-6 w-6 text-purple-400" />
                      Privacy Settings
                    </h3>
                    <button
                      onClick={() => setShowPrivacySettings(false)}
                      className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <AlertCircle className="h-5 w-5 text-gray-400" />
                    </button>
                  </div>
                  
                  <div className="space-y-4">
                    {[
                      { key: 'analyticsConsent', label: 'Analytics Tracking', icon: Activity },
                      { key: 'aiBehaviorTracking', label: 'AI Behavior Tracking', icon: Brain },
                      { key: 'performanceTracking', label: 'Performance Tracking', icon: Zap },
                      { key: 'errorReporting', label: 'Error Reporting', icon: AlertCircle },
                      { key: 'shareAnonymousStats', label: 'Share Anonymous Stats', icon: Users }
                    ].map(({ key, label, icon: Icon }) => (
                      <div key={key} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Icon className="h-5 w-5 text-gray-400" />
                          <span className="text-white">{label}</span>
                        </div>
                        <button
                          onClick={() => handlePreferenceUpdate(key, !preferences[key])}
                          disabled={updateLoading}
                          className={`relative w-12 h-6 rounded-full transition-colors ${
                            preferences[key] ? 'bg-purple-600' : 'bg-gray-600'
                          }`}
                        >
                          <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                            preferences[key] ? 'translate-x-6' : ''
                          }`} />
                        </button>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-6 pt-6 border-t border-gray-800">
                    <p className="text-sm text-gray-400">
                      Data retention: {preferences.dataRetentionDays} days
                    </p>
                    <p className="text-sm text-gray-400">
                      Anonymize after: {preferences.anonymizeAfterDays} days
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;