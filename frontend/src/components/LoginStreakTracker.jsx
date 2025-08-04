import React, { useState, useEffect } from 'react';
import { LightningBoltIcon, CalendarIcon } from '@heroicons/react/outline';

const LoginStreakTracker = () => {
  const [streak, setStreak] = useState(0);
  const [loginDays, setLoginDays] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLoginStreakData();
    recordTodayLogin();
  }, []);

  const fetchLoginStreakData = async () => {
    try {
      setLoading(true);
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');

      if (!token) return;

      // For now, we'll use localStorage to track login days and streak
      // In a production system, this would be tracked server-side
      const storedLoginDays = localStorage.getItem('login_days');
      const storedStreak = localStorage.getItem('login_streak');
      
      if (storedLoginDays) {
        setLoginDays(new Set(JSON.parse(storedLoginDays)));
      }
      
      if (storedStreak) {
        setStreak(parseInt(storedStreak, 10));
      }
      
    } catch (err) {
      console.error('Error fetching login streak:', err);
      setError('Failed to load streak data');
    } finally {
      setLoading(false);
    }
  };

  const recordTodayLogin = () => {
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toDateString();
    
    // Get current login days from localStorage
    const storedLoginDays = localStorage.getItem('login_days');
    const currentLoginDays = storedLoginDays ? new Set(JSON.parse(storedLoginDays)) : new Set();
    
    // If today is not already recorded
    if (!currentLoginDays.has(today)) {
      currentLoginDays.add(today);
      
      // Calculate streak
      let newStreak = 1;
      if (currentLoginDays.has(yesterday)) {
        // Continue existing streak
        const currentStreak = parseInt(localStorage.getItem('login_streak') || '0', 10);
        newStreak = currentStreak + 1;
      }
      
      // Update state and localStorage
      setLoginDays(currentLoginDays);
      setStreak(newStreak);
      localStorage.setItem('login_days', JSON.stringify([...currentLoginDays]));
      localStorage.setItem('login_streak', newStreak.toString());
    }
  };

  const getCurrentMonthDays = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    
    // Get first day of month and last day of month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // Get day of week for first day (0 = Sunday, 1 = Monday, etc.)
    const startDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days of the month
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      days.push(date);
    }
    
    return days;
  };

  const isLoginDay = (date) => {
    if (!date) return false;
    return loginDays.has(date.toDateString());
  };

  const isToday = (date) => {
    if (!date) return false;
    return date.toDateString() === new Date().toDateString();
  };

  const isFutureDay = (date) => {
    if (!date) return false;
    return date > new Date();
  };

  const monthDays = getCurrentMonthDays();
  const monthName = new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="bg-yellow-400 rounded-lg p-2">
            <LightningBoltIcon className="h-5 w-5 text-black" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Login Streak</h3>
            <p className="text-sm text-gray-400">Consecutive daily logins</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-yellow-400">
            {loading ? '-' : streak}
          </p>
          <p className="text-xs text-gray-400">{streak === 1 ? 'day' : 'days'}</p>
        </div>
      </div>

      {/* Calendar View */}
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <CalendarIcon className="h-4 w-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">{monthName}</span>
        </div>
        
        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {/* Day headers */}
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="text-xs text-gray-400 text-center py-1">
              {day}
            </div>
          ))}
          
          {/* Calendar days */}
          {monthDays.map((date, index) => (
            <div key={index} className="aspect-square flex items-center justify-center">
              {date && (
                <div 
                  className={`
                    w-6 h-6 rounded-full text-xs flex items-center justify-center
                    ${isLoginDay(date) 
                      ? 'bg-yellow-400 text-black font-semibold' 
                      : isToday(date)
                      ? 'bg-gray-600 text-white border border-gray-500'
                      : 'text-gray-400'
                    }
                  `}
                  title={isLoginDay(date) ? `Logged in on ${date.toLocaleDateString()}` : ''}
                >
                  {date.getDate()}
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-center space-x-4 pt-2 text-xs text-gray-400">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
            <span>Login day</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full border border-gray-500 bg-gray-600"></div>
            <span>Today</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 text-sm text-red-400 text-center">
          {error}
        </div>
      )}
    </div>
  );
};

export default LoginStreakTracker;