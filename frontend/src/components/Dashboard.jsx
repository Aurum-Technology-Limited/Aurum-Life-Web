import React, { useEffect, memo } from 'react';
import { TrendingUp, Target, BookOpen, Trophy, Flame, Loader2 } from 'lucide-react';
import { useDashboard } from '../hooks/useGraphQL';
import AlignmentScore from './AlignmentScore';
import LoginStreakTracker from './LoginStreakTracker';

const StatCard = memo(({ title, value, subtitle, icon: Icon, trend, loading = false }) => (
  <div className="p-4 sm:p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group hover:scale-105">
    <div className="flex items-center justify-between mb-3 sm:mb-4">
      <div 
        className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform"
        style={{ backgroundColor: '#F4B400' }}
      >
        {loading ? (
          <Loader2 size={20} className="animate-spin sm:w-6 sm:h-6" style={{ color: '#0B0D14' }} />
        ) : (
          <Icon size={20} className="sm:w-6 sm:h-6" style={{ color: '#0B0D14' }} />
        )}
      </div>
      {trend && (
        <div className="flex items-center space-x-1 text-green-400">
          <TrendingUp size={14} className="sm:w-4 sm:h-4" />
          <span className="text-xs sm:text-sm font-medium">+{trend}%</span>
        </div>
      )}
    </div>
    <h3 className="text-xl sm:text-2xl font-bold text-white mb-1">
      {loading ? '-' : value}
    </h3>
    <p className="text-xs sm:text-sm text-gray-400">{title}</p>
    {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
  </div>
));

StatCard.displayName = 'StatCard';

const Dashboard = memo(({ onSectionChange }) => {
  // Use GraphQL hook for dashboard data
  const { 
    dashboard: dashboardData, 
    loading, 
    error,
    refetch: refetchDashboard 
  } = useDashboard();
  
  const isError = !!error;
  
  // Performance logging for GraphQL
  useEffect(() => {
    if (loading) {
      console.log('🏠 Dashboard: GraphQL - Loading dashboard data...');
    } else if (dashboardData) {
      console.log('🏠 Dashboard: GraphQL - Data loaded from Apollo cache/network');
      console.log('🏠 Dashboard: Data source:', dashboardData ? 'Available' : 'Not available');
    }
  }, [loading, dashboardData]);

  const getCompletionRate = () => {
    if (!dashboardData?.userStats?.taskStats) return 0;
    const { completed, total } = dashboardData.userStats.taskStats;
    return total > 0 ? Math.round((completed / total) * 100) : 0;
  };

  const getActiveTasks = () => {
    if (!dashboardData?.recentTasks) return 0;
    return dashboardData.recentTasks.filter(task => !task.completed).length;
  };

  // Handle error state with retry functionality
  if (isError) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Welcome to Your Growth Journey</h1>
          <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30">
            <p className="text-red-400">Error loading dashboard: {error?.message || 'Unknown error'}</p>
            <button
              onClick={() => refetchDashboard()}
              className="mt-4 px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center mb-8 sm:mb-12">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-4">
          Welcome to Your Growth Journey
        </h1>
        <p className="text-lg sm:text-xl text-gray-300 max-w-3xl mx-auto px-4">
          Track your progress, build lasting habits, and unlock your potential with personalized insights and coaching.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <StatCard
          title="Current Streak"
          value={dashboardData?.userStats?.currentStreak || 0}
          subtitle="days of consistency"
          icon={Flame}
          trend={12}
          loading={loading}
        />
        <StatCard
          title="Tasks Completed"
          value={dashboardData ? `${dashboardData.userStats?.taskStats?.completed || 0}/${dashboardData.userStats?.taskStats?.total || 0}` : '-'}
          subtitle={`${getCompletionRate()}% complete`}
          icon={Target}
          trend={8}
          loading={loading}
        />
        <StatCard
          title="Active Tasks"
          value={getActiveTasks()}
          subtitle="tasks in progress"
          icon={BookOpen}
          loading={loading}
        />
        <StatCard
          title="Total Points"
          value={dashboardData?.userStats?.totalPoints || 0}
          subtitle="alignment points"
          icon={Trophy}
          loading={loading}
        />
      </div>

      {/* Alignment Score & Daily Streak - Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Alignment Score - Weekly Progress */}
        <AlignmentScore onSectionChange={onSectionChange} />
        
        {/* Daily Streak Tracker */}
        <LoginStreakTracker />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Today's Focus */}
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <h2 className="text-2xl font-bold text-white mb-6">Today's Focus</h2>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="p-4 rounded-lg bg-gray-800/50 animate-pulse">
                  <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {dashboardData?.recentTasks?.slice(0, 3).map((task) => (
                <div 
                  key={task.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => onSectionChange('tasks')}
                >
                  <div className="flex items-center space-x-3">
                    <div 
                      className={`w-4 h-4 rounded-full ${task.completed ? 'bg-yellow-400' : 'bg-gray-600'}`}
                    />
                    <div>
                      <p className="font-medium text-white">{task.name}</p>
                      <p className="text-sm text-gray-400">{task.priority} priority</p>
                    </div>
                  </div>
                  <div className="text-right">
                    {task.dueDate && (
                      <>
                        <p className="text-sm font-medium text-yellow-400">
                          {new Date(task.dueDate).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-500">due date</p>
                      </>
                    )}
                  </div>
                </div>
              )) || (
                <div className="text-center text-gray-400 py-8">
                  <p>No tasks yet. Create your first task!</p>
                  <button
                    onClick={() => onSectionChange('tasks')}
                    className="mt-2 text-yellow-400 hover:text-yellow-300"
                  >
                    Get started →
                  </button>
                </div>
              )}
            </div>
          )}
          <button
            onClick={() => onSectionChange('tasks')}
            className="w-full mt-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'View All Tasks'}
          </button>
        </div>

        {/* Upcoming Tasks */}
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <h2 className="text-2xl font-bold text-white mb-6">Upcoming Tasks</h2>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="p-4 rounded-lg bg-gray-800/50 animate-pulse">
                  <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {dashboardData?.upcomingDeadlines?.slice(0, 3).map((task) => (
                <div 
                  key={task.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => onSectionChange('tasks')}
                >
                  <div className="flex items-center space-x-3">
                    <div 
                      className={`w-2 h-8 rounded-full ${
                        task.priority === 'HIGH' ? 'bg-red-400' :
                        task.priority === 'MEDIUM' ? 'bg-yellow-400' : 'bg-green-400'
                      }`}
                    />
                    <div>
                      <p className="font-medium text-white">{task.name}</p>
                      <p className="text-sm text-gray-400">Project: {task.project?.name || 'No project'}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-300">
                      {task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'No due date'}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">{task.priority.toLowerCase()}</p>
                  </div>
                </div>
              )) || (
                <div className="text-center text-gray-400 py-8">
                  <p>No active tasks. Create your first task!</p>
                  <button
                    onClick={() => onSectionChange('tasks')}
                    className="mt-2 text-yellow-400 hover:text-yellow-300"
                  >
                    Get started →
                  </button>
                </div>
              )}
            </div>
          )}
          <button
            onClick={() => onSectionChange('tasks')}
            className="w-full mt-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'View All Tasks'}
          </button>
        </div>
      </div>

      {/* Recent Insights */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h2 className="text-2xl font-bold text-white mb-6">Recent Insights</h2>
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="p-4 rounded-lg bg-gray-800/50 animate-pulse">
                <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-700 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-700 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : dashboardData?.recentInsights?.length > 0 ? (
          <div className="space-y-4">
            {dashboardData.recentInsights.map((insight) => (
              <div 
                key={insight.id}
                className="p-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-all cursor-pointer"
                onClick={() => onSectionChange('insights')}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-white">{insight.title}</h3>
                  <span className="text-xs px-2 py-1 rounded-full bg-yellow-400/20 text-yellow-400">
                    {Math.round(insight.confidenceScore * 100)}% confidence
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">{insight.summary}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Impact: {Math.round((insight.impactScore || 0) * 100)}%</span>
                  <span>•</span>
                  <span>{new Date(insight.createdAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <p>No insights available yet. Keep using the app to generate insights!</p>
            <button
              onClick={() => onSectionChange('insights')}
              className="mt-2 text-yellow-400 hover:text-yellow-300"
            >
              View all insights →
            </button>
          </div>
        )}
      </div>
    </div>
  );
});

Dashboard.displayName = 'Dashboard';

export default Dashboard;