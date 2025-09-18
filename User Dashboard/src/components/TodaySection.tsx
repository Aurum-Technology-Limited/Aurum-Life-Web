import React from 'react';

export function TodaySection() {
  const timeBlocks = [
    {
      period: 'Morning',
      activities: [
        'Review weekly goals',
        'Deep work block',
        'Movement break'
      ]
    },
    {
      period: 'Afternoon',
      activities: [
        'Meetings',
        'Project review',
        'Learning sprint'
      ]
    },
    {
      period: 'Evening',
      activities: [
        'Family walk',
        'Journal reflection',
        'Plan tomorrow'
      ]
    }
  ];

  return (
    <div className="rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-2xl font-semibold tracking-tight">Today</h2>
        <div className="text-sm" style={{color: '#B8BCC8'}}>
          Focus budget: <span className="text-white font-medium">5h 20m</span>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {timeBlocks.map((block) => (
          <div key={block.period} className="rounded-xl border p-4" style={{borderColor: 'rgba(244,208,63,0.18)', background: 'rgba(11,13,20,0.35)'}}>
            <div className="text-sm mb-2" style={{color: '#B8BCC8'}}>{block.period}</div>
            <ul className="space-y-2 text-sm">
              {block.activities.map((activity, index) => (
                <li key={index}>• {activity}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}