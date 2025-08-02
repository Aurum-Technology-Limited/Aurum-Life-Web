import React, { useState } from 'react';
import { X, Moon, Save } from 'lucide-react';
import { api } from '../services/api';

const MorningReflection = ({ onClose, onComplete }) => {
  // Sleep-focused state
  const [sleepQuality, setSleepQuality] = useState(5);
  const [selectedFeeling, setSelectedFeeling] = useState('');
  const [sleepHours, setSleepHours] = useState('');
  const [sleepInfluences, setSleepInfluences] = useState('');
  const [todayIntention, setTodayIntention] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Sleep-focused feelings
  const sleepFeelings = [
    'Refreshed',
    'Groggy', 
    'Tired',
    'Well-Rested',
    'Restless',
    'Energized',
    'Sleepy',
    'Alert'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedFeeling.trim()) {
      setError('Please select how you\'re feeling this morning');
      return;
    }
    
    if (!sleepHours.trim()) {
      setError('Please enter how many hours you slept');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const reflectionData = {
        date: new Date().toISOString(),
        sleep_quality: sleepQuality,
        feeling: selectedFeeling,
        sleep_hours: sleepHours,
        sleep_influences: sleepInfluences.trim(),
        today_intention: todayIntention.trim(),
        type: 'morning_sleep_reflection'
      };

      // Submit to backend
      const response = await api.post('/sleep-reflections', reflectionData);
      
      console.log('✅ Morning sleep reflection saved:', response.data);
      
      if (onComplete) {
        onComplete(reflectionData);
      }
      
      onClose();
    } catch (err) {
      console.error('Error saving morning reflection:', err);
      setError('Failed to save reflection. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-yellow-500/20 rounded-full">
              <Moon className="h-6 w-6 text-yellow-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Morning Reflection</h2>
              <p className="text-gray-400">How was your night? Let's track your sleep.</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Sleep Quality Rating */}
          <div>
            <label className="block text-lg font-semibold text-white mb-4">
              Sleep Quality (1-10)
            </label>
            <div className="flex items-center space-x-4 mb-3">
              <span className="text-sm text-gray-400 w-16">Restless</span>
              <div className="flex-1 flex items-center space-x-2">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setSleepQuality(value)}
                    className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-semibold transition-colors ${
                      sleepQuality >= value
                        ? 'bg-yellow-500 border-yellow-500 text-black'
                        : 'border-gray-600 text-gray-400 hover:border-gray-500'
                    }`}
                  >
                    {value}
                  </button>
                ))}
              </div>
              <span className="text-sm text-gray-400 w-20">Rejuvenating</span>
            </div>
            <p className="text-center text-yellow-400 font-medium">
              Current Rating: {sleepQuality}/10
            </p>
          </div>

          {/* How are you feeling? */}
          <div>
            <label className="block text-lg font-semibold text-white mb-4">
              How are you feeling this morning?
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {sleepFeelings.map((feeling) => (
                <button
                  key={feeling}
                  type="button"
                  onClick={() => setSelectedFeeling(feeling)}
                  className={`p-3 rounded-lg border-2 text-sm font-medium transition-colors ${
                    selectedFeeling === feeling
                      ? 'bg-yellow-500/20 border-yellow-500 text-yellow-400'
                      : 'border-gray-700 text-gray-300 hover:border-gray-600 hover:bg-gray-800/50'
                  }`}
                >
                  {feeling}
                </button>
              ))}
            </div>
          </div>

          {/* Sleep Hours */}
          <div>
            <label className="block text-lg font-semibold text-white mb-4">
              How many hours did you sleep?
            </label>
            <input
              type="text"
              value={sleepHours}
              onChange={(e) => setSleepHours(e.target.value)}
              placeholder="e.g., 7.5 hours, 8 hours, 6 hours..."
              className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 focus:outline-none"
            />
          </div>

          {/* Sleep Influences */}
          <div>
            <label className="block text-lg font-semibold text-white mb-4">
              What influenced your sleep last night?
            </label>
            <textarea
              value={sleepInfluences}
              onChange={(e) => setSleepInfluences(e.target.value)}
              placeholder="e.g., late coffee, stress, comfortable temperature, good book before bed..."
              rows="4"
              className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 focus:outline-none resize-none"
            />
          </div>

          {/* Today's Intention */}
          <div>
            <label className="block text-lg font-semibold text-white mb-4">
              What is your primary intention for today?
            </label>
            <textarea
              value={todayIntention}
              onChange={(e) => setTodayIntention(e.target.value)}
              placeholder="e.g., Focus on deep work, stay hydrated, be present in meetings..."
              rows="3"
              className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-yellow-400 focus:ring-1 focus:ring-yellow-400 focus:outline-none resize-none"
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4 pt-4 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center space-x-2 bg-yellow-500 hover:bg-yellow-600 disabled:bg-yellow-600 text-black font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  <span>Save Reflection</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MorningReflection;