import React from 'react';
import { PlusCircle, Target, Brain, Zap } from 'lucide-react';

export function QuickActions() {
  const actions = [
    { icon: PlusCircle, label: 'Strategic Task' },
    { icon: Target, label: 'Pillar Balance' },
    { icon: Brain, label: 'Strategic Review' },
    { icon: Zap, label: 'Energy Optimize' }
  ];

  return (
    <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold tracking-tight">Strategic Operations</h2>
        <span className="text-xs" style={{color: '#B8BCC8'}}>Strategic thinking made simple</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <button 
              key={index}
              className="flex items-center gap-2 px-4 py-3 rounded-xl border hover:opacity-95 transition" 
              style={{borderColor: 'rgba(244,208,63,0.22)', background: 'rgba(11,13,20,0.35)'}}
            >
              <Icon className="w-5 h-5" style={{color: '#F4D03F'}} />
              <span className="text-sm font-medium">{action.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}