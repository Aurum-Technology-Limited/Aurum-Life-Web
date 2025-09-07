import React from 'react';
import { Sparkles, TrendingUp, AlertTriangle, Lightbulb } from 'lucide-react';

/**
 * AI Insights component showing AI-generated recommendations
 * Converted from TypeScript to JavaScript
 */
const AIInsights = () => {
  const insights = [
    {
      id: 1,
      type: 'recommendation',
      title: 'Focus on Health Pillar',
      description: 'Your health pillar shows declining momentum. Consider adding more training sessions.',
      icon: TrendingUp,
      priority: 'high',
      action: 'View Details'
    },
    {
      id: 2,
      type: 'warning',
      title: 'Project Overload',
      description: 'You have 8 active projects. Consider consolidating or pausing some.',
      icon: AlertTriangle,
      priority: 'medium',
      action: 'Optimize'
    },
    {
      id: 3,
      type: 'insight',
      title: 'Peak Productivity',
      description: 'You\'re most productive between 9-11 AM. Schedule important tasks then.',
      icon: Lightbulb,
      priority: 'low',
      action: 'Learn More'
    }
  ];

  const getTypeColor = (type) => {
    switch (type) {
      case 'recommendation': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'insight': return '#3B82F6';
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
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" style={{color: '#F4D03F'}} />
          <h3 className="text-lg font-semibold">AI Insights</h3>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-sm" style={{color: '#10B981'}}>Active</span>
        </div>
      </div>
      
      <div className="space-y-4">
        {insights.map((insight) => {
          const Icon = insight.icon;
          return (
            <div 
              key={insight.id} 
              className="p-4 rounded-lg border hover:opacity-90 transition cursor-pointer"
              style={{
                borderColor: 'rgba(244,208,63,0.15)', 
                background: 'rgba(11,13,20,0.35)'
              }}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" 
                  style={{
                    background: `${getTypeColor(insight.type)}20`,
                    border: `1px solid ${getTypeColor(insight.type)}40`
                  }}
                >
                  <Icon className="w-4 h-4" style={{color: getTypeColor(insight.type)}} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-medium">{insight.title}</h4>
                    <div 
                      className="text-xs px-2 py-1 rounded" 
                      style={{
                        background: `${getPriorityColor(insight.priority)}20`,
                        color: getPriorityColor(insight.priority)
                      }}
                    >
                      {insight.priority}
                    </div>
                  </div>
                  <p className="text-xs mb-2" style={{color: '#B8BCC8'}}>
                    {insight.description}
                  </p>
                  <button 
                    className="text-xs font-medium px-3 py-1 rounded border hover:opacity-90" 
                    style={{
                      borderColor: 'rgba(244,208,63,0.25)', 
                      color: '#F4D03F'
                    }}
                  >
                    {insight.action}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t" style={{borderColor: 'rgba(244,208,63,0.1)'}}>
        <div className="flex items-center justify-between">
          <span className="text-sm" style={{color: '#B8BCC8'}}>Last updated: 2 minutes ago</span>
          <button 
            className="text-sm font-medium px-3 py-1 rounded border hover:opacity-90" 
            style={{
              borderColor: 'rgba(244,208,63,0.25)', 
              color: '#F4D03F'
            }}
          >
            Refresh Insights
          </button>
        </div>
      </div>
    </div>
  );
};

export { AIInsights };
