-- Migration 019: Automated Embedding Pipeline
-- Creates triggers and functions for automatic embedding generation
-- Reference: aurum-life-impl-plan.md

-- Create function to enqueue metadata embedding via PostgreSQL notifications
CREATE OR REPLACE FUNCTION enqueue_metadata_embedding(table_name TEXT, record_id UUID, user_id UUID)
RETURNS VOID AS $$
DECLARE
  json_payload JSONB;
  user_consent BOOLEAN := false;
BEGIN
  -- Check user consent for RAG snippet recording
  SELECT record_rag_snippets INTO user_consent
  FROM public.user_analytics_preferences 
  WHERE user_analytics_preferences.user_id = enqueue_metadata_embedding.user_id;
  
  -- Default to true if no preferences record exists
  user_consent := COALESCE(user_consent, true);
  
  -- Only proceed if user has consented
  IF user_consent THEN
    json_payload := json_build_object(
      'table', table_name,
      'id', record_id,
      'user_id', user_id,
      'timestamp', NOW()
    );
    
    -- Send notification to background processing system
    PERFORM pg_notify('metadata_embedding_queue', json_payload::text);
    
    -- Log the queued embedding request
    INSERT INTO public.webhook_logs (webhook_type, user_id, table_name, triggered_at, status)
    VALUES ('metadata_embedding_queued', user_id, table_name, NOW(), 'queued');
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create webhook_logs table if it doesn't exist (for tracking embedding requests)
CREATE TABLE IF NOT EXISTS public.webhook_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_type TEXT NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  table_name TEXT,
  triggered_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'pending',
  error_message TEXT,
  processed_at TIMESTAMPTZ
);

-- Enable RLS on webhook_logs
ALTER TABLE public.webhook_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "Users can view their webhook logs" 
ON public.webhook_logs FOR SELECT 
USING (auth.uid() = user_id);

-- Create embedding triggers for PAPT hierarchy tables

-- Pillars trigger
DROP TRIGGER IF EXISTS trg_pillars_enqueue_embedding ON public.pillars;
CREATE TRIGGER trg_pillars_enqueue_embedding
AFTER INSERT OR UPDATE OF name, description ON public.pillars
FOR EACH ROW 
EXECUTE FUNCTION enqueue_metadata_embedding('pillars', NEW.id, NEW.user_id);

-- Areas trigger  
DROP TRIGGER IF EXISTS trg_areas_enqueue_embedding ON public.areas;
CREATE TRIGGER trg_areas_enqueue_embedding
AFTER INSERT OR UPDATE OF name, description ON public.areas
FOR EACH ROW 
EXECUTE FUNCTION enqueue_metadata_embedding('areas', NEW.id, NEW.user_id);

-- Projects trigger
DROP TRIGGER IF EXISTS trg_projects_enqueue_embedding ON public.projects;
CREATE TRIGGER trg_projects_enqueue_embedding
AFTER INSERT OR UPDATE OF name, description ON public.projects
FOR EACH ROW 
EXECUTE FUNCTION enqueue_metadata_embedding('projects', NEW.id, NEW.user_id);

-- Tasks trigger
DROP TRIGGER IF EXISTS trg_tasks_enqueue_embedding ON public.tasks;
CREATE TRIGGER trg_tasks_enqueue_embedding
AFTER INSERT OR UPDATE OF name, description ON public.tasks
FOR EACH ROW 
EXECUTE FUNCTION enqueue_metadata_embedding('tasks', NEW.id, NEW.user_id);

-- Journal entries trigger
DROP TRIGGER IF EXISTS trg_journal_entries_enqueue_embedding ON public.journal_entries;
CREATE TRIGGER trg_journal_entries_enqueue_embedding
AFTER INSERT OR UPDATE OF title, content ON public.journal_entries
FOR EACH ROW 
WHEN (NEW.deleted = false) -- Only embed non-deleted entries
EXECUTE FUNCTION enqueue_metadata_embedding('journal_entries', NEW.id, NEW.user_id);

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION enqueue_metadata_embedding(TEXT, UUID, UUID) TO service_role;
GRANT ALL ON public.webhook_logs TO service_role;

-- Create index for webhook log queries
CREATE INDEX IF NOT EXISTS idx_webhook_logs_user_type_status 
ON public.webhook_logs (user_id, webhook_type, status, triggered_at DESC);

-- Add comments
COMMENT ON FUNCTION enqueue_metadata_embedding IS 'Triggers embedding generation for PAPT hierarchy changes, respects user consent';
COMMENT ON TABLE public.webhook_logs IS 'Tracks background processing requests including embedding generation';