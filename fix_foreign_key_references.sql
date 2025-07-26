-- Fix foreign key references to point to public.users instead of auth.users
-- This aligns with the backend that creates users in public.users table

-- Drop existing foreign key constraints and recreate them to reference public.users

-- user_profiles
ALTER TABLE public.user_profiles DROP CONSTRAINT user_profiles_id_fkey;
ALTER TABLE public.user_profiles ADD CONSTRAINT user_profiles_id_fkey 
    FOREIGN KEY (id) REFERENCES public.users(id) ON DELETE CASCADE;

-- pillars
ALTER TABLE public.pillars DROP CONSTRAINT pillars_user_id_fkey;
ALTER TABLE public.pillars ADD CONSTRAINT pillars_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- areas  
ALTER TABLE public.areas DROP CONSTRAINT areas_user_id_fkey;
ALTER TABLE public.areas ADD CONSTRAINT areas_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- projects
ALTER TABLE public.projects DROP CONSTRAINT projects_user_id_fkey;
ALTER TABLE public.projects ADD CONSTRAINT projects_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- tasks
ALTER TABLE public.tasks DROP CONSTRAINT tasks_user_id_fkey;
ALTER TABLE public.tasks ADD CONSTRAINT tasks_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- journal_templates
ALTER TABLE public.journal_templates DROP CONSTRAINT journal_templates_user_id_fkey;
ALTER TABLE public.journal_templates ADD CONSTRAINT journal_templates_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- journal_entries
ALTER TABLE public.journal_entries DROP CONSTRAINT journal_entries_user_id_fkey;
ALTER TABLE public.journal_entries ADD CONSTRAINT journal_entries_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- resources
ALTER TABLE public.resources DROP CONSTRAINT resources_user_id_fkey;
ALTER TABLE public.resources ADD CONSTRAINT resources_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- notifications  
ALTER TABLE public.notifications DROP CONSTRAINT notifications_user_id_fkey;
ALTER TABLE public.notifications ADD CONSTRAINT notifications_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- user_stats
ALTER TABLE public.user_stats DROP CONSTRAINT user_stats_user_id_fkey;
ALTER TABLE public.user_stats ADD CONSTRAINT user_stats_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- password_reset_tokens
ALTER TABLE public.password_reset_tokens DROP CONSTRAINT password_reset_tokens_user_id_fkey;
ALTER TABLE public.password_reset_tokens ADD CONSTRAINT password_reset_tokens_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- browser_notifications
ALTER TABLE public.browser_notifications DROP CONSTRAINT browser_notifications_user_id_fkey;
ALTER TABLE public.browser_notifications ADD CONSTRAINT browser_notifications_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

-- project_templates  
ALTER TABLE public.project_templates DROP CONSTRAINT project_templates_user_id_fkey;
ALTER TABLE public.project_templates ADD CONSTRAINT project_templates_user_id_fkey 
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;