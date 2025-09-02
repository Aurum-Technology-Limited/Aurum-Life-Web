-- User Behavior Analytics Tables
-- Migration: 010_create_user_behavior_analytics.sql

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Analytics Preferences Table
CREATE TABLE IF NOT EXISTS user_analytics_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    
    -- Consent settings
    analytics_consent BOOLEAN DEFAULT true,
    ai_behavior_tracking BOOLEAN DEFAULT true,
    performance_tracking BOOLEAN DEFAULT true,
    error_reporting BOOLEAN DEFAULT true,
    
    -- Data retention preferences
    data_retention_days INTEGER DEFAULT 365,
    anonymize_after_days INTEGER DEFAULT 90,
    
    -- Feature-specific preferences
    track_ai_insights_usage BOOLEAN DEFAULT true,
    track_ai_actions_usage BOOLEAN DEFAULT true,
    track_goal_planner_usage BOOLEAN DEFAULT true,
    track_navigation_patterns BOOLEAN DEFAULT true,
    track_search_queries BOOLEAN DEFAULT false,
    
    -- Privacy settings
    share_anonymous_stats BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_analytics_preferences_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Unique constraint - one preference per user
    UNIQUE(user_id)
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_id TEXT NOT NULL,
    
    -- Session details
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    is_active BOOLEAN DEFAULT true,
    
    -- Session context
    entry_page TEXT,
    exit_page TEXT,
    page_views INTEGER DEFAULT 0,
    ai_interactions INTEGER DEFAULT 0,
    feature_usages INTEGER DEFAULT 0,
    
    -- Device/Browser info
    user_agent TEXT,
    screen_resolution TEXT,
    timezone TEXT,
    device_type TEXT,
    
    -- Privacy
    consent_given BOOLEAN DEFAULT true,
    is_anonymized BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_user_sessions_user_id (user_id),
    INDEX idx_user_sessions_session_id (session_id),
    INDEX idx_user_sessions_start_time (start_time),
    INDEX idx_user_sessions_is_active (is_active)
);

-- User Behavior Events Table
CREATE TABLE IF NOT EXISTS user_behavior_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_id TEXT NOT NULL,
    
    -- Event identification
    action_type TEXT NOT NULL CHECK (action_type IN ('page_view', 'ai_interaction', 'feature_usage', 'task_action', 'project_action', 'navigation', 'search', 'insight_feedback')),
    feature_name TEXT NOT NULL,
    ai_feature_type TEXT CHECK (ai_feature_type IN ('my_ai_insights', 'ai_quick_actions', 'goal_planner', 'semantic_search', 'hrm_analysis')),
    
    -- Event details
    event_data JSONB DEFAULT '{}',
    duration_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    -- Context
    page_url TEXT,
    referrer_url TEXT,
    user_agent TEXT,
    screen_resolution TEXT,
    timezone TEXT,
    
    -- Privacy compliance
    is_anonymized BOOLEAN DEFAULT false,
    consent_given BOOLEAN DEFAULT true,
    
    -- Timestamps
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    client_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraints
    CONSTRAINT fk_events_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    CONSTRAINT fk_events_session FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_behavior_events_user_id (user_id),
    INDEX idx_behavior_events_session_id (session_id),
    INDEX idx_behavior_events_action_type (action_type),
    INDEX idx_behavior_events_ai_feature_type (ai_feature_type),
    INDEX idx_behavior_events_feature_name (feature_name),
    INDEX idx_behavior_events_timestamp (timestamp),
    INDEX idx_behavior_events_success (success),
    
    -- Composite indexes for common queries
    INDEX idx_behavior_events_user_timestamp (user_id, timestamp DESC),
    INDEX idx_behavior_events_ai_features (user_id, ai_feature_type, timestamp DESC) WHERE ai_feature_type IS NOT NULL
);

-- Create optimized view for analytics queries
CREATE VIEW user_ai_feature_usage AS
SELECT 
    ube.user_id,
    ube.ai_feature_type,
    ube.feature_name,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT ube.session_id) as unique_sessions,
    SUM(ube.duration_ms) as total_time_spent_ms,
    AVG(ube.duration_ms) as avg_duration_ms,
    COUNT(*) FILTER (WHERE ube.success = true)::FLOAT / COUNT(*) as success_rate,
    MAX(ube.timestamp) as last_used,
    DATE(ube.timestamp) as usage_date
FROM user_behavior_events ube
WHERE ube.ai_feature_type IS NOT NULL
  AND ube.consent_given = true
GROUP BY ube.user_id, ube.ai_feature_type, ube.feature_name, DATE(ube.timestamp);

-- Create view for daily analytics
CREATE VIEW daily_user_analytics AS
SELECT 
    DATE(ube.timestamp) as analytics_date,
    ube.user_id,
    COUNT(*) as total_events,
    COUNT(DISTINCT ube.session_id) as unique_sessions,
    COUNT(*) FILTER (WHERE ube.action_type = 'page_view') as page_views,
    COUNT(*) FILTER (WHERE ube.action_type = 'ai_interaction') as ai_interactions,
    COUNT(*) FILTER (WHERE ube.ai_feature_type IS NOT NULL) as ai_feature_uses,
    SUM(ube.duration_ms) as total_time_spent_ms,
    AVG(ube.duration_ms) as avg_event_duration_ms
FROM user_behavior_events ube
WHERE ube.consent_given = true
GROUP BY DATE(ube.timestamp), ube.user_id;

-- Function to automatically anonymize old data
CREATE OR REPLACE FUNCTION anonymize_old_behavior_data()
RETURNS void AS $$
DECLARE
    anonymize_threshold TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get the earliest anonymization threshold from user preferences
    SELECT MIN(NOW() - INTERVAL '1 day' * uap.anonymize_after_days)
    INTO anonymize_threshold
    FROM user_analytics_preferences uap;
    
    -- If no preferences found, use default of 90 days
    IF anonymize_threshold IS NULL THEN
        anonymize_threshold := NOW() - INTERVAL '90 days';
    END IF;
    
    -- Anonymize behavior events
    UPDATE user_behavior_events 
    SET 
        user_agent = 'anonymized',
        page_url = regexp_replace(page_url, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        referrer_url = regexp_replace(referrer_url, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        event_data = jsonb_strip_nulls(
            event_data - 'user_id' - 'email' - 'name' - 'personal_data'
        ),
        is_anonymized = true
    WHERE timestamp < anonymize_threshold 
      AND is_anonymized = false;
    
    -- Anonymize session data
    UPDATE user_sessions 
    SET 
        user_agent = 'anonymized',
        entry_page = regexp_replace(entry_page, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        exit_page = regexp_replace(exit_page, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        is_anonymized = true
    WHERE start_time < anonymize_threshold 
      AND is_anonymized = false;
      
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old data based on user preferences
CREATE OR REPLACE FUNCTION cleanup_old_behavior_data()
RETURNS void AS $$
DECLARE
    cleanup_threshold TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get the earliest retention threshold from user preferences
    SELECT MIN(NOW() - INTERVAL '1 day' * uap.data_retention_days)
    INTO cleanup_threshold
    FROM user_analytics_preferences uap;
    
    -- If no preferences found, use default of 365 days
    IF cleanup_threshold IS NULL THEN
        cleanup_threshold := NOW() - INTERVAL '365 days';
    END IF;
    
    -- Delete old behavior events
    DELETE FROM user_behavior_events 
    WHERE timestamp < cleanup_threshold;
    
    -- Delete old sessions (this will cascade to events)
    DELETE FROM user_sessions 
    WHERE start_time < cleanup_threshold;
    
END;
$$ LANGUAGE plpgsql;

-- Create indexes for the views
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_ai_feature_usage_composite 
ON user_behavior_events (user_id, ai_feature_type, feature_name, timestamp DESC) 
WHERE ai_feature_type IS NOT NULL AND consent_given = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_analytics_composite 
ON user_behavior_events (user_id, timestamp::date, action_type) 
WHERE consent_given = true;

-- Add update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_analytics_preferences_updated_at 
    BEFORE UPDATE ON user_analytics_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_sessions_updated_at 
    BEFORE UPDATE ON user_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_behavior_events_updated_at 
    BEFORE UPDATE ON user_behavior_events 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON user_analytics_preferences TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_behavior_events TO authenticated;
GRANT SELECT ON user_ai_feature_usage TO authenticated;
GRANT SELECT ON daily_user_analytics TO authenticated;

-- Row Level Security (RLS) policies
ALTER TABLE user_analytics_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_behavior_events ENABLE ROW LEVEL SECURITY;

-- Policies for user_analytics_preferences
CREATE POLICY "Users can view their own analytics preferences" ON user_analytics_preferences 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Users can update their own analytics preferences" ON user_analytics_preferences 
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY "Users can insert their own analytics preferences" ON user_analytics_preferences 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Users can delete their own analytics preferences" ON user_analytics_preferences 
    FOR DELETE USING (auth.uid() = user_id);

-- Policies for user_sessions
CREATE POLICY "Users can view their own sessions" ON user_sessions 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Users can insert their own sessions" ON user_sessions 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Users can update their own sessions" ON user_sessions 
    FOR UPDATE USING (auth.uid() = user_id);

-- Policies for user_behavior_events
CREATE POLICY "Users can view their own behavior events" ON user_behavior_events 
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Users can insert their own behavior events" ON user_behavior_events 
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Users can update their own behavior events" ON user_behavior_events 
    FOR UPDATE USING (auth.uid() = user_id);

-- Comments for documentation
COMMENT ON TABLE user_analytics_preferences IS 'User preferences for analytics tracking and data retention';
COMMENT ON TABLE user_sessions IS 'User session tracking for analytics and behavior analysis';
COMMENT ON TABLE user_behavior_events IS 'Individual user behavior events for detailed analytics';
COMMENT ON VIEW user_ai_feature_usage IS 'Aggregated view of AI feature usage analytics';
COMMENT ON VIEW daily_user_analytics IS 'Daily aggregated user analytics for dashboard reporting';
COMMENT ON FUNCTION anonymize_old_behavior_data() IS 'Function to anonymize old behavior data based on user preferences';
COMMENT ON FUNCTION cleanup_old_behavior_data() IS 'Function to clean up old behavior data based on user retention preferences';

-- Insert default analytics preferences for existing users
INSERT INTO user_analytics_preferences (user_id)
SELECT id FROM auth.users 
WHERE id NOT IN (SELECT user_id FROM user_analytics_preferences)
ON CONFLICT (user_id) DO NOTHING;