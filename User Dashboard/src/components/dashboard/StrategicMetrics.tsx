import React from 'react';

export function StrategicMetrics() {
  return (
    <div className="strategic-metrics-panel rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <h3 className="text-lg font-semibold mb-4 tracking-tight">Strategic Health</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs mb-1" style={{color: '#B8BCC8'}}>Strategic Alignment</div>
          <div className="text-2xl font-semibold" style={{color: '#F4D03F'}}>72%</div>
          <div className="text-[10px]" style={{color: '#10B981'}}>+6% this week</div>
        </div>
        <div className="p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs mb-1" style={{color: '#B8BCC8'}}>Focus Distribution</div>
          <div className="text-sm font-medium">Balanced</div>
          <div className="text-[10px]" style={{color: '#B8BCC8'}}>Work: 40% | Health: 30% | Relationships: 30%</div>
        </div>
        <div className="p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs mb-1" style={{color: '#B8BCC8'}}>Energy Level</div>
          <div className="text-2xl font-semibold" style={{color: '#10B981'}}>High</div>
          <div className="text-[10px]" style={{color: '#B8BCC8'}}>Peak focus time: 2–4 PM</div>
        </div>
        <div className="p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs mb-1" style={{color: '#B8BCC8'}}>Context Switches</div>
          <div className="text-2xl font-semibold" style={{color: '#EF4444'}}>12</div>
          <div className="text-[10px]" style={{color: '#B8BCC8'}}>Target: &lt;8 per day</div>
        </div>
      </div>
    </div>
  );
}