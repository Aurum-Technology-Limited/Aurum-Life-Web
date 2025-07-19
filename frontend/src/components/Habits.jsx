import React, { useState, useEffect } from 'react';
import { Target, Flame, Calendar, Plus, Check, X, Loader2, AlertCircle } from 'lucide-react';
import { habitsAPI, handleApiError } from '../services/api';

const HabitCard = ({ habit, onToggle, onEdit, loading = false }) => {
  const progressPercentage = habit.progress_percentage || 0;
  
  return (
    <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30 hover:border-yellow-400/30 transition-all duration-300 group">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center cursor-pointer transition-all duration-200 ${
              habit.is_completed_today 
                ? 'bg-yellow-400 border-yellow-400' 
                : 'border-gray-500 hover:border-yellow-400'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => !loading && onToggle(habit.id, !habit.is_completed_today)}
          >
            {loading ? (
              <Loader2 size={12} className="animate-spin text-gray-400" />
            ) : habit.is_completed_today ? (
              <Check size={14} style={{ color: '#0B0D14' }} />
            ) : null}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{habit.name}</h3>
            <p className="text-sm text-gray-400">{habit.description}</p>
          </div>
        </div>
        <button
          onClick={() => onEdit(habit)}
          className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
          disabled={loading}
        >
          <Target size={16} className="text-gray-400" />
        </button>
      </div>
      
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>Progress</span>
          <span>{habit.current_streak} / {habit.target_days} days</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div 
            className="h-3 rounded-full transition-all duration-500"
            style={{ 
              backgroundColor: '#F4B400',
              width: `${Math.min(progressPercentage, 100)}%`
            }}
          />
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Flame size={16} className="text-orange-400" />
          <span className="text-sm font-medium text-white">{habit.current_streak} day streak</span>
        </div>
        <span className="text-xs text-gray-500 capitalize">{habit.category}</span>
      </div>
    </div>
  );
};

const HabitModal = ({ habit, isOpen, onClose, onSave, loading = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_days: 30,
    category: 'health'
  });

  useEffect(() => {
    if (habit) {
      setFormData({
        name: habit.name,
        description: habit.description,
        target_days: habit.target_days,
        category: habit.category
      });
    } else {
      setFormData({
        name: '',
        description: '',
        target_days: 30,
        category: 'health'
      });
    }
  }, [habit, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md border border-gray-800">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">
            {habit ? 'Edit Habit' : 'Create New Habit'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
            disabled={loading}
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Habit Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              required
              disabled={loading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              rows="3"
              disabled={loading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Target Days
            </label>
            <input
              type="number"
              value={formData.target_days}
              onChange={(e) => setFormData({ ...formData, target_days: parseInt(e.target.value) })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              min="1"
              required
              disabled={loading}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:border-yellow-400 focus:outline-none transition-colors"
              disabled={loading}
            >
              <option value="health">Health</option>
              <option value="mindfulness">Mindfulness</option>
              <option value="learning">Learning</option>
              <option value="reflection">Reflection</option>
              <option value="productivity">Productivity</option>
            </select>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 px-4 rounded-lg border border-gray-700 text-gray-300 hover:bg-gray-800 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 hover:scale-105 flex items-center justify-center space-x-2"
              style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
              disabled={loading}
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <span>{habit ? 'Update' : 'Create'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Habits = () => {
  const [habits, setHabits] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingHabit, setEditingHabit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHabits();
  }, []);

  const fetchHabits = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await habitsAPI.getHabits();
      setHabits(response.data);
    } catch (err) {
      setError(handleApiError(err, 'Failed to load habits'));
    } finally {
      setLoading(false);
    }
  };

  const handleToggleHabit = async (habitId, completed) => {
    try {
      setActionLoading(habitId);
      
      await habitsAPI.toggleHabit(habitId, completed);
      
      // Update local state optimistically
      setHabits(prev => prev.map(habit => 
        habit.id === habitId 
          ? { 
              ...habit, 
              is_completed_today: completed,
              current_streak: completed ? habit.current_streak + 1 : Math.max(0, habit.current_streak - 1),
              progress_percentage: ((completed ? habit.current_streak + 1 : Math.max(0, habit.current_streak - 1)) / habit.target_days) * 100
            }
          : habit
      ));
    } catch (err) {
      setError(handleApiError(err, 'Failed to update habit'));
    } finally {
      setActionLoading(null);
    }
  };

  const handleEditHabit = (habit) => {
    setEditingHabit(habit);
    setModalOpen(true);
  };

  const handleCreateHabit = () => {
    setEditingHabit(null);
    setModalOpen(true);
  };

  const handleSaveHabit = async (formData) => {
    try {
      setModalLoading(true);
      
      if (editingHabit) {
        await habitsAPI.updateHabit(editingHabit.id, formData);
        // Update local state
        setHabits(prev => prev.map(habit =>
          habit.id === editingHabit.id
            ? { ...habit, ...formData }
            : habit
        ));
      } else {
        const response = await habitsAPI.createHabit(formData);
        // Add to local state
        const newHabit = {
          ...response.data,
          progress_percentage: 0
        };
        setHabits(prev => [...prev, newHabit]);
      }
      
      setModalOpen(false);
      setEditingHabit(null);
    } catch (err) {
      setError(handleApiError(err, editingHabit ? 'Failed to update habit' : 'Failed to create habit'));
    } finally {
      setModalLoading(false);
    }
  };

  const completedCount = habits.filter(h => h.is_completed_today).length;
  const averageStreak = habits.length > 0 ? Math.round(habits.reduce((acc, h) => acc + h.current_streak, 0) / habits.length) : 0;

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center py-12">
          <Loader2 size={48} className="animate-spin text-yellow-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Daily Habits</h1>
          <p className="text-gray-400">Build consistency and track your daily routines</p>
        </div>
        <button
          onClick={handleCreateHabit}
          className="flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
          style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
        >
          <Plus size={20} />
          <span>Add Habit</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center space-x-2">
          <AlertCircle size={20} className="text-red-400" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={fetchHabits}
            className="ml-auto px-3 py-1 rounded bg-red-500 hover:bg-red-600 text-white text-sm transition-colors"
          >
            Retry
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Target size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{completedCount}/{habits.length}</h3>
              <p className="text-sm text-gray-400">Today's Progress</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Flame size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{averageStreak}</h3>
              <p className="text-sm text-gray-400">Average Streak</p>
            </div>
          </div>
        </div>
        
        <div className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-yellow-400 flex items-center justify-center">
              <Calendar size={20} style={{ color: '#0B0D14' }} />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{habits.length}</h3>
              <p className="text-sm text-gray-400">Active Habits</p>
            </div>
          </div>
        </div>
      </div>

      {/* Habits Grid */}
      {habits.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {habits.map((habit) => (
            <HabitCard
              key={habit.id}
              habit={habit}
              onToggle={handleToggleHabit}
              onEdit={handleEditHabit}
              loading={actionLoading === habit.id}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-lg bg-yellow-400/20 flex items-center justify-center mx-auto mb-4">
            <Target size={32} className="text-yellow-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">No habits yet</h3>
          <p className="text-gray-400 mb-6">Create your first habit to start building consistency</p>
          <button
            onClick={handleCreateHabit}
            className="px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
          >
            Create Your First Habit
          </button>
        </div>
      )}

      <HabitModal
        habit={editingHabit}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingHabit(null);
        }}
        onSave={handleSaveHabit}
        loading={modalLoading}
      />
    </div>
  );
};

export default Habits;