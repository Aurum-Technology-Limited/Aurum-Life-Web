-- Update Alignment Scores table for project-based scoring system
-- Strategic Shift: From task-based to project-based scoring (outcomes over activities)

-- First, create backup of existing data if needed
-- CREATE TABLE alignment_scores_backup AS SELECT * FROM public.alignment_scores;

-- Drop existing table constraints and indexes related to task_id
DROP INDEX IF EXISTS idx_alignment_scores_task_id;

-- Add project_id column and remove task_id
-- Note: We'll keep task_id for now to avoid data loss, but make it nullable
ALTER TABLE public.alignment_scores 
ADD COLUMN IF NOT EXISTS project_id UUID,
ALTER COLUMN task_id DROP NOT NULL;

-- Add new indexes for project-based queries  
CREATE INDEX IF NOT EXISTS idx_alignment_scores_project_id ON public.alignment_scores(project_id);
CREATE INDEX IF NOT EXISTS idx_alignment_scores_user_project ON public.alignment_scores(user_id, project_id);

-- Remove task_priority column as it's no longer relevant for project-based scoring
-- ALTER TABLE public.alignment_scores DROP COLUMN IF EXISTS task_priority;

-- Update comments to reflect project-based scoring
COMMENT ON TABLE public.alignment_scores IS 'Tracks points earned from project completions for alignment scoring system (strategic shift from task-based to project-based)';
COMMENT ON COLUMN public.alignment_scores.project_id IS 'ID of the completed project that earned these points';
COMMENT ON COLUMN public.alignment_scores.points_earned IS 'Total points earned from project completion (base 50 + priority 25 + area importance 50)';
COMMENT ON COLUMN public.alignment_scores.project_priority IS 'Priority of the completed project for analytics';
COMMENT ON COLUMN public.alignment_scores.area_importance IS 'Importance level of the parent area for analytics';

-- Add constraint to ensure either task_id or project_id is present (for backwards compatibility)
-- ALTER TABLE public.alignment_scores ADD CONSTRAINT check_task_or_project CHECK (task_id IS NOT NULL OR project_id IS NOT NULL);

-- Update RLS policies to work with project_id
DROP POLICY IF EXISTS "Users can view own alignment scores" ON public.alignment_scores;
DROP POLICY IF EXISTS "Users can insert own alignment scores" ON public.alignment_scores;

-- Recreate policies
CREATE POLICY "Users can view own alignment scores" ON public.alignment_scores
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own alignment scores" ON public.alignment_scores
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Note: Migration script for existing data can be added here if needed
-- For now, we're implementing a clean slate for project-based scoring