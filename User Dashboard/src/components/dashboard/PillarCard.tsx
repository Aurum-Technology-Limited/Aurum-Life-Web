import React from 'react';
import { HeartPulse, Users2, Briefcase } from 'lucide-react';

interface PillarCardProps {
  pillar: {
    id: string;
    name: string;
    description: string;
    icon: string;
    progress: number;
    areas: string[];
    subareas: Array<{ name: string; progress: number }>;
    metrics: {
      alignment: number;
      focus: string;
      momentum: string;
    };
  };
}

export function PillarCard({ pillar }: PillarCardProps) {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'heart-pulse':
        return HeartPulse;
      case 'users-2':
        return Users2;
      case 'briefcase':
        return Briefcase;
      default:
        return HeartPulse;
    }
  };

  const Icon = getIcon(pillar.icon);
  const circumference = 2 * Math.PI * 50;
  const strokeDashoffset = circumference - (pillar.progress / 100) * circumference;

  return (
    <div className="rounded-xl border p-4 hover:shadow-md transition" style={{background: 'rgba(26,29,41,0.5)', backdropFilter: 'blur(10px)', borderColor: 'rgba(244,208,63,0.18)'}}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{background: 'rgba(244,208,63,0.12)', border: '1px solid rgba(244,208,63,0.25)'}}>
            <Icon className="w-5 h-5" style={{color: '#F4D03F'}} />
          </div>
          <div>
            <div className="text-sm font-medium">{pillar.name}</div>
            <div className="text-xs" style={{color: '#B8BCC8'}}>{pillar.description}</div>
          </div>
        </div>
        <div className="relative">
          <svg width="52" height="52" viewBox="0 0 120 120" className="rotate-[-90deg]">
            <circle cx="60" cy="60" r="50" stroke="rgba(244,208,63,0.18)" strokeWidth="12" fill="none" />
            <circle 
              cx="60" 
              cy="60" 
              r="50" 
              stroke="#F4D03F" 
              strokeWidth="12" 
              fill="none" 
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-medium">{pillar.progress}%</span>
          </div>
        </div>
      </div>
      
      <div className="mt-4 grid grid-cols-2 gap-2">
        {pillar.areas.map((area) => (
          <div key={area} className="text-[11px] px-2 py-1 rounded-md border" style={{borderColor: 'rgba(244,208,63,0.18)', color: '#B8BCC8'}}>
            {area}
          </div>
        ))}
      </div>

      {/* Areas within Pillar */}
      {pillar.subareas.length > 0 && (
        <div className="pillar-areas mt-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium" style={{color: '#B8BCC8'}}>Areas within {pillar.name}</h4>
            <button className="text-xs" style={{color: '#F4D03F'}}>Manage Areas</button>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {pillar.subareas.map((subarea) => (
              <div key={subarea.name} className="p-2 rounded-lg border cursor-pointer hover:border-[#F4D03F]/30 transition" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium">{subarea.name}</span>
                  <span className="text-[10px]" style={{color: '#B8BCC8'}}>{subarea.progress}%</span>
                </div>
                <div className="h-1 mt-1 rounded-full overflow-hidden" style={{background: 'rgba(26,29,41,0.6)'}}>
                  <div className="h-full" style={{width: `${subarea.progress}%`, background: 'linear-gradient(90deg, #F4D03F, #F7DC6F)'}}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategic Health Breakdown + Actions */}
      <div className="grid grid-cols-3 gap-2 mt-4">
        <div className="text-center p-2 rounded border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs font-medium" style={{color: '#F4D03F'}}>Alignment</div>
          <div className="text-[10px]" style={{color: '#B8BCC8'}}>{pillar.metrics.alignment}%</div>
        </div>
        <div className="text-center p-2 rounded border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs font-medium" style={{color: '#F4D03F'}}>Focus</div>
          <div className="text-[10px]" style={{color: '#B8BCC8'}}>{pillar.metrics.focus}</div>
        </div>
        <div className="text-center p-2 rounded border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs font-medium" style={{color: '#F4D03F'}}>Momentum</div>
          <div className="text-[10px]" style={{color: '#10B981'}}>{pillar.metrics.momentum}</div>
        </div>
      </div>
      
      <div className="mt-4 pt-3 border-t" style={{borderColor: 'rgba(244,208,63,0.1)'}}>
        <div className="flex items-center justify-between">
          <span className="text-xs" style={{color: '#B8BCC8'}}>Strategic Actions</span>
          <div className="flex gap-1">
            <button className="text-[10px] px-2 py-1 rounded border hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
              Set Goals
            </button>
            <button className="text-[10px] px-2 py-1 rounded border hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
              Analyze
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}