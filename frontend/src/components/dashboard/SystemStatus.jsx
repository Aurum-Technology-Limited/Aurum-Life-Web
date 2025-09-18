import React from 'react';

/**
 * System Status component showing health metrics
 * Converted from TypeScript to JavaScript
 */
const SystemStatus = () => {
  return (
    <div 
      className="rounded-2xl border p-6" 
      style={{
        background: 'rgba(26,29,41,0.4)', 
        backdropFilter: 'blur(12px)', 
        borderColor: 'rgba(244,208,63,0.2)'
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">System Status</h3>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-sm" style={{color: '#10B981'}}>Healthy</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-2xl font-bold" style={{color: '#F4D03F'}}>72%</div>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Alignment</div>
          <div className="text-xs" style={{color: '#10B981'}}>+6%</div>
        </div>
        <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-2xl font-bold" style={{color: '#F4D03F'}}>5h 20m</div>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Focus Budget</div>
        </div>
        <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-2xl font-bold" style={{color: '#F4D03F'}}>14</div>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Tasks Done</div>
        </div>
        <div className="text-center p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-2xl font-bold" style={{color: '#F4D03F'}}>9</div>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Streak</div>
          <div className="text-xs" style={{color: '#B8BCC8'}}>days</div>
        </div>
      </div>
      
      <div className="mt-4">
        <h4 className="text-sm font-medium mb-2" style={{color: '#B8BCC8'}}>Alignment Trend</h4>
        <div className="h-16 bg-gradient-to-r from-yellow-400/20 to-yellow-600/20 rounded-lg flex items-end justify-center">
          <div className="text-xs" style={{color: '#B8BCC8'}}>Chart placeholder</div>
        </div>
      </div>
    </div>
  );
};

export { SystemStatus };
