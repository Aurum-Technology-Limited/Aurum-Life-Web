import React, { useEffect, useMemo, useState, useCallback, useRef } from 'react';
import { tasksAPI, projectsAPI } from '../services/api';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { format, addDays, startOfWeek, endOfWeek, startOfDay, setHours, setMinutes, isSameDay, parseISO } from 'date-fns';
import { PlusCircle, Filter, ChevronDown, ChevronRight } from 'lucide-react';
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
  const projColor = task.project_color || undefined;
  return (
    <div
      ref={drag}
      onClick={() => onOpen(task)}
      className={`cursor-move text-xs p-2 rounded bg-gray-900 border ${colorMap[priority] || 'border-gray-700'} shadow-sm hover:bg-gray-800`}
      style={projColor ? { boxShadow: `inset 2px 0 0 ${projColor}` } : undefined}
    >
      <div className="truncate text-white">{task.name || 'Untitled'}</div>
      {task.project_name && <div className="text-[10px] text-gray-400 truncate">{task.project_name}</div>}
    </div>
  );
};

// Droppable time slot
const TimeSlot = ({ date, onDropTask, onCreateAt, children, slotHeight }) => {
  const [, drop] = useDrop(
    () => ({ accept: ITEM_TYPE, drop: (item) => onDropTask(item.taskId, date) }),
    [date, onDropTask]
  );
  return (
    <div ref={drop} className="border-t border-gray-800 relative" style={{ height: slotHeight }} onDoubleClick={() => onCreateAt && onCreateAt(date)}>
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

const DayGrid = ({ day, tasks, onDropTask, onOpen, onCreateAt, slotHeight }) => (
  <div className="grid" style={{ gridTemplateRows: `repeat(${HOURS.length}, ${slotHeight}px)` }}>
    {HOURS.map((h) => {
      const slotDate = setMinutes(setHours(startOfDay(day), h), 0);
      const slotTasks = tasks.filter((t) => {
        const d = getDateFromISO(t.due_date);
        return !!d && isSameDay(d, day) && d.getHours() === h;
      });
      return (
        <TimeSlot key={h} date={slotDate} onDropTask={onDropTask} onCreateAt={onCreateAt} slotHeight={slotHeight}>
          <div className="absolute left-2 top-1 text-[10px] text-gray-500">{format(slotDate, 'HH:mm')}</div>
          <div className="absolute left-24 right-2 top-1.5 flex flex-col gap-1">
            {slotTasks.map((t) => (<TaskCard key={t.id} task={t} onOpen={onOpen} />))}
          </div>
        </TimeSlot>
      );
    })}
  </div>
);

const WeekGrid = ({ weekStart, tasks, onDropTask, onOpen, onCreateAt, slotHeight }) => {
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  return (
    <div className="grid" style={{ gridTemplateColumns: `80px repeat(7, 1fr)` }}>
      <div />
      {days.map((d) => (<div key={d.toISOString()} className="text-center text-xs text-gray-400 pb-2">{format(d, 'EEE dd')}</div>))}
      {HOURS.map((h) => (
        <React.Fragment key={h}>
          <div className="border-t border-gray-800 text-[10px] text-gray-500 flex items-start justify-end pr-2 pt-1" style={{ height: `${slotHeight}px` }}>{String(h).padStart(2, '0')}:00</div>
          {days.map((d) => {
            const slotDate = setMinutes(setHours(startOfDay(d), h), 0);
            const slotTasks = tasks.filter((t) => {
              const due = getDateFromISO(t.due_date);
              return !!due && isSameDay(due, d) && due.getHours() === h;
            });
            return (
              <TimeSlot key={d.toISOString() + h} date={slotDate} onDropTask={onDropTask} onCreateAt={onCreateAt} slotHeight={slotHeight}>
                <div className="px-1">
                  {slotTasks.map((t) => (<TaskCard key={t.id} task={t} onOpen={onOpen} />))}
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
  const start = startOfWeek(new Date(monthDate.getFullYear(), monthDate.getMonth(), 1));
  const end = endOfWeek(new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0));
  const days = [];
  let cursor = start;
  while (cursor <= end) { days.push(cursor); cursor = addDays(cursor, 1); }
  return (
    <div className="grid grid-cols-7 gap-1">
      {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map((d) => (<div key={d} className="text-center text-xs text-gray-400 pb-1">{d}</div>))}
      {days.map((d) => {
        const dayTasks = tasks.filter((t) => { const due = getDateFromISO(t.due_date); return !!due && isSameDay(due, d); });
        return (
          <div key={d.toISOString()} className="min-h-[90px] border border-gray-800 rounded p-1">
            <div className={`text-[10px] mb-1 ${d.getMonth() === monthDate.getMonth() ? 'text-gray-300' : 'text-gray-600'}`}>{format(d, 'd')}</div>
            <div className="space-y-0.5">
              {dayTasks.slice(0, 2).map((t) => (<div key={t.id} className="text-[10px] truncate cursor-pointer hover:underline" onClick={() => onOpen(t)}>• {t.name}</div>))}
              {dayTasks.length > 2 && (<div className="text-[10px] text-gray-500">+{dayTasks.length - 2} more</div>)}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const UnscheduledList = ({ tasks, onOpen }) => {
  const list = Array.isArray(tasks) ? tasks : [];
  return (
    <div className="space-y-2">
      {list.length === 0 ? (
        <div className="text-xs text-gray-500">No unscheduled tasks</div>
      ) : (
        list.map((t) => (<TaskCard key={t.id} task={t} onOpen={onOpen} />))
      )}
    </div>
  );
};

const CalendarBoard = () => {
  // UI state
  const [view, setView] = useState('week');
  const [anchorDate, setAnchorDate] = useState(new Date());
  const [slotHeight, setSlotHeight] = useState(48);
  const [showUnscheduled, setShowUnscheduled] = useState(true);
  const [showLegend, setShowLegend] = useState(false);
  const [showFilter, setShowFilter] = useState(false);
  const [filterActiveIndex, setFilterActiveIndex] = useState(0);
  const filterMenuRef = useRef(null);

  // Data
  const [projects, setProjects] = useState([]);
  const [projectFilterIds, setProjectFilterIds] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  // Task modal
  const [modalOpen, setModalOpen] = useState(false);
  const [activeTask, setActiveTask] = useState(null);

  // Create modal
  const [showCreate, setShowCreate] = useState(false);
  const [newTaskTime, setNewTaskTime] = useState(null);
  const [newName, setNewName] = useState('');
  const [newPriority, setNewPriority] = useState('medium');
  const [newProjectId, setNewProjectId] = useState('');

  // Effects
  useEffect(() => { (async () => { try { const resp = await projectsAPI.getProjects(); setProjects(Array.isArray(resp.data) ? resp.data : []); } catch { setProjects([]); } })(); }, []);
  const loadTasks = useCallback(async () => { try { setLoading(true); const resp = await tasksAPI.getTasks(); setTasks(Array.isArray(resp.data) ? resp.data : []); } catch { setTasks([]); } finally { setLoading(false); } }, []);
  useEffect(() => { loadTasks(); }, [loadTasks]);

  useEffect(() => { try { const raw = localStorage.getItem('calendar_unscheduled_open'); if (raw !== null) setShowUnscheduled(raw === '1'); } catch {} }, []);
  useEffect(() => { try { localStorage.setItem('calendar_unscheduled_open', showUnscheduled ? '1' : '0'); } catch {} }, [showUnscheduled]);

  useEffect(() => {
    if (showFilter && filterMenuRef.current) { try { filterMenuRef.current.focus(); } catch {} setFilterActiveIndex(0); }
  }, [showFilter]);

  // Handlers
  const onOpenTask = useCallback((t) => { setActiveTask(t); setModalOpen(true); }, []);
  const onCloseTask = useCallback(() => { setModalOpen(false); setActiveTask(null); }, []);
  const onSaveTask = useCallback(async (updated) => { try { if (!activeTask) return; await tasksAPI.updateTask(activeTask.id, updated); await loadTasks(); } catch {} finally { onCloseTask(); } }, [activeTask, loadTasks, onCloseTask]);
  const onDropTask = useCallback(async (taskId, date) => { try { await tasksAPI.updateTask(taskId, { due_date: date.toISOString() }); await loadTasks(); } catch (e) { console.error('Reschedule failed', e); } }, [loadTasks]);
  const onCreateAt = useCallback((date) => { setNewTaskTime(date); setNewName(''); setNewPriority('medium'); setNewProjectId(projects[0]?.id || ''); setShowCreate(true); }, [projects]);
  const onZoomIn = useCallback(() => setSlotHeight((h) => Math.min(h + 8, 96)), []);
  const onZoomOut = useCallback(() => setSlotHeight((h) => Math.max(h - 8, 24)), []);

  // Derived
  const scheduledTasks = useMemo(() => {
    const base = tasks.filter(t => !!t.due_date);
    return (!projectFilterIds || projectFilterIds.length === 0) ? base : base.filter(t => projectFilterIds.includes(t.project_id));
  }, [tasks, projectFilterIds]);
  const unscheduledTasks = useMemo(() => {
    const base = tasks.filter(t => !t.due_date);
    return (!projectFilterIds || projectFilterIds.length === 0) ? base : base.filter(t => projectFilterIds.includes(t.project_id));
  }, [tasks, projectFilterIds]);
  const weekStartDate = useMemo(() => startOfWeek(anchorDate, { weekStartsOn: 0 }), [anchorDate]);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 w-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-3 relative">
          {/* Left controls */}
          <div className="flex items-center gap-2">
            <button className={`px-2 py-1 rounded text-sm ${view==='day'?'bg-gray-800 text-white':'text-gray-300 hover:text-white'}`} onClick={() => setView('day')}>Day</button>
            <button className={`px-2 py-1 rounded text-sm ${view==='week'?'bg-gray-800 text-white':'text-gray-300 hover:text-white'}`} onClick={() => setView('week')}>Week</button>
            <button className={`px-2 py-1 rounded text-sm ${view==='month'?'bg-gray-800 text-white':'text-gray-300 hover:text-white'}`} onClick={() => setView('month')}>Month</button>
            <div className="ml-2 flex items-center gap-1 text-xs text-gray-400">
              <span>Zoom</span>
              <button className="px-2 py-0.5 rounded border border-gray-700 hover:bg-gray-800" onClick={onZoomOut}>-</button>
              <button className="px-2 py-0.5 rounded border border-gray-700 hover:bg-gray-800" onClick={onZoomIn}>+</button>
            </div>
            {/* Filter dropdown */}
            <div className="relative">
              <button className="px-2 py-1 rounded text-sm text-gray-300 hover:text-white flex items-center gap-1" onClick={() => setShowFilter((s)=>!s)} onKeyDown={(e) => { if (showFilter && e.key === 'Escape') setShowFilter(false); }} aria-haspopup="menu" aria-expanded={showFilter} title="Filter by project">
                <Filter className="h-4 w-4" />
                Filter
              </button>
              {showFilter && (
                <div ref={filterMenuRef} tabIndex={0} className="absolute right-0 top-8 bg-gray-900 border border-gray-700 rounded p-3 z-50 w-64 outline-none" onKeyDown={(e) => {
                  const max = projects.length - 1;
                  if (e.key === 'ArrowDown') { e.preventDefault(); setFilterActiveIndex((i) => Math.min(i + 1, max)); }
                  else if (e.key === 'ArrowUp') { e.preventDefault(); setFilterActiveIndex((i) => Math.max(i - 1, 0)); }
                  else if (e.key === 'Enter') { const p = projects[filterActiveIndex]; if (p) { const checked = !projectFilterIds.includes(p.id); setProjectFilterIds(prev => checked ? [...new Set([...prev, p.id])] : prev.filter(id => id !== p.id)); } }
                  else if (e.key === 'Escape') { setShowFilter(false); }
                }}>
                  <div className="text-xs text-gray-400 mb-2">Filter by project</div>
                  <div className="max-h-64 overflow-y-auto space-y-1">
                    {projects.map((p, idx) => (
                      <label key={p.id} className={`flex items-center gap-2 text-sm ${filterActiveIndex===idx?'bg-gray-800':''} text-gray-200 px-1 rounded`}>
                        <input type="checkbox" checked={projectFilterIds.includes(p.id)} onChange={(e) => { setProjectFilterIds(prev => e.target.checked ? [...new Set([...prev, p.id])] : prev.filter(id => id !== p.id)); }} />
                        <span className="truncate">{p.name}</span>
                      </label>
                    ))}
                  </div>
                  <div className="flex justify-end gap-2 mt-2">
                    <button className="text-xs px-2 py-1 bg-gray-800 rounded" onClick={() => setProjectFilterIds([])}>Clear</button>
                    <button className="text-xs px-2 py-1 bg-yellow-600 text-black rounded" onClick={() => setShowFilter(false)}>Done</button>
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* Right controls */}
          <div className="flex items-center gap-2">
            {/* Legend toggle */}
            <button className="px-2 py-1 rounded text-sm text-gray-300 hover:text-white" onClick={() => setShowLegend(s => !s)}>Legend</button>
            {showLegend && (
              <div className="absolute right-20 top-10 bg-gray-900 border border-gray-700 rounded p-3 z-40 w-64">
                <div className="text-xs text-gray-400 mb-2">Project Colors</div>
                <div className="max-h-64 overflow-y-auto space-y-1">
                  {projects.map(p => (
                    <div key={p.id} className="flex items-center gap-2 text-sm text-gray-200">
                      <span className="inline-block w-3 h-3 rounded-sm" style={{ backgroundColor: p.color || '#777' }} />
                      <span className="truncate">{p.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <button className="px-2 py-1 rounded text-sm text-gray-300 hover:text-white" onClick={() => setAnchorDate(addDays(anchorDate, view==='day'? -1 : view==='week'? -7 : -30))}>Prev</button>
            <div className="text-gray-400 text-sm">{format(anchorDate, view==='month' ? 'MMMM yyyy' : 'EEE MMM d, yyyy')}</div>
            <button className="px-2 py-1 rounded text-sm text-gray-300 hover:text-white" onClick={() => setAnchorDate(addDays(anchorDate, view==='day'? 1 : view==='week'? 7 : 30))}>Next</button>
          </div>
        </div>

        {/* Body */}
        {loading ? (
          <div className="text-gray-400 text-sm">Loading calendar…</div>
        ) : (
          <div className="w-full overflow-x-auto">
            {(view === 'day' || view === 'week') ? (
              <div className="grid grid-cols-12 gap-4">
                {/* Unscheduled sidebar */}
                <aside className="col-span-3">
                  <div className="bg-gray-800 border border-gray-700 rounded p-3">
                    <button className="flex items-center gap-1 text-sm text-gray-200 mb-2" onClick={() => setShowUnscheduled(s => !s)}>
                      {showUnscheduled ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      Unscheduled
                    </button>
                    {showUnscheduled && (<UnscheduledList tasks={unscheduledTasks} onOpen={onOpenTask} />)}
                  </div>
                </aside>
                {/* Calendar grid */}
                <section className="col-span-9">
                  {view === 'day' && (<DayGrid day={anchorDate} tasks={scheduledTasks} onDropTask={onDropTask} onOpen={onOpenTask} onCreateAt={onCreateAt} slotHeight={slotHeight} />)}
                  {view === 'week' && (<WeekGrid weekStart={weekStartDate} tasks={scheduledTasks} onDropTask={onDropTask} onOpen={onOpenTask} onCreateAt={onCreateAt} slotHeight={slotHeight} />)}
                </section>
              </div>
            ) : (
              <MonthGrid monthDate={anchorDate} tasks={scheduledTasks} onOpen={onOpenTask} />
            )}
          </div>
        )}

        {/* Task modal */}
        {modalOpen && activeTask && (
          <TaskModal task={activeTask} isOpen={modalOpen} onClose={onCloseTask} onSave={onSaveTask} loading={false} />
        )}
      </div>

      {/* Create task modal (overlay) */}
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
                    await loadTasks();
                  } catch (e) { console.error('Create task failed', e); }
                }}>Create</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </DndProvider>
  );
};

export default CalendarBoard;