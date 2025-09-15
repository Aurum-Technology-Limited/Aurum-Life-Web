-- RAG System PostgreSQL Functions
-- Supporting functions for semantic search and behavioral analytics
-- Reference: aurum-life-impl-plan.md

-- Function to search metadata embeddings with vector similarity
CREATE OR REPLACE FUNCTION search_metadata_embeddings(
  query_embedding vector(1536),
  p_user_id UUID,
  domain_tags TEXT[] DEFAULT NULL,
  match_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  domain_tag TEXT,
  entity_id UUID,
  text_snippet TEXT,
  similarity FLOAT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ume.id,
    ume.domain_tag,
    ume.entity_id,
    ume.text_snippet,
    1 - (ume.embedding <=> query_embedding) as similarity,
    ume.created_at
  FROM public.user_metadata_embeddings ume
  WHERE ume.user_id = p_user_id
    AND (domain_tags IS NULL OR ume.domain_tag = ANY(domain_tags))
  ORDER BY ume.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to search conversation memory with vector similarity  
CREATE OR REPLACE FUNCTION search_conversation_memory(
  query_embedding vector(1536),
  p_user_id UUID,
  match_count INTEGER DEFAULT 10,
  cutoff_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  message_role TEXT,
  message_content TEXT,
  similarity FLOAT,
  conversation_date DATE,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    acm.id,
    acm.message_role,
    acm.message_content,
    1 - (acm.message_embedding <=> query_embedding) as similarity,
    acm.conversation_date,
    acm.created_at
  FROM public.ai_conversation_memory acm
  WHERE acm.user_id = p_user_id
    AND (cutoff_date IS NULL OR acm.created_at >= cutoff_date)
  ORDER BY acm.message_embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's context summary for AI prompts
CREATE OR REPLACE FUNCTION get_user_context_summary(
  p_user_id UUID,
  include_recent_activity BOOLEAN DEFAULT TRUE,
  activity_days INTEGER DEFAULT 7
)
RETURNS JSON AS $$
DECLARE
  context_summary JSON;
  pillar_count INTEGER;
  area_count INTEGER;
  active_project_count INTEGER;
  pending_task_count INTEGER;
  recent_journal_count INTEGER;
  activity_cutoff TIMESTAMPTZ;
BEGIN
  activity_cutoff := NOW() - (activity_days || ' days')::INTERVAL;
  
  -- Get basic hierarchy counts
  SELECT COUNT(*) INTO pillar_count FROM public.pillars 
  WHERE user_id = p_user_id AND archived = false;
  
  SELECT COUNT(*) INTO area_count FROM public.areas 
  WHERE user_id = p_user_id AND archived = false;
  
  SELECT COUNT(*) INTO active_project_count FROM public.projects 
  WHERE user_id = p_user_id AND status != 'Completed' AND archived = false;
  
  SELECT COUNT(*) INTO pending_task_count FROM public.tasks 
  WHERE user_id = p_user_id AND completed = false;
  
  -- Get recent journal activity if requested
  IF include_recent_activity THEN
    SELECT COUNT(*) INTO recent_journal_count FROM public.journal_entries 
    WHERE user_id = p_user_id AND created_at >= activity_cutoff AND deleted = false;
  ELSE
    recent_journal_count := 0;
  END IF;
  
  -- Build context summary
  context_summary := json_build_object(
    'user_id', p_user_id,
    'hierarchy_summary', json_build_object(
      'pillars', pillar_count,
      'areas', area_count,
      'active_projects', active_project_count,
      'pending_tasks', pending_task_count
    ),
    'recent_activity', json_build_object(
      'journal_entries_last_' || activity_days || '_days', recent_journal_count,
      'activity_period', activity_days || ' days'
    ),
    'generated_at', NOW()
  );
  
  RETURN context_summary;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update behavioral metrics with validation
CREATE OR REPLACE FUNCTION update_behavioral_metrics(
  p_user_id UUID,
  p_entity_type TEXT,
  p_entity_id UUID,
  p_metrics JSONB
)
RETURNS BOOLEAN AS $$
DECLARE
  current_metrics JSONB;
  updated_metrics JSONB;
  max_entries INTEGER := 90; -- Keep last 90 entries
BEGIN
  -- Validate entity type
  IF p_entity_type NOT IN ('pillars', 'areas') THEN
    RAISE EXCEPTION 'Invalid entity type: %', p_entity_type;
  END IF;
  
  -- Add timestamp to new metrics
  p_metrics := p_metrics || jsonb_build_object('timestamp', NOW());
  
  -- Get current metrics based on entity type
  IF p_entity_type = 'pillars' THEN
    SELECT behavior_metrics INTO current_metrics 
    FROM public.pillars 
    WHERE id = p_entity_id AND user_id = p_user_id;
  ELSIF p_entity_type = 'areas' THEN  
    SELECT behavior_metrics INTO current_metrics 
    FROM public.areas 
    WHERE id = p_entity_id AND user_id = p_user_id;
  END IF;
  
  -- Check if entity exists
  IF current_metrics IS NULL THEN
    RAISE EXCEPTION 'Entity not found or access denied: % %', p_entity_type, p_entity_id;
  END IF;
  
  -- Initialize if empty
  IF current_metrics IS NULL OR jsonb_array_length(current_metrics) IS NULL THEN
    current_metrics := '[]'::JSONB;
  END IF;
  
  -- Append new metrics
  updated_metrics := current_metrics || jsonb_build_array(p_metrics);
  
  -- Keep only the last N entries
  IF jsonb_array_length(updated_metrics) > max_entries THEN
    updated_metrics := (
      SELECT jsonb_agg(value)
      FROM (
        SELECT value 
        FROM jsonb_array_elements(updated_metrics) 
        ORDER BY (value->>'timestamp')::TIMESTAMPTZ DESC 
        LIMIT max_entries
      ) AS recent_metrics
    );
  END IF;
  
  -- Update the entity
  IF p_entity_type = 'pillars' THEN
    UPDATE public.pillars 
    SET behavior_metrics = updated_metrics, updated_at = NOW()
    WHERE id = p_entity_id AND user_id = p_user_id;
  ELSIF p_entity_type = 'areas' THEN
    UPDATE public.areas 
    SET behavior_metrics = updated_metrics, updated_at = NOW()
    WHERE id = p_entity_id AND user_id = p_user_id;
  END IF;
  
  -- Check if update was successful
  IF FOUND THEN
    RETURN TRUE;
  ELSE
    RETURN FALSE;
  END IF;
  
EXCEPTION WHEN OTHERS THEN
  RAISE EXCEPTION 'Error updating behavioral metrics: %', SQLERRM;
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean old embeddings (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_embeddings(
  retention_days INTEGER DEFAULT 180
)
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
  cutoff_date TIMESTAMPTZ;
BEGIN
  cutoff_date := NOW() - (retention_days || ' days')::INTERVAL;
  
  -- Delete old metadata embeddings
  DELETE FROM public.user_metadata_embeddings 
  WHERE created_at < cutoff_date;
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  -- Log cleanup operation
  INSERT INTO public.webhook_logs (webhook_type, table_name, triggered_at, status)
  VALUES ('embeddings_cleanup', 'user_metadata_embeddings', NOW(), 'completed');
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get embedding statistics
CREATE OR REPLACE FUNCTION get_embedding_stats(
  p_user_id UUID DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
  stats JSON;
  total_embeddings INTEGER;
  embeddings_by_domain JSON;
BEGIN
  -- Get total embeddings
  IF p_user_id IS NOT NULL THEN
    SELECT COUNT(*) INTO total_embeddings 
    FROM public.user_metadata_embeddings 
    WHERE user_id = p_user_id;
    
    -- Get breakdown by domain
    SELECT json_object_agg(domain_tag, domain_count) INTO embeddings_by_domain
    FROM (
      SELECT domain_tag, COUNT(*) as domain_count
      FROM public.user_metadata_embeddings
      WHERE user_id = p_user_id
      GROUP BY domain_tag
    ) domain_counts;
  ELSE
    SELECT COUNT(*) INTO total_embeddings 
    FROM public.user_metadata_embeddings;
    
    SELECT json_object_agg(domain_tag, domain_count) INTO embeddings_by_domain
    FROM (
      SELECT domain_tag, COUNT(*) as domain_count
      FROM public.user_metadata_embeddings
      GROUP BY domain_tag
    ) domain_counts;
  END IF;
  
  stats := json_build_object(
    'total_embeddings', total_embeddings,
    'embeddings_by_domain', COALESCE(embeddings_by_domain, '{}'::JSON),
    'user_id', p_user_id,
    'generated_at', NOW()
  );
  
  RETURN stats;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions to functions
GRANT EXECUTE ON FUNCTION search_metadata_embeddings(vector(1536), UUID, TEXT[], INTEGER) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION search_conversation_memory(vector(1536), UUID, INTEGER, TIMESTAMPTZ) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_user_context_summary(UUID, BOOLEAN, INTEGER) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION update_behavioral_metrics(UUID, TEXT, UUID, JSONB) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION cleanup_old_embeddings(INTEGER) TO service_role;
GRANT EXECUTE ON FUNCTION get_embedding_stats(UUID) TO authenticated, service_role;

-- Add helpful comments
COMMENT ON FUNCTION search_metadata_embeddings IS 'Performs vector similarity search across user metadata embeddings';
COMMENT ON FUNCTION search_conversation_memory IS 'Performs vector similarity search across user conversation history';
COMMENT ON FUNCTION get_user_context_summary IS 'Generates JSON summary of user context for AI prompts';
COMMENT ON FUNCTION update_behavioral_metrics IS 'Updates behavioral metrics for pillars/areas with validation';
COMMENT ON FUNCTION cleanup_old_embeddings IS 'Maintenance function to remove old embeddings';
COMMENT ON FUNCTION get_embedding_stats IS 'Returns statistics about embedding storage and distribution';