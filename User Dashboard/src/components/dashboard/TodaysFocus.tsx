import React, { useState } from 'react';
import { TaskItem } from './TaskItem';
import { Plus } from 'lucide-react';

export function TodaysFocus() {
  const [tasks, setTasks] = useState([
    {
      id: 1,
      title: "Deep work: Write project proposal draft",
      priority: "P1",
      pillarArea: "Work → Portfolio",
      project: "Project: Alchemy Site",
      duration: "90m",
      completed: false,
      energyLevel: "High Energy",
      workType: "Deep Work",
      strategicImpact: "High"
    },
    {
      id: 2,
      title: "30m jog + mobility",
      priority: "P2",
      pillarArea: "Health → Training",
      project: "Project: Strength Cycle",
      duration: "",
      completed: true,
      energyLevel: "",
      workType: "Shallow Work",
      strategicImpact: "Medium"
    },
    {
      id: 3,
      title: "Call mom and plan Sunday lunch",
      priority: "P3",
      pillarArea: "Relationships → Family",
      project: "Project: Spring Brunch",
      duration: "",
      completed: false,
      energyLevel: "",
      workType: "Shallow Work",
      strategicImpact: "Low"
    }
  ]);

  const toggleTask = (taskId: number) => {
    setTasks(tasks.map(task => 
      task.id === taskId ? { ...task, completed: !task.completed } : task
    ));
  };

  return (
    <div className="xl:col-span-2 rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Today's Focus</h2>
          <p className="text-sm" style={{color: '#B8BCC8'}}>High-priority actions aligned to strategy</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="text-xs px-3 py-1.5 rounded-lg border hover:opacity-90 flex items-center gap-2" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
            <Plus className="w-4 h-4" />
            Add Task
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={() => toggleTask(task.id)}
          />
        ))}
      </div>
    </div>
  );
}