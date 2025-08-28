-- pgvector RAG Implementation for Aurum Life
-- Enables semantic search and contextual AI responses

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Journal Entries Embeddings
-- Most valuable for RAG - contains rich user reflections and insights
ALTER TABLE public.journal_entries 
ADD COLUMN IF NOT EXISTS content_embedding vector(1536), -- OpenAI embeddings dimension
ADD COLUMN IF NOT EXISTS title_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

-- Create HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_journal_content_embedding 
ON public.journal_entries 
USING hnsw (content_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 2. Daily Reflections Embeddings
-- Valuable for understanding patterns and progress over time
ALTER TABLE public.daily_reflections
ADD COLUMN IF NOT EXISTS reflection_embedding vector(1536),
ADD COLUMN IF NOT EXISTS accomplishment_embedding vector(1536),
ADD COLUMN IF NOT EXISTS challenges_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_reflection_embedding 
ON public.daily_reflections 
USING hnsw (reflection_embedding vector_cosine_ops);

-- 3. Tasks with Rich Descriptions
-- For finding similar tasks and learning from past approaches
ALTER TABLE public.tasks
ADD COLUMN IF NOT EXISTS description_embedding vector(1536),
ADD COLUMN IF NOT EXISTS name_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_task_description_embedding 
ON public.tasks 
USING hnsw (description_embedding vector_cosine_ops)
WHERE description IS NOT NULL AND description != '';

-- 4. Projects Embeddings
-- For strategic alignment and finding related initiatives
ALTER TABLE public.projects
ADD COLUMN IF NOT EXISTS combined_embedding vector(1536), -- name + description
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_project_embedding 
ON public.projects 
USING hnsw (combined_embedding vector_cosine_ops);

-- 5. AI Conversation Memory
-- New table to store conversation context for continuity
CREATE TABLE IF NOT EXISTS ai_conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
    message_content TEXT NOT NULL,
    message_embedding vector(1536),
    context_window JSONB DEFAULT '{}', -- Store relevant entity IDs
    tokens_used INTEGER DEFAULT 0,
    model_used TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_embedding 
ON ai_conversation_memory 
USING hnsw (message_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_conversation_user_date 
ON ai_conversation_memory (user_id, conversation_date DESC);

-- 6. Insights and Patterns Table
-- Store discovered patterns and insights with embeddings
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'pattern', 'recommendation', 'achievement', 'challenge', 'opportunity'
    )),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_embedding vector(1536),
    related_entities JSONB DEFAULT '{}', -- {pillars: [], areas: [], projects: [], tasks: []}
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    is_acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_insights_embedding 
ON ai_insights 
USING hnsw (content_embedding vector_cosine_ops);

-- Helper Functions for Semantic Search

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

-- Find similar tasks across all projects
CREATE OR REPLACE FUNCTION find_similar_tasks(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    user_id_filter UUID DEFAULT NULL,
    include_completed BOOLEAN DEFAULT FALSE
)
RETURNS TABLE(
    id UUID,
    name TEXT,
    description TEXT,
    project_name TEXT,
    similarity FLOAT,
    status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.name,
        t.description,
        p.name as project_name,
        1 - (t.description_embedding <=> query_embedding) as similarity,
        t.status
    FROM tasks t
    JOIN projects p ON t.project_id = p.id
    WHERE 
        t.description_embedding IS NOT NULL
        AND (user_id_filter IS NULL OR t.user_id = user_id_filter)
        AND (include_completed OR t.status != 'completed')
    ORDER BY t.description_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Multi-table semantic search
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
        
        UNION ALL
        
        -- AI insights
        SELECT 
            'ai_insight' as entity_type,
            id as entity_id,
            title,
            content,
            1 - (content_embedding <=> query_embedding) as similarity,
            created_at,
            jsonb_build_object(
                'insight_type', insight_type,
                'confidence_score', confidence_score,
                'related_entities', related_entities
            ) as metadata
        FROM ai_insights
        WHERE 
            user_id = user_id_filter
            AND content_embedding IS NOT NULL
            AND (date_range_days IS NULL OR created_at >= NOW() - INTERVAL '1 day' * date_range_days)
    )
    SELECT * FROM combined_results
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

-- RLS Policies for new tables
ALTER TABLE ai_conversation_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own AI conversations" 
ON ai_conversation_memory FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own AI insights" 
ON ai_insights FOR ALL USING (auth.uid() = user_id);

-- Maintenance function to update embeddings
CREATE OR REPLACE FUNCTION update_embedding_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.embedding_updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for embedding updates
CREATE TRIGGER update_journal_embedding_timestamp
BEFORE UPDATE OF content_embedding, title_embedding ON journal_entries
FOR EACH ROW EXECUTE FUNCTION update_embedding_timestamp();

CREATE TRIGGER update_task_embedding_timestamp
BEFORE UPDATE OF description_embedding, name_embedding ON tasks
FOR EACH ROW EXECUTE FUNCTION update_embedding_timestamp();

-- Comments for documentation
COMMENT ON COLUMN journal_entries.content_embedding IS 'Vector embedding of journal content for semantic search';
COMMENT ON COLUMN tasks.description_embedding IS 'Vector embedding of task description for finding similar tasks';
COMMENT ON TABLE ai_conversation_memory IS 'Stores AI conversation history with embeddings for context retrieval';
COMMENT ON TABLE ai_insights IS 'AI-generated insights and patterns discovered from user data';
COMMENT ON FUNCTION rag_search IS 'Multi-table semantic search for RAG implementation';