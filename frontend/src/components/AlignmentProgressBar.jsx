import React, { useEffect, useState, useCallback } from 'react';
import { alignmentScoreAPI } from '../services/api';

const AlignmentProgressBar = () => {
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      const resp = await alignmentScoreAPI.getDashboardData();
      const data = resp?.data || {};
      const val = Number(data?.alignment_score || data?.score || 0);
      setScore(Number.isFinite(val) ? Math.max(0, Math.min(100, val)) : 0);
    } catch (e) {
      console.warn('Alignment score load failed', e);
      setScore(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="w-full mb-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-white font-semibold">Alignment Score</h2>
        <span className="text-gray-400 text-sm">{loading ? '—' : `${score}%`}</span>
      </div>
      <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
        <div
          className="h-3 bg-yellow-500 transition-all duration-500"
          style={{ width: `${loading ? 0 : score}%` }}
        />
      </div>
    </div>
  );
};

export default AlignmentProgressBar;