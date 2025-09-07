import React from 'react';
import { Flame, Brain, Heart, Plus } from 'lucide-react';

export function PillarsSection() {
  const pillars = [
    {
      id: 'meaning',
      name: 'Meaning',
      description: 'Purpose & Values',
      icon: Flame,
      progress: 61,
      areas: 3,
      projects: 5,
      tasks: 42
    },
    {
      id: 'growth',
      name: 'Growth',
      description: 'Learning & Mindset',
      icon: Brain,
      progress: 74,
      areas: 4,
      projects: 3,
      tasks: 28
    },
    {
      id: 'relationships',
      name: 'Relationships',
      description: 'Family & Friends',
      icon: Heart,
      progress: 58,
      areas: 4,
      projects: 2,
      tasks: 15
    }
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold tracking-tight">Pillars</h2>
        <button className="text-xs px-3 py-1.5 rounded-lg border hover:opacity-90 flex items-center gap-2" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
          <Plus className="w-4 h-4" />
          New Pillar
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {pillars.map((pillar) => {
          const Icon = pillar.icon;
          const circumference = 2 * Math.PI * 50;
          const strokeDashoffset = circumference - (pillar.progress / 100) * circumference;

          return (
            <div key={pillar.id} className="rounded-2xl border p-6 flex flex-col gap-5" style={{background: 'rgba(26,29,41,0.45)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-lg flex items-center justify-center" style={{background: 'rgba(244,208,63,0.12)', border: '1px solid rgba(244,208,63,0.25)'}}>
                    <Icon className="w-5 h-5" style={{color: '#F4D03F'}} />
                  </div>
                  <div>
                    <div className="text-lg font-semibold tracking-tight">{pillar.name}</div>
                    <div className="text-sm" style={{color: '#B8BCC8'}}>{pillar.description}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-semibold" style={{color: '#F4D03F'}}>{pillar.progress}%</div>
                  <div className="text-xs" style={{color: '#6B7280'}}>Complete</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Areas</span>
                  <span style={{color: '#B8BCC8'}}>{pillar.areas}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Projects</span>
                  <span style={{color: '#B8BCC8'}}>{pillar.projects} active</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Tasks aligned</span>
                  <span style={{color: '#B8BCC8'}}>{pillar.tasks}</span>
                </div>
              </div>
              
              <div className="h-2 rounded-full overflow-hidden border" style={{background: 'rgba(11,13,20,0.4)', borderColor: 'rgba(244,208,63,0.2)'}}>
                <div className="h-full" style={{width: `${pillar.progress}%`, background: 'linear-gradient(90deg,#F4D03F,#F7DC6F)'}}></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}