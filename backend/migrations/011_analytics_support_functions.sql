-- Analytics Support Functions
-- Migration: 011_analytics_support_functions.sql

-- Function to increment session counters atomically
CREATE OR REPLACE FUNCTION increment_session_counter(
    p_user_id UUID,
    p_session_id TEXT,
    p_field TEXT
)
RETURNS void AS $$
BEGIN
    -- Validate field name to prevent SQL injection
    IF p_field NOT IN ('page_views', 'ai_interactions', 'feature_usages') THEN
        RAISE EXCEPTION 'Invalid field name: %', p_field;
    END IF;
    
    -- Use dynamic SQL with proper escaping
    EXECUTE format('UPDATE user_sessions SET %I = %I + 1, updated_at = NOW() WHERE user_id = $1 AND session_id = $2', p_field, p_field)
    USING p_user_id, p_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to anonymize specific user's behavior data
CREATE OR REPLACE FUNCTION anonymize_user_behavior_data(p_user_id UUID)
RETURNS void AS $$
BEGIN
    -- Anonymize behavior events for specific user
    UPDATE user_behavior_events 
    SET 
        user_agent = 'anonymized',
        page_url = regexp_replace(page_url, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        referrer_url = regexp_replace(referrer_url, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        event_data = jsonb_strip_nulls(
            event_data - 'user_id' - 'email' - 'name' - 'personal_data'
        ),
        is_anonymized = true,
        updated_at = NOW()
    WHERE user_id = p_user_id 
      AND is_anonymized = false;
    
    -- Anonymize session data for specific user
    UPDATE user_sessions 
    SET 
        user_agent = 'anonymized',
        entry_page = regexp_replace(entry_page, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        exit_page = regexp_replace(exit_page, '/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/[anonymized]', 'gi'),
        is_anonymized = true,
        updated_at = NOW()
    WHERE user_id = p_user_id 
      AND is_anonymized = false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's most active AI features
CREATE OR REPLACE FUNCTION get_user_top_ai_features(
    p_user_id UUID,
    p_days INTEGER DEFAULT 30,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE(
    ai_feature_type TEXT,
    feature_name TEXT,
    total_interactions BIGINT,
    total_time_spent_ms BIGINT,
    success_rate NUMERIC,
    last_used TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ube.ai_feature_type,
        ube.feature_name,
        COUNT(*) as total_interactions,
        COALESCE(SUM(ube.duration_ms), 0) as total_time_spent_ms,
        ROUND(
            COUNT(*) FILTER (WHERE ube.success = true)::NUMERIC / COUNT(*) * 100, 
            2
        ) as success_rate,
        MAX(ube.timestamp) as last_used
    FROM user_behavior_events ube
    WHERE ube.user_id = p_user_id
      AND ube.ai_feature_type IS NOT NULL
      AND ube.timestamp >= NOW() - INTERVAL '1 day' * p_days
      AND ube.consent_given = true
    GROUP BY ube.ai_feature_type, ube.feature_name
    ORDER BY total_interactions DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user engagement summary
CREATE OR REPLACE FUNCTION get_user_engagement_summary(
    p_user_id UUID,
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE(
    total_sessions BIGINT,
    total_time_spent_ms BIGINT,
    total_page_views BIGINT,
    total_ai_interactions BIGINT,
    avg_session_duration_ms NUMERIC,
    bounce_rate NUMERIC,
    active_days BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH session_stats AS (
        SELECT 
            COUNT(DISTINCT us.session_id) as sessions,
            COALESCE(SUM(us.duration_ms), 0) as time_spent,
            SUM(us.page_views) as page_views,
            SUM(us.ai_interactions) as ai_interactions,
            COUNT(*) FILTER (WHERE us.page_views <= 1) as single_page_sessions,
            COUNT(DISTINCT DATE(us.start_time)) as unique_days
        FROM user_sessions us
        WHERE us.user_id = p_user_id
          AND us.start_time >= NOW() - INTERVAL '1 day' * p_days
          AND us.consent_given = true
    )
    SELECT 
        ss.sessions as total_sessions,
        ss.time_spent as total_time_spent_ms,
        ss.page_views as total_page_views,
        ss.ai_interactions as total_ai_interactions,
        CASE 
            WHEN ss.sessions > 0 THEN ROUND(ss.time_spent::NUMERIC / ss.sessions, 2)
            ELSE 0
        END as avg_session_duration_ms,
        CASE 
            WHEN ss.sessions > 0 THEN ROUND(ss.single_page_sessions::NUMERIC / ss.sessions * 100, 2)
            ELSE 0
        END as bounce_rate,
        ss.unique_days as active_days
    FROM session_stats ss;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate AI feature usage trends
CREATE OR REPLACE FUNCTION get_ai_feature_trends(
    p_user_id UUID,
    p_feature_type TEXT,
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE(
    usage_date DATE,
    interactions BIGINT,
    avg_duration_ms NUMERIC,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(ube.timestamp) as usage_date,
        COUNT(*) as interactions,
        ROUND(AVG(ube.duration_ms), 2) as avg_duration_ms,
        ROUND(
            COUNT(*) FILTER (WHERE ube.success = true)::NUMERIC / COUNT(*) * 100, 
            2
        ) as success_rate
    FROM user_behavior_events ube
    WHERE ube.user_id = p_user_id
      AND ube.ai_feature_type = p_feature_type
      AND ube.timestamp >= NOW() - INTERVAL '1 day' * p_days
      AND ube.consent_given = true
    GROUP BY DATE(ube.timestamp)
    ORDER BY usage_date DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user navigation patterns
CREATE OR REPLACE FUNCTION get_user_navigation_patterns(
    p_user_id UUID,
    p_days INTEGER DEFAULT 30,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE(
    from_page TEXT,
    to_page TEXT,
    transition_count BIGINT,
    avg_time_between_ms NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH page_transitions AS (
        SELECT 
            ube1.page_url as from_page,
            ube2.page_url as to_page,
            COUNT(*) as transitions,
            AVG(EXTRACT(EPOCH FROM (ube2.timestamp - ube1.timestamp)) * 1000) as avg_time_ms
        FROM user_behavior_events ube1
        JOIN user_behavior_events ube2 ON (
            ube1.user_id = ube2.user_id 
            AND ube1.session_id = ube2.session_id
            AND ube2.timestamp > ube1.timestamp
            AND ube2.timestamp <= ube1.timestamp + INTERVAL '1 hour'
        )
        WHERE ube1.user_id = p_user_id
          AND ube1.action_type = 'page_view'
          AND ube2.action_type = 'page_view'
          AND ube1.timestamp >= NOW() - INTERVAL '1 day' * p_days
          AND ube1.consent_given = true
          AND ube2.consent_given = true
          AND ube1.page_url IS NOT NULL
          AND ube2.page_url IS NOT NULL
        GROUP BY ube1.page_url, ube2.page_url
    )
    SELECT 
        pt.from_page,
        pt.to_page,
        pt.transitions as transition_count,
        ROUND(pt.avg_time_ms, 2) as avg_time_between_ms
    FROM page_transitions pt
    WHERE pt.transitions >= 2  -- Only show patterns that occurred at least twice
    ORDER BY pt.transitions DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions to functions
GRANT EXECUTE ON FUNCTION increment_session_counter(UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION anonymize_user_behavior_data(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_top_ai_features(UUID, INTEGER, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_engagement_summary(UUID, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_ai_feature_trends(UUID, TEXT, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_navigation_patterns(UUID, INTEGER, INTEGER) TO authenticated;

-- Create indexes for better performance on common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_behavior_events_user_ai_timestamp 
ON user_behavior_events (user_id, ai_feature_type, timestamp DESC) 
WHERE ai_feature_type IS NOT NULL AND consent_given = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_behavior_events_page_transitions 
ON user_behavior_events (user_id, session_id, timestamp, page_url, action_type) 
WHERE action_type = 'page_view' AND consent_given = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_engagement_summary 
ON user_sessions (user_id, start_time, consent_given, page_views, ai_interactions);

-- Comments for documentation
COMMENT ON FUNCTION increment_session_counter(UUID, TEXT, TEXT) IS 'Atomically increment session counters for analytics tracking';
COMMENT ON FUNCTION anonymize_user_behavior_data(UUID) IS 'Anonymize a specific users behavior data for privacy compliance';
COMMENT ON FUNCTION get_user_top_ai_features(UUID, INTEGER, INTEGER) IS 'Get users most active AI features with usage statistics';
COMMENT ON FUNCTION get_user_engagement_summary(UUID, INTEGER) IS 'Get comprehensive user engagement metrics summary';
COMMENT ON FUNCTION get_ai_feature_trends(UUID, TEXT, INTEGER) IS 'Get usage trends for a specific AI feature over time';
COMMENT ON FUNCTION get_user_navigation_patterns(UUID, INTEGER, INTEGER) IS 'Get user navigation patterns and page transition analysis';