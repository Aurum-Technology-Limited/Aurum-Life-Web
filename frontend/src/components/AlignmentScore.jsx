import React, { useState, useEffect } from 'react';
import { Brain, Info, Settings } from 'lucide-react';
import { useAuth } from '../contexts/BackendAuthContext';
import { useNavigate } from 'react-router-dom';

const AlignmentScore = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
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
    if (user) {
      fetchAlignmentData();
    }
  }, [user]);

  const fetchAlignmentData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/alignment/dashboard`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch alignment data`);
      }

      const data = await response.json();
      setAlignmentData(data);
    } catch (err) {
      console.error('Error fetching alignment data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSetGoal = () => {
    // This will be handled by the Settings integration
    // For now, we can show a message or redirect to settings
    console.log('Redirect to settings to set monthly goal');
  };

  // Calculate brain fill and glow intensity based on progress
  const progressPercentage = alignmentData.progress_percentage || 0;
  const glowIntensity = Math.min(progressPercentage / 100, 1); // 0-1 scale
  const fillPercentage = Math.min(progressPercentage, 100);

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Alignment Score</h3>
        </div>
        <div className="flex items-center justify-center h-32">
          <div className="animate-pulse">
            <div className="h-16 w-16 bg-gray-700 rounded-full"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Alignment Score</h3>
        </div>
        <div className="text-center text-red-400 text-sm">
          <p>Failed to load alignment data</p>
          <button 
            onClick={fetchAlignmentData}
            className="mt-2 text-xs text-yellow-400 hover:text-yellow-300 underline"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

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
                Earn points by completing tasks. Higher-priority tasks aligned with your most important goals earn more points.
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
            {alignmentData.rolling_weekly_score}
          </div>
          <div className="text-sm text-gray-400">
            Weekly Alignment Score
          </div>
        </div>
      </div>

      {/* Goal Status and Progress */}
      <div className="space-y-3">
        {alignmentData.has_goal_set ? (
          <>
            {/* Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Monthly Progress</span>
                <span className="text-yellow-400">{Math.round(progressPercentage)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-yellow-500 to-yellow-400 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{alignmentData.monthly_score} points</span>
                <span>{alignmentData.monthly_goal} goal</span>
              </div>
            </div>
          </>
        ) : (
          /* Call-to-Action for Setting Goal */
          <div className="text-center">
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
          </div>
        )}
      </div>
    </div>
  );
};

export default AlignmentScore;