import React, { useState, useEffect } from 'react';
import { Heart, Play, Pause, RotateCcw, Volume2, Clock } from 'lucide-react';

const MeditationSession = ({ session, onStart }) => (
  <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group hover:scale-105">
    <div className="flex items-center justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">{session.title}</h3>
        <p className="text-sm text-gray-400">{session.description}</p>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-yellow-400">{session.duration} min</p>
        <p className="text-xs text-gray-500">{session.category}</p>
      </div>
    </div>
    
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <span className="text-xs text-gray-400">{session.instructor}</span>
      </div>
      <button
        onClick={() => onStart(session)}
        className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 hover:scale-105"
        style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
      >
        <Play size={16} />
        <span>Start</span>
      </button>
    </div>
  </div>
);

const Timer = ({ duration, isActive, onToggle, onReset }) => {
  const [timeLeft, setTimeLeft] = useState(duration * 60);
  
  useEffect(() => {
    let interval = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (!isActive && timeLeft !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isActive, timeLeft]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercentage = ((duration * 60 - timeLeft) / (duration * 60)) * 100;

  return (
    <div className="text-center">
      <div className="relative w-64 h-64 mx-auto mb-8">
        <svg className="w-64 h-64 transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="#374151"
            strokeWidth="3"
            fill="transparent"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="#F4B400"
            strokeWidth="3"
            fill="transparent"
            strokeLinecap="round"
            strokeDasharray={283}
            strokeDashoffset={283 - (283 * progressPercentage) / 100}
            className="transition-all duration-1000 ease-in-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-4xl font-bold text-white">{formatTime(timeLeft)}</span>
        </div>
      </div>
      
      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={onReset}
          className="p-3 rounded-full bg-gray-800 hover:bg-gray-700 transition-colors"
        >
          <RotateCcw size={20} className="text-gray-400" />
        </button>
        <button
          onClick={onToggle}
          className="p-4 rounded-full transition-all duration-200 hover:scale-105"
          style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
        >
          {isActive ? <Pause size={24} /> : <Play size={24} />}
        </button>
        <button className="p-3 rounded-full bg-gray-800 hover:bg-gray-700 transition-colors">
          <Volume2 size={20} className="text-gray-400" />
        </button>
      </div>
    </div>
  );
};

const Mindfulness = () => {
  const [activeSession, setActiveSession] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [customDuration, setCustomDuration] = useState(10);

  const meditationSessions = [
    {
      id: 1,
      title: 'Morning Awakening',
      description: 'Start your day with clarity and intention',
      duration: 10,
      category: 'morning',
      instructor: 'Sarah Chen'
    },
    {
      id: 2,
      title: 'Stress Relief',
      description: 'Release tension and find your center',
      duration: 15,
      category: 'stress-relief',
      instructor: 'Michael Torres'
    },
    {
      id: 3,
      title: 'Deep Focus',
      description: 'Enhance concentration and mental clarity',
      duration: 20,
      category: 'focus',
      instructor: 'Dr. Lisa Wang'
    },
    {
      id: 4,
      title: 'Evening Wind Down',
      description: 'Peaceful transition into restful sleep',
      duration: 12,
      category: 'evening',
      instructor: 'James Mitchell'
    },
    {
      id: 5,
      title: 'Gratitude Practice',
      description: 'Cultivate appreciation and positive mindset',
      duration: 8,
      category: 'gratitude',
      instructor: 'Maria Rodriguez'
    },
    {
      id: 6,
      title: 'Body Scan Meditation',
      description: 'Connect with your physical sensations',
      duration: 25,
      category: 'body-awareness',
      instructor: 'David Kim'
    }
  ];

  const handleStartSession = (session) => {
    setActiveSession(session);
    setIsPlaying(false);
  };

  const handleCustomTimer = () => {
    setActiveSession({
      id: 'custom',
      title: 'Custom Timer',
      description: 'Personal meditation session',
      duration: customDuration
    });
    setIsPlaying(false);
  };

  const handleTogglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    // Timer will reset automatically via the Timer component
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white mb-2">Mindfulness & Meditation</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Find peace, reduce stress, and cultivate awareness through guided meditation and mindfulness practices
        </p>
      </div>

      {/* Active Session */}
      {activeSession && (
        <div className="p-8 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-2">{activeSession.title}</h2>
            <p className="text-gray-400">{activeSession.description}</p>
          </div>
          
          <Timer
            duration={activeSession.duration}
            isActive={isPlaying}
            onToggle={handleTogglePlayback}
            onReset={handleReset}
          />
        </div>
      )}

      {/* Quick Timer */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h2 className="text-xl font-bold text-white mb-4">Quick Timer</h2>
        <div className="flex items-center space-x-4">
          <label className="text-gray-300">Duration:</label>
          <input
            type="range"
            min="5"
            max="60"
            value={customDuration}
            onChange={(e) => setCustomDuration(parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #F4B400 0%, #F4B400 ${((customDuration - 5) / 55) * 100}%, #374151 ${((customDuration - 5) / 55) * 100}%, #374151 100%)`
            }}
          />
          <span className="text-white font-medium w-12">{customDuration}m</span>
          <button
            onClick={handleCustomTimer}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
          >
            <Clock size={16} />
            <span>Start</span>
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Heart size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">127</h3>
              <p className="text-sm text-gray-400">Sessions Completed</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Clock size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">18.5</h3>
              <p className="text-sm text-gray-400">Hours This Month</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Play size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">15</h3>
              <p className="text-sm text-gray-400">Day Streak</p>
            </div>
          </div>
        </div>
      </div>

      {/* Guided Sessions */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6">Guided Sessions</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {meditationSessions.map((session) => (
            <MeditationSession
              key={session.id}
              session={session}
              onStart={handleStartSession}
            />
          ))}
        </div>
      </div>

      {/* Tips */}
      <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
        <h2 className="text-xl font-bold text-white mb-4">Mindfulness Tips</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-gray-800/50">
            <h3 className="font-semibold text-white mb-2">Find Your Space</h3>
            <p className="text-sm text-gray-400">Choose a quiet, comfortable place where you won't be disturbed.</p>
          </div>
          <div className="p-4 rounded-lg bg-gray-800/50">
            <h3 className="font-semibold text-white mb-2">Start Small</h3>
            <p className="text-sm text-gray-400">Begin with just 5-10 minutes and gradually increase duration.</p>
          </div>
          <div className="p-4 rounded-lg bg-gray-800/50">
            <h3 className="font-semibold text-white mb-2">Be Consistent</h3>
            <p className="text-sm text-gray-400">Regular practice is more beneficial than occasional long sessions.</p>
          </div>
          <div className="p-4 rounded-lg bg-gray-800/50">
            <h3 className="font-semibold text-white mb-2">Don't Judge</h3>
            <p className="text-sm text-gray-400">Accept wandering thoughts without judgment and gently return focus.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Mindfulness;