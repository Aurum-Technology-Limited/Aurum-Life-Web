-- Migration 015: AI Quota Tracking System
-- Implements real AI interaction tracking and quota management

-- ===================================
-- 1. AI INTERACTIONS TRACKING TABLE
-- ===================================

-- Create table to track all AI interactions and quota usage
CREATE TABLE IF NOT EXISTS ai_interactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  feature_type VARCHAR(100) NOT NULL,
  feature_details JSONB DEFAULT '{}',
  tokens_used INTEGER DEFAULT 0,
  success BOOLEAN NOT NULL DEFAULT true,
  error_message TEXT,
  processing_time_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT valid_feature_type CHECK (
    feature_type IN (
      'sentiment_analysis',
      'hrm_analysis', 
      'task_why_statements',
      'focus_suggestions',
      'today_priorities',
      'goal_coaching',
      'project_decomposition',
      'strategic_planning'
    )
  )
);

-- Add indexes for efficient quota queries
CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_month 
ON ai_interactions (user_id, created_at DESC) 
WHERE success = true;

CREATE INDEX IF NOT EXISTS idx_ai_interactions_feature_type 
ON ai_interactions (user_id, feature_type, created_at DESC);

-- Add RLS policy for user data isolation
ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ai_interactions_user_isolation" 
ON ai_interactions FOR ALL TO authenticated
USING (auth.uid() = user_id) 
WITH CHECK (auth.uid() = user_id);

-- Grant permissions
GRANT ALL ON ai_interactions TO authenticated;
GRANT ALL ON ai_interactions TO service_role;

-- ===================================
-- 2. AI QUOTA MANAGEMENT FUNCTIONS
-- ===================================

-- Function to get user's current month AI usage
CREATE OR REPLACE FUNCTION get_user_ai_usage_current_month(p_user_id UUID)
RETURNS TABLE(
  total_interactions INTEGER,
  successful_interactions INTEGER,
  feature_breakdown JSONB,
  month_start TIMESTAMPTZ,
  month_end TIMESTAMPTZ
) AS $$
DECLARE
  month_start_date TIMESTAMPTZ;
  month_end_date TIMESTAMPTZ;
BEGIN
  -- Get current month boundaries
  month_start_date := date_trunc('month', NOW());
  month_end_date := month_start_date + INTERVAL '1 month';
  
  RETURN QUERY
  WITH usage_stats AS (
    SELECT 
      COUNT(*) as total,
      COUNT(*) FILTER (WHERE success = true) as successful,
      jsonb_object_agg(
        feature_type, 
        COUNT(*) FILTER (WHERE success = true)
      ) as breakdown
    FROM ai_interactions 
    WHERE user_id = p_user_id 
      AND created_at >= month_start_date 
      AND created_at < month_end_date
  )
  SELECT 
    COALESCE(us.total, 0)::INTEGER,
    COALESCE(us.successful, 0)::INTEGER,
    COALESCE(us.breakdown, '{}'::JSONB),
    month_start_date,
    month_end_date
  FROM usage_stats us;
END;
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Function to check if user has quota available
CREATE OR REPLACE FUNCTION check_ai_quota_available(
  p_user_id UUID,
  p_monthly_limit INTEGER DEFAULT 250
)
RETURNS TABLE(
  has_quota BOOLEAN,
  remaining INTEGER,
  used INTEGER,
  limit_reached BOOLEAN
) AS $$
DECLARE
  current_usage INTEGER;
BEGIN
  -- Get current month usage
  SELECT successful_interactions INTO current_usage
  FROM get_user_ai_usage_current_month(p_user_id);
  
  current_usage := COALESCE(current_usage, 0);
  
  RETURN QUERY
  SELECT 
    (current_usage < p_monthly_limit) as has_quota,
    (p_monthly_limit - current_usage) as remaining,
    current_usage as used,
    (current_usage >= p_monthly_limit) as limit_reached;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Grant permissions for quota functions
GRANT EXECUTE ON FUNCTION get_user_ai_usage_current_month(UUID) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION check_ai_quota_available(UUID, INTEGER) TO authenticated, service_role;

-- ===================================
-- 3. AI USAGE ANALYTICS VIEWS
-- ===================================

-- View for daily AI usage patterns
CREATE OR REPLACE VIEW daily_ai_usage AS
SELECT 
  user_id,
  DATE(created_at) as usage_date,
  feature_type,
  COUNT(*) as interaction_count,
  COUNT(*) FILTER (WHERE success = true) as successful_count,
  AVG(processing_time_ms) as avg_processing_time,
  SUM(tokens_used) as total_tokens
FROM ai_interactions 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY user_id, DATE(created_at), feature_type
ORDER BY usage_date DESC, interaction_count DESC;

-- Grant access to the view
GRANT SELECT ON daily_ai_usage TO authenticated;

-- ===================================
-- 4. QUOTA MONITORING TRIGGERS
-- ===================================

-- Function to notify when quota is running low
CREATE OR REPLACE FUNCTION check_quota_threshold()
RETURNS TRIGGER AS $$
DECLARE
  current_usage INTEGER;
  quota_limit INTEGER := 250;
  threshold_80 INTEGER := 200;  -- 80% threshold
  threshold_95 INTEGER := 238;  -- 95% threshold
BEGIN
  -- Get current month usage for the user
  SELECT used INTO current_usage
  FROM check_ai_quota_available(NEW.user_id, quota_limit);
  
  -- Log threshold notifications
  IF current_usage = threshold_80 THEN
    INSERT INTO webhook_logs (webhook_type, user_id, table_name, triggered_at)
    VALUES ('quota_warning_80', NEW.user_id, 'ai_interactions', NOW());
    
    PERFORM pg_notify('quota_warning', json_build_object(
      'user_id', NEW.user_id,
      'usage_percent', 80,
      'remaining', quota_limit - current_usage
    )::text);
    
  ELSIF current_usage = threshold_95 THEN
    INSERT INTO webhook_logs (webhook_type, user_id, table_name, triggered_at)
    VALUES ('quota_warning_95', NEW.user_id, 'ai_interactions', NOW());
    
    PERFORM pg_notify('quota_warning', json_build_object(
      'user_id', NEW.user_id,
      'usage_percent', 95,
      'remaining', quota_limit - current_usage
    )::text);
    
  ELSIF current_usage >= quota_limit THEN
    INSERT INTO webhook_logs (webhook_type, user_id, table_name, triggered_at)
    VALUES ('quota_limit_reached', NEW.user_id, 'ai_interactions', NOW());
    
    PERFORM pg_notify('quota_limit', json_build_object(
      'user_id', NEW.user_id,
      'usage_percent', 100,
      'limit_reached', true
    )::text);
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Create trigger for quota monitoring
DROP TRIGGER IF EXISTS quota_threshold_monitor ON ai_interactions;
CREATE TRIGGER quota_threshold_monitor
  AFTER INSERT ON ai_interactions
  FOR EACH ROW 
  WHEN (NEW.success = true)
  EXECUTE FUNCTION check_quota_threshold();

-- ===================================
-- 5. CLEANUP AND MAINTENANCE
-- ===================================

-- Function to clean old AI interaction logs (keep last 6 months)
CREATE OR REPLACE FUNCTION cleanup_ai_interactions()
RETURNS void AS $$
BEGIN
  DELETE FROM ai_interactions 
  WHERE created_at < NOW() - INTERVAL '6 months';
  
  -- Log cleanup
  INSERT INTO webhook_logs (webhook_type, table_name, triggered_at, status)
  VALUES ('ai_interactions_cleanup', 'ai_interactions', NOW(), 'completed');
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Grant permissions
GRANT EXECUTE ON FUNCTION cleanup_ai_interactions() TO service_role;

-- ===================================
-- 6. VERIFICATION
-- ===================================

-- Test the quota system
DO $$
DECLARE
  test_user_id UUID;
  quota_result RECORD;
BEGIN
  -- Get first user for testing
  SELECT id INTO test_user_id FROM auth.users LIMIT 1;
  
  IF test_user_id IS NOT NULL THEN
    -- Test quota check
    SELECT * INTO quota_result FROM check_ai_quota_available(test_user_id, 250);
    
    RAISE NOTICE 'AI Quota System Test Results:';
    RAISE NOTICE '  User: %', test_user_id;
    RAISE NOTICE '  Has Quota: %', quota_result.has_quota;
    RAISE NOTICE '  Remaining: %', quota_result.remaining;
    RAISE NOTICE '  Used: %', quota_result.used;
    RAISE NOTICE '  Limit Reached: %', quota_result.limit_reached;
    
    RAISE NOTICE '✅ AI Quota System initialized successfully!';
  ELSE
    RAISE NOTICE '⚠️  No users found for quota system testing';
  END IF;
END $$;

-- Final completion message
DO $$
BEGIN
  RAISE NOTICE '=== AI QUOTA TRACKING SYSTEM SETUP COMPLETED ===';
  RAISE NOTICE 'Features implemented:';
  RAISE NOTICE '  ✅ ai_interactions table for usage tracking';
  RAISE NOTICE '  ✅ Real-time quota checking functions';
  RAISE NOTICE '  ✅ Usage analytics and breakdown reporting';
  RAISE NOTICE '  ✅ Quota threshold monitoring and warnings';
  RAISE NOTICE '  ✅ Automatic cleanup and maintenance';
  RAISE NOTICE '';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '  1. Update backend services to use AIQuotaService';
  RAISE NOTICE '  2. Add quota consumption to all OpenAI API calls';
  RAISE NOTICE '  3. Update quota endpoint to return real usage data';
  RAISE NOTICE '  4. Test quota system with actual AI interactions';
END $$;