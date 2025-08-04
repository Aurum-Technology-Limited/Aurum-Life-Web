import React, { useState, useEffect } from 'react';
import { Brain, Info, Settings } from 'lucide-react';
import { useAuth } from '../contexts/BackendAuthContext';
import { alignmentScoreAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

const AlignmentScore = ({ onSectionChange }) => {
  const { user } = useAuth();
  const [alignmentData, setAlignmentData] = useState({
    rolling_weekly_score: 0,
    monthly_score: 0,
    monthly_goal: null,
    progress_percentage: 0,
    has_goal_set: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    // Only fetch data if user is loaded and available
    if (user && Object.keys(user).length > 0) {
      fetchAlignmentData();
    }
  }, [user]);

  const fetchAlignmentData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Use centralized API client instead of manual fetch
      const response = await alignmentScoreAPI.getDashboardData();
      
      // Enhanced validation with defensive programming for response data structure
      const data = response?.data || {};
      const safeData = {
        rolling_weekly_score: typeof data.rolling_weekly_score === 'number' ? data.rolling_weekly_score : 0,
        monthly_score: typeof data.monthly_score === 'number' ? data.monthly_score : 0,
        monthly_goal: data.monthly_goal || null,
        progress_percentage: typeof data.progress_percentage === 'number' ? data.progress_percentage : 0,
        has_goal_set: Boolean(data.has_goal_set)
      };
      
      setAlignmentData(safeData);
    } catch (err) {
      console.error('Error fetching alignment data:', err);
      // Handle specific error types
      if (err?.message?.includes('Authentication failed')) {
        setError('Please log in again');
      } else if (err?.message?.includes('timeout')) {
        setError('Request timed out. Please check your connection.');
      } else if (err?.message?.includes('Server temporarily unavailable')) {
        setError('Server temporarily unavailable. Please try again later.');
      } else {
        setError('Unable to load alignment data');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSetGoal = () => {
    // Navigate to Settings page with goals subsection
    if (onSectionChange) {
      onSectionChange('settings', { subSection: 'goals' });
    }
  };

  // Calculate brain fill and glow intensity based on progress with enhanced safety checks
  const progressPercentage = alignmentData?.progress_percentage || 0;
  const safeProgressPercentage = typeof progressPercentage === 'number' && !isNaN(progressPercentage) ? progressPercentage : 0;
  const glowIntensity = Math.min(Math.max(safeProgressPercentage / 100, 0), 1); // Ensure 0-1 scale
  const fillPercentage = Math.min(Math.max(safeProgressPercentage, 0), 100); // Ensure 0-100 range

  // Loading state with skeleton
  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Alignment Score</h3>
        </div>
        <div className="flex flex-col items-center mb-6">
          <div className="w-16 h-16 bg-gray-700 rounded-full animate-pulse mb-4"></div>
          <div className="text-center">
            <div className="h-8 w-16 bg-gray-700 rounded animate-pulse mb-2"></div>
            <div className="h-4 w-32 bg-gray-700 rounded animate-pulse"></div>
          </div>
        </div>
        <div className="h-4 bg-gray-700 rounded animate-pulse"></div>
      </div>
    );
  }

  // Error state with retry option
  if (error) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Alignment Score</h3>
        </div>
        <div className="text-center py-8">
          <Brain className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-sm mb-4">
            {error.includes('Backend URL') ? 'Configuration error' : 
             error.includes('token') ? 'Please log in again' :
             'Unable to load alignment data'}
          </p>
          <button 
            onClick={fetchAlignmentData}
            className="text-yellow-400 hover:text-yellow-300 text-sm underline"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // New user state - no data yet - enhanced safety check
  const isNewUser = (alignmentData?.rolling_weekly_score || 0) === 0 && (alignmentData?.monthly_score || 0) === 0;

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      {/* Header with title and info tooltip */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-white">Alignment Score</h3>
          <div className="relative">
            <button
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
              className="text-gray-400 hover:text-gray-300 transition-colors"
            >
              <Info className="h-4 w-4" />
            </button>
            
            {showTooltip && (
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-3 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300 z-50">
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-800 border-r border-b border-gray-700 rotate-45"></div>
                Earn points by completing projects. Higher-priority projects aligned with your most important goals earn more points.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Central Brain Icon with Fill and Glow Effects */}
      <div className="flex flex-col items-center mb-6">
        <div className="relative mb-4">
          {/* Glow Effect */}
          <div 
            className="absolute inset-0 rounded-full blur-lg transition-all duration-500"
            style={{
              background: `radial-gradient(circle, rgba(244, 180, 0, ${0.3 + (glowIntensity * 0.7)}) 0%, transparent 70%)`,
              transform: `scale(${1 + (glowIntensity * 0.3)})`,
            }}
          />
          
          {/* Brain Icon Container */}
          <div className="relative w-16 h-16 flex items-center justify-center">
            {/* Background Brain (dull state) */}
            <Brain 
              className="absolute inset-0 w-full h-full text-gray-600 transition-all duration-500" 
            />
            
            {/* Foreground Brain (golden fill) */}
            <div 
              className="absolute inset-0 overflow-hidden transition-all duration-500"
              style={{
                clipPath: `inset(${100 - fillPercentage}% 0 0 0)`,
              }}
            >
              <Brain 
                className="w-full h-full text-yellow-400 transition-all duration-500"
                style={{
                  filter: `brightness(${1 + (glowIntensity * 0.5)}) saturate(${1 + (glowIntensity * 0.3)})`,
                }}
              />
            </div>
          </div>
        </div>

        {/* Weekly Score Display */}
        <div className="text-center">
          <div className="text-2xl font-bold text-white mb-1">
            {alignmentData.rolling_weekly_score || 0}
          </div>
          <div className="text-sm text-gray-400">
            Weekly Alignment Score
          </div>
        </div>
      </div>

      {/* Goal Status and Progress */}
      <div className="space-y-3">
        {alignmentData.has_goal_set && alignmentData.monthly_goal && typeof alignmentData.monthly_goal === 'number' ? (
          <>
            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Monthly Progress</span>
                <span className="text-yellow-400">{Math.round(safeProgressPercentage)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-yellow-500 to-yellow-400 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(safeProgressPercentage, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{alignmentData.monthly_score || 0} points</span>
                <span>{alignmentData.monthly_goal} goal</span>
              </div>
            </div>
          </>
        ) : (
          /* Call-to-Action for Setting Goal or New User Message */
          <div className="text-center">
            {isNewUser ? (
              <>
                <p className="text-gray-400 text-sm mb-3">
                  Start completing tasks to see your score!
                </p>
                <button
                  onClick={handleSetGoal}
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-400 hover:bg-yellow-500/30 transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  <span>Set Your Monthly Goal!</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleSetGoal}
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-400 hover:bg-yellow-500/30 transition-colors"
                >
                  <Settings className="w-4 h-4" />
                  <span>Set Your Monthly Goal!</span>
                </button>
                <p className="text-xs text-gray-500 mt-2">
                  Define your target to track progress
                </p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AlignmentScore;