import React, { useMemo } from 'react';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { useAppStore } from '../../stores/basicAppStore';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import PrivacyBanner from '../enhanced/PrivacyBanner';
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
  Zap,
  Plus,
  AlertTriangle,
  Clock,
  Flag
} from 'lucide-react';
import { toast } from 'sonner';

export default function SimpleDashboard() {
  const { 
    pillars,
    quickCaptureItems, 
    openQuickCapture, 
    getUnprocessedQuickCapture
  } = useEnhancedFeaturesStore();
  
  const { setActiveSection, navigateToPillar, addNotification } = useAppStore();
  
  const unprocessedItems = getUnprocessedQuickCapture();
  const recentCaptureItems = quickCaptureItems.slice(0, 3);

  // Calculate statistics from data
  const stats = useMemo(() => {
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
    
    // Sort today's tasks by priority
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
    
    // Priority task counts
    const urgentTasksCount = allTasks.filter(t => t.priority === 'urgent' && t.status !== 'completed').length;
    const highTasksCount = allTasks.filter(t => t.priority === 'high' && t.status !== 'completed').length;
    
    return {
      activePillars,
      tasksToday,
      weekProgress,
      todayTasks: sortedTodayTasks.slice(0, 6),
      completedTodayCount: completedTodayTasks.length,
      totalTodayCount: todayTasks.length,
      urgentTasksCount,
      highTasksCount
    };
  }, [pillars]);

  // Get today's focus tasks
  const todaysFocusTasks = stats.todayTasks.map(task => {
    const project = pillars.flatMap(p => p.areas).flatMap(a => a.projects).find(proj => proj.id === task.projectId);
    const pillar = pillars.find(p => p.areas.some(a => a.projects.some(proj => proj.id === task.projectId)));
    
    return {
      ...task,
      pillarName: pillar?.name || 'Unknown',
      pillarIcon: getIconForPillar(pillar?.icon || 'Target'),
      projectName: project?.name || 'Unknown Project'
    };
  });

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

  const handleTaskToggle = (taskId: string, currentStatus: string) => {
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
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-[#B8BCC8]">Your personal operating system command center</p>
      </div>

      {/* Privacy Banner */}
      <PrivacyBanner />

      {/* Quick Stats */}
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
        {/* Today's Focus */}
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
                    className={`p-3 rounded-md border transition-all duration-200 ${
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
                          <h4 className={`font-medium text-sm truncate ${
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
                        </div>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <div className="w-2.5 h-2.5">{task.pillarIcon}</div>
                          <p className="text-xs text-muted-foreground truncate">
                            {task.pillarName}
                          </p>
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

        {/* Quick Capture */}
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
                          <p className="text-xs text-white line-clamp-2 mb-1">
                            {item.content}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(item.timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Pillar Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {pillars.slice(0, 4).map((pillar) => (
          <Card key={pillar.id} className="glassmorphism-card border-0 cursor-pointer hover:border-primary/30" onClick={() => navigateToPillar(pillar.id, pillar.name)}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {getIconForPillar(pillar.icon)}
                  <h3 className="font-medium text-white text-sm">{pillar.name}</h3>
                </div>
                <Badge variant="outline" className="text-xs">
                  {pillar.healthScore}%
                </Badge>
              </div>
              <Progress value={pillar.healthScore} className="h-2" />
              <p className="text-xs text-muted-foreground mt-2">
                {pillar.streak > 0 ? `${pillar.streak} day streak` : 'New start'}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}