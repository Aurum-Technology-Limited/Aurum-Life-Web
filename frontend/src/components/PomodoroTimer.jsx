import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Clock, Settings } from 'lucide-react';

const PomodoroTimer = ({ taskName, onSessionComplete }) => {
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState('work'); // 'work', 'short-break', 'long-break'
  const [sessionCount, setSessionCount] = useState(0);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    workDuration: 25,
    shortBreakDuration: 5,
    longBreakDuration: 15,
    sessionsUntilLongBreak: 4
  });
  
  const intervalRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    if (isRunning && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(prevTime => {
          if (prevTime <= 1) {
            handlePhaseComplete();
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);
    } else {
      clearInterval(intervalRef.current);
    }

    return () => clearInterval(intervalRef.current);
  }, [isRunning, timeLeft]);

  useEffect(() => {
    // Update timeLeft when settings change
    if (currentPhase === 'work') {
      setTimeLeft(settings.workDuration * 60);
    } else if (currentPhase === 'short-break') {
      setTimeLeft(settings.shortBreakDuration * 60);
    } else if (currentPhase === 'long-break') {
      setTimeLeft(settings.longBreakDuration * 60);
    }
  }, [settings, currentPhase]);

  const handlePhaseComplete = () => {
    setIsRunning(false);
    
    // Play notification sound
    if (audioRef.current) {
      audioRef.current.play().catch(() => {
        // Fallback notification
        if ('Notification' in window && Notification.permission === 'granted') {
          new Notification('Pomodoro Timer', {
            body: currentPhase === 'work' ? 'Work session complete! Time for a break.' : 'Break time over! Ready to work?',
            icon: '/favicon.ico'
          });
        }
      });
    }

    if (currentPhase === 'work') {
      const newSessionCount = sessionCount + 1;
      setSessionCount(newSessionCount);
      
      // Call completion callback
      if (onSessionComplete) {
        onSessionComplete({
          taskName,
          sessionType: 'work',
          duration: settings.workDuration,
          sessionCount: newSessionCount
        });
      }

      // Determine next phase
      if (newSessionCount % settings.sessionsUntilLongBreak === 0) {
        setCurrentPhase('long-break');
        setTimeLeft(settings.longBreakDuration * 60);
      } else {
        setCurrentPhase('short-break');
        setTimeLeft(settings.shortBreakDuration * 60);
      }
    } else {
      // Break completed, back to work
      setCurrentPhase('work');
      setTimeLeft(settings.workDuration * 60);
    }
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
    
    // Request notification permission on first start
    if (!isRunning && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  };

  const resetTimer = () => {
    setIsRunning(false);
    setCurrentPhase('work');
    setTimeLeft(settings.workDuration * 60);
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getPhaseColor = () => {
    switch (currentPhase) {
      case 'work': return '#F4B400'; // Aurum gold
      case 'short-break': return '#10B981'; // Green
      case 'long-break': return '#3B82F6'; // Blue
      default: return '#F4B400';
    }
  };

  const getPhaseLabel = () => {
    switch (currentPhase) {
      case 'work': return 'Focus Time';
      case 'short-break': return 'Short Break';
      case 'long-break': return 'Long Break';
      default: return 'Focus Time';
    }
  };

  const progress = currentPhase === 'work' 
    ? ((settings.workDuration * 60 - timeLeft) / (settings.workDuration * 60)) * 100
    : currentPhase === 'short-break'
    ? ((settings.shortBreakDuration * 60 - timeLeft) / (settings.shortBreakDuration * 60)) * 100
    : ((settings.longBreakDuration * 60 - timeLeft) / (settings.longBreakDuration * 60)) * 100;

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      {/* Hidden audio for notifications */}
      <audio ref={audioRef} preload="auto">
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmASBzqO1vLNeSsFJHfH8N+QQAoUXrPq66hVFAlFnt7xvWARBz+O1vLMeSwGJXfH8N2QQAoUXrPo7KpVGAlFnt7xvWARBz+O1/LKeSsFJHfH8N6QQgkUXrPn7KpWGAlFnt7xvWAQBz6O1/LKeSwFJHfH8N6QQQoTXrPo7KtVFglFntnsv2AQBz6O2O/LeSsFJHbH8N6QQgkUXrTo7KtWGQlEnt7xvWAQBz6O2O/KeSsFJHbH8N6QQgkUXrPp7KtWGAlEnt7xvWAQBz6O2O/KeSsFJHbI8N2QQgkUXrTo7K1WGAlEnt7xvV0QBz6O2O/KeS0FJHbI8N2QQgkUXrTo7K1WGQlEnt7xvV8QBz6O2O/KeS0FJHbI8N2QQgkVXbPr7KpWGQpFnt7xvV0QBz6O2O/KeS0GI3bH8N2QQgkVX7Dp7K1WGQpFnt7xuV0QBz6O2O/LeS0FI3bI8NyQQgkVX7Dp7K1WGQpFnt7xuV0QBz6O2O/LeS0FI3bH8NyQQgkVX7Dp7K1WGQpFnt7xuV0RBz+O2PPLeS0FI3bH8NyQQQsVX7Dq7K1WGQlFnt7xuV0RBz+O2PPLeS0FI3bI8NuQQgsVX7Dp7K5WGQlFnt7xuV0RBz+P2fPKeS0GI3bI8NuQQgsVX7Dp7a5WGQpFnt7xuV4RBz+P2fPKeS0GI3bI8NuQQgsVX7Dp7a5XGQpFnt7xuV4RBz+P2fPKeS0GI3bI8NuQQgsVX7Dp7a5XGQpFnt7wuF4RBz+P2fPKeS0GI3bI8NyQQgsVX7Do7a5XGQpFnt7wuF4RBz+P2fPLeS4GI3bI8NyQQgsVX7Dp7a5XGQpFnt7wuF4RBz+P2fPLeS4GI3bI8NyQQgsVX7Dp7a5XGQpFnt7yuF4RBz+P2fPLeS0GI3bI8NyQQgsVX7Dpa5XGQpFnt7yuF4RBz+P2fPLeS0GI3bI8NyQQgsVX7Dpa5XGQpFnt7yuF4RBz+P2fPLeS0GI3bI8NyQQgsVX7Dpa5XGQpFnt7yuF4RBz+P2fPLeS0GI3bI8NyQQgsVX7Dpa5XGQpFnt7yuF4RBz+P2fPLeS0GI3bI8NyQQg=" type="audio/wav" />
      </audio>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">{getPhaseLabel()}</span>
          <span className="text-xs px-2 py-1 rounded-full bg-gray-800 text-gray-400">
            Session {sessionCount + 1}
          </span>
        </div>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-1 text-gray-400 hover:text-white rounded transition-colors"
        >
          <Settings className="h-4 w-4" />
        </button>
      </div>

      {/* Timer Display */}
      <div className="text-center mb-4">
        <div 
          className="text-4xl font-bold mb-2"
          style={{ color: getPhaseColor() }}
        >
          {formatTime(timeLeft)}
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-800 rounded-full h-2 mb-2">
          <div
            className="h-2 rounded-full transition-all duration-1000"
            style={{
              backgroundColor: getPhaseColor(),
              width: `${progress}%`
            }}
          />
        </div>

        {taskName && (
          <div className="text-sm text-gray-400 mb-3">
            Working on: <span className="text-white">{taskName}</span>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center space-x-3">
        <button
          onClick={toggleTimer}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:scale-105"
          style={{ backgroundColor: getPhaseColor(), color: '#0B0D14' }}
        >
          {isRunning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          <span>{isRunning ? 'Pause' : 'Start'}</span>
        </button>
        
        <button
          onClick={resetTimer}
          className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          title="Reset Timer"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="mt-4 p-3 bg-gray-800 rounded-lg border border-gray-700">
          <h4 className="text-sm font-medium text-white mb-3">Timer Settings</h4>
          
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block text-gray-400 mb-1">Work Duration (min)</label>
              <input
                type="number"
                value={settings.workDuration}
                onChange={(e) => setSettings({...settings, workDuration: parseInt(e.target.value) || 25})}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-yellow-400"
                min="1"
                max="60"
              />
            </div>
            
            <div>
              <label className="block text-gray-400 mb-1">Short Break (min)</label>
              <input
                type="number"
                value={settings.shortBreakDuration}
                onChange={(e) => setSettings({...settings, shortBreakDuration: parseInt(e.target.value) || 5})}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-yellow-400"
                min="1"
                max="30"
              />
            </div>
            
            <div>
              <label className="block text-gray-400 mb-1">Long Break (min)</label>
              <input
                type="number"
                value={settings.longBreakDuration}
                onChange={(e) => setSettings({...settings, longBreakDuration: parseInt(e.target.value) || 15})}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-yellow-400"
                min="1"
                max="60"
              />
            </div>
            
            <div>
              <label className="block text-gray-400 mb-1">Sessions to Long Break</label>
              <input
                type="number"
                value={settings.sessionsUntilLongBreak}
                onChange={(e) => setSettings({...settings, sessionsUntilLongBreak: parseInt(e.target.value) || 4})}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-1 focus:ring-yellow-400"
                min="2"
                max="10"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PomodoroTimer;