import React, { useState, useEffect } from 'react';
import { StarIcon, HeartIcon, LightningBoltIcon, TrendingUpIcon, XIcon } from '@heroicons/react/outline';
import { StarIcon as StarSolidIcon } from '@heroicons/react/solid';

const DailyReflectionModal = ({ isOpen, onClose, onReflectionSaved }) => {
  const [reflectionData, setReflectionData] = useState({
    reflection_text: '',
    completion_score: 0,
    mood: '',
    biggest_accomplishment: '',
    challenges_faced: '',
    tomorrow_focus: ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [currentStreak, setCurrentStreak] = useState(0);

  const moods = [
    { value: 'excellent', label: 'Excellent', icon: '🚀', color: 'text-green-400' },
    { value: 'good', label: 'Good', icon: '😊', color: 'text-blue-400' },
    { value: 'okay', label: 'Okay', icon: '😐', color: 'text-yellow-400' },
    { value: 'challenging', label: 'Challenging', icon: '😓', color: 'text-orange-400' },
    { value: 'difficult', label: 'Difficult', icon: '😔', color: 'text-red-400' }
  ];

  useEffect(() => {
    if (isOpen) {
      fetchCurrentStreak();
    }
  }, [isOpen]);

  const fetchCurrentStreak = async () => {
    try {
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
        setCurrentStreak(data.daily_streak || 0);
      }
    } catch (err) {
      console.error('Error fetching streak:', err);
    }
  };

  const handleInputChange = (field, value) => {
    setReflectionData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleScoreClick = (score) => {
    setReflectionData(prev => ({
      ...prev,
      completion_score: score
    }));
  };

  const handleMoodSelect = (mood) => {
    setReflectionData(prev => ({
      ...prev,
      mood: mood
    }));
  };

  const handleSave = async () => {
    if (!reflectionData.reflection_text.trim()) {
      setError('Please share at least one reflection');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');

      if (!token) {
        setError('Authentication required');
        return;
      }

      const response = await fetch(`${BACKEND_URL}/api/ai/daily-reflection`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reflectionData)
      });

      if (response.ok) {
        const savedReflection = await response.json();
        
        // Call parent callback
        if (onReflectionSaved) {
          onReflectionSaved(savedReflection);
        }
        
        // Close modal
        onClose();
        
        // Reset form
        setReflectionData({
          reflection_text: '',
          completion_score: 0,
          mood: '',
          biggest_accomplishment: '',
          challenges_faced: '',
          tomorrow_focus: ''
        });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to save reflection');
      }
    } catch (err) {
      console.error('Error saving reflection:', err);
      setError('Network error occurred');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <HeartIcon className="h-6 w-6 text-yellow-400" />
              <h2 className="text-xl font-semibold text-white">Daily Reflection</h2>
            </div>
            <div className="flex items-center space-x-4">
              {/* Streak Display */}
              <div className="flex items-center space-x-2 text-yellow-400">
                <LightningBoltIcon className="h-5 w-5" />
                <span className="text-sm font-medium">{currentStreak} day streak</span>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white"
              >
                <XIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
          <p className="text-gray-300 mt-2">
            Take a moment to reflect on your day and celebrate your progress
          </p>
        </div>

        {/* Content */}
        <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Main Reflection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              What was your biggest accomplishment today? <span className="text-red-400">*</span>
            </label>
            <textarea
              value={reflectionData.reflection_text}
              onChange={(e) => handleInputChange('reflection_text', e.target.value)}
              placeholder="Share what you're proud of, no matter how small..."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              rows={3}
            />
          </div>

          {/* Completion Score */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              How would you rate your day overall?
            </label>
            <div className="flex items-center space-x-2">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((score) => (
                <button
                  key={score}
                  onClick={() => handleScoreClick(score)}
                  className={`p-2 rounded-lg transition-colors ${
                    reflectionData.completion_score >= score
                      ? 'text-yellow-400'
                      : 'text-gray-600 hover:text-gray-400'
                  }`}
                >
                  <StarSolidIcon className="h-5 w-5" />
                </button>
              ))}
              <span className="ml-3 text-sm text-gray-400">
                {reflectionData.completion_score > 0 && `${reflectionData.completion_score}/10`}
              </span>
            </div>
          </div>

          {/* Mood Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              How are you feeling?
            </label>
            <div className="grid grid-cols-5 gap-2">
              {moods.map((moodOption) => (
                <button
                  key={moodOption.value}
                  onClick={() => handleMoodSelect(moodOption.value)}
                  className={`p-3 rounded-lg border transition-colors ${
                    reflectionData.mood === moodOption.value
                      ? 'border-yellow-500 bg-yellow-500 bg-opacity-10'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-2xl mb-1">{moodOption.icon}</div>
                    <div className={`text-xs ${
                      reflectionData.mood === moodOption.value 
                        ? 'text-yellow-400' 
                        : 'text-gray-400'
                    }`}>
                      {moodOption.label}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Additional Reflections */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                What challenges did you face?
              </label>
              <textarea
                value={reflectionData.challenges_faced}
                onChange={(e) => handleInputChange('challenges_faced', e.target.value)}
                placeholder="Any obstacles or difficulties you encountered..."
                className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                rows={2}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                What's your focus for tomorrow?
              </label>
              <textarea
                value={reflectionData.tomorrow_focus}
                onChange={(e) => handleInputChange('tomorrow_focus', e.target.value)}
                placeholder="What do you want to prioritize tomorrow..."
                className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                rows={2}
              />
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-900 border border-red-700 rounded-lg">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-700 bg-gray-900">
          <div className="flex items-center justify-between">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !reflectionData.reflection_text.trim()}
              className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-black px-6 py-2 rounded-lg font-medium hover:from-yellow-600 hover:to-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></div>
                  <span>Saving...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <HeartIcon className="h-4 w-4" />
                  <span>Save Reflection</span>
                </div>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailyReflectionModal;