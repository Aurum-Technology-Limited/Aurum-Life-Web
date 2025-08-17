import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { tasksAPI, projectsAPI } from '../services/api';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { format, addDays, startOfWeek, endOfWeek, startOfDay, addHours, setHours, setMinutes, isSameDay, isWithinInterval, parseISO } from 'date-fns';
import { List, Calendar as CalIcon, PlusCircle } from 'lucide-react';
import { TaskModal } from './Tasks';

const HOURS = Array.from({ length: 24 }, (_, i) => i); // 00:00 - 23:00
const ITEM_TYPE = 'TASK_CARD';

const getDateFromISO = (d) => {
  if (!d) return null;
  if (d instanceof Date) return d;
  try { return parseISO(d); } catch { return null; }
};

// Draggable task card
const TaskCard = ({ task, onOpen }) => {
  const [, drag] = useDrag(() => ({ type: ITEM_TYPE, item: { taskId: task.id, task } }), [task]);
  const priority = (task.priority || 'medium').toLowerCase();
  const colorMap = { high: 'border-red-500/60', medium: 'border-yellow-500/60', low: 'border-green-500/60' };
  return (
    <div ref={drag} onClick={() => onOpen(task)} className={`cursor-move text-xs p-2 rounded bg-gray-900 border ${colorMap[priority] || 'border-gray-700'} shadow-sm hover:bg-gray-800`}>
      <div className="truncate text-white">{task.name || 'Untitled'}</div>
      {task.project_name && <div className="text-[10px] text-gray-400 truncate">{task.project_name}</div>}
    </div>
  );
};

// Droppable time slot
const TimeSlot = ({ date, onDropTask, onCreateAt, children }) => {
  const [, drop] = useDrop(
    () => ({
      accept: ITEM_TYPE,
      drop: (item) => onDropTask(item.taskId, date),
    }),
    [date, onDropTask]
  );
  return (
    <div ref={drop} className="border-t border-gray-800 h-16 relative" onDoubleClick={() => onCreateAt && onCreateAt(date)}>
      {children}
      <button
        className="absolute right-2 top-1 text-gray-600 hover:text-gray-300"
        title="Create task here"
        onClick={(e) => { e.stopPropagation(); onCreateAt && onCreateAt(date); }}
      >
        <PlusCircle size={14} />
      </button>
    </div>
  );
};

const DayGrid = ({ day, tasks, onDropTask, onOpen, onCreateAt, slotHeight }) => {
  return (
    <div className="grid" style={{ gridTemplateRows: `repeat(${HOURS.length}, ${slotHeight}px)` }}>
      {HOURS.map((h) => {
        const slotDate = setMinutes(setHours(startOfDay(day), h), 0);
        const slotTasks = tasks.filter((t) => {
          const d = getDateFromISO(t.due_date);
          if (!d) return false;
          return isSameDay(d, day) && d.getHours() === h;
        });
        return (
          <TimeSlot key={h} date={slotDate} onDropTask={onDropTask} onCreateAt={onCreateAt}>
            <div className="absolute left-2 top-1 text-[10px] text-gray-500">{format(slotDate, 'HH:mm')}</div>
            <div className="absolute left-24 right-2 top-1.5 flex flex-col gap-1">
              {slotTasks.map((t) => (
                <TaskCard key={t.id} task={t} onOpen={onOpen} />
              ))}
            </div>
          </TimeSlot>
        );
      })}
    </div>
  );
};

const WeekGrid = ({ weekStart, tasks, onDropTask, onOpen, onCreateAt, slotHeight }) => {
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  return (
    <div className="grid" style={{ gridTemplateColumns: `80px repeat(7, 1fr)` }}>
      {/* Hour labels column */}
      <div />
      {days.map((d) => (
        <div key={d.toISOString()} className="text-center text-xs text-gray-400 pb-2">{format(d, 'EEE dd')}</div>
      ))}
      {HOURS.map((h) => (
        <React.Fragment key={h}>
          <div className="border-t border-gray-800 text-[10px] text-gray-500 flex items-start justify-end pr-2 pt-1" style={{ height: `${slotHeight}px` }}>{String(h).padStart(2, '0')}:00</div>
          {days.map((d) => {
            const slotDate = setMinutes(setHours(startOfDay(d), h), 0);
            const slotTasks = tasks.filter((t) => {
              const due = getDateFromISO(t.due_date);
              if (!due) return false;
              return isSameDay(due, d) && due.getHours() === h;
            });
            return (
              <TimeSlot key={d.toISOString() + h} date={slotDate} onDropTask={onDropTask} onCreateAt={onCreateAt}>
                <div className="px-1">
                  {slotTasks.map((t) => (
                    <TaskCard key={t.id} task={t} onOpen={onOpen} />
                  ))}
                </div>
              </TimeSlot>
            );
          })}
        </React.Fragment>
      ))}
    </div>
  );
};

const MonthGrid = ({ monthDate, tasks, onOpen }) => {
  // Simple month view: show counts and first 2 tasks per day
  const start = startOfWeek(new Date(monthDate.getFullYear(), monthDate.getMonth(), 1));
  const end = endOfWeek(new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0));
  const days = [];
  let cursor = start;
  while (cursor <= end) {
    days.push(cursor);
    cursor = addDays(cursor, 1);
  }
  return (
    <div className="grid grid-cols-7 gap-1">
      {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map((d) => (
        <div key={d} className="text-center text-xs text-gray-400 pb-1">{d}</div>
      ))}
      {days.map((d) => {
        const dayTasks = tasks.filter((t) => {
          const due = getDateFromISO(t.due_date);
          return due && isSameDay(due, d);
        });
        return (
          <div key={d.toISOString()} className="min-h-[90px] border border-gray-800 rounded p-1">
            <div className={`text-[10px] mb-1 ${d.getMonth() === monthDate.getMonth() ? 'text-gray-300' : 'text-gray-600'}`}>{format(d, 'd')}</div>
            <div className="space-y-0.5">
              {dayTasks.slice(0, 2).map((t) => (
                <div key={t.id} className="text-[10px] truncate cursor-pointer hover:underline" onClick={() => onOpen(t)}>
                  • {t.name}
                </div>
              ))}
              {dayTasks.length > 2 && (
                <div className="text-[10px] text-gray-500">+{dayTasks.length - 2} more</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const CalendarBoard = () => {
  const [showCreate, setShowCreate] = useState(false);
  const [newTaskTime, setNewTaskTime] = useState(null);
  const [newName, setNewName] = useState('');
  const [newPriority, setNewPriority] = useState('medium');
  const [newProjectId, setNewProjectId] = useState('');
  const [projects, setProjects] = useState([]);

  const loadProjects = useCallback(async () => {
    try {
      const resp = await projectsAPI.getProjects();
      setProjects(Array.isArray(resp.data) ? resp.data : []);
    } catch (e) {
      console.warn('Projects load failed', e);
      setProjects([]);
    }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);

  const [view, setView] = useState('week'); // day | week | month
  const [anchorDate, setAnchorDate] = useState(new Date());
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [activeTask, setActiveTask] = useState(null);

  const [slotHeight, setSlotHeight] = useState(48); // px per hour

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const resp = await tasksAPI.getTasks();
      setTasks(Array.isArray(resp.data) ? resp.data : []);
    } catch (e) {
      console.error('Calendar load error', e);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, []);
  const onCreateAt = useCallback((date) => {
    setNewTaskTime(date);
    setNewName('');
    setNewPriority('medium');
    setNewProjectId(projects[0]?.id || '');
    setShowCreate(true);
  }, [projects]);


  useEffect(() => { load(); }, [load]);

  const onOpenTask = useCallback((t) => { setActiveTask(t); setModalOpen(true); }, []);
  const onCloseTask = useCallback(() => { setModalOpen(false); setActiveTask(null); }, []);

  const onSaveTask = useCallback(async (updated) => {
    try {
      if (!activeTask) return;
      await tasksAPI.updateTask(activeTask.id, updated);
      await load();
    } catch (e) {
      console.error('Save task failed', e);
    } finally {
      onCloseTask();
    }
  }, [activeTask, load, onCloseTask]);

  const onDropTask = useCallback(async (taskId, date) => {
    try {
      await tasksAPI.updateTask(taskId, { due_date: date.toISOString() });
      await load();
    } catch (e) {
      console.error('Reschedule failed', e);
    }
  }, [load]);

  // Filter tasks with due_date
  const scheduledTasks = useMemo(() => tasks.filter(t => !!t.due_date), [tasks]);

  const weekStartDate = useMemo(() => startOfWeek(anchorDate, { weekStartsOn: 0 }), [anchorDate]);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <button className={`px-2 py-1 rounded text-sm ${view==='day'?'bg-gray-800 text-white':'text-gray-300 hover:text-white'}`} onClick={() => setView('day')}>Day</button>
            <button className={`px-2 py-1 rounded text-sm ${view==='week'?'bg-gray-800 text-white':'text-gray-300 hover:text-white'}`} onClick={() => setView('week')}>Week</button>
            <button className={`px-2 py-1 rounded text-sm ${view==='month'?'bg-gray-800 text-white':'text-gray-300 hover:text-white'}`} onClick={() => setView('month')}>Month</button>

        {showCreate && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={(e) => { if (e.target === e.currentTarget) setShowCreate(false); }}>
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 w-full max-w-md" onClick={(e) => e.stopPropagation()}>
              <div className="text-white font-semibold mb-2">Create Task</div>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-gray-400">Name</label>
                  <input value={newName} onChange={(e) => setNewName(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-700 rounded p-2 text-white text-sm" placeholder="Task name" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-400">Priority</label>
                    <select value={newPriority} onChange={(e) => setNewPriority(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-700 rounded p-2 text-white text-sm">
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-gray-400">Project</label>
                    <select value={newProjectId} onChange={(e) => setNewProjectId(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-700 rounded p-2 text-white text-sm">
                      <option value="">Unassigned</option>
                      {projects.map(p => (<option key={p.id} value={p.id}>{p.name}</option>))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-400">When</label>
                  <input value={newTaskTime ? newTaskTime.toISOString().slice(0,16) : ''} onChange={() => {}} className="w-full mt-1 bg-gray-800 border border-gray-700 rounded p-2 text-white text-sm" disabled />
                </div>
                <div className="flex justify-end gap-2">
                  <button className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded" onClick={() => setShowCreate(false)}>Cancel</button>
                  <button className="px-3 py-1.5 text-sm bg-yellow-600 hover:bg-yellow-700 rounded text-black font-semibold" onClick={async () => {
                    try {
                      if (!newName || !newTaskTime) return;
                      const payload = { name: newName, priority: newPriority, project_id: newProjectId || null, due_date: newTaskTime.toISOString() };
                      await tasksAPI.createTask(payload);
                      setShowCreate(false);
                      await load();
                    } catch (e) {
                      console.error('Create task failed', e);
                    }
                  }}>Create</button>
                </div>
              </div>
            </div>
          </div>
        )}

          </div>
          <div className="flex items-center gap-2">
            <button className="px-2 py-1 rounded text-sm text-gray-300 hover:text-white" onClick={() => setAnchorDate(addDays(anchorDate, view==='day'? -1 : view==='week'? -7 : -30))}>Prev</button>
            <div className="text-gray-400 text-sm">{format(anchorDate, view==='month' ? 'MMMM yyyy' : 'EEE MMM d, yyyy')}</div>
            <button className="px-2 py-1 rounded text-sm text-gray-300 hover:text-white" onClick={() => setAnchorDate(addDays(anchorDate, view==='day'? 1 : view==='week'? 7 : 30))}>Next</button>
          </div>
        </div>

        {loading ? (
          <div className="text-gray-400 text-sm">Loading calendar…</div>
        ) : (
          <div className="overflow-x-auto">
            {view === 'day' && (
              <DayGrid day={anchorDate} tasks={scheduledTasks} onDropTask={onDropTask} onOpen={onOpenTask} onCreateAt={onCreateAt} />
            )}
            {view === 'week' && (
              <WeekGrid weekStart={weekStartDate} tasks={scheduledTasks} onDropTask={onDropTask} onOpen={onOpenTask} onCreateAt={onCreateAt} />
            )}
            {view === 'month' && (
              <MonthGrid monthDate={anchorDate} tasks={scheduledTasks} onOpen={onOpenTask} />
            )}
          </div>
        )}

        {modalOpen && activeTask && (
          <TaskModal
            task={activeTask}
            isOpen={modalOpen}
            onClose={onCloseTask}
            onSave={onSaveTask}
            loading={false}
          />
        )}
      </div>
    </DndProvider>
  );
};

export default CalendarBoard;