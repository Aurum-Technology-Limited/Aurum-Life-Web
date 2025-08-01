import React, { useState, useEffect } from 'react';
import { Sun, Moon, Clock, Settings } from 'lucide-react';
import MorningPlanningPrompt from './MorningPlanningPrompt';
import EveningReflectionPrompt from './EveningReflectionPrompt';
import { api } from '../services/api';

const DailyRitualManager = () => {
  const [showMorningPrompt, setShowMorningPrompt] = useState(false);
  const [showEveningPrompt, setShowEveningPrompt] = useState(false);
  const [ritualSettings, setRitualSettings] = useState({
    morningTime: '08:00',
    eveningTime: '18:00',
    morningEnabled: true,
    eveningEnabled: true
  });
  const [lastMorningPrompt, setLastMorningPrompt] = useState(null);
  const [lastEveningPrompt, setLastEveningPrompt] = useState(null);

  useEffect(() => {
    // Load ritual settings from localStorage
    const savedSettings = localStorage.getItem('aurum_ritual_settings');
    if (savedSettings) {
      setRitualSettings(JSON.parse(savedSettings));
    }

    // Check if prompts should be shown
    checkPromptTiming();

    // Set up interval to check timing every minute
    const interval = setInterval(checkPromptTiming, 60000);
    return () => clearInterval(interval);
  }, []);

  const checkPromptTiming = () => {
    const now = new Date();
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    const currentDate = now.toDateString();

    // Check morning prompt
    if (
      ritualSettings.morningEnabled &&
      currentTime === ritualSettings.morningTime &&
      lastMorningPrompt !== currentDate
    ) {
      console.log('🌅 Triggering morning planning prompt');
      setShowMorningPrompt(true);
    }

    // Check evening prompt
    if (
      ritualSettings.eveningEnabled &&
      currentTime === ritualSettings.eveningTime &&
      lastEveningPrompt !== currentDate
    ) {
      console.log('🌛 Triggering evening reflection prompt');
      setShowEveningPrompt(true);
    }
  };

  // Manual trigger functions for testing and user-initiated prompts
  const triggerMorningPrompt = () => {
    console.log('🌅 Manually triggering morning planning prompt');
    setShowMorningPrompt(true);
  };

  const triggerEveningPrompt = () => {
    console.log('🌛 Manually triggering evening reflection prompt');
    setShowEveningPrompt(true);
  };

  const handleMorningComplete = (selectedTasks) => {
    console.log('🌅 Morning planning completed:', selectedTasks);
    setShowMorningPrompt(false);
    setLastMorningPrompt(new Date().toDateString());
    localStorage.setItem('aurum_last_morning_prompt', new Date().toDateString());
    
    // TODO: In a full implementation, we could:
    // - Add selected tasks to Today view
    // - Track morning ritual completion
    // - Update user streak
  };

  const handleEveningComplete = (reflectionData) => {
    console.log('🌛 Evening reflection completed:', reflectionData);
    setShowEveningPrompt(false);
    setLastEveningPrompt(new Date().toDateString());
    localStorage.setItem('aurum_last_evening_prompt', new Date().toDateString());
    
    // Update daily streak (this could be handled by the API, but we'll track it here too)
    updateDailyStreak();
  };

  const updateDailyStreak = async () => {
    try {
      // The streak is automatically updated by the backend when a reflection is created
      // But we could add additional client-side tracking here if needed
      console.log('✅ Daily streak updated via reflection submission');
    } catch (err) {
      console.error('Failed to update daily streak:', err);
    }
  };

  const closeMorningPrompt = () => {
    setShowMorningPrompt(false);
    setLastMorningPrompt(new Date().toDateString());
    localStorage.setItem('aurum_last_morning_prompt', new Date().toDateString());
  };

  const closeEveningPrompt = () => {
    setShowEveningPrompt(false);
    setLastEveningPrompt(new Date().toDateString());
    localStorage.setItem('aurum_last_evening_prompt', new Date().toDateString());
  };

  const updateRitualSettings = (newSettings) => {
    setRitualSettings(newSettings);
    localStorage.setItem('aurum_ritual_settings', JSON.stringify(newSettings));
  };

  // Component returns the prompts when they should be shown
  return (
    <>
      {showMorningPrompt && (
        <MorningPlanningPrompt
          onComplete={handleMorningComplete}
          onClose={closeMorningPrompt}
        />
      )}

      {showEveningPrompt && (
        <EveningReflectionPrompt
          onComplete={handleEveningComplete}
          onClose={closeEveningPrompt}
        />
      )}

      {/* Debug/Manual Triggers (can be removed in production) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 right-4 space-y-2 z-40">
          <button
            onClick={triggerMorningPrompt}
            className="flex items-center space-x-2 px-3 py-2 bg-yellow-500 text-black text-sm rounded-lg hover:bg-yellow-600 transition-colors"
            title="Test Morning Prompt"
          >
            <Sun className="w-4 h-4" />
            <span>Morning</span>
          </button>
          <button
            onClick={triggerEveningPrompt}
            className="flex items-center space-x-2 px-3 py-2 bg-purple-500 text-white text-sm rounded-lg hover:bg-purple-600 transition-colors"
            title="Test Evening Prompt"
          >
            <Moon className="w-4 h-4" />
            <span>Evening</span>
          </button>
        </div>
      )}
    </>
  );
};

// Hook for other components to manually trigger rituals
export const useDailyRituals = () => {
  const [manager, setManager] = useState(null);

  return {
    triggerMorningPrompt: () => manager?.triggerMorningPrompt(),
    triggerEveningPrompt: () => manager?.triggerEveningPrompt(),
    setManager
  };
};

export default DailyRitualManager;