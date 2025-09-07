import React from 'react';
import { CheckCircle, Clock, Target } from 'lucide-react';

/**
 * Today's Focus component showing daily priorities
 * Converted from TypeScript to JavaScript
 */
const TodaysFocus = () => {
  const focusItems = [
    { id: 1, text: 'Complete strategic project assessment', priority: 'high', completed: false, time: '2h' },
    { id: 2, text: 'Review pillar alignment metrics', priority: 'medium', completed: true, time: '30m' },
    { id: 3, text: 'Plan next week\'s focus areas', priority: 'high', completed: false, time: '1h' },
    { id: 4, text: 'Update project status dashboard', priority: 'low', completed: false, time: '45m' }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#EF4444';
      case 'medium': return '#F59E0B';
      case 'low': return '#6B7280';
      default: return '#6B7280';
    }
  };

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
        <h3 className="text-lg font-semibold">Today's Focus</h3>
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4" style={{color: '#F4D03F'}} />
          <span className="text-sm" style={{color: '#B8BCC8'}}>4 items</span>
        </div>
      </div>
      
      <div className="space-y-3">
        {focusItems.map((item) => (
          <div 
            key={item.id} 
            className={`flex items-center gap-3 p-3 rounded-lg border transition ${
              item.completed ? 'opacity-60' : 'hover:opacity-90'
            }`}
            style={{
              borderColor: 'rgba(244,208,63,0.15)', 
              background: 'rgba(11,13,20,0.35)'
            }}
          >
            <div className="flex-shrink-0">
              {item.completed ? (
                <CheckCircle className="w-5 h-5" style={{color: '#10B981'}} />
              ) : (
                <div 
                  className="w-5 h-5 rounded-full border-2" 
                  style={{borderColor: getPriorityColor(item.priority)}}
                />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className={`text-sm ${item.completed ? 'line-through' : ''}`} style={{color: '#B8BCC8'}}>
                {item.text}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <div 
                  className="text-xs px-2 py-1 rounded" 
                  style={{
                    background: `${getPriorityColor(item.priority)}20`,
                    color: getPriorityColor(item.priority)
                  }}
                >
                  {item.priority}
                </div>
                <div className="flex items-center gap-1 text-xs" style={{color: '#6B7280'}}>
                  <Clock className="w-3 h-3" />
                  {item.time}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t" style={{borderColor: 'rgba(244,208,63,0.1)'}}>
        <div className="flex items-center justify-between">
          <span className="text-sm" style={{color: '#B8BCC8'}}>Focus Time Remaining</span>
          <span className="text-sm font-medium" style={{color: '#F4D03F'}}>4h 15m</span>
        </div>
        <div className="mt-2 h-2 rounded-full overflow-hidden" style={{background: 'rgba(26,29,41,0.6)'}}>
          <div 
            className="h-full" 
            style={{
              width: '65%', 
              background: 'linear-gradient(90deg, #F4D03F, #F7DC6F)'
            }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export { TodaysFocus };
