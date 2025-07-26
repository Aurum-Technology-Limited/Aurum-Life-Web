-- Fix user_stats table schema by dropping and recreating with correct structure
DROP TABLE IF EXISTS public.user_stats CASCADE;

CREATE TABLE public.user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    total_journal_entries INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    total_areas INTEGER DEFAULT 0,
    total_projects INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    courses_enrolled INTEGER DEFAULT 0,
    courses_completed INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Create index on user_id for performance
    CONSTRAINT user_stats_user_id_key UNIQUE (user_id)
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON public.user_stats (user_id);

-- Enable RLS if needed
ALTER TABLE public.user_stats ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for user isolation
CREATE POLICY "Users can only access their own stats" ON public.user_stats
    FOR ALL USING (auth.uid()::text = user_id::text);