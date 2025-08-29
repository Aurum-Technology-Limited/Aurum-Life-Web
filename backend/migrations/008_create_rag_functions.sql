-- HRM Phase 3: RAG Helper Functions
-- Reference: RAG_IMPLEMENTATION_GUIDE.md

-- Find similar journal entries
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

-- Multi-table semantic search for RAG
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