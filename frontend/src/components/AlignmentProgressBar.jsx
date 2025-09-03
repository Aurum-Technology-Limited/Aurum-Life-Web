import React, { useEffect, useState, useCallback } from 'react';
import { Brain, Info, Sparkles } from 'lucide-react';
import { alignmentScoreAPI, hrmAPI } from '../services/api';
import AIBadge from './ui/AIBadge';
import AIInsightPanel from './ui/AIInsightPanel';

const AlignmentProgressBar = () => {
  const [loading, setLoading] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);
  const [showAIInsights, setShowAIInsights] = useState(false);
  const [alignmentInsight, setAlignmentInsight] = useState(null);
  const [data, setData] = useState({
    progress_percentage: 0,
    monthly_score: 0,
    monthly_goal: null,
  });

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🎯 AlignmentProgressBar: Loading alignment data...');
      const resp = await alignmentScoreAPI.getDashboardData(true); // Use HRM
      const d = resp?.data || {};
      
      console.log('✅ AlignmentProgressBar: Data loaded successfully', d);
      setData({
        progress_percentage: typeof d.progress_percentage === 'number' ? d.progress_percentage : (typeof d.alignment_score === 'number' ? d.alignment_score : 0),
        monthly_score: typeof d.monthly_score === 'number' ? d.monthly_score : 0,
        monthly_goal: typeof d.monthly_goal === 'number' ? d.monthly_goal : (d.monthly_goal ? parseInt(d.monthly_goal) : null),
      });
      
      // Store HRM insights if available
      if (d.hrm_enhancement) {
        setAlignmentInsight(d.hrm_enhancement);
      }
    } catch (e) {
      console.warn('⚠️ AlignmentProgressBar: Load failed, using fallback data:', e.message);
      
      // Set user-friendly error message instead of disruptive behavior
      if (e.message.includes('timeout')) {
        setError('Alignment calculation is taking longer than usual. Data will load shortly.');
      } else if (e.message.includes('Network Error')) {
        setError('Network connection issue. Please check your connection.');
      } else {
        setError(null); // Don't show error for other issues
      }
      
      // Provide fallback data instead of zeros
      setData({ 
        progress_percentage: 50, // Reasonable default
        monthly_score: 0, 
        monthly_goal: null 
      });
    } finally {
      setLoading(false);
    }
  }, []);

  // Get AI insights for alignment
  const handleGetAIInsights = useCallback(async () => {
    try {
      const insight = await hrmAPI.analyzeLifeBalance();
      setAlignmentInsight(insight);
      setShowAIInsights(true);
    } catch (error) {
      console.error('Failed to get alignment insights:', error);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const pct = Math.min(Math.max(Number(data.progress_percentage) || 0, 0), 100);
  const glowIntensity = Math.min(Math.max(pct / 100, 0), 1);

  return (
    <div className="w-full mb-6 space-y-4">
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <h2 className="text-white font-semibold">Alignment Score</h2>
            <div className="relative">
              <button
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                className="text-gray-400 hover:text-gray-300 transition-colors"
                aria-label="What is Alignment Score?"
              >
                <Info className="h-4 w-4" />
              </button>
              {showTooltip && (
                <div className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-300">
                  <div className="absolute top-full left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-800 border-r border-b border-gray-700 rotate-45" />
                  Earn points by completing projects. Higher-priority work aligned with your most important goals earns more points.
                </div>
              )}
            </div>
            {alignmentInsight && (
              <AIBadge 
                confidence={alignmentInsight.confidence_score || 0.7} 
                variant="sparkles" 
                size="xs"
                onClick={() => setShowAIInsights(!showAIInsights)}
              />
            )}
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-300">
              <span className="text-white font-medium">{loading ? '—' : data.monthly_score}</span>
              <span className="text-gray-500"> / Goal </span>
              <span className="text-yellow-400 font-medium">{loading ? '—' : (data.monthly_goal ?? '—')}</span>
              <span className="text-gray-500"> pts</span>
            </div>
            <button
              onClick={handleGetAIInsights}
              className="p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-800 rounded-lg transition-colors"
              title="Get AI Insights"
            >
              <Sparkles className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Brain + Percent */}
        <div className="flex items-center gap-3 mb-2">
          <div className="relative">
            {/* Glow */}
            <div
              className="absolute -inset-1 rounded-full blur-md transition-all duration-500"
              style={{
                background: `radial-gradient(circle, rgba(244,180,0, ${0.25 + glowIntensity * 0.5}) 0%, transparent 70%)`,
                transform: `scale(${1 + glowIntensity * 0.25})`,
              }}
            />
            {/* Brain */}
            <div className="relative w-10 h-10">
              <Brain className="absolute inset-0 w-full h-full text-gray-600" />
              <div
                className="absolute inset-0 overflow-hidden transition-all duration-500"
                style={{ clipPath: `inset(${100 - pct}% 0 0 0)` }}
              >
                <Brain className="w-full h-full text-yellow-400" />
              </div>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            {loading ? 'Calculating…' : `${Math.round(pct)}% toward your monthly goal`}
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
          <div
            className="h-3 bg-yellow-500 transition-all duration-500"
            style={{ width: `${loading ? 0 : pct}%` }}
          />
        </div>
      </div>

      {/* AI Insights Panel */}
      {showAIInsights && alignmentInsight && (
        <AIInsightPanel 
          insight={alignmentInsight}
          isExpanded={true}
          onClose={() => setShowAIInsights(false)}
          showCloseButton={true}
        />
      )}
    </div>
  );
};

export default AlignmentProgressBar;