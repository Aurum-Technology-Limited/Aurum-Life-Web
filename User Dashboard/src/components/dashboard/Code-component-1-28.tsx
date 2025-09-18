import React from 'react';
import { PillarCard } from './PillarCard';

export function StrategicOverview() {
  const pillars = [
    {
      id: 'health',
      name: 'Health',
      description: 'Vitality & Longevity',
      icon: 'heart-pulse',
      progress: 68,
      areas: ['Nutrition', 'Training', 'Sleep', 'Recovery'],
      subareas: [
        { name: 'Nutrition', progress: 75 },
        { name: 'Training', progress: 68 }
      ],
      metrics: {
        alignment: 68,
        focus: '4.1h',
        momentum: '+2%'
      }
    },
    {
      id: 'relationships',
      name: 'Relationships',
      description: 'Family & Community',
      icon: 'users-2',
      progress: 54,
      areas: ['Partner', 'Friends', 'Family', 'Community'],
      subareas: [],
      metrics: {
        alignment: 54,
        focus: '2.0h',
        momentum: '+1%'
      }
    },
    {
      id: 'work',
      name: 'Work',
      description: 'Impact & Mastery',
      icon: 'briefcase',
      progress: 76,
      areas: ['Career', 'Learning', 'Portfolio', 'Network'],
      subareas: [],
      metrics: {
        alignment: 76,
        focus: '6.3h',
        momentum: '+4%'
      }
    }
  ];

  return (
    <div className="xl:col-span-2 rounded-2xl border p-5" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Strategic Overview</h2>
          <p className="text-sm" style={{color: '#B8BCC8'}}>Pillars with progress and connected areas</p>
        </div>
        <button className="text-xs px-3 py-1.5 rounded-lg border hover:opacity-90" style={{color: '#F4D03F', borderColor: 'rgba(244,208,63,0.25)'}}>
          Manage Pillars
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {pillars.map((pillar) => (
          <PillarCard key={pillar.id} pillar={pillar} />
        ))}
      </div>
    </div>
  );
}