import React from 'react';
import { BarChart3, TrendingUp, Target, Clock } from 'lucide-react';

/**
 * Strategic Metrics component showing key performance indicators
 * Converted from TypeScript to JavaScript
 */
const StrategicMetrics = () => {
  const metrics = [
    {
      title: 'Strategic Alignment',
      value: '72%',
      change: '+6%',
      trend: 'up',
      icon: Target,
      color: '#F4D03F'
    },
    {
      title: 'Focus Efficiency',
      value: '84%',
      change: '+2%',
      trend: 'up',
      icon: Clock,
      color: '#10B981'
    },
    {
      title: 'Goal Progress',
      value: '68%',
      change: '+12%',
      trend: 'up',
      icon: TrendingUp,
      color: '#3B82F6'
    },
    {
      title: 'System Health',
      value: '91%',
      change: '+1%',
      trend: 'up',
      icon: BarChart3,
      color: '#8B5CF6'
    }
  ];

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
        <h3 className="text-xl font-semibold">Strategic Metrics</h3>
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5" style={{color: '#F4D03F'}} />
          <span className="text-sm" style={{color: '#B8BCC8'}}>Last 30 days</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div 
              key={index} 
              className="p-3 lg:p-4 rounded-lg border hover:opacity-90 transition-all duration-200 hover:scale-[1.02]"
              style={{
                borderColor: 'rgba(244,208,63,0.15)', 
                background: 'rgba(11,13,20,0.35)'
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <Icon className="w-5 h-5" style={{color: metric.color}} />
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" style={{color: '#10B981'}} />
                  <span className="text-xs" style={{color: '#10B981'}}>{metric.change}</span>
                </div>
              </div>
              <div className="text-2xl font-bold mb-1" style={{color: metric.color}}>
                {metric.value}
              </div>
              <div className="text-sm" style={{color: '#B8BCC8'}}>
                {metric.title}
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-6">
        <h4 className="text-sm font-medium mb-3" style={{color: '#B8BCC8'}}>Alignment Trend</h4>
        <div className="h-32 bg-gradient-to-r from-yellow-400/10 to-yellow-600/10 rounded-lg flex items-center justify-center">
          <div className="text-sm" style={{color: '#B8BCC8'}}>Chart visualization placeholder</div>
        </div>
      </div>
    </div>
  );
};

export { StrategicMetrics };
