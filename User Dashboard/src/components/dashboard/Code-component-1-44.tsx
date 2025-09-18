import React from 'react';
import { Check, MoreHorizontal, ArrowRight } from 'lucide-react';

interface TaskItemProps {
  task: {
    id: number;
    title: string;
    priority: string;
    pillarArea: string;
    project: string;
    duration?: string;
    completed: boolean;
    energyLevel?: string;
    workType: string;
    strategicImpact: string;
  };
  onToggle: () => void;
}

export function TaskItem({ task, onToggle }: TaskItemProps) {
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High':
        return { bg: 'rgba(16,185,129,0.15)', color: '#10B981' };
      case 'Medium':
        return { bg: 'rgba(59,130,246,0.15)', color: '#3B82F6' };
      case 'Low':
        return { bg: 'rgba(59,130,246,0.15)', color: '#3B82F6' };
      default:
        return { bg: 'rgba(59,130,246,0.15)', color: '#3B82F6' };
    }
  };

  const getEnergyColor = (level: string) => {
    switch (level) {
      case 'High Energy':
        return { bg: 'rgba(239,68,68,0.15)', color: '#EF4444' };
      default:
        return { bg: 'rgba(59,130,246,0.15)', color: '#3B82F6' };
    }
  };

  const impactStyle = getImpactColor(task.strategicImpact);
  const energyStyle = getEnergyColor(task.energyLevel || '');

  return (
    <div className="flex items-start gap-3 rounded-xl border p-3 transition" style={{background: 'rgba(11,13,20,0.35)', borderColor: 'rgba(244,208,63,0.15)'}}>
      <button 
        onClick={onToggle}
        aria-checked={task.completed}
        className="mt-0.5 w-5 h-5 rounded-md border flex items-center justify-center shrink-0 transition"
        style={{
          borderColor: 'rgba(244,208,63,0.35)',
          background: task.completed ? 'linear-gradient(135deg,#F4D03F,#F7DC6F)' : 'rgba(26,29,41,0.6)',
          color: task.completed ? '#0B0D14' : 'transparent'
        }}
      >
        <Check className={`w-3.5 h-3.5 ${task.completed ? 'opacity-100' : 'opacity-0'}`} />
      </button>
      
      <div className="flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className={`text-sm font-medium ${task.completed ? 'line-through text-[#B8BCC8]' : ''}`}>
            {task.title}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full border" style={{borderColor: 'rgba(244,208,63,0.35)', color: '#F4D03F'}}>
            {task.priority}
          </span>
        </div>
        
        <div className="mt-1 flex flex-wrap items-center gap-2">
          <span className="text-[11px] px-2 py-0.5 rounded border" style={{borderColor: 'rgba(244,208,63,0.18)', color: '#B8BCC8'}}>
            {task.pillarArea}
          </span>
          <span className="text-[11px] px-2 py-0.5 rounded border" style={{borderColor: 'rgba(244,208,63,0.18)', color: '#B8BCC8'}}>
            {task.project}
          </span>
          {task.duration && (
            <span className="text-[11px] px-2 py-0.5 rounded" style={{background: 'rgba(59,130,246,0.15)', color: '#3B82F6'}}>
              {task.duration}
            </span>
          )}
          {task.completed && (
            <span className="text-[11px] px-2 py-0.5 rounded" style={{background: 'rgba(16,185,129,0.15)', color: '#10B981'}}>
              Completed
            </span>
          )}
        </div>

        {/* Strategic Impact Visualization */}
        <div className="strategic-impact-chain mt-2">
          <div className="flex items-center gap-1 text-xs">
            <span className="px-2 py-0.5 rounded" style={{background: 'rgba(244,208,63,0.15)', color: '#F4D03F'}}>
              {task.priority}
            </span>
            <ArrowRight className="w-3 h-3" style={{color: '#B8BCC8'}} />
            <span className="px-2 py-0.5 rounded border" style={{borderColor: 'rgba(244,208,63,0.18)'}}>
              {task.pillarArea}
            </span>
            <ArrowRight className="w-3 h-3" style={{color: '#B8BCC8'}} />
            <span className="px-2 py-0.5 rounded border" style={{borderColor: 'rgba(244,208,63,0.18)'}}>
              {task.project}
            </span>
            <ArrowRight className="w-3 h-3" style={{color: '#B8BCC8'}} />
            <span className="px-2 py-0.5 rounded" style={{background: impactStyle.bg, color: impactStyle.color}}>
              Strategic Impact: {task.strategicImpact}
            </span>
          </div>
        </div>

        {/* Time and Energy Indicators */}
        <div className="task-meta mt-2 flex items-center gap-2">
          {task.energyLevel && (
            <span className="text-[11px] px-2 py-0.5 rounded" style={{background: energyStyle.bg, color: energyStyle.color}}>
              {task.energyLevel}
            </span>
          )}
          <span className="text-[11px] px-2 py-0.5 rounded" style={{background: 'rgba(59,130,246,0.15)', color: '#3B82F6'}}>
            {task.workType}
          </span>
        </div>
      </div>
      
      <button className="p-2 rounded-lg hover:bg-white/5">
        <MoreHorizontal className="w-4 h-4" style={{color: '#B8BCC8'}} />
      </button>
    </div>
  );
}