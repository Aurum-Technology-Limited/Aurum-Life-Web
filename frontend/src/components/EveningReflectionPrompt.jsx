import React, { useState } from 'react';
import { Moon, Star, Send, X, TrendingUp, Heart, Zap, Clock } from 'lucide-react';
import { api } from '../services/api';

const EveningReflectionPrompt = ({ onClose, onComplete }) => {
  const [reflectionData, setReflectionData] = useState({
    reflection_text: '',
    completion_score: '',
    mood: '',
    biggest_accomplishment: '',
    challenges_faced: '',
    tomorrow_focus: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const moodOptions = [
    { value: 'accomplished', label: 'Accomplished', icon: '🎯', color: 'green' },
    { value: 'productive', label: 'Productive', icon: '⚡', color: 'blue' },
    { value: 'peaceful', label: 'Peaceful', icon: '🧘', color: 'purple' },
    { value: 'grateful', label: 'Grateful', icon: '🙏', color: 'yellow' },
    { value: 'challenged', label: 'Challenged', icon: '💪', color: 'orange' },
    { value: 'reflective', label: 'Reflective', icon: '🤔', color: 'indigo' },
    { value: 'tired', label: 'Tired', icon: '😴', color: 'gray' },
    { value: 'excited', label: 'Excited', icon: '🎉', color: 'pink' }
  ];

  const handleInputChange = (field, value) => {
    setReflectionData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setError('');

      // Validate required fields
      if (!reflectionData.reflection_text.trim()) {
        setError('Please write a reflection for today');
        return;
      }

      // Prepare the data - handle empty strings and nulls properly
      const submissionData = {
        reflection_text: reflectionData.reflection_text.trim(),
        completion_score: reflectionData.completion_score && reflectionData.completion_score !== '' 
          ? parseInt(reflectionData.completion_score) 
          : null,
        mood: reflectionData.mood || null,
        biggest_accomplishment: reflectionData.biggest_accomplishment.trim() || null,
        challenges_faced: reflectionData.challenges_faced.trim() || null,
        tomorrow_focus: reflectionData.tomorrow_focus.trim() || null
      };

      console.log('🌛 Submitting evening reflection:', submissionData);

      // Submit the reflection
      const response = await api.post('/ai/daily-reflection', submissionData);
      console.log('🌛 Evening reflection submitted successfully:', response.data);

      onComplete(response.data);
    } catch (err) {
      console.error('🌛 Evening reflection submission failed:', err);
      console.error('🌛 Error response:', err.response?.data);
      console.error('🌛 Submitted data was:', submissionData);
      
      let errorMessage = 'Failed to save reflection. Please try again.';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-400';
    if (score >= 6) return 'text-yellow-400';
    if (score >= 4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getMoodColor = (color) => {
    const colors = {
      green: 'bg-green-500/20 text-green-400 border-green-500/30',
      blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      orange: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      indigo: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
      gray: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      pink: 'bg-pink-500/20 text-pink-400 border-pink-500/30'
    };
    return colors[color] || colors.gray;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-800">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Moon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Evening Reflection</h2>
              <p className="text-gray-400 text-sm">How was your day? Let's reflect and grow.</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Main Reflection */}
          <div>
            <label className="block text-white font-medium mb-2">
              <Star className="w-4 h-4 inline mr-2 text-yellow-400" />
              How was your day? *
            </label>
            <textarea
              value={reflectionData.reflection_text}
              onChange={(e) => handleInputChange('reflection_text', e.target.value)}
              placeholder="Reflect on your day... What happened? How did you feel? What did you learn?"
              className="w-full h-24 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400"
              disabled={submitting}
            />
          </div>

          {/* Completion Score */}
          <div>
            <label className="block text-white font-medium mb-2">
              <TrendingUp className="w-4 h-4 inline mr-2 text-blue-400" />
              Overall Day Score (1-10)
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="1"
                max="10"
                value={reflectionData.completion_score || 5}
                onChange={(e) => handleInputChange('completion_score', e.target.value)}
                className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                disabled={submitting}
              />
              <div className={`text-xl font-bold w-12 text-center ${getScoreColor(reflectionData.completion_score)}`}>
                {reflectionData.completion_score || 5}
              </div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Challenging</span>
              <span>Amazing</span>
            </div>
          </div>

          {/* Mood Selection */}
          <div>
            <label className="block text-white font-medium mb-2">
              <Heart className="w-4 h-4 inline mr-2 text-pink-400" />
              How are you feeling?
            </label>
            <div className="grid grid-cols-4 gap-2">
              {moodOptions.map((mood) => (
                <button
                  key={mood.value}
                  onClick={() => handleInputChange('mood', mood.value)}
                  disabled={submitting}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    reflectionData.mood === mood.value
                      ? getMoodColor(mood.color)
                      : 'border-gray-700 bg-gray-800/50 text-gray-400 hover:border-gray-600'
                  }`}
                >
                  <div className="text-lg mb-1">{mood.icon}</div>
                  <div className="text-xs font-medium">{mood.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Quick Inputs Grid */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-white font-medium mb-2">
                🏆 Biggest Accomplishment
              </label>
              <textarea
                value={reflectionData.biggest_accomplishment}
                onChange={(e) => handleInputChange('biggest_accomplishment', e.target.value)}
                placeholder="What are you most proud of today?"
                className="w-full h-20 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 text-sm"
                disabled={submitting}
              />
            </div>

            <div>
              <label className="block text-white font-medium mb-2">
                💪 Challenges Faced
              </label>
              <textarea
                value={reflectionData.challenges_faced}
                onChange={(e) => handleInputChange('challenges_faced', e.target.value)}
                placeholder="What was difficult? What did you learn?"
                className="w-full h-20 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 text-sm"
                disabled={submitting}
              />
            </div>
          </div>

          {/* Tomorrow Focus */}
          <div>
            <label className="block text-white font-medium mb-2">
              <Clock className="w-4 h-4 inline mr-2 text-green-400" />
              Tomorrow's Focus
            </label>
            <textarea
              value={reflectionData.tomorrow_focus}
              onChange={(e) => handleInputChange('tomorrow_focus', e.target.value)}
              placeholder="What's your main priority for tomorrow?"
              className="w-full h-16 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 text-sm"
              disabled={submitting}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-900/20 border border-red-600 rounded-lg p-3">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between items-center pt-4 border-t border-gray-800">
            <button
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              Skip Tonight
            </button>
            
            <button
              onClick={handleSubmit}
              disabled={submitting || !reflectionData.reflection_text.trim()}
              className="flex items-center space-x-2 px-6 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Complete Reflection</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EveningReflectionPrompt;