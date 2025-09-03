-- Migration 014: Setup Performance Webhooks
-- Configure database triggers and webhooks for real-time performance optimization

-- ===================================
-- 1. JOURNAL ENTRY SENTIMENT ANALYSIS WEBHOOK
-- ===================================

-- Function to trigger sentiment analysis webhook
CREATE OR REPLACE FUNCTION trigger_journal_sentiment_analysis()
RETURNS TRIGGER AS $$
BEGIN
  -- Only process if content exists and hasn't been analyzed
  IF NEW.content IS NOT NULL AND NEW.content != '' AND NEW.sentiment_score IS NULL THEN
    -- Call webhook to trigger background sentiment analysis
    PERFORM pg_notify('journal_entry_webhook', json_build_object(
      'table', 'journal_entries',
      'action', 'created',
      'record', json_build_object(
        'id', NEW.id,
        'user_id', NEW.user_id,
        'content', NEW.content,
        'created_at', NEW.created_at
      )
    )::text);
    
    -- Log the webhook trigger
    INSERT INTO webhook_logs (
      webhook_type, 
      user_id, 
      table_name, 
      record_id, 
      triggered_at
    ) VALUES (
      'journal_sentiment_analysis',
      NEW.user_id,
      'journal_entries',
      NEW.id,
      NOW()
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for journal entries
DROP TRIGGER IF EXISTS journal_sentiment_webhook_trigger ON journal_entries;
CREATE TRIGGER journal_sentiment_webhook_trigger
  AFTER INSERT ON journal_entries
  FOR EACH ROW EXECUTE FUNCTION trigger_journal_sentiment_analysis();

-- ===================================
-- 2. ALIGNMENT SCORE RECALCULATION WEBHOOKS
-- ===================================

-- Function to trigger alignment recalculation
CREATE OR REPLACE FUNCTION trigger_alignment_recalculation()
RETURNS TRIGGER AS $$
DECLARE
  affected_user_id UUID;
BEGIN
  -- Determine affected user ID
  affected_user_id := COALESCE(NEW.user_id, OLD.user_id);
  
  IF affected_user_id IS NOT NULL THEN
    -- Notify alignment recalculation webhook
    PERFORM pg_notify('alignment_recalc_webhook', json_build_object(
      'table', TG_TABLE_NAME,
      'action', TG_OP,
      'record', json_build_object(
        'user_id', affected_user_id,
        'id', COALESCE(NEW.id, OLD.id),
        'updated_at', NOW()
      )
    )::text);
    
    -- Log the webhook trigger
    INSERT INTO webhook_logs (
      webhook_type, 
      user_id, 
      table_name, 
      record_id, 
      triggered_at
    ) VALUES (
      'alignment_recalculation',
      affected_user_id,
      TG_TABLE_NAME,
      COALESCE(NEW.id, OLD.id),
      NOW()
    );
  END IF;
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply alignment webhook to key tables
DROP TRIGGER IF EXISTS alignment_tasks_webhook ON tasks;
CREATE TRIGGER alignment_tasks_webhook
  AFTER INSERT OR UPDATE OR DELETE ON tasks
  FOR EACH ROW EXECUTE FUNCTION trigger_alignment_recalculation();

DROP TRIGGER IF EXISTS alignment_projects_webhook ON projects;
CREATE TRIGGER alignment_projects_webhook
  AFTER INSERT OR UPDATE OR DELETE ON projects
  FOR EACH ROW EXECUTE FUNCTION trigger_alignment_recalculation();

DROP TRIGGER IF EXISTS alignment_journal_webhook ON journal_entries;
CREATE TRIGGER alignment_journal_webhook
  AFTER INSERT OR UPDATE ON journal_entries
  FOR EACH ROW EXECUTE FUNCTION trigger_alignment_recalculation();

-- ===================================
-- 3. HRM INSIGHTS GENERATION WEBHOOK
-- ===================================

-- Function to trigger HRM insight generation
CREATE OR REPLACE FUNCTION trigger_hrm_insights()
RETURNS TRIGGER AS $$
BEGIN
  -- Trigger HRM insights for significant behavioral events
  IF NEW.event_type IN (
    'project_completed', 'goal_achieved', 'streak_milestone',
    'productivity_pattern_change', 'sentiment_trend_change',
    'focus_session_completed', 'daily_reflection_completed'
  ) THEN
    PERFORM pg_notify('hrm_insights_webhook', json_build_object(
      'table', 'user_behavior_events',
      'action', 'hrm_trigger',
      'record', json_build_object(
        'user_id', NEW.user_id,
        'event_type', NEW.event_type,
        'event_data', NEW.event_data,
        'created_at', NEW.created_at
      )
    )::text);
    
    -- Log the webhook trigger
    INSERT INTO webhook_logs (
      webhook_type, 
      user_id, 
      table_name, 
      record_id, 
      triggered_at
    ) VALUES (
      'hrm_insights_generation',
      NEW.user_id,
      'user_behavior_events',
      NEW.id,
      NOW()
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create HRM insights trigger
DROP TRIGGER IF EXISTS hrm_insights_webhook_trigger ON user_behavior_events;
CREATE TRIGGER hrm_insights_webhook_trigger
  AFTER INSERT ON user_behavior_events
  FOR EACH ROW EXECUTE FUNCTION trigger_hrm_insights();

-- ===================================
-- 4. REAL-TIME ANALYTICS AGGREGATION WEBHOOK
-- ===================================

-- Function to trigger analytics aggregation
CREATE OR REPLACE FUNCTION trigger_analytics_aggregation()
RETURNS TRIGGER AS $$
BEGIN
  -- Trigger real-time analytics updates
  PERFORM pg_notify('analytics_aggregation_webhook', json_build_object(
    'table', 'user_behavior_events',
    'action', 'analytics_update',
    'record', json_build_object(
      'user_id', NEW.user_id,
      'event_type', NEW.event_type,
      'session_id', NEW.session_id,
      'created_at', NEW.created_at
    )
  )::text);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create analytics aggregation trigger
DROP TRIGGER IF EXISTS analytics_aggregation_webhook_trigger ON user_behavior_events;
CREATE TRIGGER analytics_aggregation_webhook_trigger
  AFTER INSERT ON user_behavior_events
  FOR EACH ROW EXECUTE FUNCTION trigger_analytics_aggregation();

-- ===================================
-- 5. CACHE INVALIDATION WEBHOOKS
-- ===================================

-- Function to trigger cache invalidation
CREATE OR REPLACE FUNCTION trigger_cache_invalidation()
RETURNS TRIGGER AS $$
DECLARE
  affected_user_id UUID;
BEGIN
  affected_user_id := COALESCE(NEW.user_id, OLD.user_id);
  
  IF affected_user_id IS NOT NULL THEN
    PERFORM pg_notify('cache_invalidation_webhook', json_build_object(
      'table', TG_TABLE_NAME,
      'action', TG_OP,
      'record', json_build_object(
        'user_id', affected_user_id,
        'id', COALESCE(NEW.id, OLD.id)
      )
    )::text);
  END IF;
  
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply cache invalidation to key tables
DROP TRIGGER IF EXISTS cache_tasks_webhook ON tasks;
CREATE TRIGGER cache_tasks_webhook
  AFTER INSERT OR UPDATE OR DELETE ON tasks
  FOR EACH ROW EXECUTE FUNCTION trigger_cache_invalidation();

DROP TRIGGER IF EXISTS cache_projects_webhook ON projects;
CREATE TRIGGER cache_projects_webhook
  AFTER INSERT OR UPDATE OR DELETE ON projects
  FOR EACH ROW EXECUTE FUNCTION trigger_cache_invalidation();

DROP TRIGGER IF EXISTS cache_journal_webhook ON journal_entries;
CREATE TRIGGER cache_journal_webhook
  AFTER INSERT OR UPDATE OR DELETE ON journal_entries
  FOR EACH ROW EXECUTE FUNCTION trigger_cache_invalidation();

-- ===================================
-- 6. WEBHOOK LOGGING TABLE
-- ===================================

-- Create table to log webhook activities
CREATE TABLE IF NOT EXISTS webhook_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  webhook_type VARCHAR(255) NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  table_name VARCHAR(255) NOT NULL,
  record_id UUID,
  triggered_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  status VARCHAR(50) DEFAULT 'pending',
  error_message TEXT,
  processing_duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_webhook_logs_user_id ON webhook_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook_type ON webhook_logs(webhook_type);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_triggered_at ON webhook_logs(triggered_at);

-- Add RLS policy
ALTER TABLE webhook_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can see their own webhook logs"
ON webhook_logs FOR SELECT
USING (auth.uid() = user_id);

-- ===================================
-- 7. WEBHOOK HEALTH MONITORING
-- ===================================

-- Function to clean old webhook logs (run daily)
CREATE OR REPLACE FUNCTION cleanup_webhook_logs()
RETURNS void AS $$
BEGIN
  -- Delete webhook logs older than 30 days
  DELETE FROM webhook_logs 
  WHERE created_at < NOW() - INTERVAL '30 days';
  
  -- Log cleanup activity
  INSERT INTO webhook_logs (
    webhook_type, 
    table_name, 
    triggered_at,
    status
  ) VALUES (
    'system_cleanup',
    'webhook_logs',
    NOW(),
    'completed'
  );
END;
$$ LANGUAGE plpgsql;

-- ===================================
-- 8. PERFORMANCE OPTIMIZATION FUNCTIONS
-- ===================================

-- Function to get webhook statistics
CREATE OR REPLACE FUNCTION get_webhook_stats(user_id_param UUID DEFAULT NULL)
RETURNS TABLE (
  webhook_type VARCHAR(255),
  total_triggers BIGINT,
  avg_processing_time_ms NUMERIC,
  success_rate NUMERIC,
  last_triggered TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    wl.webhook_type,
    COUNT(*) as total_triggers,
    AVG(wl.processing_duration_ms) as avg_processing_time_ms,
    (COUNT(CASE WHEN wl.status = 'completed' THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
    MAX(wl.triggered_at) as last_triggered
  FROM webhook_logs wl
  WHERE (user_id_param IS NULL OR wl.user_id = user_id_param)
    AND wl.triggered_at > NOW() - INTERVAL '7 days'
  GROUP BY wl.webhook_type
  ORDER BY total_triggers DESC;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON webhook_logs TO authenticated;
GRANT EXECUTE ON FUNCTION get_webhook_stats(UUID) TO authenticated;

-- Notify completion
DO $$
BEGIN
  RAISE NOTICE 'Performance webhooks setup completed successfully!';
  RAISE NOTICE 'Configured webhooks: journal_sentiment, alignment_recalc, hrm_insights, analytics_aggregation, cache_invalidation';
  RAISE NOTICE 'Webhook logging and monitoring enabled';
END $$;