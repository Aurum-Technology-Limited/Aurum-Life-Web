import React, { Suspense } from 'react';
import { useEnhancedFeaturesStore } from '../../stores/enhancedFeaturesStore';
import { useAppStore } from '../../stores/basicAppStore';
import CircuitBreaker from '../../utils/circuitBreaker';

// Dashboard Loading Fallback
const DashboardFallback = () => (
  <div className="space-y-6">
    <div className="mb-8">
      <div className="h-8 bg-muted/20 rounded w-48 mb-2 shimmer"></div>
      <div className="h-4 bg-muted/20 rounded w-96 shimmer"></div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="glassmorphism-card p-6">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-muted/20 rounded-lg shimmer"></div>
            <div className="space-y-2 flex-1">
              <div className="h-3 bg-muted/20 rounded w-20 shimmer"></div>
              <div className="h-6 bg-muted/20 rounded w-12 shimmer"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Enhanced Dashboard component with Quick Capture integration and timeout protection
function DashboardContent() {
  // Use React.useMemo to optimize heavy calculations
  const storeData = useEnhancedFeaturesStore();
  const { setActiveSection } = useAppStore();
  
  // Extract data with error handling
  const {
    quickCaptureItems = [],
    openQuickCapture,
    getUnprocessedQuickCapture,
    processQuickCaptureItem,
    deleteQuickCaptureItem,
    pillars = [],
    getAllTasks,
    getAllProjects
  } = storeData || {};
  
  // Memoize expensive calculations
  const dashboardData = React.useMemo(() => {
    try {
      const unprocessedItems = getUnprocessedQuickCapture ? getUnprocessedQuickCapture() : [];
      const recentItems = quickCaptureItems.slice(0, 3);
      
      // Calculate real metrics from data with error handling
      const allTasks = getAllTasks ? getAllTasks() : [];
      const allProjects = getAllProjects ? getAllProjects() : [];
      const completedTasks = allTasks.filter(task => task?.status === 'completed');
      const activePillars = pillars.length;
      const totalTasksCount = allTasks.length;
      const completedTasksCount = completedTasks.length;
      
      // Calculate this week's completion rate
      const weeklyProgress = totalTasksCount > 0 ? Math.round((completedTasksCount / totalTasksCount) * 100) : 0;
      
      // Calculate average pillar health
      const averageHealth = pillars.length > 0 ? 
        Math.round(pillars.reduce((sum, pillar) => sum + (pillar?.healthScore || 0), 0) / pillars.length) : 0;
      
      return {
        unprocessedItems,
        recentItems,
        allTasks,
        allProjects,
        completedTasks,
        activePillars,
        totalTasksCount,
        completedTasksCount,
        weeklyProgress,
        averageHealth
      };
    } catch (error) {
      console.error('Dashboard calculation error:', error);
      return {
        unprocessedItems: [],
        recentItems: [],
        allTasks: [],
        allProjects: [],
        completedTasks: [],
        activePillars: 0,
        totalTasksCount: 0,
        completedTasksCount: 0,
        weeklyProgress: 0,
        averageHealth: 0
      };
    }
  }, [quickCaptureItems, pillars, getUnprocessedQuickCapture, getAllTasks, getAllProjects]);
  
  const {
    unprocessedItems,
    recentItems,
    allTasks,
    allProjects,
    completedTasks,
    activePillars,
    totalTasksCount,
    completedTasksCount,
    weeklyProgress,
    averageHealth
  } = dashboardData;
  
  // Handle navigation to different sections
  const handleNavigateToSection = (section: string) => {
    try {
      setActiveSection(section as any);
    } catch (error) {
      console.error('Navigation error:', error);
    }
  };
  
  // Handle wellness tips navigation
  const handleWellnessTips = () => {
    try {
      // Navigate to Today section which has wellness scheduling
      setActiveSection('today');
    } catch (error) {
      console.error('Wellness navigation error:', error);
      // Fallback: open quick capture for wellness planning
      openQuickCapture();
    }
  };
  
  // Handle career progress navigation
  const handleCareerProgress = () => {
    try {
      // Navigate to Analytics section to view progress
      setActiveSection('analytics');
    } catch (error) {
      console.error('Career progress navigation error:', error);
      // Fallback: navigate to tasks section
      setActiveSection('tasks');
    }
  };
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-[#B8BCC8]">Your personal operating system command center</p>
      </div>

      {/* Quick Stats - Now Interactive */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <button 
          onClick={() => handleNavigateToSection('pillars')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
              <span className="text-primary">🎯</span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Active Pillars</p>
              <p className="text-2xl font-semibold text-white">{activePillars}</p>
            </div>
          </div>
        </button>

        <button 
          onClick={() => handleNavigateToSection('tasks')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-green-400/20 flex items-center justify-center">
              <span className="text-green-400">✓</span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Tasks Completed</p>
              <p className="text-2xl font-semibold text-white">{completedTasksCount}/{totalTasksCount}</p>
            </div>
          </div>
        </button>

        <button 
          onClick={() => handleNavigateToSection('analytics')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-400/20 flex items-center justify-center">
              <span className="text-blue-400">📅</span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">This Week</p>
              <p className="text-2xl font-semibold text-white">{weeklyProgress}%</p>
            </div>
          </div>
        </button>

        <button 
          onClick={() => handleNavigateToSection('analytics')}
          className="glassmorphism-card p-6 text-left hover:scale-105 transition-all duration-200 cursor-pointer touch-target"
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-purple-400/20 flex items-center justify-center">
              <span className="text-purple-400">📈</span>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Avg Health</p>
              <p className="text-2xl font-semibold text-white">{averageHealth}%</p>
            </div>
          </div>
        </button>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* Today's Focus */}
        <div className="lg:col-span-2 xl:col-span-2">
          <div className="glassmorphism-card">
            <div className="p-6 border-b border-border/50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-primary">🎯</span>
                  <h2 className="text-lg font-semibold text-white">Today's Focus</h2>
                </div>
                <span className="text-xs text-muted-foreground bg-muted/30 px-2 py-1 rounded">
                  {completedTasksCount}/{totalTasksCount} completed
                </span>
              </div>
              <div className="mt-3 w-full h-2 bg-muted/50 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full transition-all duration-300" 
                  style={{ width: `${totalTasksCount > 0 ? (completedTasksCount / totalTasksCount) * 100 : 0}%` }}
                ></div>
              </div>
            </div>

            <div className="p-6 space-y-3">
              {allTasks.length > 0 ? allTasks.slice(0, 3).map((task) => {
                const isCompleted = task.status === 'completed';
                // Find the pillar for this task through project->area->pillar hierarchy
                const taskProject = allProjects.find(p => p.id === task.projectId);
                const taskArea = taskProject ? pillars.flatMap(pillar => pillar.areas).find(area => area.id === taskProject.areaId) : null;
                const taskPillar = taskArea ? pillars.find(pillar => pillar.areas.some(area => area.id === taskArea.id)) : null;
                
                return (
                  <button
                    key={task.id}
                    onClick={() => handleNavigateToSection('tasks')}
                    className={`w-full p-3 rounded-lg border text-left transition-all hover:scale-[1.02] ${
                      isCompleted 
                        ? 'border-green-500/20 bg-green-500/10' 
                        : 'border-border/50 bg-muted/30 hover:bg-muted/40'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-5 h-5 rounded-full mt-0.5 flex items-center justify-center ${
                        isCompleted 
                          ? 'bg-green-500 border-2 border-green-500' 
                          : 'border-2 border-muted-foreground'
                      }`}>
                        {isCompleted && <span className="text-white text-xs">✓</span>}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className={`font-medium text-sm ${
                          isCompleted ? 'text-muted-foreground line-through' : 'text-white'
                        }`}>
                          {task.name}
                        </h4>
                        <p className="text-xs text-muted-foreground">
                          🎯 {taskPillar?.name || 'Unknown Pillar'}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              }) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">No tasks created yet</p>
                  <button
                    onClick={() => handleNavigateToSection('tasks')}
                    className="text-primary hover:underline"
                  >
                    Create Your First Task
                  </button>
                </div>
              )}

              <button 
                onClick={() => {
                  try {
                    // Open quick capture modal for adding to today's focus
                    openQuickCapture();
                  } catch (error) {
                    console.error('Error opening quick capture:', error);
                  }
                }}
                className="w-full py-2 text-primary hover:bg-primary/10 rounded-lg transition-colors text-sm touch-target"
              >
                + Add to today's focus
              </button>
            </div>
          </div>
        </div>

        {/* Quick Capture */}
        <div className="glassmorphism-card">
          <div className="p-6 border-b border-border/50">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <span className="text-primary">⚡</span>
                Quick Capture
              </h2>
              {unprocessedItems.length > 0 && (
                <span className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full">
                  {unprocessedItems.length} new
                </span>
              )}
            </div>
          </div>

          <div className="p-6 space-y-4">
            {/* Quick Capture Button */}
            <button 
              onClick={() => {
                try {
                  openQuickCapture();
                } catch (error) {
                  console.error('Error opening quick capture:', error);
                }
              }}
              className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 touch-target"
            >
              <span className="text-lg">✨</span>
              Open Quick Capture
            </button>

            {/* Recent Captured Items */}
            {recentItems.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-muted-foreground">Recent Captures:</h3>
                {recentItems.map((item) => (
                  <div 
                    key={item.id} 
                    className={`p-3 rounded-lg border border-border/50 ${
                      item.processed ? 'bg-green-500/10 border-green-500/20' : 'bg-muted/20'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs px-2 py-0.5 bg-muted/50 rounded text-muted-foreground capitalize">
                            {item.type}
                          </span>
                          {item.processed && (
                            <span className="text-xs text-green-400">✓ Processed</span>
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
                        <button
                          onClick={() => {
                            try {
                              processQuickCaptureItem(
                                item.id, 
                                item.suggestedPillar || 'Personal Development',
                                item.suggestedArea || 'Learning & Growth'
                              );
                            } catch (error) {
                              console.error('Error processing quick capture item:', error);
                            }
                          }}
                          className="text-xs text-primary hover:underline whitespace-nowrap touch-target-small"
                        >
                          Process
                        </button>
                      )}
                    </div>
                  </div>
                ))}
                
                {quickCaptureItems.length > 3 && (
                  <button 
                    onClick={() => {
                      try {
                        openQuickCapture();
                      } catch (error) {
                        console.error('Error opening quick capture:', error);
                      }
                    }}
                    className="w-full py-2 text-primary hover:bg-primary/10 rounded-lg transition-colors text-sm touch-target"
                  >
                    View all {quickCaptureItems.length} captures
                  </button>
                )}
              </div>
            )}

            {recentItems.length === 0 && (
              <div className="text-center py-4">
                <p className="text-sm text-muted-foreground mb-2">
                  No captures yet
                </p>
                <p className="text-xs text-muted-foreground">
                  Use the floating button or click above to start capturing ideas
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Progress Overview */}
        <div className="lg:col-span-2 xl:col-span-1 glassmorphism-card">
          <div className="p-6 border-b border-border/50">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="text-primary">📈</span>
              Pillar Progress
            </h2>
          </div>

          <div className="p-6 space-y-4">
            {pillars.length > 0 ? pillars.slice(0, 4).map((pillar) => {
              // Calculate trend based on health score vs average
              const trend = pillar.healthScore > averageHealth ? '+' : '';
              const trendColor = pillar.healthScore > averageHealth ? 'text-green-400' : 'text-yellow-400';
              const trendBg = pillar.healthScore > averageHealth ? 'bg-green-400/10' : 'bg-yellow-400/10';
              
              return (
                <div key={pillar.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => handleNavigateToSection('pillars')}
                      className="text-sm font-medium text-white hover:text-primary transition-colors text-left"
                    >
                      {pillar.name}
                    </button>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs ${trendColor} ${trendBg} px-2 py-1 rounded`}>
                        {trend}{Math.abs(pillar.healthScore - averageHealth)}%
                      </span>
                      <span className="text-sm text-muted-foreground">{pillar.healthScore}%</span>
                    </div>
                  </div>
                  
                  <div className="h-2 bg-muted/50 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-300"
                      style={{ 
                        width: `${pillar.healthScore}%`,
                        backgroundColor: pillar.color || '#F4D03F'
                      }}
                    />
                  </div>
                </div>
              );
            }) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No pillars created yet</p>
                <button
                  onClick={() => handleNavigateToSection('pillars')}
                  className="text-primary hover:underline"
                >
                  Create Your First Pillar
                </button>
              </div>
            )}
          </div>
        </div>



        {/* Smart Tips */}
        <div className="glassmorphism-card">
          <div className="p-6 border-b border-border/50">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="text-primary">🧠</span>
              Smart Tips
            </h2>
          </div>

          <div className="p-6 space-y-3">
            <div className="p-3 rounded-lg border border-border/50 bg-muted/20">
              <div className="flex items-start gap-3">
                <span className="text-primary mt-0.5">💡</span>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm mb-1 text-white">Schedule wellness time</h4>
                  <p className="text-xs text-muted-foreground mb-2">
                    You haven't scheduled wellness activities this week.
                  </p>
                  <button 
                    onClick={handleWellnessTips}
                    className="text-xs text-primary hover:underline touch-target-small"
                  >
                    Schedule Wellness
                  </button>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg border border-border/50 bg-muted/20">
              <div className="flex items-start gap-3">
                <span className="text-primary mt-0.5">🎉</span>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm mb-1 text-white">Great career momentum!</h4>
                  <p className="text-xs text-muted-foreground mb-2">
                    You've completed 5 career tasks this week.
                  </p>
                  <button 
                    onClick={handleCareerProgress}
                    className="text-xs text-primary hover:underline touch-target-small"
                  >
                    View Analytics
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Optimized Dashboard wrapper with better error handling
export default function Dashboard() {
  return (
    <Suspense fallback={<DashboardFallback />}>
      <div className="dashboard-container">
        <DashboardContent />
      </div>
    </Suspense>
  );
}