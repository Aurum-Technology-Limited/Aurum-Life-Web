import React, { useState, useEffect } from 'react';
import { LightningBoltIcon, CalendarIcon } from '@heroicons/react/outline';

const LoginStreakTracker = () => {
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [loginDays, setLoginDays] = useState(new Set());
  const [monthOffset, setMonthOffset] = useState(0); // 0 = current month, -1 = prev, +1 = next
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLoginStreakData();
    recordTodayLogin();
  }, []);

  const keyFromDate = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).toDateString();

  const fetchLoginStreakData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      // Local persistence for MVP (DB-backed planned)
      const storedLoginDays = localStorage.getItem('login_days');
      const storedStreak = localStorage.getItem('login_streak');
      const storedBest = localStorage.getItem('login_best_streak');
      
      if (storedLoginDays) {
        setLoginDays(new Set(JSON.parse(storedLoginDays)));
      }
      
      if (storedStreak) {
        setStreak(parseInt(storedStreak, 10));
      }

      if (storedBest) {
        setBestStreak(parseInt(storedBest, 10));
      } else {
        // Compute best from history if not stored
        try {
          const arr = storedLoginDays ? JSON.parse(storedLoginDays) : [];
          const best = computeBestStreak(arr);
          setBestStreak(best);
          localStorage.setItem('login_best_streak', String(best));
        } catch {}
      }
      
    } catch (err) {
      console.error('Error fetching login streak:', err);
      setError('Failed to load streak data');
    } finally {
      setLoading(false);
    }
  };

  const computeBestStreak = (dayStrings = []) => {
    const days = dayStrings.map(s => new Date(s)).sort((a,b)=>a-b);
    let best = 0;
    let current = 0;
    let prevDay = null;
    for (const d of days) {
      if (!prevDay) {
        current = 1;
      } else {
        const diff = (new Date(d.getFullYear(), d.getMonth(), d.getDate()) - new Date(prevDay.getFullYear(), prevDay.getMonth(), prevDay.getDate())) / (24*60*60*1000);
        current = (diff === 1) ? current + 1 : 1;
      }
      best = Math.max(best, current);
      prevDay = d;
    }
    return best;
  };

  const recordTodayLogin = () => {
    const today = keyFromDate(new Date());
    const yesterday = keyFromDate(new Date(Date.now() - 24 * 60 * 60 * 1000));
    
    // Get current login days from localStorage
    const storedLoginDays = localStorage.getItem('login_days');
    const currentLoginDays = storedLoginDays ? new Set(JSON.parse(storedLoginDays)) : new Set();
    
    // If today is not already recorded
    if (!currentLoginDays.has(today)) {
      currentLoginDays.add(today);
      
      // Calculate streak
      let newStreak = 1;
      if (currentLoginDays.has(yesterday)) {
        const currentStreak = parseInt(localStorage.getItem('login_streak') || '0', 10);
        newStreak = currentStreak + 1;
      }
      
      // Update state and localStorage
      setLoginDays(currentLoginDays);
      setStreak(newStreak);
      localStorage.setItem('login_days', JSON.stringify([...currentLoginDays]));
      localStorage.setItem('login_streak', newStreak.toString());
      
      const prevBest = parseInt(localStorage.getItem('login_best_streak') || '0', 10);
      const nextBest = Math.max(prevBest, newStreak);
      setBestStreak(nextBest);
      localStorage.setItem('login_best_streak', String(nextBest));
    }
  };

  const getMonthRef = () => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth() + monthOffset, 1);
  };

  const getMonthDays = () => {
    const ref = getMonthRef();
    const year = ref.getFullYear();
    const month = ref.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDayOfWeek = firstDay.getDay();
    const days = [];
    for (let i = 0; i < startDayOfWeek; i++) days.push(null);
    for (let day = 1; day <= lastDay.getDate(); day++) {
      const date = new Date(year, month, day);
      days.push(date);
    }
    return days;
  };

  const isLoginDay = (date) => {
    if (!date) return false;
    return loginDays.has(keyFromDate(date));
  };

  const isToday = (date) => {
    if (!date) return false;
    return keyFromDate(date) === keyFromDate(new Date());
  };

  const isFutureDay = (date) => {
    if (!date) return false;
    const today = new Date();
    today.setHours(0,0,0,0);
    const d = new Date(date);
    d.setHours(0,0,0,0);
    return d > today;
  };

  const monthDays = getMonthDays();
  const monthName = getMonthRef().toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  const canGoNext = monthOffset < 0; // only allow navigating up to current month (no future)

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
          <p className="text-xs text-gray-400">{streak === 1 ? 'day' : 'days'} • Best: {bestStreak}</p>
        </div>
      </div>

      {/* Calendar View */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CalendarIcon className="h-4 w-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-300">{monthName}</span>
          </div>
          <div className="flex items-center space-x-2">
            <button className="text-xs text-gray-300 hover:text-white px-2 py-1 rounded border border-gray-600"
              onClick={() => setMonthOffset(o => o - 1)}>
              ◀ Prev
            </button>
            <button className={`text-xs px-2 py-1 rounded border ${canGoNext ? 'text-gray-300 border-gray-600 hover:text-white' : 'text-gray-600 border-gray-700 cursor-not-allowed'}`}
              onClick={() => canGoNext && setMonthOffset(o => o + 1)}
              disabled={!canGoNext}>
              Next ▶
            </button>
          </div>
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
                    w-6 h-6 rounded-full text-xs flex items-center justify-center font-medium transition-colors
                    ${isLoginDay(date) 
                      ? 'bg-yellow-400 text-black font-bold shadow-lg' 
                      : isToday(date)
                      ? 'bg-gray-600 text-white border-2 border-yellow-400'
                      : isFutureDay(date) || !isLoginDay(date)
                      ? 'bg-gray-700 text-gray-500'
                      : 'bg-gray-700 text-gray-400'
                    }
                  `}
                  title={
                    isLoginDay(date) 
                      ? `✅ Logged in on ${date.toLocaleDateString()}` 
                      : isToday(date)
                      ? `Today - ${date.toLocaleDateString()}`
                      : isFutureDay(date)
                      ? `Future day - ${date.toLocaleDateString()}`
                      : `Missed day - ${date.toLocaleDateString()}`
                  }
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
            <div className="w-3 h-3 rounded-full border-2 border-yellow-400 bg-gray-600"></div>
            <span>Today</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-gray-700"></div>
            <span>Missed/Future</span>
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