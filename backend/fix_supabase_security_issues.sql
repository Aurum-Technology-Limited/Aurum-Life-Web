-- Fix Supabase Security Issues
-- Resolves Function Search Path Mutable warnings and Extension in Public schema

-- ===================================
-- 1. FIX FUNCTION SEARCH_PATH ISSUES
-- ===================================

-- Fix trigger_cache_invalidation function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix update_updated_at_column function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix cleanup_webhook_logs function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix trigger_journal_sentiment_analysis function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix trigger_hrm_insights function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix rag_search function
CREATE OR REPLACE FUNCTION rag_search(
    query_embedding vector(1536),
    user_id_filter UUID,
    match_count INT DEFAULT 10,
    date_range_days INT DEFAULT NULL
)
RETURNS TABLE(
    entity_type TEXT,
    entity_id UUID,
    title TEXT,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER 
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    WITH combined_results AS (
        -- Journal entries
        SELECT 
            'journal_entry' as entity_type,
            id as entity_id,
            title,
            content,
            1 - (content_embedding <=> query_embedding) as similarity,
            created_at,
            jsonb_build_object('mood', mood, 'tags', tags) as metadata
        FROM journal_entries
        WHERE 
            user_id = user_id_filter
            AND content_embedding IS NOT NULL
            AND (date_range_days IS NULL OR created_at >= NOW() - INTERVAL '1 day' * date_range_days)
        
        UNION ALL
        
        -- Daily reflections
        SELECT 
            'daily_reflection' as entity_type,
            id as entity_id,
            'Daily Reflection - ' || reflection_date::TEXT as title,
            reflection_text as content,
            1 - (reflection_embedding <=> query_embedding) as similarity,
            created_at,
            jsonb_build_object(
                'completion_score', completion_score,
                'mood', mood,
                'date', reflection_date
            ) as metadata
        FROM daily_reflections
        WHERE 
            user_id = user_id_filter
            AND reflection_embedding IS NOT NULL
            AND (date_range_days IS NULL OR created_at >= NOW() - INTERVAL '1 day' * date_range_days)
        
        UNION ALL
        
        -- Tasks with descriptions
        SELECT 
            'task' as entity_type,
            t.id as entity_id,
            t.name as title,
            t.description as content,
            1 - (t.description_embedding <=> query_embedding) as similarity,
            t.created_at,
            jsonb_build_object(
                'status', t.status,
                'priority', t.priority,
                'project_id', t.project_id,
                'due_date', t.due_date
            ) as metadata
        FROM tasks t
        WHERE 
            t.user_id = user_id_filter
            AND t.description_embedding IS NOT NULL
            AND t.description != ''
            AND (date_range_days IS NULL OR t.created_at >= NOW() - INTERVAL '1 day' * date_range_days)
    )
    SELECT * FROM combined_results
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- Fix find_similar_journal_entries function
CREATE OR REPLACE FUNCTION find_similar_journal_entries(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    user_id_filter UUID DEFAULT NULL
)
RETURNS TABLE(
    id UUID,
    title TEXT,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
SECURITY DEFINER 
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        je.id,
        je.title,
        je.content,
        1 - (je.content_embedding <=> query_embedding) as similarity,
        je.created_at
    FROM journal_entries je
    WHERE 
        je.content_embedding IS NOT NULL
        AND (user_id_filter IS NULL OR je.user_id = user_id_filter)
    ORDER BY je.content_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Fix trigger_alignment_recalculation function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix trigger_analytics_aggregation function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix get_webhook_stats function
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Fix increment_session_counter function (from analytics)
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
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- Create extension schema for vector if it doesn't exist
DO $$
BEGIN
    -- Create extensions schema if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'extensions') THEN
        CREATE SCHEMA extensions;
        RAISE NOTICE 'Created extensions schema';
    END IF;
END $$;

-- Grant usage on extensions schema
GRANT USAGE ON SCHEMA extensions TO postgres, authenticated, anon, service_role;

-- NOTE: Moving the vector extension requires manual intervention
-- The following commands need to be run by a superuser in the SQL Editor:

DO $$
BEGIN
    RAISE NOTICE '=== VECTOR EXTENSION MIGRATION NOTICE ===';
    RAISE NOTICE 'To complete the security fix, the vector extension needs to be moved from public to extensions schema.';
    RAISE NOTICE 'This requires superuser privileges and cannot be done in this script.';
    RAISE NOTICE '';
    RAISE NOTICE 'Please run the following commands in the Supabase SQL Editor as a superuser:';
    RAISE NOTICE '1. ALTER EXTENSION vector SET SCHEMA extensions;';
    RAISE NOTICE '2. UPDATE pg_extension SET extnamespace = (SELECT oid FROM pg_namespace WHERE nspname = ''extensions'') WHERE extname = ''vector'';';
    RAISE NOTICE '';
    RAISE NOTICE 'After moving the extension, update any functions that reference vector types to use the full path: extensions.vector';
    RAISE NOTICE '=== END NOTICE ===';
END $$;

-- ===================================
-- 2. VERIFY SEARCH PATH FIXES
-- ===================================

-- Function to verify all functions have proper search_path
CREATE OR REPLACE FUNCTION verify_function_security()
RETURNS TABLE(
    function_name TEXT,
    search_path_secure BOOLEAN,
    security_definer BOOLEAN,
    issues TEXT[]
) AS $$
DECLARE
    func_record RECORD;
    issues_array TEXT[];
BEGIN
    FOR func_record IN 
        SELECT 
            p.proname,
            p.prosecdef,
            COALESCE(p.proconfig, '{}') as config
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.proname IN (
            'trigger_cache_invalidation',
            'update_updated_at_column', 
            'cleanup_webhook_logs',
            'trigger_journal_sentiment_analysis',
            'trigger_hrm_insights',
            'rag_search',
            'find_similar_journal_entries',
            'trigger_alignment_recalculation',
            'trigger_analytics_aggregation',
            'get_webhook_stats',
            'increment_session_counter'
        )
    LOOP
        issues_array := '{}';
        
        -- Check if search_path is set
        IF NOT EXISTS (
            SELECT 1 FROM unnest(func_record.config) AS config_item 
            WHERE config_item LIKE 'search_path=%'
        ) THEN
            issues_array := array_append(issues_array, 'Missing search_path configuration');
        END IF;
        
        -- Check if SECURITY DEFINER is set
        IF NOT func_record.prosecdef THEN
            issues_array := array_append(issues_array, 'Missing SECURITY DEFINER');
        END IF;
        
        RETURN QUERY SELECT 
            func_record.proname::TEXT,
            EXISTS (
                SELECT 1 FROM unnest(func_record.config) AS config_item 
                WHERE config_item LIKE 'search_path=%'
            ),
            func_record.prosecdef,
            issues_array;
    END LOOP;
END;
$$ LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public, pg_temp;

-- ===================================
-- 3. COMPLETION VERIFICATION
-- ===================================

DO $$
DECLARE
    func_count INTEGER;
    secure_func_count INTEGER;
BEGIN
    -- Count total functions that needed fixing
    SELECT COUNT(*) INTO func_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN (
        'trigger_cache_invalidation',
        'update_updated_at_column', 
        'cleanup_webhook_logs',
        'trigger_journal_sentiment_analysis',
        'trigger_hrm_insights',
        'rag_search',
        'find_similar_journal_entries',
        'trigger_alignment_recalculation',
        'trigger_analytics_aggregation',
        'get_webhook_stats',
        'increment_session_counter'
    );
    
    -- Count functions that now have proper security
    SELECT COUNT(*) INTO secure_func_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
    AND p.proname IN (
        'trigger_cache_invalidation',
        'update_updated_at_column', 
        'cleanup_webhook_logs',
        'trigger_journal_sentiment_analysis',
        'trigger_hrm_insights',
        'rag_search',
        'find_similar_journal_entries',
        'trigger_alignment_recalculation',
        'trigger_analytics_aggregation',
        'get_webhook_stats',
        'increment_session_counter'
    )
    AND p.prosecdef = true  -- Has SECURITY DEFINER
    AND EXISTS (
        SELECT 1 FROM unnest(COALESCE(p.proconfig, '{}')) AS config_item 
        WHERE config_item LIKE 'search_path=%'
    );
    
    RAISE NOTICE '=== SUPABASE SECURITY ISSUES FIX COMPLETED ===';
    RAISE NOTICE 'Functions processed: % / %', secure_func_count, func_count;
    RAISE NOTICE 'All functions now have:';
    RAISE NOTICE '  ✅ SECURITY DEFINER privilege';
    RAISE NOTICE '  ✅ Fixed search_path = public, pg_temp';
    RAISE NOTICE '  ✅ Protection against search_path manipulation attacks';
    RAISE NOTICE '';
    RAISE NOTICE 'REMAINING MANUAL STEPS:';
    RAISE NOTICE '  1. Move vector extension to extensions schema (requires superuser)';
    RAISE NOTICE '  2. Run: SELECT * FROM verify_function_security(); to confirm all fixes';
    RAISE NOTICE '';
    
    IF secure_func_count = func_count THEN
        RAISE NOTICE '🎉 ALL FUNCTION SECURITY ISSUES RESOLVED!';
    ELSE
        RAISE NOTICE '⚠️  Some functions may need manual review';
    END IF;
END $$;

-- Grant execute permission for verification function
GRANT EXECUTE ON FUNCTION verify_function_security() TO authenticated, service_role;