-- Add scoring fields to tasks table for The Architect's performance optimization
-- These fields support the event-driven scoring engine with Celery tasks

ALTER TABLE public.tasks 
ADD COLUMN IF NOT EXISTS current_score DECIMAL(5,2) DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS area_importance INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS project_importance INTEGER DEFAULT 3,
ADD COLUMN IF NOT EXISTS dependencies_met BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS scheduled_date DATE,
ADD COLUMN IF NOT EXISTS is_overdue BOOLEAN DEFAULT FALSE;

-- Add indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed_score ON public.tasks(user_id, completed, current_score DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_user_score_due ON public.tasks(user_id, current_score DESC, due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled_date ON public.tasks(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_tasks_dependencies ON public.tasks(dependencies_met);

-- Update existing tasks with default scoring values
UPDATE public.tasks 
SET 
    current_score = CASE 
        WHEN priority = 'high' THEN 75.0
        WHEN priority = 'medium' THEN 50.0
        ELSE 25.0
    END,
    area_importance = 3,
    project_importance = 3,
    dependencies_met = TRUE,
    is_overdue = (due_date IS NOT NULL AND due_date < NOW())
WHERE current_score IS NULL OR current_score = 0.0;

-- Add user_stats table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    level INTEGER DEFAULT 1,
    total_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    projects_completed INTEGER DEFAULT 0,
    journal_entries INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create index for user_stats
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON public.user_stats(user_id);

-- Insert default user stats for existing users
INSERT INTO public.user_stats (user_id, level, total_points, current_streak)
SELECT id, 1, 0, 0 
FROM auth.users 
WHERE id NOT IN (SELECT user_id FROM public.user_stats)
ON CONFLICT (user_id) DO NOTHING;