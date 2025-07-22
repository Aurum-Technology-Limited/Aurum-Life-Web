import React, { useState, useEffect } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { 
  Calendar, 
  Clock, 
  CheckCircle2, 
  Circle, 
  Plus, 
  Star, 
  AlertCircle, 
  Timer,
  GripVertical,
  X,
  ArrowRight
} from 'lucide-react';
import { todayAPI, tasksAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import PomodoroTimer from './PomodoroTimer';

const DragTaskItem = ({ task, index, moveTask, onToggleComplete, onStartPomodoro, onRemove }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'daily-task',
    item: { id: task.id, index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const [, drop] = useDrop({
    accept: 'daily-task',
    hover: (draggedItem) => {
      if (draggedItem.index !== index) {
        moveTask(draggedItem.index, index);
        draggedItem.index = index;
      }
    },
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10';
      case 'medium': return 'text-yellow-400 bg-yellow-400/10';
      case 'low': return 'text-green-400 bg-green-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return null;
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  return (
    <div
      ref={(node) => drag(drop(node))}
      className={`bg-gray-900/50 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-all duration-200 cursor-move ${
        isDragging ? 'opacity-50' : ''
      } ${task.completed ? 'opacity-60' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <button
            onClick={() => onToggleComplete(task.id, task.completed)}
            className="mt-1 text-yellow-400 hover:text-yellow-300 transition-colors"
          >
            {task.completed ? (
              <CheckCircle2 className="h-5 w-5" />
            ) : (
              <Circle className="h-5 w-5" />
            )}
          </button>
          
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <h4 className={`font-medium ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>
                {task.name}
              </h4>
              <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(task.priority)}`}>
                {task.priority}
              </span>
            </div>
            
            {task.description && (
              <p className={`text-sm ${task.completed ? 'text-gray-600' : 'text-gray-400'} mb-2`}>
                {task.description}
              </p>
            )}
            
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              {task.due_date && (
                <div className="flex items-center space-x-1">
                  <Calendar className="h-3 w-3" />
                  <span>{new Date(task.due_date).toLocaleDateString()}</span>
                  {task.due_time && (
                    <>
                      <Clock className="h-3 w-3 ml-2" />
                      <span>{formatTime(task.due_time)}</span>
                    </>
                  )}
                </div>
              )}
              
              {task.estimated_duration && (
                <div className="flex items-center space-x-1">
                  <Timer className="h-3 w-3" />
                  <span>{task.estimated_duration}min</span>
                </div>
              )}
              
              {task.project_name && (
                <div className="flex items-center space-x-1">
                  <span className="text-blue-400">{task.project_name}</span>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <GripVertical className="h-4 w-4 text-gray-500" />
          {!task.completed && (
            <button
              onClick={() => onStartPomodoro(task)}
              className="p-2 text-gray-400 hover:text-yellow-400 hover:bg-gray-800 rounded-lg transition-colors"
              title="Start Pomodoro"
            >
              <Timer className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={() => onRemove(task.id)}
            className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
            title="Remove from Today"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

const AvailableTaskItem = ({ task, onAdd }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'available-task',
    item: { id: task.id, task },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div
      ref={drag}
      className={`bg-gray-800/50 border border-gray-700 rounded-lg p-3 hover:border-gray-600 transition-all duration-200 cursor-move ${
        isDragging ? 'opacity-50' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <h5 className="text-sm font-medium text-white truncate">{task.name}</h5>
            <div className={`h-2 w-2 rounded-full ${getPriorityColor(task.priority).replace('text-', 'bg-')}`} />
          </div>
          <div className="text-xs text-gray-500">
            {task.project_name && <span>{task.project_name}</span>}
          </div>
        </div>
        <button
          onClick={() => onAdd(task.id)}
          className="p-1 text-gray-400 hover:text-yellow-400 transition-colors"
          title="Add to Today"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

const Today = () => {
  const { onDataMutation } = useDataContext();
  const [todayData, setTodayData] = useState(null);
  const [availableTasks, setAvailableTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAvailable, setShowAvailable] = useState(false);
  const [activePomodoro, setActivePomodoro] = useState(null);

  const loadTodayView = async () => {
    try {
      setLoading(true);
      const [todayResponse, availableResponse] = await Promise.all([
        todayAPI.getTodayView(),
        todayAPI.getAvailableTasks()
      ]);
      setTodayData(todayResponse.data);
      setAvailableTasks(availableResponse.data);
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

  const moveTask = (fromIndex, toIndex) => {
    if (!todayData?.tasks) return;

    const newTasks = [...todayData.tasks];
    const [movedTask] = newTasks.splice(fromIndex, 1);
    newTasks.splice(toIndex, 0, movedTask);

    setTodayData(prev => ({
      ...prev,
      tasks: newTasks
    }));

    // Update order on backend
    const taskIds = newTasks.map(task => task.id);
    todayAPI.reorderDailyTasks(taskIds).catch(err => {
      console.error('Error reordering tasks:', err);
      loadTodayView(); // Revert on error
    });
  };

  const handleToggleTask = async (taskId, currentCompleted) => {
    try {
      const newCompleted = !currentCompleted;
      await tasksAPI.updateTask(taskId, { completed: newCompleted });
      
      // Update local state
      setTodayData(prev => ({
        ...prev,
        tasks: prev.tasks.map(task => 
          task.id === taskId ? { ...task, completed: newCompleted } : task
        ),
        completed_tasks: newCompleted 
          ? prev.completed_tasks + 1 
          : prev.completed_tasks - 1
      }));
      
      onDataMutation('task', 'update', { taskId, completed: newCompleted });
    } catch (err) {
      console.error('Error toggling task:', err);
    }
  };

  const handleAddToToday = async (taskId) => {
    try {
      await todayAPI.addTaskToToday(taskId);
      loadTodayView(); // Refresh to get updated data
      onDataMutation('today', 'add_task', { taskId });
    } catch (err) {
      console.error('Error adding task to today:', err);
    }
  };

  const handleRemoveFromToday = async (taskId) => {
    try {
      await todayAPI.removeTaskFromToday(taskId);
      loadTodayView(); // Refresh to get updated data
      onDataMutation('today', 'remove_task', { taskId });
    } catch (err) {
      console.error('Error removing task from today:', err);
    }
  };

  const handleStartPomodoro = (task) => {
    setActivePomodoro(task);
  };

  const handlePomodoroComplete = (sessionData) => {
    console.log('Pomodoro session completed:', sessionData);
    onDataMutation('pomodoro', 'complete', sessionData);
  };

  const [, drop] = useDrop({
    accept: 'available-task',
    drop: (item) => {
      handleAddToToday(item.id);
    },
  });

  if (loading) {
    return (
      <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-24 bg-gray-800 rounded-lg"></div>
                ))}
              </div>
              <div className="h-80 bg-gray-800 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const completionPercentage = todayData?.total_tasks > 0 
    ? (todayData.completed_tasks / todayData.total_tasks) * 100 
    : 0;

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0B0D14', color: '#ffffff' }}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: '#F4B400' }}>
              Today's Focus
            </h1>
            <p className="text-gray-400 mt-1">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
          
          <button
            onClick={() => setShowAvailable(!showAvailable)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              showAvailable 
                ? 'bg-yellow-500 text-gray-900' 
                : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700'
            }`}
          >
            <Plus className="h-4 w-4" />
            <span>Add Tasks</span>
          </button>
        </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                <span className="text-red-400">{error}</span>
              </div>
            </div>
          )}

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-white">{todayData?.total_tasks || 0}</p>
                  <p className="text-sm text-gray-400">Total Tasks</p>
                </div>
                <Calendar className="h-8 w-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-green-400">{todayData?.completed_tasks || 0}</p>
                  <p className="text-sm text-gray-400">Completed</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-400" />
              </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold" style={{ color: '#F4B400' }}>
                    {Math.round(completionPercentage)}%
                  </p>
                  <p className="text-sm text-gray-400">Progress</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-gray-800 relative">
                  <div
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: `conic-gradient(#F4B400 ${completionPercentage}%, #1F2937 ${completionPercentage}%)`,
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-purple-400">{Math.round((todayData?.estimated_duration || 0) / 60)}h</p>
                  <p className="text-sm text-gray-400">Est. Time</p>
                </div>
                <Clock className="h-8 w-8 text-purple-400" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Today's Tasks */}
            <div className="lg:col-span-2">
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-6">Today's Tasks</h2>
                
                {todayData?.tasks?.length === 0 ? (
                  <div
                    ref={drop}
                    className="text-center py-12 border-2 border-dashed border-gray-700 rounded-lg"
                  >
                    <Calendar className="mx-auto h-16 w-16 text-gray-600 mb-4" />
                    <h3 className="text-lg font-medium text-gray-400 mb-2">No tasks for today</h3>
                    <p className="text-gray-500 mb-4">
                      Drag tasks from the available list or click "Add Tasks" to get started
                    </p>
                    <button
                      onClick={() => setShowAvailable(true)}
                      className="px-4 py-2 rounded-lg font-medium"
                      style={{ backgroundColor: '#F4B400', color: '#0B0D14' }}
                    >
                      Browse Available Tasks
                    </button>
                  </div>
                ) : (
                  <div ref={drop} className="space-y-4">
                    {todayData.tasks.map((task, index) => (
                      <DragTaskItem
                        key={task.id}
                        task={task}
                        index={index}
                        moveTask={moveTask}
                        onToggleComplete={handleToggleTask}
                        onStartPomodoro={handleStartPomodoro}
                        onRemove={handleRemoveFromToday}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Pomodoro Timer & Available Tasks */}
            <div className="space-y-6">
              {/* Pomodoro Timer */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Pomodoro Timer</h3>
                <PomodoroTimer
                  taskName={activePomodoro?.name}
                  onSessionComplete={handlePomodoroComplete}
                />
              </div>

              {/* Available Tasks */}
              {showAvailable && (
                <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Available Tasks</h3>
                    <button
                      onClick={() => setShowAvailable(false)}
                      className="p-1 text-gray-400 hover:text-white rounded"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  
                  {availableTasks.length === 0 ? (
                    <div className="text-center py-8">
                      <CheckCircle2 className="mx-auto h-12 w-12 text-green-400 mb-3" />
                      <p className="text-gray-400">All caught up!</p>
                      <p className="text-sm text-gray-500">No more tasks to add</p>
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {availableTasks.map((task) => (
                        <AvailableTaskItem
                          key={task.id}
                          task={task}
                          onAdd={handleAddToToday}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Today;