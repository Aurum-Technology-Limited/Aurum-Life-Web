import React, { useState, useEffect, memo } from 'react';
import { BarChart3, Target, CheckCircle, FolderOpen, TrendingUp, Clock, Lightbulb, ArrowRight, Users, Folder, List } from 'lucide-react';
import { insightsAPI, insightsDrilldownAPI } from '../services/api';

const Insights = memo(() => {
  const [loading, setLoading] = useState(true);
  const [insightsData, setInsightsData] = useState(null);
  const [error, setError] = useState(null);
  const [drilldown, setDrilldown] = useState({ type: null, payload: null, loading: false, items: [] });

  useEffect(() => {
    fetchAlignmentSnapshot();
  }, []);

  const fetchAlignmentSnapshot = async () => {
    try {
      setLoading(true);
      console.log('🚀 Insights component: Using insightsAPI service with ultra-performance...');
      
      // Use the insightsAPI service which includes ultra-performance optimization
      const response = await insightsAPI.getInsights('all_time');
      
      console.log('✅ Insights component: Successfully fetched via insightsAPI service');
      setInsightsData(response.data);
      setError(null);
    } catch (err) {
      console.error('❌ Insights component: Failed to fetch insights:', err);
      setError(err.message || 'Failed to fetch insights');
      setInsightsData(null);
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

  const { alignment_snapshot, productivity_trends, area_distribution, alignment_progress, eisenhower_matrix, insights_text, recommendations, generated_at } = insightsData || {};

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

        {/* Enhanced Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="h-6 w-6 text-green-500" />
              <h2 className="text-lg font-semibold text-white">Tasks Completed</h2>
            </div>
            <div className="text-3xl font-bold text-green-500 mb-2">
              {alignment_snapshot?.total_tasks_completed || 0}
            </div>
            <p className="text-gray-400 text-sm">
              of {alignment_snapshot?.total_tasks || 0} total tasks
            </p>
            {alignment_snapshot?.completion_rate && (
              <div className="mt-2">
                <div className="text-xs text-gray-500 mb-1">Completion Rate</div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${alignment_snapshot.completion_rate}%` }}
                  ></div>
                </div>
                <div className="text-xs text-green-400 mt-1">{alignment_snapshot.completion_rate}%</div>
              </div>
            )}
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <FolderOpen className="h-6 w-6 text-blue-500" />
              <h2 className="text-lg font-semibold text-white">Projects Completed</h2>
            </div>
            <div className="text-3xl font-bold text-blue-500 mb-2">
              {alignment_snapshot?.total_projects_completed || 0}
            </div>
            <p className="text-gray-400 text-sm">
              of {alignment_snapshot?.total_projects || 0} total projects
            </p>
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="h-6 w-6 text-purple-500" />
              <h2 className="text-lg font-semibold text-white">This Week</h2>
            </div>
            <div className="text-3xl font-bold text-purple-500 mb-2">
              {productivity_trends?.this_week || 0}%
            </div>
            <p className="text-gray-400 text-sm">Productivity score</p>
            {productivity_trends?.trend && (
              <div className="text-xs text-purple-400 mt-1">
                Trend: {productivity_trends.trend}
              </div>
            )}
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Target className="h-6 w-6 text-yellow-500" />
              <h2 className="text-lg font-semibold text-white">Active Pillars</h2>
            </div>
            <div className="text-3xl font-bold text-yellow-500 mb-2">
              {alignment_snapshot?.pillar_alignment?.length || 0}
            </div>
            <p className="text-gray-400 text-sm">Life pillars with activity</p>
          </div>
        </div>

        {/* Eisenhower Matrix (Urgency vs Importance) */}
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="h-6 w-6 text-red-500" />
            <h2 className="text-xl font-semibold text-white">Eisenhower Matrix</h2>
          </div>

          {eisenhower_matrix ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-3">Active Tasks</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-gray-900 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Urgent & Important</div>
                    <button
                      onClick={async () => {
                        setDrilldown({ type: 'matrix', payload: { quadrant: 'urgent_important' }, loading: true, items: [] });
                        try {
                          const resp = await insightsDrilldownAPI.getEisenhowerTasks('urgent_important', 'active');
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'urgent_important' }, loading: false, items: resp.data.tasks || [] });
                        } catch (e) {
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'urgent_important' }, loading: false, items: [], error: e?.message });
                        }
                      }}
                      className="text-2xl font-bold text-red-400 hover:underline"
                    >
                      {eisenhower_matrix.active_counts?.urgent_important || 0}
                    </button>
                  </div>
                  <div className="bg-gray-900 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Important & Not Urgent</div>
                    <button
                      onClick={async () => {
                        setDrilldown({ type: 'matrix', payload: { quadrant: 'important_not_urgent' }, loading: true, items: [] });
                        try {
                          const resp = await insightsDrilldownAPI.getEisenhowerTasks('important_not_urgent', 'active');
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'important_not_urgent' }, loading: false, items: resp.data.tasks || [] });
                        } catch (e) {
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'important_not_urgent' }, loading: false, items: [], error: e?.message });
                        }
                      }}
                      className="text-2xl font-bold text-green-400 hover:underline"
                    >
                      {eisenhower_matrix.active_counts?.important_not_urgent || 0}
                    </button>
                  </div>
                  <div className="bg-gray-900 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Urgent & Not Important</div>
                    <button
                      onClick={async () => {
                        setDrilldown({ type: 'matrix', payload: { quadrant: 'urgent_not_important' }, loading: true, items: [] });
                        try {
                          const resp = await insightsDrilldownAPI.getEisenhowerTasks('urgent_not_important', 'active');
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'urgent_not_important' }, loading: false, items: resp.data.tasks || [] });
                        } catch (e) {
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'urgent_not_important' }, loading: false, items: [], error: e?.message });
                        }
                      }}
                      className="text-2xl font-bold text-yellow-400 hover:underline"
                    >
                      {eisenhower_matrix.active_counts?.urgent_not_important || 0}
                    </button>
                  </div>
                  <div className="bg-gray-900 p-3 rounded border border-gray-700">
                    <div className="text-xs text-gray-400 mb-1">Not Urgent & Not Important</div>
                    <button
                      onClick={async () => {
                        setDrilldown({ type: 'matrix', payload: { quadrant: 'not_urgent_not_important' }, loading: true, items: [] });
                        try {
                          const resp = await insightsDrilldownAPI.getEisenhowerTasks('not_urgent_not_important', 'active');
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'not_urgent_not_important' }, loading: false, items: resp.data.tasks || [] });
                        } catch (e) {
                          setDrilldown({ type: 'matrix', payload: { quadrant: 'not_urgent_not_important' }, loading: false, items: [], error: e?.message });
                        }
                      }}
                      className="text-2xl font-bold text-gray-400 hover:underline"
                    >
                      {eisenhower_matrix.active_counts?.not_urgent_not_important || 0}
                    </button>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-white font-semibold mb-3">Trend (Last 6 Weeks)</h3>
                <div className="space-y-2">
                  {Array.isArray(eisenhower_matrix.trends) && eisenhower_matrix.trends.length > 0 ? (
                    eisenhower_matrix.trends.map((w) => (
                      <div key={w.week_start} className="flex items-center justify-between text-sm">
                        <div className="text-gray-400 w-40">Week of {w.week_start}</div>
                        <div className="flex items-center gap-3">
                          <span className="text-red-400">UI: {w.urgent_important}</span>
                          <span className="text-green-400">IN-U: {w.important_not_urgent}</span>
                          <span className="text-yellow-400">UN-I: {w.urgent_not_important}</span>
                          <span className="text-gray-400">NN: {w.not_urgent_not_important}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-500">No trend data yet</div>
                  )}
                </div>
                <div className="mt-3 text-xs text-gray-400">
                  Behavior: {eisenhower_matrix.behavior_summary?.message} (Reactive Index {eisenhower_matrix.behavior_summary?.reactive_index || 0}%)
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">No matrix data available</div>
          )}
        </div>

        {/* Enhanced Pillar Alignment Distribution */}
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Target className="h-6 w-6 text-yellow-500" />
            <h2 className="text-xl font-semibold text-white">Pillar Alignment Distribution</h2>
          </div>

          {alignment_snapshot?.pillar_alignment && alignment_snapshot.pillar_alignment.length > 0 ? (
            <div className="space-y-4">
              <p className="text-gray-400 mb-4">
                How your {alignment_snapshot.total_tasks_completed} completed tasks are distributed across your life pillars
              </p>
              
              {alignment_snapshot.pillar_alignment.map((pillar, index) => (
                <div key={pillar.pillar_id} className="space-y-3 p-4 bg-gray-800 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-3">
                      <div 
                        className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                        style={{ backgroundColor: pillar.pillar_color }}
                      >
                        {pillar.pillar_icon}
                      </div>
                      <div>
                        <h3 className="text-white font-semibold text-lg">{pillar.pillar_name}</h3>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <Folder className="h-3 w-3" />
                            {pillar.areas_count} areas
                          </span>
                          <span className="flex items-center gap-1">
                            <List className="h-3 w-3" />
                            {pillar.projects_count} projects
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-gray-400 text-sm">
                          {pillar.task_count} tasks
                        </span>
                        <span className="text-yellow-500 font-bold text-lg">
                          {pillar.percentage}%
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        of completed tasks
                      </div>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-700 rounded-full h-4">
                    <div
                      className="h-4 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${pillar.percentage}%`,
                        backgroundColor: pillar.pillar_color
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="h-12 w-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-300 mb-2">No Completed Tasks Yet</h3>
              <p className="text-gray-500">
                Complete some tasks to see your pillar alignment distribution
              </p>
            </div>
          )}
        </div>

        {/* Vertical Alignment Progress */}
        {alignment_progress && Array.isArray(alignment_progress.projects) && alignment_progress.projects.length > 0 && (
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <Target className="h-6 w-6 text-teal-500" />
              <h2 className="text-xl font-semibold text-white">Vertical Alignment Progress</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {alignment_progress.projects.map((p) => (
                <div key={p.project_id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-white font-semibold">{p.project_name}</div>
                    <div className="text-sm text-gray-400">{p.completion_percentage}%</div>
                  </div>
                  <div className="text-xs text-gray-500 mb-2">
                    {p.pillar_name ? (
                      <>via {p.area_name || '—'} → {p.pillar_name}</>
                    ) : (
                      <>Unaligned</>
                    )}
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full transition-all duration-500 bg-teal-500" style={{ width: `${p.completion_percentage}%` }}></div>
                  </div>
                  <div className="mt-2 flex justify-end">
                    <button
                      onClick={async () => {
                        setDrilldown({ type: 'project', payload: { project_id: p.project_id, project_name: p.project_name }, loading: true, items: [] });
                        try {
                          const resp = await insightsDrilldownAPI.getProjectTasks(p.project_id, 'all');
                          setDrilldown({ type: 'project', payload: { project_id: p.project_id, project_name: p.project_name }, loading: false, items: resp.data.tasks || [] });
                        } catch (e) {
                          setDrilldown({ type: 'project', payload: { project_id: p.project_id, project_name: p.project_name }, loading: false, items: [], error: e?.message });
                        }
                      }}
                      className="text-xs text-teal-400 hover:text-teal-300"
                    >
                      View tasks
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Area Distribution (New Section) */}
        {area_distribution && area_distribution.length > 0 && (
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3 mb-6">
              <Users className="h-6 w-6 text-green-500" />
              <h2 className="text-xl font-semibold text-white">Top Performing Areas</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {area_distribution.map((area, index) => (
                <div key={area.area_id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div 
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
                      style={{ backgroundColor: area.area_color }}
                    >
                      {area.area_icon}
                    </div>
                    <div>
                      <h4 className="text-white font-medium">{area.area_name}</h4>
                      <div className="text-xs text-gray-400">
                        {area.projects_count} projects
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">{area.task_count} tasks</span>
                    <span className="text-green-500 font-semibold">{area.percentage}%</span>
                  </div>
                  
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${area.percentage}%`,
                        backgroundColor: area.area_color
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actionable Insights & Recommendations */}
        {(insights_text && insights_text.length > 0) || (recommendations && recommendations.length > 0) ? (
          <div className="space-y-6">
            {/* Insights Text */}
            {insights_text && insights_text.length > 0 && (
              <div className="bg-gray-900 border border-yellow-500/30 rounded-lg p-6">
                <div className="flex items-start gap-3">
                  <Lightbulb className="h-6 w-6 text-yellow-500 mt-1" />
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-3">Key Insights</h3>
                    <div className="space-y-2">
                      {insights_text.map((insight, index) => (
                        <p key={index} className="text-gray-300 leading-relaxed">
                          {insight}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {recommendations && recommendations.length > 0 && (
              <div className="bg-gray-900 border border-blue-500/30 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <ArrowRight className="h-6 w-6 text-blue-500" />
                  <h3 className="text-lg font-semibold text-white">Recommended Actions</h3>
                </div>
                <div className="space-y-4">
                  {recommendations.map((rec, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg p-4 border-l-4 border-blue-500">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-white font-medium">{rec.title}</h4>
                        <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                          {rec.type?.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {rec.description}
                      </p>
                      {rec.count && (
                        <div className="mt-2 text-xs text-blue-400">
                          Count: {rec.count}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : alignment_snapshot?.pillar_alignment && alignment_snapshot.pillar_alignment.length > 0 && (
          <div className="mt-8 bg-gray-900 border border-yellow-500/30 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <Target className="h-6 w-6 text-yellow-500 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Alignment Insight</h3>
                <p className="text-gray-300">
                  {alignment_snapshot.pillar_alignment[0]?.percentage > 50 ? (
                    <>
                      You're heavily focused on <strong>{alignment_snapshot.pillar_alignment[0]?.pillar_name}</strong> ({alignment_snapshot.pillar_alignment[0]?.percentage}% of completed tasks). 
                      Consider if this aligns with your current priorities.
                    </>
                  ) : (
                    <>
                      Your effort is well-distributed across pillars. Your top focus is <strong>{alignment_snapshot.pillar_alignment[0]?.pillar_name}</strong> at {alignment_snapshot.pillar_alignment[0]?.percentage}%.
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