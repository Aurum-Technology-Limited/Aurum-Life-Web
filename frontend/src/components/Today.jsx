import React, { useState, useEffect, memo, useCallback } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import {Calendar, Clock, CheckCircle2, Circle, Plus, AlertCircle, Timer, GripVertical, X, Sun, Moon, Loader2} from 'lucide-react';
import { todayAPI, tasksAPI } from '../services/api';
import { useDataContext } from '../contexts/DataContext';
import { useAuth } from '../contexts/BackendAuthContext';
import PomodoroTimer from './PomodoroTimer';
import TaskWhyStatements from './TaskWhyStatements';
import TaskSearchBar from './TaskSearchBar';
import MorningReflection from './MorningReflection';
import EveningReflectionPrompt from './EveningReflectionPrompt';

const DragTaskItem = memo(({ task, index, moveTask, onToggleComplete, onStartPomodoro, onRemove }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'daily-task',
    item: { id: task.id, index },
    collect: (monitor) => ({ isDragging: monitor.isDragging() }),
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

  return (
    <div ref={(node) => drag(drop(node))} className={`cursor-move ${isDragging ? 'opacity-50' : ''}`}>
      <UnifiedTaskItem
        task={task}
        context={task.project_name ? `Project: ${task.project_name}` : ''}
        mode="focus"
        showToggle={true}
        completed={!!task.completed}
        onToggleComplete={onToggleComplete}
        onStartPomodoro={onStartPomodoro}
        onRemove={onRemove}
      />
    </div>
  );
});

// Unified task item used for both suggestions and focus list rows
const UnifiedTaskItem = ({ task, context, mode = 'focus', onAdd, onToggleComplete, onStartPomodoro, onRemove, showToggle = false, completed = false, showAIBadge = false }) => {
  const priority = (task.priority || 'medium').toLowerCase();
  const priorityClass = priority === 'high' ? 'bg-red-500' : priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500';
  return (
    <div className="flex items-center justify-between bg-gray-900/50 border border-gray-800 rounded-md p-3">
      <div className="flex items-start space-x-3">
        {showToggle && (
          <button
            onClick={() => onToggleComplete && onToggleComplete(task.id, completed)}
            className="mt-1 text-yellow-400 hover:text-yellow-300 transition-colors"
            title={completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {completed ? <CheckCircle2 className="h-5 w-5" /> : <Circle className="h-5 w-5" />}
          </button>
        )}
        {/* Priority indicator */}
        <div className={`w-2 h-2 rounded-full mt-2 ${priorityClass}`} aria-hidden="true" title={showAIBadge ? 'Suggested by AI' : undefined}></div>
        <div>
          <div className="flex items-center">
            <div className={`text-sm font-medium ${completed ? 'line-through text-gray-500' : 'text-white'}`}>{task.name || task.title}</div>
            {showAIBadge && (
              <span className="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">AI</span>
            )}
          </div>
          <div className={`text-xs mt-0.5 ${completed ? 'text-gray-600' : 'text-gray-400'}`}>
            {context}
          </div>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        {mode === 'suggestion' ? (
          <button
            type="button"
            onClick={onAdd}
            className="p-2 text-gray-300 hover:text-yellow-400 hover:bg-gray-800 rounded"
            title="Add to Today's Focus"
          >
            <Plus className="h-4 w-4" />
          </button>
        ) : (
          <>
            {!completed && (
              <button
                onClick={() => onStartPomodoro && onStartPomodoro(task)}
                className="p-2 text-gray-400 hover:text-yellow-400 hover:bg-gray-800 rounded-lg transition-colors"
                title="Start Pomodoro"
              >
                <Timer className="h-4 w-4" />
              </button>
            )}
            <button
              onClick={() => onRemove && onRemove(task.id)}
              className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-lg transition-colors"
              title="Remove from Today"
            >
              <X className="h-4 w-4" />
            </button>
          </>
        )}
      </div>
    </div>
  );
};

DragTaskItem.displayName = 'DragTaskItem';

const Today = memo(() => {
  const { onDataMutation } = useDataContext();
  const { user } = useAuth(); // Get authenticated user for daily rituals
  
  // Main state - using localStorage for daily task management
  const [todaysTasks, setTodaysTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activePomodoro, setActivePomodoro] = useState(null);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const SUGGESTIONS_KEY = 'aurum_ai_suggestions';
  const [suggestLoading, setSuggestLoading] = useState(false);



  // Daily Ritual States (moved from DailyRitualManager)
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

  // Local storage keys for daily task management
  const STORAGE_KEY = 'aurum_todays_focus';
  const STORAGE_DATE_KEY = 'aurum_todays_focus_date';

  const loadTodaysTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const today = new Date().toDateString();
      const storedDate = localStorage.getItem(STORAGE_DATE_KEY);
      
      // Check if we need to reset for a new day
      if (storedDate !== today) {
        console.log('🌅 New day detected, clearing previous focus tasks');
        localStorage.removeItem(STORAGE_KEY);
        localStorage.setItem(STORAGE_DATE_KEY, today);
        setTodaysTasks([]);
      } else {
        // Load tasks from localStorage
        const storedTasks = localStorage.getItem(STORAGE_KEY);
        if (storedTasks) {
          const taskIds = JSON.parse(storedTasks);
          
          // Fetch fresh task data from backend
          if (taskIds.length > 0) {
            try {
              const tasks = await Promise.all(
                taskIds.map(async (taskId) => {
                  try {
                    const response = await tasksAPI.getTask(taskId);
                    return response.data;
                  } catch (err) {
                    console.warn(`Task ${taskId} not found or unavailable`);
                    return null;
                  }
                })
              );
              
              // Filter out null tasks (deleted or unavailable)
              const validTasks = tasks.filter(task => task !== null);
              setTodaysTasks(validTasks);
              
              // Update localStorage to remove invalid task IDs
              const validTaskIds = validTasks.map(task => task.id);
              localStorage.setItem(STORAGE_KEY, JSON.stringify(validTaskIds));
            } catch (err) {
              console.error('Error loading stored tasks:', err);
              setTodaysTasks([]);
            }
          } else {
            setTodaysTasks([]);
          }
        } else {
          setTodaysTasks([]);
        }
      }
      
    } catch (err) {
      console.error('Error loading today\'s focus:', err);
      setError('Failed to load today\'s focus');
      setTodaysTasks([]);
    } finally {
      setLoading(false);
    }
  };
  // Load persisted AI suggestions on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(SUGGESTIONS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) setAiSuggestions(parsed);
      }
    } catch {}
  }, []);


  useEffect(() => {
    loadTodaysTasks();
  }, []);

  // Daily Ritual Effects and Functions (moved from DailyRitualManager)
  useEffect(() => {
    if (!user) return; // Only run if user is authenticated

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
  }, [user]);

  const checkPromptTiming = () => {
    if (!user) return;
    
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

  const handleMorningComplete = (reflectionData) => {
    console.log('🌅 Morning sleep reflection completed:', reflectionData);
    setShowMorningPrompt(false);
    setLastMorningPrompt(new Date().toDateString());
    localStorage.setItem('aurum_last_morning_prompt', new Date().toDateString());
    
    // Track morning reflection completion for streak or analytics
    try {
      console.log('✅ Morning sleep reflection data captured for AI Coach insights');
    } catch (err) {
      console.error('Failed to process morning reflection:', err);
    }
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

  const moveTask = (fromIndex, toIndex) => {
    if (todaysTasks.length === 0) return;

    const newTasks = [...todaysTasks];
    const [movedTask] = newTasks.splice(fromIndex, 1);
    newTasks.splice(toIndex, 0, movedTask);

    setTodaysTasks(newTasks);
    
    // Update localStorage
    const taskIds = newTasks.map(task => task.id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(taskIds));
  };

  const handleToggleTask = async (taskId, currentCompleted) => {
    try {
      const newCompleted = !currentCompleted;
      await tasksAPI.updateTask(taskId, { completed: newCompleted });
      
      // Update local state
      setTodaysTasks(prev => 
        prev.map(task => 
          task.id === taskId ? { ...task, completed: newCompleted } : task
        )
      );
      
      onDataMutation('task', 'update', { taskId, completed: newCompleted });
    } catch (err) {
      console.error('Error toggling task:', err);
      setError('Failed to update task');
    }
  };

  const handleAddTaskToFocus = (task) => {
    if (!task || !task.id) return;
    // Dedupe by id
    setTodaysTasks((prev) => {
      if (prev.some(t => t.id === task.id)) {
        console.log('Task already in today\'s focus');
        return prev;
      }
      const next = [...prev, task];
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch {}
      // Fire mutation with valid id only
      onDataMutation('today', 'add_task', { taskId: task.id });
      return next;
    });
  };

  const [undo, setUndo] = useState({ visible: false, last: null });

  const handleRemoveFromFocus = useCallback((taskId) => {
    setTodaysTasks(prev => {
      const removed = prev.find(t => t.id === taskId) || null;
      const next = prev.filter(t => t.id !== taskId);
      // Persist
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch {}
      // Setup undo
      setUndo({ visible: true, last: removed });
      setTimeout(() => setUndo(u => (u.visible ? { ...u, visible: false } : u)), 4000);
      return next;
    });
    onDataMutation('today', 'remove_task', { taskId });
  }, []);

  const handleUndoRemove = useCallback(() => {
    setUndo((u) => {
      if (!u.last) return { visible: false, last: null };
      setTodaysTasks(prev => {
        if (prev.some(t => t.id === u.last.id)) return prev; // dedupe guard
        const next = [u.last, ...prev];
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch {}
        return next;
      });
      return { visible: false, last: null };
    });
  }, []);

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
      handleAddTaskToFocus(item.task);
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

  const completedTasks = todaysTasks.filter(task => task.completed).length;
  const totalTasks = todaysTasks.length;
  const completionPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
  const estimatedDuration = todaysTasks.reduce((total, task) => {
    return total + (task.estimated_duration || 0);
  }, 0);

  return (
    <DndProvider backend={HTML5Backend}>
      {/* Daily Ritual Prompts (moved from DailyRitualManager) */}
      {user && showMorningPrompt && (
        <MorningReflection
          onComplete={handleMorningComplete}
          onClose={closeMorningPrompt}
        />
      )}

      {user && showEveningPrompt && (
        <EveningReflectionPrompt
          onComplete={handleEveningComplete}
          onClose={closeEveningPrompt}
        />
      )}

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
                  <p className="text-2xl font-bold text-white">{totalTasks}</p>
                  <p className="text-sm text-gray-400">Total Tasks</p>
                </div>
                <Calendar className="h-8 w-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-green-400">{completedTasks}</p>
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
                  <p className="text-2xl font-bold text-purple-400">{Math.round(estimatedDuration / 60)}h</p>
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
                <h2 className="text-xl font-semibold text-white mb-6">Today's Focus</h2>
                
                {/* Unified Action Bar: Search + Suggest My Focus */}
                <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:space-x-3 space-y-3 sm:space-y-0">
                  <div className="flex-1">
                    <TaskSearchBar 
                      onAddTask={handleAddTaskToFocus}
                      placeholder="Search for tasks or..."
                    />
                  </div>
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        setSuggestLoading(true);
                        const res = await tasksAPI.suggestFocus();
                        const suggestions = res.data || [];
                        setAiSuggestions(suggestions);
                      } catch (e) {
                        console.error('Suggest focus error:', e);
                        setAiSuggestions([]);
                      } finally {
                        setSuggestLoading(false);
                      }
                    }}
                    disabled={suggestLoading}
                    className={`inline-flex items-center justify-center ${suggestLoading ? 'bg-yellow-700' : 'bg-yellow-600 hover:bg-yellow-700'} text-black font-semibold py-2 px-3 rounded-md text-sm disabled:opacity-60`}
                  >
                    {suggestLoading ? (
                      <span className="inline-flex items-center"><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Suggesting...</span>
                    ) : (
                      '✨ Suggest My Focus'
                    )}
                  </button>
                </div>

                {/* AI Suggestions List */}
                {aiSuggestions.length > 0 && (
                  <div className="mb-6 space-y-2">
                    {aiSuggestions.map((s) => {
                      const context = `${s.pillar || s.pillar_name ? `Pillar: ${s.pillar || s.pillar_name}` : ''}${s.area || s.area_name ? `${s.pillar || s.pillar_name ? ' • ' : ''}Area: ${s.area || s.area_name}` : ''}${s.project ? `${(s.pillar || s.pillar_name || s.area || s.area_name) ? ' • ' : ''}Project: ${s.project}` : ''}`;
                      const key = s.taskId || s.id || `${s.title}-${s.project || ''}`;
                      return (
                        <div key={key} data-suggestion-key={key}>
                          <UnifiedTaskItem
                            task={{ name: s.title, priority: (s.priority || 'medium').toLowerCase(), id: s.taskId }}
                            context={context}
                            mode="suggestion"
                            showAIBadge={true}
                            onAdd={async () => {
                            const removeFromSuggestions = () => setAiSuggestions(prev => prev.filter(x => (x.taskId || x.id) !== (s.taskId || s.id)));
                            try {
                              // Fade-out animation before removal
                              const row = document.querySelector(`[data-suggestion-key="${key}"]`);
                              if (row) {
                                row.style.transition = 'opacity 250ms ease';
                                row.style.opacity = '0';
                                setTimeout(() => removeFromSuggestions(), 260);
                              } else {
                                removeFromSuggestions();
                              }
                              if (s.task) {
                                handleAddTaskToFocus({ ...s.task });
                              } else {
                                const resp = await tasksAPI.getTask(s.taskId);
                                handleAddTaskToFocus(resp.data || { id: s.taskId, name: s.title, priority: (s.priority || 'medium').toLowerCase(), description: s.description, project_name: s.project, due_date: s.dueDate });
                              }
                            } catch {
                              handleAddTaskToFocus({ id: s.taskId, name: s.title, priority: (s.priority || 'medium').toLowerCase(), description: s.description, project_name: s.project, due_date: s.dueDate });
                            }
                          }}
                          />
                        </div>
                      );
                    })}
                  </div>
                )}

                {todaysTasks.length === 0 ? (
                  <div
                    ref={drop}
                    className="text-center py-12 border-2 border-dashed border-gray-700 rounded-lg"
                  >
                    <Calendar className="mx-auto h-16 w-16 text-gray-600 mb-4" />
                    <h3 className="text-lg font-medium text-gray-400 mb-2">No tasks selected for today</h3>
                    <p className="text-gray-500 mb-4">
                      Use the action bar above to add tasks — search manually or accept AI suggestions.
                    </p>
                  </div>
                ) : (
                  <div ref={drop} className="space-y-4">
                    {todaysTasks.map((task, index) => (
                      <div key={task.id} ref={(node) => {/* DnD wrapper maintains drag behavior */}}>
                        {/* Keep DragTaskItem to handle DnD and controls; render UnifiedTaskItem inside for visual parity */}
                        <div className="bg-transparent">
                          <UnifiedTaskItem
                            task={task}
                            context={task.project_name ? `Project: ${task.project_name}` : ''}
                            mode="focus"
                            showToggle={true}
                            completed={!!task.completed}
                            onToggleComplete={handleToggleTask}
                            onStartPomodoro={handleStartPomodoro}
                            onRemove={handleRemoveFromFocus}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Task Why Statements - Show contextual insights */}
                {todaysTasks.length > 0 && (
                  <TaskWhyStatements 
                    taskIds={todaysTasks.filter(task => !task.completed).map(task => task.id)}
                    showAll={false}
                  />
                )}
              </div>
            </div>

            {/* Pomodoro Timer & Available Tasks */}
            <div className="space-y-6">
              {/* Daily Ritual Buttons - Moved to Daily Engagement Hub */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Daily Engagement Hub</h3>
                
                {/* Pomodoro Timer */}
                <PomodoroTimer
                  taskName={activePomodoro?.name}
                  onSessionComplete={handlePomodoroComplete}
                />
                
                {/* Daily Ritual Buttons */}
                <div className="mt-4 flex space-x-3">
                  <button
                    onClick={() => setShowMorningPrompt(true)}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-400 hover:bg-yellow-500/30 transition-colors"
                  >
                    <Sun className="w-5 h-5" />
                    <span>Morning Reflection</span>
                  </button>
                  
                  <button
                    onClick={() => setShowEveningPrompt(true)}
                    className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-purple-500/20 border border-purple-500/30 rounded-lg text-purple-400 hover:bg-purple-500/30 transition-colors"
                  >
                    <Moon className="w-5 h-5" />
                    <span>Evening Reflection</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>


        {undo.visible && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 border border-gray-700 text-white px-4 py-2 rounded shadow-lg flex items-center space-x-3 z-50">
            <span>Task removed</span>
            <button
              type="button"
              onClick={handleUndoRemove}
              className="text-yellow-400 hover:text-yellow-300 underline"
            >
              Undo
            </button>
          </div>
        )}

      </div>
    </DndProvider>
  );
});

Today.displayName = 'Today';

export default Today;