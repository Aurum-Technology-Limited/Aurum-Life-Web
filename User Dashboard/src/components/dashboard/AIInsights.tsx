import React, { useState } from 'react';
import { Sparkles, MessageCircle } from 'lucide-react';

export function AIInsights() {
  const [query, setQuery] = useState('');

  const insights = [
    {
      id: 1,
      message: "Your Work pillar is strong. Schedule 2 x 45min deep-work blocks today to push Alchemy Site over 80% this week.",
      type: "Suggestion",
      impact: "Impact ↑"
    },
    {
      id: 2,
      message: "You're under target on Relationships. Consider adding a 15m check-in ritual after dinner.",
      type: "Alignment",
      impact: "+ Small habit"
    }
  ];

  const handleAskAI = () => {
    if (query.trim()) {
      console.log('AI Query:', query);
      setQuery('');
    }
  };

  return (
    <div className="rounded-2xl border p-5 flex flex-col gap-4" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight">AI Insights</h2>
        <Sparkles className="w-5 h-5" style={{color: '#F4D03F'}} />
      </div>

      <div className="space-y-3">
        {insights.map((insight) => (
          <div key={insight.id} className="rounded-xl border p-3" style={{borderColor: 'rgba(244,208,63,0.18)', background: 'rgba(11,13,20,0.35)'}}>
            <div className="text-sm">
              {insight.message}
            </div>
            <div className="mt-2 flex items-center gap-2">
              <span 
                className="text-[11px] px-2 py-0.5 rounded"
                style={{
                  background: insight.type === 'Suggestion' ? 'rgba(59,130,246,0.15)' : 'rgba(244,208,63,0.15)',
                  color: insight.type === 'Suggestion' ? '#3B82F6' : '#F4D03F'
                }}
              >
                {insight.type}
              </span>
              <span className="text-[11px]" style={{color: '#B8BCC8'}}>
                {insight.impact}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-2">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg border" style={{borderColor: 'rgba(244,208,63,0.2)', background: 'rgba(26,29,41,0.5)'}}>
          <MessageCircle className="w-4 h-4" style={{color: '#B8BCC8'}} />
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask for a plan or insight..." 
            className="w-full bg-transparent text-sm focus:outline-none placeholder:text-[#6B7280]"
            onKeyPress={(e) => e.key === 'Enter' && handleAskAI()}
          />
          <button 
            onClick={handleAskAI}
            className="text-xs px-2 py-1 rounded-md border hover:opacity-90" 
            style={{borderColor: 'rgba(244,208,63,0.25)', color: '#F4D03F'}}
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}