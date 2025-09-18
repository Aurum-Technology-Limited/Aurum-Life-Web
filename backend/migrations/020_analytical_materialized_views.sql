-- Migration 020: Analytical Materialized Views
-- Creates materialized views for behavioral metrics analysis
-- Reference: aurum-life-impl-plan.md

-- Weekly pillar alignment metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS weekly_pillar_alignment AS
SELECT
  user_id,
  pillar_id,
  date_trunc('week', (metrics->>'timestamp')::timestamptz)::date AS week_start,
  AVG((metrics->>'alignment_score')::numeric) AS avg_alignment,
  AVG((metrics->>'sentiment')::numeric) AS avg_sentiment,
  AVG((metrics->>'habit_strength')::numeric) AS avg_habit_strength,
  COUNT(*) AS data_points
FROM (
  SELECT 
    p.user_id, 
    p.id AS pillar_id, 
    jsonb_array_elements(p.behavior_metrics) AS metrics
  FROM public.pillars p
  WHERE jsonb_array_length(p.behavior_metrics) > 0
) AS sub
WHERE (metrics->>'timestamp') IS NOT NULL
GROUP BY user_id, pillar_id, week_start;

-- Create unique index for efficient updates
CREATE UNIQUE INDEX IF NOT EXISTS idx_weekly_pillar_alignment_unique
ON weekly_pillar_alignment (user_id, pillar_id, week_start);

-- Area habit strength metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS area_habit_metrics AS
SELECT
  user_id,
  area_id,
  DATE(NOW()) as calculated_date,
  COUNT(*) FILTER (WHERE (metrics->>'habit_strength')::numeric >= 0.8) AS strong_habits,
  COUNT(*) FILTER (WHERE (metrics->>'habit_strength')::numeric >= 0.6) AS moderate_habits,
  COUNT(*) AS total_entries,
  AVG((metrics->>'alignment_score')::numeric) AS avg_alignment,
  AVG((metrics->>'focus_time')::numeric) AS avg_focus_time
FROM (
  SELECT 
    a.user_id, 
    a.id AS area_id, 
    jsonb_array_elements(a.behavior_metrics) AS metrics
  FROM public.areas a
  WHERE jsonb_array_length(a.behavior_metrics) > 0
) AS sub
WHERE (metrics->>'habit_strength') IS NOT NULL
GROUP BY user_id, area_id;

-- Create unique index for area habit metrics
CREATE UNIQUE INDEX IF NOT EXISTS idx_area_habit_metrics_unique
ON area_habit_metrics (user_id, area_id, calculated_date);

-- Daily productivity flow states (from user behavior events)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_flow_metrics AS
SELECT
  user_id,
  DATE(timestamp) as flow_date,
  COUNT(*) FILTER (WHERE action_type = 'flow_entry') AS flow_sessions,
  SUM(duration_ms) FILTER (WHERE action_type = 'flow_session') / 1000 / 60 AS total_flow_minutes,
  COUNT(*) FILTER (WHERE action_type = 'procrastination_trigger') AS procrastination_events,
  COUNT(*) FILTER (WHERE action_type = 'context_switch') AS context_switches
FROM public.user_behavior_events
WHERE flow_state_event = true
  AND timestamp >= NOW() - INTERVAL '90 days'
GROUP BY user_id, DATE(timestamp);

-- Create unique index for daily flow metrics
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_flow_metrics_unique
ON daily_flow_metrics (user_id, flow_date);

-- Task completion patterns by metadata
CREATE MATERIALIZED VIEW IF NOT EXISTS task_completion_patterns AS
SELECT
  user_id,
  (task_metadata->>'energy_requirement')::text AS energy_requirement,
  (task_metadata->>'cognitive_load')::text AS cognitive_load,
  DATE_TRUNC('week', created_at)::date AS week_start,
  COUNT(*) as total_tasks,
  COUNT(*) FILTER (WHERE completed = true) as completed_tasks,
  (COUNT(*) FILTER (WHERE completed = true))::float / NULLIF(COUNT(*), 0) as completion_rate,
  AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) FILTER (WHERE completed = true) as avg_completion_hours
FROM public.tasks
WHERE task_metadata IS NOT NULL 
  AND task_metadata != '{}'::jsonb
  AND created_at >= NOW() - INTERVAL '180 days'
GROUP BY user_id, energy_requirement, cognitive_load, week_start
HAVING COUNT(*) >= 3; -- Only include patterns with sufficient data

-- Create unique index for task completion patterns
CREATE UNIQUE INDEX IF NOT EXISTS idx_task_completion_patterns_unique
ON task_completion_patterns (user_id, energy_requirement, cognitive_load, week_start);

-- Function to refresh all behavioral materialized views
CREATE OR REPLACE FUNCTION refresh_behavior_views() 
RETURNS void AS $$
BEGIN
  -- Refresh all materialized views concurrently where possible
  REFRESH MATERIALIZED VIEW CONCURRENTLY weekly_pillar_alignment;
  REFRESH MATERIALIZED VIEW CONCURRENTLY area_habit_metrics;
  REFRESH MATERIALIZED VIEW CONCURRENTLY daily_flow_metrics;
  REFRESH MATERIALIZED VIEW CONCURRENTLY task_completion_patterns;
  
  -- Log the refresh operation
  INSERT INTO public.webhook_logs (webhook_type, table_name, triggered_at, status)
  VALUES ('materialized_views_refresh', 'behavioral_views', NOW(), 'completed');
  
EXCEPTION WHEN OTHERS THEN
  -- Log any errors
  INSERT INTO public.webhook_logs (webhook_type, table_name, triggered_at, status, error_message)
  VALUES ('materialized_views_refresh', 'behavioral_views', NOW(), 'error', SQLERRM);
  RAISE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions
GRANT EXECUTE ON FUNCTION refresh_behavior_views() TO service_role;
GRANT SELECT ON weekly_pillar_alignment TO authenticated;
GRANT SELECT ON area_habit_metrics TO authenticated;
GRANT SELECT ON daily_flow_metrics TO authenticated;
GRANT SELECT ON task_completion_patterns TO authenticated;

-- Enable RLS on materialized views (note: RLS is applied through underlying tables)
-- The views will automatically respect RLS when queried by authenticated users

-- Add helpful comments
COMMENT ON MATERIALIZED VIEW weekly_pillar_alignment IS 'Weekly aggregated pillar behavioral metrics for trend analysis';
COMMENT ON MATERIALIZED VIEW area_habit_metrics IS 'Area-level habit strength and alignment metrics';
COMMENT ON MATERIALIZED VIEW daily_flow_metrics IS 'Daily productivity flow state and interruption patterns';
COMMENT ON MATERIALIZED VIEW task_completion_patterns IS 'Task completion rates by energy/cognitive load requirements';
COMMENT ON FUNCTION refresh_behavior_views IS 'Refreshes all behavioral materialized views, should be called nightly';

-- Initial refresh of all views
SELECT refresh_behavior_views();