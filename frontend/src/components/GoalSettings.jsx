import React, { useState, useEffect } from 'react';
import { Target, Save, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/BackendAuthContext';
import { alignmentScoreAPI } from '../services/api';

const GoalSettings = () => {
  const { user } = useAuth();
  const [monthlyGoal, setMonthlyGoal] = useState('');
  const [currentGoal, setCurrentGoal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [alignmentData, setAlignmentData] = useState(null);

  useEffect(() => {
    if (user) {
      fetchCurrentGoal();
      fetchAlignmentData();
    }
  }, [user]);

  const fetchCurrentGoal = async () => {
    try {
      // Use centralized API client instead of manual fetch
      const response = await alignmentScoreAPI.getMonthlyGoal();
      const data = response.data;
      const goalValue = data?.monthly_goal || null;
      setCurrentGoal(goalValue);
      setMonthlyGoal(goalValue || '');
    } catch (err) {
      console.error('Error fetching current goal:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlignmentData = async () => {
    try {
      // Use centralized API client instead of manual fetch
      const response = await alignmentScoreAPI.getDashboardData();
      const data = response.data;
      
      // Safe data assignment with defaults
      const safeData = {
        rolling_weekly_score: data?.rolling_weekly_score || 0,
        monthly_score: data?.monthly_score || 0,
        progress_percentage: data?.progress_percentage || 0
      };
      setAlignmentData(safeData);
    } catch (err) {
      console.error('Error fetching alignment data:', err);
    }
  };

  const handleSaveGoal = async () => {
    if (!monthlyGoal || isNaN(monthlyGoal) || parseInt(monthlyGoal) <= 0) {
      setMessage({
        type: 'error',
        text: 'Please enter a valid positive number for your monthly goal.'
      });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      // Use centralized API client instead of manual fetch
      const response = await alignmentScoreAPI.setMonthlyGoal(parseInt(monthlyGoal));
      
      setCurrentGoal(parseInt(monthlyGoal));
      setMessage({
        type: 'success',
        text: `Monthly goal successfully set to ${monthlyGoal} points!`
      });
      
      // Refresh alignment data to show updated progress
      fetchAlignmentData();
    } catch (err) {
      console.error('Error saving goal:', err);
      
      // Handle specific API error types
      let errorMessage = 'Failed to save goal. Please try again.';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message.includes('Authentication failed')) {
        errorMessage = 'Please log in again';
      } else if (err.message.includes('timeout')) {
        errorMessage = 'Request timed out. Please check your connection.';
      }
      
      setMessage({
        type: 'error',
        text: errorMessage
      });
    } finally {
      setSaving(false);
    }
  };

  const getSuggestedGoals = () => {
    // Safe defaults if no alignment data is available
    if (!alignmentData || typeof alignmentData !== 'object') {
      return [100, 300, 500, 1000];
    }
    
    const currentMonthly = alignmentData?.monthly_score || 0;
    const weeklyAvg = alignmentData?.rolling_weekly_score || 0;
    
    // Suggest goals based on current performance with safe calculations
    const conservative = Math.max(100, Math.round(currentMonthly * 1.2));
    const moderate = Math.max(300, Math.round(weeklyAvg * 4.5));
    const ambitious = Math.max(500, Math.round(weeklyAvg * 6));
    const stretch = Math.max(1000, Math.round(weeklyAvg * 8));
    
    // Return unique, sorted values
    const goals = Array.from(new Set([conservative, moderate, ambitious, stretch])).sort((a, b) => a - b);
    return goals.length >= 4 ? goals : [100, 300, 500, 1000];
  };

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-700 rounded w-1/3"></div>
          <div className="h-4 bg-gray-700 rounded w-2/3"></div>
          <div className="h-10 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  const suggestedGoals = getSuggestedGoals();

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
      <div className="flex items-center mb-6">
        <Target className="h-6 w-6 text-yellow-400 mr-3" />
        <div>
          <h2 className="text-xl font-semibold text-white">Monthly Alignment Goals</h2>
          <p className="text-gray-400 text-sm mt-1">
            Set your monthly point target to track progress and stay motivated
          </p>
        </div>
      </div>

      {/* Current Status */}
      {alignmentData && typeof alignmentData === 'object' && (
        <div className="mb-6 p-4 bg-gray-800/50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-300 mb-3">Current Progress</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-yellow-400">
                {alignmentData?.rolling_weekly_score || 0}
              </div>
              <div className="text-xs text-gray-400">Weekly Score</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white">
                {alignmentData?.monthly_score || 0}
              </div>
              <div className="text-xs text-gray-400">Monthly Score</div>
            </div>
            <div>
              <div className="text-lg font-bold text-green-400">
                {alignmentData?.progress_percentage?.toFixed(1) || '0.0'}%
              </div>
              <div className="text-xs text-gray-400">Goal Progress</div>
            </div>
          </div>
        </div>
      )}

      {/* Goal Setting Form */}
      <div className="space-y-4">
        <div>
          <label htmlFor="monthlyGoal" className="block text-sm font-medium text-gray-300 mb-2">
            Monthly Goal (Points)
          </label>
          <div className="flex space-x-3">
            <input
              type="number"
              id="monthlyGoal"
              value={monthlyGoal}
              onChange={(e) => setMonthlyGoal(e.target.value)}
              placeholder="Enter your monthly point goal..."
              className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              min="1"
              step="1"
            />
            <button
              onClick={handleSaveGoal}
              disabled={saving}
              className="px-4 py-2 bg-yellow-500 text-black rounded-lg hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent"></div>
              ) : (
                <Save className="h-4 w-4" />
              )}
              <span>{saving ? 'Saving...' : 'Save Goal'}</span>
            </button>
          </div>
        </div>

        {/* Suggested Goals */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Suggested Goals
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {suggestedGoals && Array.isArray(suggestedGoals) && suggestedGoals.length > 0 ? (
              suggestedGoals.map((goal) => (
                <button
                  key={goal}
                  onClick={() => setMonthlyGoal(goal.toString())}
                  className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition-colors text-sm"
                >
                  {goal} pts
                </button>
              ))
            ) : (
              <div className="col-span-full text-gray-500 text-sm text-center py-2">
                Complete some tasks to see personalized suggestions
              </div>
            )}
          </div>
        </div>

        {/* Status Message */}
        {message && (
          <div className={`flex items-center space-x-2 p-3 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-900/20 border border-green-600 text-green-400' 
              : 'bg-red-900/20 border border-red-600 text-red-400'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <span className="text-sm">{message.text}</span>
          </div>
        )}

        {/* Current Goal Display */}
        {currentGoal && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4 text-yellow-400" />
              <span className="text-sm text-yellow-400">
                Current Monthly Goal: <strong>{currentGoal} points</strong>
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Scoring Information */}
      <div className="mt-6 p-4 bg-gray-800/30 rounded-lg">
        <h4 className="text-sm font-medium text-gray-300 mb-2">How Points Are Earned</h4>
        <div className="text-xs text-gray-400 space-y-1">
          <div>• Base Points: <span className="text-white">+5</span> for any completed task</div>
          <div>• Task Priority: <span className="text-white">+10</span> for high priority tasks</div>
          <div>• Project Priority: <span className="text-white">+15</span> for tasks in high priority projects</div>
          <div>• Area Importance: <span className="text-white">+20</span> for tasks in top importance areas (5/5)</div>
          <div className="pt-2 border-t border-gray-700">
            <strong className="text-yellow-400">Maximum: 50 points</strong> per perfectly aligned task
          </div>
        </div>
      </div>
    </div>
  );
};

export default GoalSettings;