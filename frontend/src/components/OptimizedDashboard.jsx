import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { TrendingUp, Target, BookOpen, Trophy, Flame, Loader2, RefreshCw, Search, Sparkles, X } from 'lucide-react';
import fixedAPI from '../services/fixedApi';
import ErrorBoundary from './ErrorBoundary';
import LoginStreakTracker from './LoginStreakTracker';
import OnboardingWizard from './OnboardingWizard';
import AlignmentScore from './AlignmentScore';
import { api, tasksAPI } from '../services/api';
import { useAuth } from '../contexts/BackendAuthContext';

// Debounce hook
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// Memoized StatCard component with data sanitization
const StatCard = React.memo(({ title, value, subtitle, icon: Icon, trend, loading = false }) => {
  // Sanitize value to prevent React children errors
  const sanitizedValue = React.useMemo(() => {
    if (loading) return '-';
    if (value === null || value === undefined) return '0';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }, [value, loading]);

  // Sanitize trend to prevent errors
  const sanitizedTrend = React.useMemo(() => {
    if (!trend || loading) return null;
    if (typeof trend === 'object') return null;
    return String(trend);
  }, [trend, loading]);

  return (
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
        {sanitizedTrend && (
          <div className="flex items-center space-x-1 text-green-400">
            <TrendingUp size={14} className="sm:w-4 sm:h-4" />
            <span className="text-xs sm:text-sm font-medium">+{sanitizedTrend}%</span>
          </div>
        )}
      </div>
      <h3 className="text-xl sm:text-2xl font-bold text-white mb-1">
        {sanitizedValue}
      </h3>
      <p className="text-xs sm:text-sm text-gray-400">{title}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  );
});

// Simple AI Coach Card component
const SimpleAiCoach = React.memo(() => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadAiCoach = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fixedAPI.getAiCoach();
      setRecommendations(response.data.recommendations || []);
    } catch (err) {
      console.error('AI Coach error:', err);
      setError('Unable to load AI recommendations');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAiCoach();
  }, [loadAiCoach]);

  if (loading) {
    return (
      <div className="mt-6 sm:mt-8 bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl p-4 sm:p-6 border border-blue-800/30">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
            <Loader2 size={16} className="animate-spin text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white">AI Coach</h3>
        </div>
        <p className="text-gray-400">Loading your personalized recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-6 sm:mt-8 bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl p-4 sm:p-6 border border-blue-800/30">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
            <Target size={16} className="text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white">AI Coach</h3>
          <button onClick={loadAiCoach} className="ml-auto text-blue-400 hover:text-blue-300">
            <RefreshCw size={16} />
          </button>
        </div>
        <p className="text-gray-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="mt-6 sm:mt-8 bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl p-4 sm:p-6 border border-blue-800/30">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
          <Target size={16} className="text-white" />
        </div>
        <h3 className="text-lg font-semibold text-white">AI Coach</h3>
      </div>
      
      {recommendations.length > 0 ? (
        <div className="space-y-3">
          <p className="text-gray-300 text-sm">Focus on these tasks to maximize your progress today:</p>
          {recommendations.slice(0, 3).map((rec, index) => {
            // Sanitize recommendation data to prevent React children errors
            const title = typeof rec?.title === 'string' ? rec.title : 'Recommended Task';
            const reason = typeof rec?.reason === 'string' ? rec.reason : '';
            
            return (
              <div key={index} className="bg-gray-804/50 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-yellow-400 font-bold">#{index + 1}</span>
                  <span className="text-white font-medium text-sm">{title}</span>
                </div>
                {reason && (
                  <p className="text-gray-400 text-xs">{reason}</p>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-gray-400">No recommendations available right now.</p>
      )}
    </div>
  );
});

// Main Dashboard component
const OptimizedDashboard = ({ onSectionChange }) => {
  const { user } = useAuth(); // Add user context
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [checkingNewUser, setCheckingNewUser] = useState(true);
  const [isLoading, setIsLoading] = useState(true); // Add explicit loading state

  // Today's Focus state
  const [focusList, setFocusList] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 300);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [searchError, setSearchError] = useState('');

  // Local persistence key scoped per user
  const getFocusStorageKey = useCallback(() => (user && user.id ? `FOCUS_LIST_${user.id}` : null), [user]);

  // Hydrate focus list from localStorage when user is ready
  useEffect(() => {
    const key = getFocusStorageKey();
    if (!key) return;
    try {
      const raw = localStorage.getItem(key);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          setFocusList(parsed);
        }
      }
    } catch (e) {
      console.warn('Failed to load focus list from storage', e);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [getFocusStorageKey]);

  // Persist focus list when it changes
  useEffect(() => {
    const key = getFocusStorageKey();
    if (!key) return;
    try {
      localStorage.setItem(key, JSON.stringify(focusList));
    } catch (e) {
      console.warn('Failed to persist focus list', e);
    }
  }, [focusList, getFocusStorageKey]);

  // Check if user is new (has no data) - but respect onboarding completion status
  const checkNewUser = useCallback(async () => {
    try {
      console.log('🔍 Checking if user is new...');
      setCheckingNewUser(true);
      
      // First check if user has completed onboarding - if yes, don't show onboarding regardless of data
      if (user && user.has_completed_onboarding) {
        console.log('✅ User has completed onboarding - skipping data check');
        setShowOnboarding(false);
        return;
      }
      
      // Only check data if user hasn't completed onboarding
      console.log('🔍 User has not completed onboarding - checking data...');
      
      // Check for existing data across all main entities using ULTRA-PERFORMANCE endpoints
      const [pillarsResponse, areasResponse, projectsResponse] = await Promise.all([
        api.get('/ultra/pillars?include_areas=true'), // Include areas for consistency with Pillars component
        api.get('/ultra/areas?include_projects=true'), // Include projects for consistency with Areas component
        api.get('/ultra/projects')
      ]);

      const totalItems = 
        (pillarsResponse.data?.length || 0) + 
        (areasResponse.data?.length || 0) + 
        (projectsResponse.data?.length || 0);

      console.log('📊 User data check:', {
        pillars: pillarsResponse.data?.length || 0,
        areas: areasResponse.data?.length || 0,
        projects: projectsResponse.data?.length || 0,
        total: totalItems,
        has_completed_onboarding: user?.has_completed_onboarding || false
      });

      // Only show onboarding if user has no data AND hasn't completed onboarding
      if (totalItems === 0 && !user?.has_completed_onboarding) {
        console.log('🎯 New user detected - showing onboarding wizard');
        setShowOnboarding(true);
      } else {
        console.log('✅ User has data or completed onboarding - no onboarding needed');
        setShowOnboarding(false);
      }

    } catch (err) {
      console.error('❌ Error checking new user status:', err);
      // On error, don't show onboarding to avoid blocking access
      setShowOnboarding(false);
    } finally {
      setCheckingNewUser(false);
    }
  }, [user]);

  const fetchDashboard = useCallback(async () => {
    try {
      console.log('🏠 Loading dashboard data...');
      setLoading(true);
      setIsLoading(true); // Set explicit loading state
      setError('');
      
      // Use resilient dashboard fetch that falls back to regular endpoint if ultra fails
      // Switch to dashboardAPI for consistent axios behavior with interceptors
      const response = await (async () => {
        try {
          // Prefer service with built-in fallback
          const { dashboardAPI } = await import('../services/api');
          return await dashboardAPI.getDashboard();
        } catch (e) {
          // Fallback to fixedAPI wrapper which also supports regular dashboard
          try {
            return await fixedAPI.getDashboard();
          } catch (err) {
            throw err;
          }
        }
      })();
      setDashboardData(response.data);
      console.log('🏠 Dashboard loaded successfully');
    } catch (err) {
      console.error('🏠 Dashboard error:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
      setIsLoading(false); // Clear explicit loading state
    }
  }, []);

  useEffect(() => {
    // Check for new user first, then load dashboard
    const initializeDashboard = async () => {
      await checkNewUser();
      await fetchDashboard();
    };
    
    initializeDashboard();
  }, [checkNewUser, fetchDashboard]);

  const handleOnboardingComplete = () => {
    console.log('🎉 Onboarding completed successfully');
    setShowOnboarding(false);
    // Refresh dashboard data to show new structure
    fetchDashboard();
  };

  const handleOnboardingClose = () => {
    console.log('❌ User closed onboarding wizard');
    setShowOnboarding(false);
  };

  // Search logic (debounced)
  useEffect(() => {
    const run = async () => {
      if (!debouncedQuery || debouncedQuery.trim().length < 1) {
        setSearchResults([]);
        return;
      }
      try {
        setSearchError('');
        setSearchLoading(true);
        const res = await tasksAPI.searchTasks(debouncedQuery.trim(), 8);
        setSearchResults(res.data || []);
      } catch (e) {
        console.error('Search error:', e);
        setSearchError('Search failed');
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    };
    run();
  }, [debouncedQuery]);

  const addToFocus = useCallback((task) => {
    setFocusList((prev) => {
      if (prev.some((t) => t.taskId === task.taskId)) return prev;
      return [...prev, task];
    });
    setSearchQuery('');
    setSearchResults([]);
  }, []);

  const removeFromFocus = useCallback((taskId) => {
    setFocusList((prev) => prev.filter((t) => t.taskId !== taskId));
  }, []);

  const handleSuggestFocus = useCallback(async () => {
    try {
      setSuggestLoading(true);
      const res = await tasksAPI.suggestFocus();
      const suggestions = res.data || [];
      setFocusList((prev) => {
        const deduped = [...prev];
        suggestions.forEach(s => {
          if (!deduped.some((t) => t.taskId === s.taskId)) deduped.push(s);
        });
        return deduped;
      });
    } catch (e) {
      console.error('Suggest focus error:', e);
    } finally {
      setSuggestLoading(false);
    }
  }, []);

  // Memoized stats calculations with enhanced data sanitization and defensive programming
  const stats = useMemo(() => {
    // Return safe defaults if data is not loaded yet
    if (!dashboardData || !dashboardData.stats || loading || isLoading) {
      return {
        currentStreak: 0,
        habitsToday: 0,
        activeLearning: 0,
        achievements: 0
      };
    }

    const { stats } = dashboardData;
    
    // Enhanced sanitization to ensure they're numbers and handle all edge cases
    const sanitizeStat = (value, defaultValue = 0) => {
      if (value === null || value === undefined) return defaultValue;
      if (typeof value === 'number' && !isNaN(value)) return value;
      if (typeof value === 'string') {
        const parsed = parseInt(value, 10);
        return isNaN(parsed) ? defaultValue : parsed;
      }
      if (typeof value === 'object') return defaultValue;
      return defaultValue;
    };

    return {
      currentStreak: sanitizeStat(stats.current_streak, 0),
      habitsToday: sanitizeStat(stats.habits_completed_today, 0),
      activeLearning: sanitizeStat(stats.courses_enrolled, 0),
      achievements: sanitizeStat(stats.badges_earned, 0)
    };
  }, [dashboardData, loading, isLoading]);

  // Show onboarding wizard if user is new
  if (showOnboarding) {
    return (
      <OnboardingWizard 
        onComplete={handleOnboardingComplete}
        onClose={handleOnboardingClose}
      />
    );
  }

  // Show loading state while checking for new user or loading dashboard data
  if (checkingNewUser || isLoading) {
    return (
      <div className="min-h-screen p-4 sm:p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
              <p className="text-gray-400 text-sm">
                {checkingNewUser ? 'Setting up your experience...' : 'Loading dashboard...'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-4 sm:p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="text-red-400 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold mb-4">Dashboard Error</h2>
            <p className="text-gray-400 mb-6">{error}</p>
            <button
              onClick={fetchDashboard}
              className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 sm:p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-yellow-400 to-yellow-600 bg-clip-text text-transparent">
            Welcome to Your Growth Journey
          </h1>
          <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto">
            Track your progress, build lasting habits, and unlock your potential with personalized insights and coaching.
          </p>
        </div>

        {/* Today's Focus Section */}
        <div className="mb-8 sm:mb-10 bg-gradient-to-br from-gray-900/50 to-gray-800/30 rounded-xl p-4 sm:p-6 border border-gray-800">
          <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-3 sm:space-y-0 mb-4">
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tasks to add to Today's Focus..."
                className="w-full bg-gray-800 border border-gray-700 rounded-md py-2 pl-9 pr-3 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
              {/* Results dropdown */}
              {debouncedQuery && (searchLoading || searchResults.length > 0) && (
                <div className="absolute z-20 mt-2 w-full bg-gray-900 border border-gray-800 rounded-md shadow-lg max-h-60 overflow-auto">
                  {searchLoading ? (
                    <div className="p-3 text-gray-400 text-sm">Searching...</div>
                  ) : (
                    searchResults.map((r) => (
                      <button
                        key={r.taskId}
                        type="button"
                        className="w-full text-left px-3 py-2 hover:bg-gray-800"
                        onClick={() => addToFocus(r)}
                      >
                        <div className="text-sm text-white">{r.title}</div>
                        <div className="text-xs text-gray-400">{r.project || 'No project'} • {r.priority || 'medium'}{r.dueDate ? ` • Due ${new Date(r.dueDate).toLocaleDateString()}` : ''}</div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={handleSuggestFocus}
              disabled={suggestLoading}
              className="inline-flex items-center justify-center bg-yellow-600 hover:bg-yellow-700 disabled:opacity-60 text-black font-semibold py-2 px-3 rounded-md text-sm"
            >
              <Sparkles size={16} className="mr-2" /> {suggestLoading ? 'Suggesting...' : 'Suggest My Focus'}
            </button>
          </div>
          {/* Focus list */}
          <div className="space-y-2">
            {focusList.length === 0 ? (
              <div className="text-sm text-gray-400">No focus tasks yet. Use search or Suggest My Focus to add tasks.</div>
            ) : (
              focusList.map((t) => (
                <div key={t.taskId} className="flex items-center justify-between bg-gray-900/50 border border-gray-800 rounded-md p-3">
                  <div>
                    <div className="text-sm text-white font-medium">{t.title}</div>
                    <div className="text-xs text-gray-400">{t.project || 'No project'} • {t.priority || 'medium'}{t.dueDate ? ` • Due ${new Date(t.dueDate).toLocaleDateString()}` : ''}</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFromFocus(t.taskId)}
                    className="text-gray-400 hover:text-red-400"
                    aria-label="Remove from focus"
                  >
                    <X size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <StatCard
            title="Current Streak"
            value={stats.currentStreak}
            subtitle="days of consistency"
            icon={Flame}
            trend={12}
            loading={loading || isLoading}
          />
          <StatCard
            title="Habits Today"
            value={`${stats.habitsToday}/5`}
            subtitle="0% complete"
            icon={Target}
            trend={8}
            loading={loading || isLoading}
          />
          <StatCard
            title="Active Learning"
            value={stats.activeLearning}
            subtitle="courses in progress"
            icon={BookOpen}
            loading={loading || isLoading}
          />
          <StatCard
            title="Achievements"
            value={stats.achievements}
            subtitle="badges earned"
            icon={Trophy}
            loading={loading || isLoading}
          />
        </div>

        {/* Alignment Score & Daily Streak - Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Alignment Score Section */}
          <AlignmentScore onSectionChange={onSectionChange} />
          
          {/* Daily Streak Tracker */}
          <LoginStreakTracker />
        </div>
      </div>
    </div>
  );
};

// Wrap in error boundary and forward props (critical to preserve navigation callbacks)
const Dashboard = (props) => (
  <ErrorBoundary>
    <OptimizedDashboard {...props} />
  </ErrorBoundary>
);

export default Dashboard;