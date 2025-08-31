import React, { useState } from 'react';
import { Brain, Sparkles, Target, Clock, CheckCircle, TrendingUp } from 'lucide-react';
import AIBadge from './ui/AIBadge';
import ConfidenceIndicator from './ui/ConfidenceIndicator';
import ReasoningPath from './ui/ReasoningPath';
import AIInsightPanel from './ui/AIInsightPanel';
import AIRecommendations from './ui/AIRecommendations';

/**
 * HRMDemo Component - Demonstrates the new HRM-powered AI components
 * Shows all the new UI components with sample data
 */
const HRMDemo = () => {
  const [selectedDemo, setSelectedDemo] = useState('overview');

  // Sample data for demonstrations
  const sampleInsight = {
    title: 'Task Priority Analysis',
    summary: 'AI analysis suggests this task has high strategic value for your Business Development pillar',
    reasoning: [
      {
        type: 'goal',
        title: 'Strategic Alignment',
        description: 'This task directly supports your primary business growth objectives',
        confidence: 0.9
      },
      {
        type: 'analysis',
        title: 'Impact Assessment',
        description: 'Completing this task will unlock 3 dependent tasks and accelerate project timeline',
        confidence: 0.85
      },
      {
        type: 'recommendation',
        title: 'Priority Recommendation',
        description: 'Schedule this task for today to maintain momentum on critical path',
        confidence: 0.92
      }
    ],
    recommendations: [
      'Schedule for morning when energy is highest',
      'Block 2 hours of uninterrupted time',
      'Prepare supporting materials in advance'
    ],
    confidence_score: 0.89,
    priority_score: 8.7,
    insight_type: 'priority_reasoning',
    created_at: new Date().toISOString()
  };

  const sampleRecommendations = [
    {
      title: 'Focus on High-Impact Tasks',
      description: 'Your Business Development pillar has 3 overdue tasks that could unlock significant progress',
      type: 'priority',
      priority: 0.9,
      confidence: 0.87,
      action: 'Review and prioritize these tasks today'
    },
    {
      title: 'Optimize Time Allocation',
      description: 'You\'re spending 60% of time on low-priority activities. Consider delegating or eliminating some tasks',
      type: 'optimization',
      priority: 0.75,
      confidence: 0.82,
      action: 'Audit your task list and identify delegation opportunities'
    },
    {
      title: 'Maintain Project Momentum',
      description: 'Your current project velocity is strong. Keep up the consistent daily progress',
      type: 'improvement',
      priority: 0.6,
      confidence: 0.78,
      action: 'Continue current work patterns'
    }
  ];

  const sampleReasoningPath = [
    {
      type: 'goal',
      title: 'Business Growth',
      description: 'Primary objective: Increase revenue by 25% this quarter'
    },
    {
      type: 'analysis',
      title: 'Current Status',
      description: 'Currently at 60% of quarterly target with 4 weeks remaining'
    },
    {
      type: 'insight',
      title: 'Key Bottleneck',
      description: 'Client onboarding process is taking 40% longer than expected'
    },
    {
      type: 'recommendation',
      title: 'Action Plan',
      description: 'Streamline onboarding by automating 3 key steps'
    }
  ];

  const renderOverview = () => (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-4">HRM-Enhanced AI Components</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          The Hierarchical Reasoning Model (HRM) powers intelligent task prioritization, 
          alignment analysis, and personalized recommendations throughout the application.
        </p>
      </div>

      {/* AI Badges Demo */}
      <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-yellow-400" />
          <span>AI Confidence Badges</span>
        </h3>
        <div className="flex flex-wrap gap-4">
          <AIBadge confidence={0.95} variant="confidence" size="sm" />
          <AIBadge confidence={0.78} variant="default" size="md" />
          <AIBadge confidence={0.45} variant="sparkles" size="lg" />
          <AIBadge confidence={0.92} variant="confidence" size="xs" />
        </div>
      </div>

      {/* Confidence Indicators Demo */}
      <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
          <TrendingUp className="h-5 w-5 text-green-400" />
          <span>Confidence Indicators</span>
        </h3>
        <div className="space-y-4">
          <ConfidenceIndicator confidence={0.92} showPercentage={true} showTrend={true} trend="up" />
          <ConfidenceIndicator confidence={0.67} showPercentage={true} showTrend={true} trend="stable" />
          <ConfidenceIndicator confidence={0.34} showPercentage={true} showTrend={true} trend="down" />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => setSelectedDemo('insight')}
          className="p-4 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg transition-colors text-left"
        >
          <Brain className="h-6 w-6 text-purple-400 mb-2" />
          <h4 className="text-white font-medium">AI Insight Panel</h4>
          <p className="text-gray-400 text-sm">Detailed reasoning and recommendations</p>
        </button>
        
        <button
          onClick={() => setSelectedDemo('reasoning')}
          className="p-4 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg transition-colors text-left"
        >
          <Target className="h-6 w-6 text-blue-400 mb-2" />
          <h4 className="text-white font-medium">Reasoning Path</h4>
          <p className="text-gray-400 text-sm">Step-by-step AI decision process</p>
        </button>
        
        <button
          onClick={() => setSelectedDemo('recommendations')}
          className="p-4 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg transition-colors text-left"
        >
          <CheckCircle className="h-6 w-6 text-green-400 mb-2" />
          <h4 className="text-white font-medium">AI Recommendations</h4>
          <p className="text-gray-400 text-sm">Actionable suggestions and insights</p>
        </button>
      </div>
    </div>
  );

  const renderInsightDemo = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">AI Insight Panel Demo</h2>
        <button
          onClick={() => setSelectedDemo('overview')}
          className="text-yellow-400 hover:text-yellow-300 transition-colors"
        >
          ← Back to Overview
        </button>
      </div>
      
      <AIInsightPanel 
        insight={sampleInsight}
        isExpanded={true}
        showCloseButton={false}
      />
      
      <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Features</h3>
        <ul className="space-y-2 text-gray-300">
          <li>• Expandable/collapsible interface</li>
          <li>• Confidence scoring with visual indicators</li>
          <li>• Step-by-step reasoning visualization</li>
          <li>• Actionable recommendations</li>
          <li>• Priority scoring and metadata</li>
        </ul>
      </div>
    </div>
  );

  const renderReasoningDemo = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Reasoning Path Demo</h2>
        <button
          onClick={() => setSelectedDemo('overview')}
          className="text-yellow-400 hover:text-yellow-300 transition-colors"
        >
          ← Back to Overview
        </button>
      </div>
      
      <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Vertical Layout</h3>
        <ReasoningPath reasoning={sampleReasoningPath} orientation="vertical" />
      </div>
      
      <div className="bg-gray-900/50 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Horizontal Layout</h3>
        <ReasoningPath reasoning={sampleReasoningPath} orientation="horizontal" />
      </div>
    </div>
  );

  const renderRecommendationsDemo = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">AI Recommendations Demo</h2>
        <button
          onClick={() => setSelectedDemo('overview')}
          className="text-yellow-400 hover:text-yellow-300 transition-colors"
        >
          ← Back to Overview
        </button>
      </div>
      
      <AIRecommendations 
        recommendations={sampleRecommendations}
        title="Personalized AI Recommendations"
        showPriority={true}
        showConfidence={true}
        onRecommendationClick={(rec, index) => {
          alert(`Clicked recommendation ${index + 1}: ${rec.title}`);
        }}
      />
    </div>
  );

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-6xl mx-auto">
        {selectedDemo === 'overview' && renderOverview()}
        {selectedDemo === 'insight' && renderInsightDemo()}
        {selectedDemo === 'reasoning' && renderReasoningDemo()}
        {selectedDemo === 'recommendations' && renderRecommendationsDemo()}
      </div>
    </div>
  );
};

export default HRMDemo;