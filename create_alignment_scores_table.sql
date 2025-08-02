-- Alignment Scores table for tracking user task completion points
-- This table logs every task completion event with calculated points for analytics and rolling calculations

CREATE TABLE IF NOT EXISTS public.alignment_scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL,
    points_earned INTEGER NOT NULL,
    task_priority TEXT,
    project_priority TEXT,
    area_importance INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_alignment_scores_user_id ON public.alignment_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_alignment_scores_created_at ON public.alignment_scores(created_at);
CREATE INDEX IF NOT EXISTS idx_alignment_scores_user_created ON public.alignment_scores(user_id, created_at);

-- Add RLS (Row Level Security) policies
ALTER TABLE public.alignment_scores ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own alignment scores
CREATE POLICY "Users can view own alignment scores" ON public.alignment_scores
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can only insert their own alignment scores
CREATE POLICY "Users can insert own alignment scores" ON public.alignment_scores
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER set_alignment_scores_updated_at
    BEFORE UPDATE ON public.alignment_scores
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

-- Add monthly_goal to user_profiles table if it doesn't exist
ALTER TABLE public.user_profiles 
ADD COLUMN IF NOT EXISTS monthly_alignment_goal INTEGER DEFAULT NULL;

COMMENT ON TABLE public.alignment_scores IS 'Tracks points earned from task completions for alignment scoring system';
COMMENT ON COLUMN public.alignment_scores.points_earned IS 'Total points earned from this task completion (base + bonuses)';
COMMENT ON COLUMN public.alignment_scores.task_priority IS 'Priority of the completed task for analytics';
COMMENT ON COLUMN public.alignment_scores.project_priority IS 'Priority of the parent project for analytics';
COMMENT ON COLUMN public.alignment_scores.area_importance IS 'Importance level of the parent area for analytics';
COMMENT ON COLUMN public.user_profiles.monthly_alignment_goal IS 'User-set monthly alignment score goal';