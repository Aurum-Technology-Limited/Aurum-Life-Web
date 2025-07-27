import React, { useState, useEffect } from 'react';
import { TrendingUp, Target, BookOpen, Trophy, Flame, Loader2 } from 'lucide-react';
import { useDashboardQuery, usePrefetchQueries } from '../hooks/useQueries';
import AiCoachCard from './AiCoachCard';

const StatCard = ({ title, value, subtitle, icon: Icon, trend, loading = false }) => (
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
);

const Dashboard = ({ onSectionChange }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      console.log('🏠 Dashboard: Starting data fetch');
      setLoading(true);
      setError(null);
      
      const response = await emergencyAPI.dashboard();
      console.log('🏠 Dashboard: Data loaded successfully');
      setDashboardData(response.data);
    } catch (err) {
      console.error('🏠 Dashboard: Failed to load data:', err.message);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getCompletionRate = () => {
    if (!dashboardData?.stats) return 0;
    const { habits_completed_today, total_habits } = dashboardData.stats;
    return total_habits > 0 ? Math.round((habits_completed_today / total_habits) * 100) : 0;
  };

  const getActiveCourses = () => {
    if (!dashboardData?.recent_courses) return 0;
    return dashboardData.recent_courses.filter(course => course.progress_percentage < 100).length;
  };

  if (error) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Welcome to Your Growth Journey</h1>
          <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30">
            <p className="text-red-400">Error loading dashboard: {error}</p>
            <button
              onClick={fetchDashboardData}
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
          value={dashboardData?.user?.current_streak || 0}
          subtitle="days of consistency"
          icon={Flame}
          trend={12}
          loading={loading}
        />
        <StatCard
          title="Habits Today"
          value={dashboardData ? `${dashboardData.stats?.habits_completed_today || 0}/${dashboardData.stats?.total_habits || 0}` : '-'}
          subtitle={`${getCompletionRate()}% complete`}
          icon={Target}
          trend={8}
          loading={loading}
        />
        <StatCard
          title="Active Learning"
          value={getActiveCourses()}
          subtitle="courses in progress"
          icon={BookOpen}
          loading={loading}
        />
        <StatCard
          title="Achievements"
          value={dashboardData?.stats?.badges_earned || 0}
          subtitle="badges earned"
          icon={Trophy}
          loading={loading}
        />
      </div>

      {/* AI Coach - Daily Priorities */}
      <AiCoachCard 
        onStartFocusSession={(taskId, taskName) => {
          // TODO: Integrate with existing Pomodoro timer or task navigation
          console.log(`Starting focus session for task ${taskId}: ${taskName}`);
          // For now, we could navigate to tasks or open a focus modal
          onSectionChange('tasks');
        }}
      />

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
              {dashboardData?.recent_habits?.slice(0, 3).map((habit) => (
                <div 
                  key={habit.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => onSectionChange('habits')}
                >
                  <div className="flex items-center space-x-3">
                    <div 
                      className={`w-4 h-4 rounded-full ${habit.is_completed_today ? 'bg-yellow-400' : 'bg-gray-600'}`}
                    />
                    <div>
                      <p className="font-medium text-white">{habit.name}</p>
                      <p className="text-sm text-gray-400">{habit.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-yellow-400">{habit.current_streak} days</p>
                    <p className="text-xs text-gray-500">streak</p>
                  </div>
                </div>
              )) || (
                <div className="text-center text-gray-400 py-8">
                  <p>No habits yet. Create your first habit!</p>
                  <button
                    onClick={() => onSectionChange('habits')}
                    className="mt-2 text-yellow-400 hover:text-yellow-300"
                  >
                    Get started →
                  </button>
                </div>
              )}
            </div>
          )}
          <button
            onClick={() => onSectionChange('habits')}
            className="w-full mt-4 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'View All Habits'}
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
              {dashboardData?.recent_tasks?.filter(task => !task.completed).slice(0, 3).map((task) => (
                <div 
                  key={task.id}
                  className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-colors cursor-pointer"
                  onClick={() => onSectionChange('tasks')}
                >
                  <div className="flex items-center space-x-3">
                    <div 
                      className={`w-2 h-8 rounded-full ${
                        task.priority === 'high' ? 'bg-red-400' :
                        task.priority === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
                      }`}
                    />
                    <div>
                      <p className="font-medium text-white">{task.title}</p>
                      <p className="text-sm text-gray-400">{task.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-300">
                      {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">{task.priority}</p>
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

      {/* Progress Overview */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h2 className="text-2xl font-bold text-white mb-6">Learning Progress</h2>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="p-4 rounded-lg bg-gray-800/50 animate-pulse">
                <div className="h-32 bg-gray-700 rounded-lg mb-4"></div>
                <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-700 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : dashboardData?.recent_courses?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {dashboardData.recent_courses.map((course) => (
              <div 
                key={course.id}
                className="p-4 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 transition-all cursor-pointer hover:scale-105"
                onClick={() => onSectionChange('learning')}
              >
                <img 
                  src={course.image_url} 
                  alt={course.title}
                  className="w-full h-32 object-cover rounded-lg mb-4"
                />
                <h3 className="font-semibold text-white mb-2">{course.title}</h3>
                <div className="mb-3">
                  <div className="flex justify-between text-sm text-gray-400 mb-1">
                    <span>Progress</span>
                    <span>{course.progress_percentage || 0}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        backgroundColor: '#F4B400',
                        width: `${course.progress_percentage || 0}%`
                      }}
                    />
                  </div>
                </div>
                <p className="text-sm text-gray-400">by {course.instructor}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <p>No courses enrolled yet. Start your learning journey!</p>
            <button
              onClick={() => onSectionChange('learning')}
              className="mt-2 text-yellow-400 hover:text-yellow-300"
            >
              Browse courses →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;