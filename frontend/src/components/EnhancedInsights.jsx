import React, { useState, useEffect } from 'react';
import { BarChart3, Brain, TrendingUp, Target, ArrowRight, Tabs, TabList, Tab, TabPanels, TabPanel } from 'lucide-react';
import { insightsAPI, hrmAPI, aiCoachAPI } from '../services/api';
import { useQuery } from '@tanstack/react-query';
import AIInsightCard from './ui/AIInsightCard';
import CrossNavigationWidget from './ui/CrossNavigationWidget';

const EnhancedInsights = ({ onSectionChange }) => {
  const [activeTab, setActiveTab] = useState('analytics'); // 'analytics', 'ai-insights'
  
  // Fetch analytics data
  const { data: analyticsData, isLoading: analyticsLoading, error: analyticsError } = useQuery({
    queryKey: ['insights-analytics'],
    queryFn: async () => {
      const response = await insightsAPI.getInsights('all_time');
      return response.data;
    },
    staleTime: 5 * 60 * 1000
  });

  // Fetch AI insights data
  const { data: aiInsightsData, isLoading: aiInsightsLoading } = useQuery({
    queryKey: ['ai-insights-enhanced'],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: '10',
        is_active: 'true'
      });
      const response = await hrmAPI.getInsights(params);
      return response.insights || [];
    },
    staleTime: 2 * 60 * 1000
  });

  // Fetch AI statistics
  const { data: aiStatistics } = useQuery({
    queryKey: ['ai-statistics-enhanced'],
    queryFn: () => hrmAPI.getStatistics(),
    staleTime: 10 * 60 * 1000
  });

  const { alignment_snapshot, productivity_trends, area_distribution, eisenhower_matrix } = analyticsData || {};

  return (
    <div className="min-h-screen bg-[#0B0D14] text-white p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Cross-Navigation Widget */}
        <CrossNavigationWidget 
          currentScreen="insights"
          onNavigate={(screen) => onSectionChange && onSectionChange(screen)}
        />

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg">
                <BarChart3 className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Intelligence Hub</h1>
                <p className="text-gray-400">Your complete analytics and AI insights dashboard</p>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mt-6 flex items-center space-x-1 bg-gray-800/50 p-1 rounded-lg w-fit">
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>Performance Analytics</span>
            </button>
            <button
              onClick={() => setActiveTab('ai-insights')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                activeTab === 'ai-insights'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              <Brain className="h-4 w-4" />
              <span>AI Intelligence</span>
            </button>
          </div>
        </div>

        {/* Analytics Tab Content */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            
            {analyticsLoading ? (
              <div className="text-center py-12">
                <BarChart3 className="h-8 w-8 text-blue-400 animate-pulse mx-auto mb-4" />
                <p className="text-gray-400">Loading analytics...</p>
              </div>
            ) : analyticsError ? (
              <div className="text-center py-12">
                <BarChart3 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-gray-300 mb-2">Unable to Load Analytics</h2>
                <p className="text-gray-500">{analyticsError.message}</p>
              </div>
            ) : (
              <>
                {/* Statistics Overview */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Tasks Completed</p>
                        <p className="text-2xl font-bold text-green-400">
                          {alignment_snapshot?.total_tasks_completed || 0}
                        </p>
                      </div>
                      <Target className="h-8 w-8 text-green-400" />
                    </div>
                  </div>
                  
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Projects Active</p>
                        <p className="text-2xl font-bold text-blue-400">
                          {alignment_snapshot?.total_projects || 0}
                        </p>
                      </div>
                      <FolderOpen className="h-8 w-8 text-blue-400" />
                    </div>
                  </div>
                  
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Weekly Score</p>
                        <p className="text-2xl font-bold text-purple-400">
                          {productivity_trends?.this_week || 0}%
                        </p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-purple-400" />
                    </div>
                  </div>
                  
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Active Pillars</p>
                        <p className="text-2xl font-bold text-yellow-400">
                          {alignment_snapshot?.pillar_alignment?.length || 0}
                        </p>
                      </div>
                      <Target className="h-8 w-8 text-yellow-400" />
                    </div>
                  </div>
                </div>

                {/* Eisenhower Matrix */}
                {eisenhower_matrix && (
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                        <Target className="h-5 w-5 text-red-400" />
                        Priority Matrix
                      </h2>
                      <button
                        onClick={() => onSectionChange && onSectionChange('ai-insights')}
                        className="text-purple-400 hover:text-purple-300 text-sm flex items-center gap-1"
                      >
                        Get AI Analysis
                        <ArrowRight className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                        <h3 className="text-red-400 font-medium mb-2">Urgent & Important</h3>
                        <div className="text-2xl font-bold text-white">
                          {eisenhower_matrix.active_counts?.urgent_important || 0}
                        </div>
                        <p className="text-red-300 text-sm">Critical tasks</p>
                      </div>
                      
                      <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
                        <h3 className="text-green-400 font-medium mb-2">Important & Not Urgent</h3>
                        <div className="text-2xl font-bold text-white">
                          {eisenhower_matrix.active_counts?.important_not_urgent || 0}
                        </div>
                        <p className="text-green-300 text-sm">Strategic work</p>
                      </div>
                      
                      <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4">
                        <h3 className="text-yellow-400 font-medium mb-2">Urgent & Not Important</h3>
                        <div className="text-2xl font-bold text-white">
                          {eisenhower_matrix.active_counts?.urgent_not_important || 0}
                        </div>
                        <p className="text-yellow-300 text-sm">Interruptions</p>
                      </div>
                      
                      <div className="bg-gray-700/30 border border-gray-500/30 rounded-lg p-4">
                        <h3 className="text-gray-400 font-medium mb-2">Not Urgent & Not Important</h3>
                        <div className="text-2xl font-bold text-white">
                          {eisenhower_matrix.active_counts?.not_urgent_not_important || 0}
                        </div>
                        <p className="text-gray-300 text-sm">Distractions</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Pillar Alignment */}
                {alignment_snapshot?.pillar_alignment && (
                  <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                    <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
                      <Target className="h-5 w-5 text-yellow-400" />
                      Pillar Alignment Distribution
                    </h2>
                    
                    <div className="space-y-4">
                      {alignment_snapshot.pillar_alignment.map((pillar) => (
                        <div key={pillar.pillar_id} className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <div 
                              className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                              style={{ backgroundColor: pillar.pillar_color }}
                            >
                              {pillar.pillar_icon}
                            </div>
                            <div>
                              <h3 className="text-white font-semibold">{pillar.pillar_name}</h3>
                              <p className="text-gray-400 text-sm">{pillar.task_count} completed tasks</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-bold text-white">{pillar.percentage}%</div>
                            <div className="w-20 bg-gray-700 rounded-full h-2 mt-1">
                              <div
                                className="h-2 rounded-full"
                                style={{ 
                                  width: `${pillar.percentage}%`,
                                  backgroundColor: pillar.pillar_color
                                }}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* AI Insights Tab Content */}
        {activeTab === 'ai-insights' && (
          <div className="space-y-8">
            
            {/* AI Statistics Overview */}
            {aiStatistics && (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Total AI Insights</p>
                      <p className="text-2xl font-bold text-purple-400">{aiStatistics.total_insights || 0}</p>
                    </div>
                    <Brain className="h-8 w-8 text-purple-400" />
                  </div>
                </div>
                
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Avg Confidence</p>
                      <p className="text-2xl font-bold text-green-400">
                        {aiStatistics.avg_confidence ? (aiStatistics.avg_confidence * 100).toFixed(0) : 0}%
                      </p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-400" />
                  </div>
                </div>
                
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Feedback Rate</p>
                      <p className="text-2xl font-bold text-blue-400">
                        {aiStatistics.feedback_rate ? (aiStatistics.feedback_rate * 100).toFixed(0) : 0}%
                      </p>
                    </div>
                    <MessageSquare className="h-8 w-8 text-blue-400" />
                  </div>
                </div>
                
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-400">Acceptance Rate</p>
                      <p className="text-2xl font-bold text-yellow-400">
                        {aiStatistics.acceptance_rate ? (aiStatistics.acceptance_rate * 100).toFixed(0) : 0}%
                      </p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-yellow-400" />
                  </div>
                </div>
              </div>
            )}

            {/* Recent AI Insights */}
            {aiInsightsLoading ? (
              <div className="text-center py-12">
                <Brain className="h-8 w-8 text-purple-400 animate-pulse mx-auto mb-4" />
                <p className="text-gray-400">Loading AI insights...</p>
              </div>
            ) : aiInsightsData && aiInsightsData.length > 0 ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-400" />
                    Recent AI Insights
                  </h2>
                  <button
                    onClick={() => onSectionChange && onSectionChange('ai-insights')}
                    className="text-purple-400 hover:text-purple-300 text-sm flex items-center gap-1"
                  >
                    View All Insights
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {aiInsightsData.slice(0, 6).map((insight) => (
                    <AIInsightCard
                      key={insight.id}
                      insight={insight}
                      onClick={() => onSectionChange && onSectionChange('ai-insights', { selectedInsight: insight.id })}
                      compact={true}
                      showActions={false}
                      showMetrics={true}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Brain className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-300 mb-2">No AI insights yet</h3>
                <p className="text-gray-500 mb-4">Use AI features to generate your first insights</p>
                <button
                  onClick={() => onSectionChange && onSectionChange('goal-planner')}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Get AI Coaching
                </button>
              </div>
            )}

            {/* Cross-Integration Suggestions */}
            <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recommended Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => onSectionChange && onSectionChange('goal-planner')}
                  className="flex items-center gap-3 p-4 bg-green-900/30 border border-green-500/30 rounded-lg hover:bg-green-900/40 transition-colors text-left"
                >
                  <Target className="h-6 w-6 text-green-400" />
                  <div>
                    <div className="text-green-300 font-medium">Plan New Goals</div>
                    <div className="text-green-400 text-sm">Use AI to break down objectives</div>
                  </div>
                </button>
                
                <button
                  onClick={() => onSectionChange && onSectionChange('ai-actions')}
                  className="flex items-center gap-3 p-4 bg-yellow-900/30 border border-yellow-500/30 rounded-lg hover:bg-yellow-900/40 transition-colors text-left"
                >
                  <Zap className="h-6 w-6 text-yellow-400" />
                  <div>
                    <div className="text-yellow-300 font-medium">Quick AI Help</div>
                    <div className="text-yellow-400 text-sm">Fast access to AI tools</div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedInsights;