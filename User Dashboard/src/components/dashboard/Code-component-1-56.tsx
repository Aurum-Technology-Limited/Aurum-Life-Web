import React from 'react';

export function StrategicIntelligence() {
  const pillarBalance = [
    { name: 'Work', percentage: 40, status: 'Optimal', color: '#10B981' },
    { name: 'Health', percentage: 30, status: 'Under-invested', color: '#F59E0B' },
    { name: 'Relationships', percentage: 20, status: 'Critical', color: '#EF4444' }
  ];

  const recommendations = [
    {
      title: 'Boost Health Investment',
      description: 'Add 2h weekly to reach optimal 35% allocation',
      actionLabel: 'Schedule'
    },
    {
      title: 'Relationships Crisis',
      description: 'Schedule 3x 30min family time this week',
      actionLabel: 'Plan'
    }
  ];

  return (
    <div className="strategic-intelligence-panel rounded-2xl border p-5 mt-6" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <h3 className="text-lg font-semibold mb-4 tracking-tight">Strategic Intelligence</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pillar Balance Analysis */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium" style={{color: '#B8BCC8'}}>Pillar Balance Analysis</h4>
          <div className="space-y-3">
            {pillarBalance.map((pillar) => (
              <div key={pillar.name} className="flex items-center justify-between p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{background: pillar.color}}></div>
                  <span className="text-sm">{pillar.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">{pillar.percentage}%</div>
                  <div className="text-xs" style={{color: pillar.color}}>{pillar.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strategic Recommendations */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium" style={{color: '#B8BCC8'}}>Strategic Recommendations</h4>
          <div className="space-y-3">
            {recommendations.map((recommendation, index) => (
              <div key={index} className="p-3 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.18)', background: 'rgba(11,13,20,0.35)'}}>
                <div className="text-sm font-medium mb-1">{recommendation.title}</div>
                <div className="text-xs mb-2" style={{color: '#B8BCC8'}}>{recommendation.description}</div>
                <button className="text-xs px-2 py-1 rounded border hover:opacity-90" style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}>
                  {recommendation.actionLabel}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}