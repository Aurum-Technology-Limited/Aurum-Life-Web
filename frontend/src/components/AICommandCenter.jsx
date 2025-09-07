import React, { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Brain, 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  Zap, 
  BarChart3, 
  Lightbulb,
  ArrowRight,
  Plus
} from 'lucide-react';
import { hrmAPI, aiCoachAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
// AIQuotaWidget, AIInsightCard, and AIActionButton removed during refactoring

const AICommandCenter = ({ onSectionChange }) => {
  const { toast } = useToast();
  
  // State for quick actions
  const [goalText, setGoalText] = useState('');
  const [isCreatingGoal, setIsCreatingGoal] = useState(false);
  const [showGoalInput, setShowGoalInput] = useState(false);

  // Fetch AI quota
  const { data: quota, isLoading: quotaLoading } = useQuery({
    queryKey: ['ai-quota'],
    queryFn: async () => {
      try {
        const response = await aiCoachAPI.getQuota();
        return response.data;
      } catch (error) {
        console.error('Error loading quota:', error);
        return { remaining: 10, total: 10 }; // Fallback
      }
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  // Fetch recent insights
  const { data: recentInsights, isLoading: insightsLoading } = useQuery({
    queryKey: ['recent-insights'],
    queryFn: async () => {
      try {
        const response = await hrmAPI.getInsights(new URLSearchParams({
          limit: '5',
          is_active: 'true'
        }));
        return response.insights || [];
      } catch (error) {
        console.error('Error loading insights:', error);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch AI statistics
  const { data: statistics } = useQuery({
    queryKey: ['ai-statistics'],
    queryFn: () => hrmAPI.getStatistics(),
    staleTime: 10 * 60 * 1000 // 10 minutes
  });

  const handleQuickGoal = async () => {
    if (!goalText.trim()) {
      toast({
        title: "Please enter a goal",
        description: "Describe what you'd like to achieve",
        variant: "destructive"
      });
      return;
    }

    if (!quota || quota.remaining <= 0) {
      toast({
        title: "AI quota exhausted",
        description: "You've reached your monthly limit",
        variant: "destructive"
      });
      return;
    }

    setIsCreatingGoal(true);
    try {
      // This would typically call the AI Coach API
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call
      
      toast({
        title: "Goal analysis started!",
        description: "Opening AI Coach with your goal...",
        variant: "default"
      });
      
      // Navigate to AI Coach with the goal pre-filled
      onSectionChange('ai-coach', { prefillGoal: goalText });
      
    } catch (error) {
      console.error('Error creating goal:', error);
      toast({
        title: "Failed to analyze goal",
        description: "Please try again or use the full AI Coach",
        variant: "destructive"
      });
    } finally {
      setIsCreatingGoal(false);
      setGoalText('');
      setShowGoalInput(false);
    }
  };

  const handleInsightClick = (insight) => {
    // Navigate to Intelligence Center with the insight pre-selected
    onSectionChange('ai-intelligence', { selectedInsight: insight.id });
  };

  const currentQuota = quota || { remaining: 0, total: 10 };

  return (
    <div className="min-h-screen bg-[#0B0D14] text-white p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
              <Zap size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white">AI Quick Actions</h1>
              <p className="text-gray-400">Fast AI assistance and productivity overview</p>
            </div>
          </div>
        </div>

        {/* AI Quota Status - temporarily removed during refactoring */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-2">AI Quota</h3>
          <p className="text-gray-400 text-sm">
            AI quota tracking has been temporarily removed during refactoring.
          </p>
        </div>

        {/* Quick Actions Section */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-400" />
              Quick Actions
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Quick Goal Decomposition */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 space-y-4">
              <div className="flex items-center gap-3">
                <Target className="h-5 w-5 text-yellow-400" />
                <h3 className="text-lg font-semibold text-white">Quick Goal Setup</h3>
              </div>
              
              {!showGoalInput ? (
                <button
                  onClick={() => setShowGoalInput(true)}
                  className="w-full py-3 px-4 bg-yellow-400 text-black rounded-lg font-medium hover:bg-yellow-500 transition-colors flex items-center justify-center gap-2"
                  disabled={currentQuota.remaining === 0}
                >
                  <Plus className="h-4 w-4" />
                  Start New Goal
                </button>
              ) : (
                <div className="space-y-3">
                  <textarea
                    value={goalText}
                    onChange={(e) => setGoalText(e.target.value)}
                    placeholder="e.g., Learn Spanish, Launch my business, Get fit..."
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 transition-colors resize-none"
                    rows="2"
                    disabled={isCreatingGoal}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleQuickGoal}
                      disabled={!goalText.trim() || isCreatingGoal}
                      className="flex-1 py-2 px-3 bg-yellow-400 text-black rounded-lg font-medium hover:bg-yellow-500 transition-colors disabled:opacity-50 text-sm"
                    >
                      {isCreatingGoal ? 'Analyzing...' : 'Analyze Goal'}
                    </button>
                    <button
                      onClick={() => {
                        setShowGoalInput(false);
                        setGoalText('');
                      }}
                      className="px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
              
              <p className="text-xs text-gray-400">
                Get AI-powered breakdown of your goal into actionable steps
              </p>
            </div>

            {/* Weekly Review */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-2">Weekly Review</h3>
              <p className="text-gray-400 text-sm mb-3">Quick strategic analysis of your progress</p>
              <button className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors">
                Coming Soon
              </button>
            </div>

            {/* Obstacle Help */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-2">Get Unstuck</h3>
              <p className="text-gray-400 text-sm mb-3">AI help when you're blocked on projects</p>
              <button className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors">
                Coming Soon
              </button>
            </div>
          </div>
        </div>

        {/* AI Insights Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Recent Insights */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-purple-400" />
                Recent AI Insights
              </h2>
              <button
                onClick={() => onSectionChange('ai-intelligence')}
                className="flex items-center gap-1 text-purple-400 hover:text-purple-300 text-sm transition-colors"
              >
                View All
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>

            {insightsLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="bg-gray-800/50 rounded-lg p-4 animate-pulse">
                    <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : recentInsights && recentInsights.length > 0 ? (
              <div className="space-y-4">
                {recentInsights.slice(0, 3).map((insight) => (
                  <div key={insight.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <h3 className="text-lg font-semibold text-white mb-2">{insight.title || 'AI Insight'}</h3>
                    <p className="text-gray-400 text-sm mb-3">{insight.description || 'AI insight description'}</p>
                    <button className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors">
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Brain className="h-12 w-12 mx-auto mb-3 text-gray-600" />
                <p className="text-sm">No insights yet</p>
                <p className="text-xs">Use AI Coach to generate your first insights</p>
              </div>
            )}
          </div>

          {/* AI Statistics */}
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-400" />
                AI Performance
              </h2>
            </div>

            {statistics ? (
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400 mb-1">
                    {statistics.total_insights || 0}
                  </div>
                  <div className="text-xs text-gray-400">Total Insights</div>
                </div>
                
                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-400 mb-1">
                    {statistics.avg_confidence ? (statistics.avg_confidence * 100).toFixed(0) : 0}%
                  </div>
                  <div className="text-xs text-gray-400">Avg Confidence</div>
                </div>
                
                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-400 mb-1">
                    {statistics.feedback_rate ? (statistics.feedback_rate * 100).toFixed(0) : 0}%
                  </div>
                  <div className="text-xs text-gray-400">Feedback Rate</div>
                </div>
                
                <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400 mb-1">
                    {statistics.acceptance_rate ? (statistics.acceptance_rate * 100).toFixed(0) : 0}%
                  </div>
                  <div className="text-xs text-gray-400">Acceptance Rate</div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <BarChart3 className="h-12 w-12 mx-auto mb-3 text-gray-600" />
                <p className="text-sm">No statistics available</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div 
            className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 border border-purple-500/30 rounded-xl p-6 cursor-pointer hover:border-purple-400/50 transition-colors"
            onClick={() => onSectionChange('ai-insights')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-purple-600 flex items-center justify-center">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">My AI Insights</h3>
                  <p className="text-purple-300 text-sm">
                    Browse what AI has learned about you
                  </p>
                  <p className="text-purple-400 text-xs mt-1">
                    Review past analysis, manage insights, see patterns
                  </p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-purple-400" />
            </div>
          </div>

          <div 
            className="bg-gradient-to-br from-green-900/50 to-blue-800/30 border border-green-500/30 rounded-xl p-6 cursor-pointer hover:border-green-400/50 transition-colors"
            onClick={() => onSectionChange('goal-planner')}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-green-600 flex items-center justify-center">
                  <Target className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Goal Planner</h3>
                  <p className="text-green-300 text-sm">
                    Strategic planning & AI coaching
                  </p>
                  <p className="text-green-400 text-xs mt-1">
                    Break down goals, weekly reviews, overcome obstacles
                  </p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-green-400" />
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

// Export hook for global access
export const useAICommandCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false)
  };
};

export default AICommandCenter;