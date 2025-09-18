import React, { useMemo } from 'react';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { useAppStore } from '../../stores/basicAppStore';
import { useRealTimeData } from '../../hooks/useRealTimeData';
import { apiService } from '../../services/apiService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { 
  Heart, 
  Briefcase, 
  Users, 
  BookOpen, 
  DollarSign,
  Target,
  CheckCircle,
  Calendar,
  TrendingUp,
  Brain,
  Lightbulb,
  Zap,
  Plus,
  ArrowRight,
  AlertTriangle,
  Clock,
  Flag,
  RefreshCw,
  Wifi,
  WifiOff,
  AlertCircle,
  Activity
} from 'lucide-react';
import { toast } from 'sonner';

export default function FunctionalDashboard() {
  const { 
    pillars,
    quickCaptureItems, 
    openQuickCapture, 
    getUnprocessedQuickCapture,  
    processQuickCaptureItem,
    deleteQuickCaptureItem 
  } = useEnhancedFeaturesStore();
  
  const { setActiveSection, navigateToPillar, addNotification } = useAppStore();
  
  // Real-time data integration
  // Completely disable real-time features until backend is ready
  const {
    userStats,
    pillarHealth,
    isLoading: realTimeLoading,
    error: realTimeError,
    isConnected,
    refresh: refreshRealTimeData,
    hasData,
    isStale,
    lastUpdated
  } = {
    userStats: null,
    pillarHealth: [],
    isLoading: false,
    error: null,
    isConnected: false,
    refresh: () => {},
    hasData: false,
    isStale: false,
    lastUpdated: null
  };
  
  const unprocessedItems = getUnprocessedQuickCapture();
  const recentCaptureItems = quickCaptureItems.slice(0, 3);

  // Calculate real statistics from data - now enhanced with backend data
  const stats = useMemo(() => {
    // Use backend data if available, otherwise fall back to local calculation
    if (userStats && hasData) {
      return {
        activePillars: userStats.active_pillars,
        tasksToday: `${userStats.completed_tasks_today}/${userStats.total_tasks_today}`,
        weekProgress: userStats.weekly_progress,
        growthTrend: userStats.growth_trend,
        completedTodayCount: userStats.completed_tasks_today,
        totalTodayCount: userStats.total_tasks_today,
        urgentTasksCount: userStats.urgent_tasks_count,
        highTasksCount: userStats.high_tasks_count,
        todayTasks: [], // Will be populated from local data for now
        isFromBackend: true
      };
    }

    // Fallback to local calculation
    const activePillars = pillars.filter(p => p.healthScore > 0).length;
    
    // Calculate all tasks across all projects
    const allTasks = pillars.flatMap(pillar => 
      pillar.areas.flatMap(area => 
        area.projects.flatMap(project => project.tasks)
      )
    );
    
    const todayTasks = allTasks.filter(task => {
      const today = new Date();
      const taskDate = new Date(task.dueDate || new Date());
      return taskDate.toDateString() === today.toDateString();
    });
    
    // Sort today's tasks by priority (urgent -> high -> medium -> low)
    const priorityOrder = { 'urgent': 0, 'high': 1, 'medium': 2, 'low': 3 };
    const sortedTodayTasks = todayTasks.sort((a, b) => {
      const priorityA = priorityOrder[a.priority as keyof typeof priorityOrder] ?? 3;
      const priorityB = priorityOrder[b.priority as keyof typeof priorityOrder] ?? 3;
      if (priorityA !== priorityB) return priorityA - priorityB;
      // If same priority, completed tasks go to bottom
      if (a.status === 'completed' && b.status !== 'completed') return 1;
      if (a.status !== 'completed' && b.status === 'completed') return -1;
      return 0;
    });
    
    const completedTodayTasks = todayTasks.filter(task => task.status === 'completed');
    const tasksToday = `${completedTodayTasks.length}/${todayTasks.length}`;
    
    // Calculate this week's progress
    const thisWeek = new Date();
    const weekStart = new Date(thisWeek.setDate(thisWeek.getDate() - thisWeek.getDay()));
    const thisWeekTasks = allTasks.filter(task => {
      const taskDate = new Date(task.dueDate || new Date());
      return taskDate >= weekStart;
    });
    const completedThisWeek = thisWeekTasks.filter(task => task.status === 'completed');
    const weekProgress = thisWeekTasks.length > 0 ? Math.round((completedThisWeek.length / thisWeekTasks.length) * 100) : 0;
    
    // Calculate overall growth trend with priority weighting
    const completedTasks = allTasks.filter(task => task.status === 'completed').length;
    const totalTasks = allTasks.length;
    const growthTrend = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    // Priority task counts
    const urgentTasksCount = allTasks.filter(t => t.priority === 'urgent' && t.status !== 'completed').length;
    const highTasksCount = allTasks.filter(t => t.priority === 'high' && t.status !== 'completed').length;
    
    return {
      activePillars,
      tasksToday,
      weekProgress,
      growthTrend,
      todayTasks: sortedTodayTasks.slice(0, 8), // Increased to 8 since they're smaller now
      completedTodayCount: completedTodayTasks.length,
      totalTodayCount: todayTasks.length,
      urgentTasksCount,
      highTasksCount,
      isFromBackend: false
    };
  }, [pillars, userStats, hasData]);

  // Get pillar health data for progress visualization - enhanced with backend data
  const pillarHealthData = useMemo(() => {
    return pillars.slice(0, 4).map(pillar => {
      // Find corresponding backend health data
      const backendHealth = pillarHealth.find(h => h.pillar_id === pillar.id);
      
      if (backendHealth) {
        return {
          name: pillar.name,
          progress: backendHealth.health_score,
          trend: backendHealth.streak_days > 0 
            ? `+${backendHealth.streak_days} day streak` 
            : 'New start',
          color: pillar.color,
          weeklyTime: backendHealth.weekly_time_actual,
          targetTime: backendHealth.weekly_time_target,
          trendDirection: backendHealth.trend_direction,
          isFromBackend: true,
          lastUpdated: backendHealth.last_updated
        };
      }
      
      // Fallback to local data
      return {
        name: pillar.name,
        progress: pillar.healthScore,
        trend: pillar.streak > 0 ? `+${pillar.streak} day streak` : 'New start',
        color: pillar.color,
        weeklyTime: pillar.weeklyTimeActual || 0,
        targetTime: pillar.weeklyTimeTarget || 0,
        trendDirection: 'stable' as const,
        isFromBackend: false
      };
    });
  }, [pillars, pillarHealth]);

  // Get today's focus tasks
  const todaysFocusTasks = stats.todayTasks.map(task => {
    const project = pillars.flatMap(p => p.areas).flatMap(a => a.projects).find(proj => proj.id === task.projectId);
    const area = pillars.flatMap(p => p.areas).find(a => a.projects.some(proj => proj.id === task.projectId));
    const pillar = pillars.find(p => p.areas.some(a => a.projects.some(proj => proj.id === task.projectId)));
    
    return {
      ...task,
      pillarName: pillar?.name || 'Unknown',
      pillarIcon: getIconForPillar(pillar?.icon || 'Target'),
      projectName: project?.name || 'Unknown Project'
    };
  });

  // Smart tips based on real data - now enhanced with AI recommendations
  const smartTips = useMemo(() => {
    const tips = [];
    
    // Note: AI recommendations are handled asynchronously and don't block initial render
    // The useMemo will return local tips immediately, AI tips would require state management
    
    // Fallback to local analysis if AI recommendations aren't available
    const allTasks = pillars.flatMap(p => p.areas.flatMap(a => a.projects.flatMap(proj => proj.tasks)));
    const urgentTasks = allTasks.filter(t => t.priority === 'urgent' && t.status !== 'completed' && t.status !== 'cancelled');
    const overdueTasks = allTasks.filter(t => {
      const today = new Date();
      const taskDate = new Date(t.dueDate || new Date());
      return taskDate < today && t.status !== 'completed' && t.status !== 'cancelled';
    });
    
    if (urgentTasks.length > 0) {
      tips.push({
        icon: '🚨',
        title: `${urgentTasks.length} urgent task${urgentTasks.length > 1 ? 's' : ''} need attention`,
        description: 'These high-priority tasks should be completed as soon as possible.',
        action: 'View Tasks',
        priority: 'urgent' as const,
        onClick: () => setActiveSection('tasks'),
        isAI: false
      });
    }
    
    if (overdueTasks.length > 0) {
      tips.push({
        icon: '⏰',
        title: `${overdueTasks.length} overdue task${overdueTasks.length > 1 ? 's' : ''}`,
        description: 'Some tasks have passed their due dates and need immediate attention.',
        action: 'Review Tasks',
        priority: 'high' as const,
        onClick: () => setActiveSection('tasks'),
        isAI: false
      });
    }
    
    // Check for urgent projects
    const urgentProjects = pillars.flatMap(p => p.areas.flatMap(a => a.projects.filter(proj => proj.priority === 'urgent' && proj.status === 'active')));
    if (urgentProjects.length > 0 && tips.length < 2) {
      tips.push({
        icon: '🔥',
        title: `${urgentProjects.length} urgent project${urgentProjects.length > 1 ? 's' : ''} active`,
        description: `Focus on: ${urgentProjects[0].name}`,
        action: 'View Projects',
        priority: 'high' as const,
        onClick: () => setActiveSection('projects'),
        isAI: false
      });
    }
    
    // Check for pillars with low health scores
    const lowHealthPillars = pillars.filter(p => p.healthScore < 70);
    if (lowHealthPillars.length > 0 && tips.length < 2) {
      tips.push({
        icon: '⚠️',
        title: `${lowHealthPillars[0].name} needs attention`,
        description: `Health score is ${lowHealthPillars[0].healthScore}%. Consider adding more time to this pillar.`,
        action: 'View Details',
        priority: 'medium' as const,
        onClick: () => navigateToPillar(lowHealthPillars[0].id, lowHealthPillars[0].name),
        isAI: false
      });
    }
    
    // Check for high-performing pillars
    const highHealthPillars = pillars.filter(p => p.healthScore >= 85);
    if (highHealthPillars.length > 0 && tips.length < 2) {
      tips.push({
        icon: '🎉',
        title: `Excellent progress in ${highHealthPillars[0].name}!`,
        description: `You're maintaining ${highHealthPillars[0].healthScore}% health score. Keep up the momentum!`,
        action: 'View Progress',
        priority: 'low' as const,
        onClick: () => navigateToPillar(highHealthPillars[0].id, highHealthPillars[0].name),
        isAI: false
      });
    }
    
    // Check for unprocessed quick captures
    if (unprocessedItems.length > 0 && tips.length < 2) {
      tips.push({
        icon: '📝',
        title: `${unprocessedItems.length} items need processing`,
        description: 'You have captured ideas waiting to be organized into your system.',
        action: 'Process Items',
        priority: 'medium' as const,
        onClick: () => openQuickCapture(),
        isAI: false
      });
    }
    
    // Sort tips by priority
    const priorityOrder = { 'urgent': 0, 'high': 1, 'medium': 2, 'low': 3 };
    return tips
      .sort((a, b) => (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3))
      .slice(0, 2); // Show max 2 tips
  }, [pillars, unprocessedItems, navigateToPillar, openQuickCapture, setActiveSection, hasData]);

  function getIconForPillar(iconName: string) {
    const iconMap: Record<string, React.ReactNode> = {
      'Heart': <Heart className="w-4 h-4" />,
      'Briefcase': <Briefcase className="w-4 h-4" />,
      'Users': <Users className="w-4 h-4" />,
      'BookOpen': <BookOpen className="w-4 h-4" />,
      'DollarSign': <DollarSign className="w-4 h-4" />,
      'Target': <Target className="w-4 h-4" />
    };
    return iconMap[iconName] || <Target className="w-4 h-4" />;
  }

  function getPriorityConfig(priority: string) {
    const configs = {
      'urgent': { 
        icon: <AlertTriangle className="w-3 h-3" />, 
        color: 'text-red-400', 
        bgColor: 'bg-red-500/10', 
        borderColor: 'border-red-500/20',
        symbol: '!!'
      },
      'high': { 
        icon: <Flag className="w-3 h-3" />, 
        color: 'text-yellow-400', 
        bgColor: 'bg-yellow-500/10', 
        borderColor: 'border-yellow-500/20',
        symbol: '!'
      },
      'medium': { 
        icon: <Clock className="w-3 h-3" />, 
        color: 'text-blue-400', 
        bgColor: 'bg-blue-500/10', 
        borderColor: 'border-blue-500/20',
        symbol: '•'
      },
      'low': { 
        icon: <Target className="w-3 h-3" />, 
        color: 'text-gray-400', 
        bgColor: 'bg-gray-500/10', 
        borderColor: 'border-gray-500/20',
        symbol: '·'
      }
    };
    return configs[priority as keyof typeof configs] || configs.medium;
  }

  const handleTaskToggle = (taskId: string, currentStatus: string) => {
    // This would integrate with your task management system
    const newStatus = currentStatus === 'completed' ? 'todo' : 'completed';
    toast.success(`Task ${newStatus === 'completed' ? 'completed' : 'reopened'}!`);
    
    // Add notification
    addNotification({
      title: 'Task Updated',
      message: `Task has been ${newStatus === 'completed' ? 'completed' : 'reopened'}`,
      type: 'success',
      timestamp: new Date()
    });
  };

  const progressPercentage = stats.totalTodayCount > 0 ? (stats.completedTodayCount / stats.totalTodayCount) * 100 : 0;

  return (
    <div className="space-y-8">
      {/* Header with Real-time Status */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          
          {/* Real-time Status Indicator */}
          <div className="flex items-center space-x-4">
            {/* Data freshness indicator */}
            {lastUpdated && (
              <div className="text-xs text-muted-foreground">
                Last updated: {lastUpdated.toLocaleTimeString()}
                {isStale && (
                  <span className="text-yellow-400 ml-1">
                    <AlertCircle className="w-3 h-3 inline ml-1" />
                  </span>
                )}
              </div>
            )}
            
            {/* Connection status */}
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <div className="flex items-center space-x-1 text-green-400">
                  <Wifi className="w-4 h-4" />
                  <span className="text-xs">Live</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 text-yellow-400">
                  <WifiOff className="w-4 h-4" />
                  <span className="text-xs">Offline</span>
                </div>
              )}
              
              {/* Manual refresh button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={refreshRealTimeData}
                disabled={realTimeLoading}
                className="h-8 w-8 p-0 text-muted-foreground hover:text-primary"
              >
                <RefreshCw className={`w-4 h-4 ${realTimeLoading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <p className="text-[#B8BCC8]">Your personal operating system command center</p>
          
          {/* Backend data indicator */}
          {stats.isFromBackend && (
            <div className="flex items-center space-x-1 text-green-400 text-xs">
              <Activity className="w-3 h-3" />
              <span>Real-time data</span>
            </div>
          )}
        </div>
        
        {/* Error indicator */}
        {realTimeError && (
          <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <div className="flex items-center space-x-2 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Backend connection issue: {realTimeError}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={refreshRealTimeData}
                className="text-red-400 hover:text-red-300 text-xs"
              >
                Retry
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Quick Stats - Real Data */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
                <Target className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Pillars</p>
                <p className="text-2xl font-semibold text-white">{stats.activePillars}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-green-400/20 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Tasks Today</p>
                <p className="text-2xl font-semibold text-white">{stats.tasksToday}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-blue-400/20 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">This Week</p>
                <p className="text-2xl font-semibold text-white">{stats.weekProgress}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glassmorphism-card border-0">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-purple-400/20 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-purple-400" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">Priority Tasks</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-semibold text-white">
                    {stats.urgentTasksCount + stats.highTasksCount}
                  </p>
                  <div className="flex items-center gap-1">
                    {stats.urgentTasksCount > 0 && (
                      <Badge variant="destructive" className="text-xs py-0 px-1 h-4">
                        {stats.urgentTasksCount}!!
                      </Badge>
                    )}
                    {stats.highTasksCount > 0 && (
                      <Badge variant="outline" className="text-xs py-0 px-1 h-4 border-yellow-500/50 text-yellow-400">
                        {stats.highTasksCount}!
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
        {/* Today's Focus - Real Tasks */}
        <div className="lg:col-span-2 xl:col-span-2">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-primary" />
                  <CardTitle className="text-white">Today's Focus</CardTitle>
                </div>
                <Badge variant="outline" className="border-primary/30 text-primary">
                  {stats.tasksToday}
                </Badge>
              </div>
              <Progress value={progressPercentage} className="w-full" />
            </CardHeader>
            <CardContent className="space-y-3">
              {todaysFocusTasks.length > 0 ? (
                todaysFocusTasks.map((task) => (
                  <div 
                    key={task.id} 
                    className={`p-2 rounded-md border transition-all duration-200 ${
                      task.status === 'completed' 
                        ? 'border-green-500/20 bg-green-500/5' 
                        : 'border-border/50 bg-muted/10 hover:bg-muted/20'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleTaskToggle(task.id, task.status)}
                        className={`w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors flex-shrink-0 ${
                          task.status === 'completed'
                            ? 'bg-green-500 border-green-500'
                            : 'border-muted-foreground hover:border-primary'
                        }`}
                      >
                        {task.status === 'completed' && (
                          <CheckCircle className="w-2.5 h-2.5 text-white" />
                        )}
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className={`font-medium text-xs truncate ${
                            task.status === 'completed' 
                              ? 'text-muted-foreground line-through' 
                              : 'text-white'
                          }`}>
                            {task.name}
                          </h4>
                          {task.priority === 'urgent' && (
                            <Badge variant="destructive" className="text-xs py-0 px-1.5 h-4">
                              !!
                            </Badge>
                          )}
                          {task.priority === 'high' && (
                            <Badge variant="outline" className="text-xs py-0 px-1.5 h-4 border-yellow-500/50 text-yellow-400">
                              !
                            </Badge>
                          )}
                          {task.priority === 'medium' && (
                            <Badge variant="outline" className="text-xs py-0 px-1.5 h-4 border-blue-500/50 text-blue-400">
                              •
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <div className="w-2.5 h-2.5">{task.pillarIcon}</div>
                          <p className="text-xs text-muted-foreground truncate">
                            {task.pillarName}
                          </p>
                          {task.estimatedHours && (
                            <span className="text-xs text-muted-foreground">
                              • {task.estimatedHours}h
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground mb-2">
                    No tasks scheduled for today
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Great job staying on top of your schedule!
                  </p>
                </div>
              )}

              <Button 
                onClick={() => setActiveSection('tasks')}
                variant="ghost"
                className="w-full text-primary hover:bg-primary/10"
              >
                <Plus className="w-4 h-4 mr-2" />
                View All Tasks
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Capture - Real Data */}
        <div className="xl:col-span-1">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-primary" />
                  <CardTitle className="text-white">Quick Capture</CardTitle>
                </div>
                {unprocessedItems.length > 0 && (
                  <Badge className="bg-primary/20 text-primary">
                    {unprocessedItems.length} new
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={openQuickCapture}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Zap className="w-4 h-4 mr-2" />
                Quick Capture
              </Button>

              {recentCaptureItems.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-muted-foreground">Recent Captures:</h3>
                  {recentCaptureItems.map((item) => (
                    <div 
                      key={item.id} 
                      className={`p-3 rounded-lg border transition-all ${
                        item.processed 
                          ? 'border-green-500/20 bg-green-500/10' 
                          : 'border-border/50 bg-muted/20'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs capitalize">
                              {item.type}
                            </Badge>
                            {item.processed && (
                              <Badge variant="outline" className="text-xs text-green-400 border-green-400/50">
                                ✓ Processed
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-white line-clamp-2">
                            {item.content}
                          </p>
                          {item.suggestedPillar && (
                            <p className="text-xs text-muted-foreground mt-1">
                              📍 {item.suggestedPillar}
                              {item.suggestedArea && ` › ${item.suggestedArea}`}
                            </p>
                          )}
                        </div>
                        {!item.processed && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => processQuickCaptureItem(
                              item.id, 
                              item.suggestedPillar || 'Personal Development',
                              item.suggestedArea || 'Learning & Growth'
                            )}
                            className="text-xs text-primary hover:underline whitespace-nowrap"
                          >
                            Process
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {quickCaptureItems.length > 3 && (
                    <Button 
                      onClick={openQuickCapture}
                      variant="ghost"
                      className="w-full text-primary hover:bg-primary/10"
                    >
                      View all {quickCaptureItems.length} captures
                    </Button>
                  )}
                </div>
              )}

              {recentCaptureItems.length === 0 && (
                <div className="text-center py-6">
                  <Brain className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground mb-2">
                    No captures yet
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Use Quick Capture to save ideas instantly
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Pillar Progress & Priority Overview */}
        <div className="lg:col-span-2 xl:col-span-2">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary" />
                <CardTitle className="text-white">Pillar Health & Priority Focus</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {pillarHealthData.map((pillar) => {
                const pillarData = pillars.find(p => p.name === pillar.name);
                const urgentProjects = pillarData?.areas.flatMap(a => a.projects.filter(p => p.priority === 'urgent')).length || 0;
                const highProjects = pillarData?.areas.flatMap(a => a.projects.filter(p => p.priority === 'high')).length || 0;
                const urgentTasks = pillarData?.areas.flatMap(a => a.projects.flatMap(p => p.tasks.filter(t => t.priority === 'urgent' && t.status !== 'completed'))).length || 0;
                const highTasks = pillarData?.areas.flatMap(a => a.projects.flatMap(p => p.tasks.filter(t => t.priority === 'high' && t.status !== 'completed'))).length || 0;
                
                return (
                  <div key={pillar.name} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: pillar.color }}
                        />
                        <span className="text-sm font-medium text-white">{pillar.name}</span>
                        <div className="flex items-center gap-1">
                          {urgentProjects > 0 && (
                            <Badge variant="destructive" className="text-xs py-0 px-1 h-4">
                              {urgentProjects}P!!
                            </Badge>
                          )}
                          {highProjects > 0 && (
                            <Badge variant="outline" className="text-xs py-0 px-1 h-4 border-yellow-500/50 text-yellow-400">
                              {highProjects}P!
                            </Badge>
                          )}
                          {urgentTasks > 0 && (
                            <Badge variant="destructive" className="text-xs py-0 px-1 h-4">
                              {urgentTasks}T!!
                            </Badge>
                          )}
                          {highTasks > 0 && (
                            <Badge variant="outline" className="text-xs py-0 px-1 h-4 border-yellow-500/50 text-yellow-400">
                              {highTasks}T!
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Badge variant="outline" className="text-xs text-green-400 border-green-400/50">
                          {pillar.trend}
                        </Badge>
                        <span className="text-muted-foreground">{pillar.progress}%</span>
                      </div>
                    </div>
                    <Progress 
                      value={pillar.progress} 
                      className="h-1.5"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Weekly: {pillar.weeklyTime}h / {pillar.targetTime}h</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          if (pillarData) {
                            navigateToPillar(pillarData.id, pillarData.name);
                          }
                        }}
                        className="h-auto p-0 text-xs text-primary hover:bg-transparent hover:underline"
                      >
                        View Details <ArrowRight className="w-3 h-3 ml-1" />
                      </Button>
                    </div>
                  </div>
                );
              })}
              
              {/* Priority Legend */}
              <div className="pt-3 border-t border-border/50">
                <p className="text-xs text-muted-foreground mb-2">Priority Legend:</p>
                <div className="flex flex-wrap gap-2 text-xs">
                  <div className="flex items-center gap-1">
                    <Badge variant="destructive" className="text-xs py-0 px-1 h-4">!!</Badge>
                    <span className="text-muted-foreground">Urgent</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Badge variant="outline" className="text-xs py-0 px-1 h-4 border-yellow-500/50 text-yellow-400">!</Badge>
                    <span className="text-muted-foreground">High</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Badge variant="outline" className="text-xs py-0 px-1 h-4 border-blue-500/50 text-blue-400">•</Badge>
                    <span className="text-muted-foreground">Medium</span>
                  </div>
                  <span className="text-muted-foreground">P=Projects, T=Tasks</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Smart Tips - AI-like recommendations */}
        <div className="xl:col-span-1">
          <Card className="glassmorphism-card border-0">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary" />
                <CardTitle className="text-white">Smart Tips</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {smartTips.length > 0 ? (
                smartTips.map((tip, index) => (
                  <div key={index} className="p-4 rounded-lg border border-border/50 bg-muted/20">
                    <div className="flex items-start gap-3">
                      <span className="text-primary text-lg">{tip.icon}</span>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-sm mb-1 text-white">{tip.title}</h4>
                        <p className="text-xs text-muted-foreground mb-3">
                          {tip.description}
                        </p>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={tip.onClick}
                          className="h-auto p-0 text-xs text-primary hover:bg-transparent hover:underline"
                        >
                          {tip.action} <ArrowRight className="w-3 h-3 ml-1" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6">
                  <Lightbulb className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground mb-2">
                    All systems running smoothly
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Keep up the great work!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}