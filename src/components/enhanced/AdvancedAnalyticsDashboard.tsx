/**
 * Phase 2: Advanced Analytics Dashboard
 * Comprehensive analytics with AI insights and predictive analytics
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  TrendingUp, TrendingDown, Zap, Target, Clock, 
  Brain, AlertTriangle, CheckCircle, BarChart3, 
  PieChart, Calendar, Lightbulb, Star, Award,
  ArrowUp, ArrowDown, Minus, RefreshCw, 
  Download, Share2, Filter
} from 'lucide-react';
import { 
  advancedAnalyticsService, 
  ProductivityMetrics, 
  PillarHealth, 
  AIInsight 
} from '../../services/advancedAnalyticsService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Separator } from '../ui/separator';
import toast from '../../utils/toast';

interface AdvancedAnalyticsDashboardProps {
  className?: string;
}

const AdvancedAnalyticsDashboard: React.FC<AdvancedAnalyticsDashboardProps> = ({
  className = ''
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [productivityMetrics, setProductivityMetrics] = useState<ProductivityMetrics | null>(null);
  const [pillarHealth, setPillarHealth] = useState<PillarHealth[]>([]);
  const [aiInsights, setAiInsights] = useState<AIInsight[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'productivity' | 'pillars' | 'insights'>('overview');

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedPeriod]);

  const loadAnalyticsData = async () => {
    setIsLoading(true);
    try {
      const endDate = new Date();
      const startDate = new Date();
      
      switch (selectedPeriod) {
        case '7d':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case '30d':
          startDate.setDate(endDate.getDate() - 30);
          break;
        case '90d':
          startDate.setDate(endDate.getDate() - 90);
          break;
        case '1y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
      }

      // Load all analytics data
      const [metrics, health, insights] = await Promise.all([
        advancedAnalyticsService.getProductivityMetrics(startDate, endDate),
        advancedAnalyticsService.analyzePillarHealth(),
        advancedAnalyticsService.generateAIInsights()
      ]);

      setProductivityMetrics(metrics);
      setPillarHealth(health);
      setAiInsights(insights);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  const getPeriodLabel = () => {
    switch (selectedPeriod) {
      case '7d': return 'Last 7 days';
      case '30d': return 'Last 30 days';
      case '90d': return 'Last 90 days';
      case '1y': return 'Last year';
      default: return 'Last 30 days';
    }
  };

  const getInsightIcon = (type: AIInsight['type']) => {
    switch (type) {
      case 'productivity': return <Zap className="w-4 h-4" />;
      case 'balance': return <Target className="w-4 h-4" />;
      case 'goal_progress': return <TrendingUp className="w-4 h-4" />;
      case 'time_management': return <Clock className="w-4 h-4" />;
      case 'habit_formation': return <CheckCircle className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: AIInsight['priority']) => {
    switch (priority) {
      case 'critical': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const getTrendIcon = (trend: PillarHealth['trend']) => {
    switch (trend) {
      case 'improving': return <ArrowUp className="w-4 h-4 text-green-400" />;
      case 'declining': return <ArrowDown className="w-4 h-4 text-red-400" />;
      case 'stable': return <Minus className="w-4 h-4 text-yellow-400" />;
      default: return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const dismissInsight = (insightId: string) => {
    advancedAnalyticsService.dismissInsight(insightId);
    setAiInsights(prev => prev.filter(insight => insight.id !== insightId));
  };

  const exportAnalytics = () => {
    const data = {
      period: selectedPeriod,
      metrics: productivityMetrics,
      pillarHealth,
      insights: aiInsights,
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aurum-analytics-${selectedPeriod}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success('Analytics data exported successfully');
  };

  if (isLoading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="glassmorphism-card p-8 text-center">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="glassmorphism-card p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Advanced Analytics</h1>
            <p className="text-muted-foreground">
              AI-powered insights into your productivity and goal progress
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Select value={selectedPeriod} onValueChange={(value: any) => setSelectedPeriod(value)}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
                <SelectItem value="1y">Last year</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              size="sm"
              onClick={loadAnalyticsData}
              disabled={isLoading}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={exportAnalytics}
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <Tabs value={activeTab} onValueChange={(value: any) => setActiveTab(value)} className="w-full">
        <TabsList className="grid w-full grid-cols-4 glassmorphism-panel">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="productivity">Productivity</TabsTrigger>
          <TabsTrigger value="pillars">Pillar Health</TabsTrigger>
          <TabsTrigger value="insights">AI Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          {productivityMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0 }}
              >
                <Card className="glassmorphism-card">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Productivity Score</p>
                        <p className="text-2xl font-bold text-primary">
                          {productivityMetrics.productivityScore}%
                        </p>
                      </div>
                      <div className="p-3 bg-primary/20 rounded-full">
                        <TrendingUp className="w-6 h-6 text-primary" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="glassmorphism-card">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Tasks Completed</p>
                        <p className="text-2xl font-bold text-green-400">
                          {productivityMetrics.tasksCompleted}
                        </p>
                      </div>
                      <div className="p-3 bg-green-500/20 rounded-full">
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="glassmorphism-card">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Focus Hours</p>
                        <p className="text-2xl font-bold text-blue-400">
                          {Math.round(productivityMetrics.focusTime / 60)}h
                        </p>
                      </div>
                      <div className="p-3 bg-blue-500/20 rounded-full">
                        <Clock className="w-6 h-6 text-blue-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="glassmorphism-card">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Active Insights</p>
                        <p className="text-2xl font-bold text-purple-400">
                          {aiInsights.length}
                        </p>
                      </div>
                      <div className="p-3 bg-purple-500/20 rounded-full">
                        <Brain className="w-6 h-6 text-purple-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          )}

          {/* Top Insights Preview */}
          {aiInsights.length > 0 && (
            <Card className="glassmorphism-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-primary" />
                  Top AI Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {aiInsights.slice(0, 3).map((insight, index) => (
                  <motion.div
                    key={insight.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-3 p-4 glassmorphism-panel rounded-lg"
                  >
                    <div className="p-2 bg-primary/20 rounded-full flex-shrink-0">
                      {getInsightIcon(insight.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-foreground truncate">
                          {insight.title}
                        </h4>
                        <Badge className={getPriorityColor(insight.priority)}>
                          {insight.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {insight.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
                <div className="text-center pt-2">
                  <Button
                    variant="ghost"
                    onClick={() => setActiveTab('insights')}
                    className="text-primary hover:text-primary/80"
                  >
                    View all insights →
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Productivity Tab */}
        <TabsContent value="productivity" className="space-y-6">
          {productivityMetrics && (
            <>
              {/* Detailed Productivity Metrics */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="glassmorphism-card">
                  <CardHeader>
                    <CardTitle>Task Completion Analysis</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Completion Rate</span>
                      <span className="font-medium">
                        {productivityMetrics.tasksCreated > 0 
                          ? Math.round((productivityMetrics.tasksCompleted / productivityMetrics.tasksCreated) * 100)
                          : 0}%
                      </span>
                    </div>
                    <Progress 
                      value={productivityMetrics.tasksCreated > 0 
                        ? (productivityMetrics.tasksCompleted / productivityMetrics.tasksCreated) * 100
                        : 0} 
                      className="h-2"
                    />
                    
                    <div className="grid grid-cols-2 gap-4 pt-2">
                      <div className="text-center p-3 glassmorphism-panel rounded-lg">
                        <p className="text-2xl font-bold text-green-400">
                          {productivityMetrics.tasksCompleted}
                        </p>
                        <p className="text-xs text-muted-foreground">Completed</p>
                      </div>
                      <div className="text-center p-3 glassmorphism-panel rounded-lg">
                        <p className="text-2xl font-bold text-yellow-400">
                          {productivityMetrics.tasksCreated - productivityMetrics.tasksCompleted}
                        </p>
                        <p className="text-xs text-muted-foreground">Remaining</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="glassmorphism-card">
                  <CardHeader>
                    <CardTitle>Focus & Time Management</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Average Completion Time</span>
                      <span className="font-medium">
                        {Math.round(productivityMetrics.averageCompletionTime)} min
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 glassmorphism-panel rounded-lg">
                        <p className="text-xl font-bold text-blue-400">
                          {Math.round(productivityMetrics.focusTime / 60)}h
                        </p>
                        <p className="text-xs text-muted-foreground">Focus Time</p>
                      </div>
                      <div className="text-center p-3 glassmorphism-panel rounded-lg">
                        <p className="text-xl font-bold text-red-400">
                          {productivityMetrics.distractionEvents}
                        </p>
                        <p className="text-xs text-muted-foreground">Distractions</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Productivity Score Breakdown */}
              <Card className="glassmorphism-card">
                <CardHeader>
                  <CardTitle>Productivity Score Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center mb-6">
                    <div className="text-4xl font-bold text-primary mb-2">
                      {productivityMetrics.productivityScore}%
                    </div>
                    <p className="text-muted-foreground">Overall Productivity Score</p>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm">Task Completion (40%)</span>
                        <span className="text-sm text-primary">
                          {Math.round((productivityMetrics.tasksCompleted / Math.max(productivityMetrics.tasksCreated, 1)) * 40)}%
                        </span>
                      </div>
                      <Progress 
                        value={(productivityMetrics.tasksCompleted / Math.max(productivityMetrics.tasksCreated, 1)) * 100} 
                        className="h-2"
                      />
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm">Focus Time (40%)</span>
                        <span className="text-sm text-primary">
                          {Math.round(Math.min(productivityMetrics.focusTime / (8 * 60), 1) * 40)}%
                        </span>
                      </div>
                      <Progress 
                        value={Math.min(productivityMetrics.focusTime / (8 * 60), 1) * 100} 
                        className="h-2"
                      />
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm">Distraction Management (20%)</span>
                        <span className="text-sm text-primary">
                          {Math.round((1 - Math.min(productivityMetrics.distractionEvents * 0.1, 0.3)) * 20)}%
                        </span>
                      </div>
                      <Progress 
                        value={(1 - Math.min(productivityMetrics.distractionEvents * 0.1, 0.3)) * 100} 
                        className="h-2"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* Pillar Health Tab */}
        <TabsContent value="pillars" className="space-y-6">
          {pillarHealth.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {pillarHealth.map((pillar, index) => (
                <motion.div
                  key={pillar.pillarId}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="glassmorphism-card">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="truncate">{pillar.pillarName}</CardTitle>
                        <div className="flex items-center gap-2">
                          {getTrendIcon(pillar.trend)}
                          <Badge variant="secondary" className="text-xs">
                            {pillar.trend}
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Health Score */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-muted-foreground">Health Score</span>
                          <span className="font-medium text-primary">
                            {pillar.healthScore}%
                          </span>
                        </div>
                        <Progress value={pillar.healthScore} className="h-2" />
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="p-2 glassmorphism-panel rounded">
                          <p className="text-sm font-medium">{pillar.areasCount}</p>
                          <p className="text-xs text-muted-foreground">Areas</p>
                        </div>
                        <div className="p-2 glassmorphism-panel rounded">
                          <p className="text-sm font-medium">{pillar.activeProjectsCount}</p>
                          <p className="text-xs text-muted-foreground">Projects</p>
                        </div>
                        <div className="p-2 glassmorphism-panel rounded">
                          <p className="text-sm font-medium">{pillar.completedTasksCount}</p>
                          <p className="text-xs text-muted-foreground">Tasks</p>
                        </div>
                      </div>

                      {/* Recommendations */}
                      {pillar.recommendations.length > 0 && (
                        <div>
                          <p className="text-sm text-muted-foreground mb-2">Recommendations:</p>
                          <div className="space-y-1">
                            {pillar.recommendations.slice(0, 2).map((rec, i) => (
                              <p key={i} className="text-xs text-foreground bg-primary/10 p-2 rounded">
                                • {rec}
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : (
            <Card className="glassmorphism-card">
              <CardContent className="p-8 text-center">
                <Target className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No Pillar Data Available</h3>
                <p className="text-muted-foreground">
                  Create some pillars and start tracking your progress to see health analytics.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* AI Insights Tab */}
        <TabsContent value="insights" className="space-y-6">
          {aiInsights.length > 0 ? (
            <div className="space-y-4">
              <AnimatePresence>
                {aiInsights.map((insight, index) => (
                  <motion.div
                    key={insight.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="glassmorphism-card">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex items-start gap-3 flex-1">
                            <div className="p-2 bg-primary/20 rounded-full flex-shrink-0">
                              {getInsightIcon(insight.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <h3 className="font-medium text-foreground">
                                  {insight.title}
                                </h3>
                                <Badge className={getPriorityColor(insight.priority)}>
                                  {insight.priority}
                                </Badge>
                                <Badge variant="outline" className="text-xs">
                                  {Math.round(insight.confidence * 100)}% confident
                                </Badge>
                              </div>
                              
                              <p className="text-sm text-muted-foreground mb-3">
                                {insight.description}
                              </p>

                              {insight.actionable && insight.suggestedActions.length > 0 && (
                                <div className="mb-3">
                                  <p className="text-xs text-muted-foreground mb-2">
                                    Suggested Actions:
                                  </p>
                                  <div className="space-y-1">
                                    {insight.suggestedActions.map((action, i) => (
                                      <p key={i} className="text-xs text-foreground bg-primary/10 p-2 rounded">
                                        • {action}
                                      </p>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <span>Based on:</span>
                                {insight.basedOn.slice(0, 3).map((source, i) => (
                                  <Badge key={i} variant="outline" className="text-xs px-1 py-0">
                                    {source}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </div>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => dismissInsight(insight.id)}
                            className="text-muted-foreground hover:text-foreground"
                          >
                            Dismiss
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <Card className="glassmorphism-card">
              <CardContent className="p-8 text-center">
                <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No AI Insights Available</h3>
                <p className="text-muted-foreground mb-4">
                  Start using Aurum Life more actively to generate personalized insights.
                </p>
                <Button onClick={loadAnalyticsData} variant="outline">
                  Generate Insights
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;