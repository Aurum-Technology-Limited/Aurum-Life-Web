-- Fix Foreign Key Constraints to Reference public.users Instead of auth.users
-- This resolves the critical foreign key constraint issue preventing data creation
-- Issue: Users exist in public.users but constraints reference auth.users

-- Step 1: Drop existing foreign key constraints that reference auth.users
-- Note: We'll identify the actual constraint names first

-- For pillars table
ALTER TABLE public.pillars DROP CONSTRAINT IF EXISTS pillars_user_id_fkey;
ALTER TABLE public.pillars DROP CONSTRAINT IF EXISTS fk_pillars_user_id;

-- For areas table  
ALTER TABLE public.areas DROP CONSTRAINT IF EXISTS areas_user_id_fkey;
ALTER TABLE public.areas DROP CONSTRAINT IF EXISTS fk_areas_user_id;

-- For projects table
ALTER TABLE public.projects DROP CONSTRAINT IF EXISTS projects_user_id_fkey;
ALTER TABLE public.projects DROP CONSTRAINT IF EXISTS fk_projects_user_id;

-- For tasks table
ALTER TABLE public.tasks DROP CONSTRAINT IF EXISTS tasks_user_id_fkey;
ALTER TABLE public.tasks DROP CONSTRAINT IF EXISTS fk_tasks_user_id;

-- For daily_reflections table
ALTER TABLE public.daily_reflections DROP CONSTRAINT IF EXISTS daily_reflections_user_id_fkey;

-- For sleep_reflections table
ALTER TABLE public.sleep_reflections DROP CONSTRAINT IF EXISTS sleep_reflections_user_id_fkey;

-- For journals table
ALTER TABLE public.journals DROP CONSTRAINT IF EXISTS journals_user_id_fkey;

-- For ai_interactions table
ALTER TABLE public.ai_interactions DROP CONSTRAINT IF EXISTS ai_interactions_user_id_fkey;

-- For user_points table
ALTER TABLE public.user_points DROP CONSTRAINT IF EXISTS user_points_user_id_fkey;

-- For achievements table
ALTER TABLE public.achievements DROP CONSTRAINT IF EXISTS achievements_user_id_fkey;

-- For alignment_scores table
ALTER TABLE public.alignment_scores DROP CONSTRAINT IF EXISTS alignment_scores_user_id_fkey;

-- For username_change_records table
ALTER TABLE public.username_change_records DROP CONSTRAINT IF EXISTS username_change_records_user_id_fkey;

-- For journal_templates table (if exists)
ALTER TABLE public.journal_templates DROP CONSTRAINT IF EXISTS journal_templates_user_id_fkey;
ALTER TABLE public.journal_templates DROP CONSTRAINT IF EXISTS fk_journal_templates_user_id;

-- For journal_entries table (if exists)
ALTER TABLE public.journal_entries DROP CONSTRAINT IF EXISTS journal_entries_user_id_fkey;
ALTER TABLE public.journal_entries DROP CONSTRAINT IF EXISTS fk_journal_entries_user_id;

-- For resources table (if exists)
ALTER TABLE public.resources DROP CONSTRAINT IF EXISTS resources_user_id_fkey;
ALTER TABLE public.resources DROP CONSTRAINT IF EXISTS fk_resources_user_id;

-- For notifications table (if exists)
ALTER TABLE public.notifications DROP CONSTRAINT IF EXISTS notifications_user_id_fkey;
ALTER TABLE public.notifications DROP CONSTRAINT IF EXISTS fk_notifications_user_id;

-- For notification_preferences table (if exists)
ALTER TABLE public.notification_preferences DROP CONSTRAINT IF EXISTS notification_preferences_user_id_fkey;
ALTER TABLE public.notification_preferences DROP CONSTRAINT IF EXISTS fk_notification_preferences_user_id;

-- For project_templates table (if exists)
ALTER TABLE public.project_templates DROP CONSTRAINT IF EXISTS project_templates_user_id_fkey;
ALTER TABLE public.project_templates DROP CONSTRAINT IF EXISTS fk_project_templates_user_id;

-- For user_stats table (if exists)
ALTER TABLE public.user_stats DROP CONSTRAINT IF EXISTS user_stats_user_id_fkey;
ALTER TABLE public.user_stats DROP CONSTRAINT IF EXISTS fk_user_stats_user_id;

-- For password_reset_tokens table (if exists)
ALTER TABLE public.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_user_id_fkey;
ALTER TABLE public.password_reset_tokens DROP CONSTRAINT IF EXISTS fk_password_reset_tokens_user_id;

-- Step 2: Add correct foreign key constraints that reference public.users(id)

-- Pillars table
ALTER TABLE public.pillars 
ADD CONSTRAINT pillars_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Areas table
ALTER TABLE public.areas 
ADD CONSTRAINT areas_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Projects table
ALTER TABLE public.projects 
ADD CONSTRAINT projects_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Tasks table
ALTER TABLE public.tasks 
ADD CONSTRAINT tasks_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Daily reflections table
ALTER TABLE public.daily_reflections 
ADD CONSTRAINT daily_reflections_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Sleep reflections table
ALTER TABLE public.sleep_reflections 
ADD CONSTRAINT sleep_reflections_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Journals table
ALTER TABLE public.journals 
ADD CONSTRAINT journals_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- AI interactions table
ALTER TABLE public.ai_interactions 
ADD CONSTRAINT ai_interactions_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- User points table
ALTER TABLE public.user_points 
ADD CONSTRAINT user_points_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Achievements table
ALTER TABLE public.achievements 
ADD CONSTRAINT achievements_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Alignment scores table
ALTER TABLE public.alignment_scores 
ADD CONSTRAINT alignment_scores_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Username change records table
ALTER TABLE public.username_change_records 
ADD CONSTRAINT username_change_records_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Optional tables (if they exist)

-- Journal templates table
ALTER TABLE public.journal_templates 
ADD CONSTRAINT journal_templates_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Journal entries table
ALTER TABLE public.journal_entries 
ADD CONSTRAINT journal_entries_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Resources table
ALTER TABLE public.resources 
ADD CONSTRAINT resources_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Notifications table
ALTER TABLE public.notifications 
ADD CONSTRAINT notifications_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Notification preferences table
ALTER TABLE public.notification_preferences 
ADD CONSTRAINT notification_preferences_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Project templates table
ALTER TABLE public.project_templates 
ADD CONSTRAINT project_templates_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- User stats table
ALTER TABLE public.user_stats 
ADD CONSTRAINT user_stats_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Password reset tokens table
ALTER TABLE public.password_reset_tokens 
ADD CONSTRAINT password_reset_tokens_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- Step 3: Create a comment to document this change
COMMENT ON TABLE public.users IS 'Legacy users table for hybrid authentication system. All foreign keys reference this table instead of auth.users for compatibility.';

-- Step 4: Verify the changes
-- (This will be done through testing)