import React from 'react';
import { Brain, AlertCircle, CheckCircle, Lightbulb } from 'lucide-react';

/**
 * Strategic Intelligence component showing AI-powered strategic analysis
 * Converted from TypeScript to JavaScript
 */
const StrategicIntelligence = () => {
  const intelligence = [
    {
      id: 1,
      type: 'balance',
      title: 'Pillar Balance Analysis',
      description: 'Your Health pillar is receiving 40% of focus while Work gets 35%. Consider rebalancing.',
      icon: Brain,
      priority: 'medium',
      recommendation: 'Increase Health focus by 15%'
    },
    {
      id: 2,
      type: 'opportunity',
      title: 'Strategic Opportunity',
      description: 'You have 3 hours of free time tomorrow. Perfect for deep work on your main project.',
      icon: Lightbulb,
      priority: 'high',
      recommendation: 'Block calendar for focused work'
    },
    {
      id: 3,
      type: 'warning',
      title: 'Resource Allocation',
      description: 'You\'re overcommitted on low-impact tasks. Consider delegating or eliminating.',
      icon: AlertCircle,
      priority: 'high',
      recommendation: 'Review and prioritize tasks'
    },
    {
      id: 4,
      type: 'success',
      title: 'Pattern Recognition',
      description: 'You\'re most productive on Tuesdays and Thursdays. Schedule important work then.',
      icon: CheckCircle,
      priority: 'low',
      recommendation: 'Optimize schedule around peak days'
    }
  ];

  const getTypeColor = (type) => {
    switch (type) {
      case 'balance': return '#3B82F6';
      case 'opportunity': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'success': return '#8B5CF6';
      default: return '#6B7280';
    }
  };

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
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Brain className="w-6 h-6" style={{color: '#F4D03F'}} />
          <h3 className="text-xl font-semibold">Strategic Intelligence</h3>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-sm" style={{color: '#10B981'}}>AI Active</span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {intelligence.map((item) => {
          const Icon = item.icon;
          return (
            <div 
              key={item.id} 
              className="p-4 rounded-lg border hover:opacity-90 transition cursor-pointer"
              style={{
                borderColor: 'rgba(244,208,63,0.15)', 
                background: 'rgba(11,13,20,0.35)'
              }}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" 
                  style={{
                    background: `${getTypeColor(item.type)}20`,
                    border: `1px solid ${getTypeColor(item.type)}40`
                  }}
                >
                  <Icon className="w-5 h-5" style={{color: getTypeColor(item.type)}} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="text-sm font-medium">{item.title}</h4>
                    <div 
                      className="text-xs px-2 py-1 rounded" 
                      style={{
                        background: `${getPriorityColor(item.priority)}20`,
                        color: getPriorityColor(item.priority)
                      }}
                    >
                      {item.priority}
                    </div>
                  </div>
                  <p className="text-xs mb-3" style={{color: '#B8BCC8'}}>
                    {item.description}
                  </p>
                  <div className="p-2 rounded border" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.2)'}}>
                    <div className="text-xs font-medium mb-1" style={{color: '#F4D03F'}}>Recommendation:</div>
                    <div className="text-xs" style={{color: '#B8BCC8'}}>{item.recommendation}</div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-6 pt-4 border-t" style={{borderColor: 'rgba(244,208,63,0.1)'}}>
        <div className="flex items-center justify-between">
          <span className="text-sm" style={{color: '#B8BCC8'}}>Analysis updated 5 minutes ago</span>
          <button 
            className="text-sm font-medium px-4 py-2 rounded-lg border hover:opacity-90" 
            style={{
              borderColor: 'rgba(244,208,63,0.25)', 
              color: '#F4D03F'
            }}
          >
            Generate New Analysis
          </button>
        </div>
      </div>
    </div>
  );
};

export { StrategicIntelligence };
