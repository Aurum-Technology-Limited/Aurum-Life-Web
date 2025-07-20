import React, { useState, useEffect } from 'react';
import { Calendar, Clock, CheckCircle2, Circle, Plus, Star, AlertCircle } from 'lucide-react';
import { todayAPI, tasksAPI } from '../services/api';

const Today = () => {
  const [todayData, setTodayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadTodayView = async () => {
    try {
      setLoading(true);
      const response = await todayAPI.getTodayView();
      setTodayData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load today\'s data');
      console.error('Error loading today view:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTodayView();
  }, []);

  const handleToggleTask = async (taskId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'completed' ? 'todo' : 'completed';
      await tasksAPI.updateTask(taskId, { status: newStatus });
      loadTodayView(); // Refresh the view
    } catch (err) {
      console.error('Error toggling task:', err);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-16 bg-gray-800 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-900/20 border border-red-600 rounded-lg p-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
            <h3 className="text-lg font-medium text-red-400 mb-2">Error Loading Today's View</h3>
            <p className="text-red-300">{error}</p>
            <button
              onClick={loadTodayView}
              className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!todayData) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto text-center py-12">
          <Calendar className="mx-auto h-16 w-16 text-gray-600 mb-4" />
          <h3 className="text-xl font-medium text-gray-400">No data available for today</h3>
        </div>
      </div>
    );
  }

  const todayTasks = todayData.tasks || [];
  const overdueTasksCount = todayData.overdue_tasks_count || 0;
  const completedToday = todayTasks.filter(task => task.status === 'completed').length;
  const totalTasks = todayTasks.length;

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
                Today's Focus
              </h1>
              <p className="text-gray-400 mt-1">
                {formatDate(new Date().toISOString())}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-2xl font-bold" style={{ color: '#F4B400' }}>
                  {completedToday}/{totalTasks}
                </p>
                <p className="text-sm text-gray-400">Tasks Complete</p>
              </div>
              {overdueTasksCount > 0 && (
                <div className="bg-red-900/20 border border-red-600 rounded-lg px-3 py-2">
                  <p className="text-red-400 font-medium">{overdueTasksCount} Overdue</p>
                </div>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-300"
              style={{
                backgroundColor: '#F4B400',
                width: totalTasks > 0 ? `${(completedToday / totalTasks) * 100}%` : '0%'
              }}
            />
          </div>
        </div>

        {/* Quick Stats */}
        {todayData.stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Active Projects</p>
                  <p className="text-2xl font-bold text-white">{todayData.stats.active_projects}</p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded-lg">
                  <Calendar className="h-6 w-6 text-blue-400" />
                </div>
              </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Areas</p>
                  <p className="text-2xl font-bold text-white">{todayData.stats.total_areas}</p>
                </div>
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <Star className="h-6 w-6 text-green-400" />
                </div>
              </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Focus Time</p>
                  <p className="text-2xl font-bold text-white">
                    {Math.round((completedToday / Math.max(totalTasks, 1)) * 8)}h
                  </p>
                </div>
                <div className="p-3 bg-purple-500/10 rounded-lg">
                  <Clock className="h-6 w-6 text-purple-400" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Today's Tasks */}
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Today's Tasks</h2>
            <button className="flex items-center space-x-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
              <Plus className="h-4 w-4" />
              <span>Add Task</span>
            </button>
          </div>

          {todayTasks.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle2 className="mx-auto h-16 w-16 text-gray-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-400 mb-2">All caught up!</h3>
              <p className="text-gray-500">No tasks scheduled for today. Great job!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {todayTasks.map((task) => (
                <div
                  key={task.id}
                  className={`flex items-center space-x-4 p-4 rounded-lg border transition-all duration-200 hover:shadow-md ${
                    task.status === 'completed'
                      ? 'bg-green-900/10 border-green-700/30'
                      : 'bg-gray-800/50 border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <button
                    onClick={() => handleToggleTask(task.id, task.status)}
                    className="flex-shrink-0"
                  >
                    {task.status === 'completed' ? (
                      <CheckCircle2 className="h-6 w-6 text-green-400" />
                    ) : (
                      <Circle className="h-6 w-6 text-gray-400 hover:text-gray-300" />
                    )}
                  </button>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className={`font-medium truncate ${
                        task.status === 'completed' 
                          ? 'text-gray-400 line-through' 
                          : 'text-white'
                      }`}>
                        {task.title}
                      </h4>
                      <div className="flex items-center space-x-2 ml-4">
                        <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </span>
                        {task.project_name && (
                          <span className="px-2 py-1 text-xs bg-blue-500/10 text-blue-400 rounded-full">
                            {task.project_name}
                          </span>
                        )}
                      </div>
                    </div>
                    {task.description && (
                      <p className={`text-sm mt-1 ${
                        task.status === 'completed' ? 'text-gray-500' : 'text-gray-400'
                      }`}>
                        {task.description}
                      </p>
                    )}
                    {task.due_date && (
                      <div className="flex items-center mt-2 text-xs text-gray-500">
                        <Clock className="h-3 w-3 mr-1" />
                        Due: {new Date(task.due_date).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Today;