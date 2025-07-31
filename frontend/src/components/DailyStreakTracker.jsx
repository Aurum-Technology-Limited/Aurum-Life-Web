import React, { useState, useEffect } from 'react';
import { LightningBoltIcon, TrendingUpIcon, CalendarIcon } from '@heroicons/react/outline';
import DailyReflectionModal from './DailyReflectionModal';

const DailyStreakTracker = ({ showReflectionPrompt = true }) => {
  const [streak, setStreak] = useState(0);
  const [shouldShowPrompt, setShouldShowPrompt] = useState(false);
  const [showReflectionModal, setShowReflectionModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStreakData();
    
    if (showReflectionPrompt) {
      checkDailyPrompt();
    }
  }, [showReflectionPrompt]);

  const fetchStreakData = async () => {
    try {
      setLoading(true);
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');

      if (!token) return;

      const response = await fetch(`${BACKEND_URL}/api/ai/daily-streak`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStreak(data.daily_streak || 0);
      } else {
        console.error('Failed to fetch streak data');
      }
    } catch (err) {
      console.error('Error fetching streak:', err);
      setError('Failed to load streak data');
    } finally {
      setLoading(false);
    }
  };

  const checkDailyPrompt = async () => {
    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');

      if (!token) return;

      const response = await fetch(`${BACKEND_URL}/api/ai/should-show-daily-prompt`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setShouldShowPrompt(data.should_show_prompt || false);
      }
    } catch (err) {
      console.error('Error checking daily prompt:', err);
    }
  };

  const handleReflectionSaved = () => {
    // Refresh streak data
    fetchStreakData();
    setShouldShowPrompt(false);
    setShowReflectionModal(false);
  };

  const getStreakMessage = () => {
    if (streak === 0) {
      return "Start your reflection journey today!";
    } else if (streak === 1) {
      return "Great start! Keep the momentum going.";
    } else if (streak < 7) {
      return `${streak} days strong! You're building a great habit.`;
    } else if (streak < 30) {
      return `Amazing ${streak}-day streak! You're crushing it!`;
    } else {
      return `Incredible ${streak}-day streak! You're a reflection master!`;
    }
  };

  const getStreakColor = () => {
    if (streak === 0) return 'text-gray-400';
    if (streak < 7) return 'text-blue-400';
    if (streak < 30) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getStreakIcon = () => {
    if (streak === 0) return '🌱';
    if (streak < 7) return '🔥';
    if (streak < 30) return '⚡';
    return '🏆';
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <LightningBoltIcon className="h-5 w-5 text-yellow-400 animate-pulse" />
          <span className="text-gray-300">Loading streak...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <LightningBoltIcon className={`h-6 w-6 ${getStreakColor()}`} />
            <h3 className="text-lg font-semibold text-white">Daily Streak</h3>
          </div>
        </div>

        {/* Streak Display */}
        <div className="text-center mb-4">
          <div className="text-4xl mb-2">{getStreakIcon()}</div>
          <div className={`text-3xl font-bold ${getStreakColor()}`}>
            {streak}
          </div>
          <div className="text-sm text-gray-400 mb-2">
            {streak === 0 || streak === 1 ? 'day' : 'days'}
          </div>
          <p className="text-sm text-gray-300">
            {getStreakMessage()}
          </p>
        </div>

        {/* Daily Prompt */}
        {shouldShowPrompt && showReflectionPrompt && (
          <div className="mt-4 p-4 bg-yellow-500 bg-opacity-10 border border-yellow-500 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <CalendarIcon className="h-5 w-5 text-yellow-400" />
              <span className="text-yellow-400 font-medium">Daily Check-in</span>
            </div>
            <p className="text-gray-300 text-sm mb-3">
              Ready to reflect on your day and keep your streak going?
            </p>
            <button
              onClick={() => setShowReflectionModal(true)}
              className="w-full bg-gradient-to-r from-yellow-500 to-yellow-600 text-black px-4 py-2 rounded-lg font-medium hover:from-yellow-600 hover:to-yellow-700 transition-colors"
            >
              Start Daily Reflection
            </button>
          </div>
        )}

        {/* Manual Reflection Button */}
        {!shouldShowPrompt && (
          <div className="mt-4">
            <button
              onClick={() => setShowReflectionModal(true)}
              className="w-full bg-gray-700 text-gray-300 px-4 py-2 rounded-lg font-medium hover:bg-gray-600 hover:text-white transition-colors"
            >
              Add Today's Reflection
            </button>
          </div>
        )}

        {/* Streak Milestones */}
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex justify-between text-xs text-gray-400">
            <div className="text-center">
              <div className={streak >= 7 ? 'text-yellow-400' : 'text-gray-500'}>🏅</div>
              <div>7 days</div>
            </div>
            <div className="text-center">
              <div className={streak >= 30 ? 'text-yellow-400' : 'text-gray-500'}>🎯</div>
              <div>30 days</div>
            </div>
            <div className="text-center">
              <div className={streak >= 100 ? 'text-yellow-400' : 'text-gray-500'}>🏆</div>
              <div>100 days</div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-3 bg-red-900 border border-red-700 rounded-lg">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Daily Reflection Modal */}
      <DailyReflectionModal
        isOpen={showReflectionModal}
        onClose={() => setShowReflectionModal(false)}
        onReflectionSaved={handleReflectionSaved}
      />
    </>
  );
};

export default DailyStreakTracker;