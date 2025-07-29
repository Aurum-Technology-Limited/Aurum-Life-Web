import React, { useState, useEffect, memo } from 'react';
import { BarChart3, Target, CheckCircle, FolderOpen, TrendingUp, Clock, Lightbulb, ArrowRight, Users, Folder, List } from 'lucide-react';

const Insights = memo(() => {
  const [loading, setLoading] = useState(true);
  const [insightsData, setInsightsData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlignmentSnapshot();
  }, []);

  const fetchAlignmentSnapshot = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${backendUrl}/api/insights`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      // Extract alignment_snapshot from the insights response
      setAlignmentSnapshot(data.alignment_snapshot || data);
      setError(null);
    } catch (err) {
      console.error('Error fetching alignment snapshot:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-64 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="h-32 bg-gray-800 rounded-lg"></div>
              <div className="h-32 bg-gray-800 rounded-lg"></div>
            </div>
            <div className="h-96 bg-gray-800 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 text-white p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <BarChart3 className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-300 mb-2">Unable to Load Insights</h2>
            <p className="text-gray-500 mb-4">{error}</p>
            <button
              onClick={fetchAlignmentSnapshot}
              className="px-4 py-2 bg-yellow-500 text-gray-900 rounded-lg hover:bg-yellow-400 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { lifetime_stats, pillar_alignment, generated_at } = alignmentSnapshot || {};

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="h-8 w-8 text-yellow-500" />
            <h1 className="text-3xl font-bold text-white">Insights & Analytics</h1>
          </div>
          <p className="text-gray-400">Your alignment snapshot • See how your actions connect to your pillars</p>
          {generated_at && (
            <div className="flex items-center gap-2 mt-2 text-sm text-gray-500">
              <Clock className="h-4 w-4" />
              <span>Last updated: {new Date(generated_at).toLocaleString()}</span>
            </div>
          )}
        </div>

        {/* Lifetime Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="h-6 w-6 text-green-500" />
              <h2 className="text-xl font-semibold text-white">Tasks Completed</h2>
            </div>
            <div className="text-4xl font-bold text-green-500 mb-2">
              {lifetime_stats?.total_tasks_completed || 0}
            </div>
            <p className="text-gray-400">Total tasks you've completed</p>
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <FolderOpen className="h-6 w-6 text-blue-500" />
              <h2 className="text-xl font-semibold text-white">Projects Completed</h2>
            </div>
            <div className="text-4xl font-bold text-blue-500 mb-2">
              {lifetime_stats?.total_projects_completed || 0}
            </div>
            <p className="text-gray-400">Total projects you've finished</p>
          </div>
        </div>

        {/* Pillar Alignment Distribution */}
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-6">
            <Target className="h-6 w-6 text-yellow-500" />
            <h2 className="text-xl font-semibold text-white">Pillar Alignment</h2>
          </div>

          {pillar_alignment && pillar_alignment.length > 0 ? (
            <div className="space-y-4">
              <p className="text-gray-400 mb-4">
                Distribution of your completed tasks across life pillars
              </p>
              
              {pillar_alignment.map((pillar, index) => (
                <div key={pillar.pillar_id} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-white font-medium">{pillar.pillar_name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400 text-sm">
                        {pillar.task_count} tasks
                      </span>
                      <span className="text-yellow-500 font-semibold">
                        {pillar.percentage}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-800 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-500 ${
                        index === 0 ? 'bg-yellow-500' :
                        index === 1 ? 'bg-blue-500' :
                        index === 2 ? 'bg-green-500' :
                        index === 3 ? 'bg-purple-500' :
                        'bg-gray-600'
                      }`}
                      style={{ width: `${pillar.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-300 mb-2">No Data Yet</h3>
              <p className="text-gray-500">
                Complete some tasks to see your pillar alignment distribution
              </p>
            </div>
          )}
        </div>

        {/* Action Prompt */}
        {pillar_alignment && pillar_alignment.length > 0 && (
          <div className="mt-8 bg-gray-900 border border-yellow-500/30 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <Target className="h-6 w-6 text-yellow-500 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Alignment Insight</h3>
                <p className="text-gray-300">
                  {pillar_alignment[0]?.percentage > 50 ? (
                    <>
                      You're heavily focused on <strong>{pillar_alignment[0]?.pillar_name}</strong> ({pillar_alignment[0]?.percentage}% of completed tasks). 
                      Consider if this aligns with your current priorities.
                    </>
                  ) : (
                    <>
                      Your effort is well-distributed across pillars. Your top focus is <strong>{pillar_alignment[0]?.pillar_name}</strong> at {pillar_alignment[0]?.percentage}%.
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

Insights.displayName = 'Insights';

export default Insights;