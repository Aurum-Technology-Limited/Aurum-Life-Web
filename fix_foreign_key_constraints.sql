-- Fix Foreign Key Constraints to Reference auth.users Instead of Legacy users Table
-- This resolves the critical foreign key constraint issue preventing data creation

-- Step 1: Drop existing foreign key constraints that reference the wrong table
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

-- For journal_templates table
ALTER TABLE public.journal_templates DROP CONSTRAINT IF EXISTS journal_templates_user_id_fkey;
ALTER TABLE public.journal_templates DROP CONSTRAINT IF EXISTS fk_journal_templates_user_id;

-- For journal_entries table
ALTER TABLE public.journal_entries DROP CONSTRAINT IF EXISTS journal_entries_user_id_fkey;
ALTER TABLE public.journal_entries DROP CONSTRAINT IF EXISTS fk_journal_entries_user_id;

-- For resources table
ALTER TABLE public.resources DROP CONSTRAINT IF EXISTS resources_user_id_fkey;
ALTER TABLE public.resources DROP CONSTRAINT IF EXISTS fk_resources_user_id;

-- For notifications table
ALTER TABLE public.notifications DROP CONSTRAINT IF EXISTS notifications_user_id_fkey;
ALTER TABLE public.notifications DROP CONSTRAINT IF EXISTS fk_notifications_user_id;

-- For notification_preferences table
ALTER TABLE public.notification_preferences DROP CONSTRAINT IF EXISTS notification_preferences_user_id_fkey;
ALTER TABLE public.notification_preferences DROP CONSTRAINT IF EXISTS fk_notification_preferences_user_id;

-- For project_templates table
ALTER TABLE public.project_templates DROP CONSTRAINT IF EXISTS project_templates_user_id_fkey;
ALTER TABLE public.project_templates DROP CONSTRAINT IF EXISTS fk_project_templates_user_id;

-- For user_stats table
ALTER TABLE public.user_stats DROP CONSTRAINT IF EXISTS user_stats_user_id_fkey;
ALTER TABLE public.user_stats DROP CONSTRAINT IF EXISTS fk_user_stats_user_id;

-- For password_reset_tokens table
ALTER TABLE public.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_user_id_fkey;
ALTER TABLE public.password_reset_tokens DROP CONSTRAINT IF EXISTS fk_password_reset_tokens_user_id;

-- Step 2: Add correct foreign key constraints that reference auth.users

-- Pillars table
ALTER TABLE public.pillars 
ADD CONSTRAINT pillars_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Areas table
ALTER TABLE public.areas 
ADD CONSTRAINT areas_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Projects table
ALTER TABLE public.projects 
ADD CONSTRAINT projects_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Tasks table
ALTER TABLE public.tasks 
ADD CONSTRAINT tasks_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Journal templates table
ALTER TABLE public.journal_templates 
ADD CONSTRAINT journal_templates_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Journal entries table
ALTER TABLE public.journal_entries 
ADD CONSTRAINT journal_entries_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Resources table
ALTER TABLE public.resources 
ADD CONSTRAINT resources_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Notifications table
ALTER TABLE public.notifications 
ADD CONSTRAINT notifications_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Notification preferences table
ALTER TABLE public.notification_preferences 
ADD CONSTRAINT notification_preferences_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Project templates table
ALTER TABLE public.project_templates 
ADD CONSTRAINT project_templates_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- User stats table
ALTER TABLE public.user_stats 
ADD CONSTRAINT user_stats_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Password reset tokens table
ALTER TABLE public.password_reset_tokens 
ADD CONSTRAINT password_reset_tokens_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

-- Step 3: Verify the changes
-- (This will be done through testing)