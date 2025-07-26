-- Aurum Life PostgreSQL Schema for Supabase
-- Generated for migration from MongoDB to Supabase
-- Date: January 2025

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable RLS on auth.users (Supabase managed)
-- Users table is managed by Supabase Auth, we'll extend it with a profile

-- User Profiles (extends Supabase auth.users)
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    google_id TEXT,
    profile_picture TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    level INTEGER DEFAULT 1,
    total_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pillars (Top-level life areas)
CREATE TABLE public.pillars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    icon TEXT DEFAULT '🎯',
    color TEXT DEFAULT '#F4B400',
    sort_order INTEGER DEFAULT 0,
    archived BOOLEAN DEFAULT FALSE,
    time_allocation_percentage DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Areas (Sub-categories within pillars)  
CREATE TABLE public.areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    pillar_id UUID REFERENCES public.pillars(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    icon TEXT DEFAULT '🎯',
    color TEXT DEFAULT '#F4B400',
    importance INTEGER DEFAULT 3 CHECK (importance >= 1 AND importance <= 5),
    archived BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects (Specific initiatives within areas)
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    area_id UUID NOT NULL REFERENCES public.areas(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    icon TEXT DEFAULT '🚀',
    deadline TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'Not Started' CHECK (status IN ('Not Started', 'In Progress', 'Completed', 'On Hold')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    importance INTEGER DEFAULT 3 CHECK (importance >= 1 AND importance <= 5),
    completion_percentage DECIMAL(5,2) DEFAULT 0.0,
    archived BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks (Individual action items)
CREATE TABLE public.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'review', 'completed')),
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    due_date TIMESTAMP WITH TIME ZONE,
    due_time TEXT, -- Time in HH:MM format
    reminder_date TIMESTAMP WITH TIME ZONE,
    category TEXT DEFAULT 'general',
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    dependency_task_ids UUID[] DEFAULT ARRAY[]::UUID[],
    recurrence TEXT DEFAULT 'none' CHECK (recurrence IN ('none', 'daily', 'weekly', 'monthly', 'custom')),
    recurrence_interval INTEGER DEFAULT 1,
    recurrence_pattern JSONB,
    next_due_date TIMESTAMP WITH TIME ZONE,
    kanban_column TEXT DEFAULT 'to_do' CHECK (kanban_column IN ('to_do', 'in_progress', 'review', 'done')),
    sort_order INTEGER DEFAULT 0,
    estimated_duration INTEGER, -- in minutes
    sub_task_completion_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal Templates
CREATE TABLE public.journal_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    template_type TEXT NOT NULL CHECK (template_type IN (
        'daily_reflection', 'gratitude', 'goal_setting', 'weekly_review', 
        'mood_tracker', 'learning_log', 'creative_writing', 'problem_solving', 
        'habit_tracker', 'custom'
    )),
    prompts TEXT[] DEFAULT ARRAY[]::TEXT[],
    default_tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_default BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    icon TEXT DEFAULT '📝',
    color TEXT DEFAULT '#F4B400',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Journal Entries
CREATE TABLE public.journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id UUID REFERENCES public.journal_templates(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    mood TEXT DEFAULT 'reflective' CHECK (mood IN (
        'optimistic', 'inspired', 'reflective', 'challenging', 'anxious', 
        'grateful', 'excited', 'frustrated', 'peaceful', 'motivated'
    )),
    energy_level TEXT DEFAULT 'moderate' CHECK (energy_level IN (
        'very_low', 'low', 'moderate', 'high', 'very_high'
    )),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    template_responses JSONB DEFAULT '{}'::JSONB,
    weather TEXT,
    location TEXT,
    word_count INTEGER DEFAULT 0,
    reading_time_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Resources (File attachments)
CREATE TABLE public.resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('document', 'image', 'spreadsheet', 'presentation', 'archive', 'other')),
    category TEXT DEFAULT 'document' CHECK (category IN ('reference', 'template', 'attachment', 'archive', 'media', 'document')),
    mime_type TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    file_path TEXT, -- Supabase Storage path instead of base64
    description TEXT DEFAULT '',
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    
    -- Contextual attachment fields
    parent_id UUID,
    parent_type TEXT CHECK (parent_type IN ('project', 'task', 'area', 'pillar', 'journal_entry')),
    
    -- Legacy attachment arrays (for migration compatibility)
    attached_to_tasks UUID[] DEFAULT ARRAY[]::UUID[],
    attached_to_projects UUID[] DEFAULT ARRAY[]::UUID[],
    attached_to_areas UUID[] DEFAULT ARRAY[]::UUID[],
    attached_to_pillars UUID[] DEFAULT ARRAY[]::UUID[],
    attached_to_journal_entries UUID[] DEFAULT ARRAY[]::UUID[],
    
    version INTEGER DEFAULT 1,
    parent_resource_id UUID REFERENCES public.resources(id),
    is_current_version BOOLEAN DEFAULT TRUE,
    folder_path TEXT DEFAULT '/',
    is_archived BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN (
        'task_due', 'task_overdue', 'task_reminder', 'project_deadline', 
        'recurring_task', 'achievement_unlocked', 'unblocked_task'
    )),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    
    -- Related entity references
    related_task_id UUID REFERENCES public.tasks(id) ON DELETE CASCADE,
    related_project_id UUID REFERENCES public.projects(id) ON DELETE CASCADE,
    related_area_id UUID REFERENCES public.areas(id) ON DELETE CASCADE,
    related_pillar_id UUID REFERENCES public.pillars(id) ON DELETE CASCADE,
    
    -- Metadata
    project_name TEXT,
    task_name TEXT,
    priority TEXT CHECK (priority IN ('low', 'medium', 'high')),
    
    -- Notification state
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    channels TEXT[] DEFAULT ARRAY['browser']::TEXT[],
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification Preferences
CREATE TABLE public.notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Channel preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    browser_notifications BOOLEAN DEFAULT TRUE,
    
    -- Type preferences
    task_due_notifications BOOLEAN DEFAULT TRUE,
    task_overdue_notifications BOOLEAN DEFAULT TRUE,
    task_reminder_notifications BOOLEAN DEFAULT TRUE,
    project_deadline_notifications BOOLEAN DEFAULT TRUE,
    recurring_task_notifications BOOLEAN DEFAULT TRUE,
    achievement_notifications BOOLEAN DEFAULT TRUE,
    unblocked_task_notifications BOOLEAN DEFAULT TRUE,
    
    -- Timing preferences
    reminder_advance_time INTEGER DEFAULT 30,
    overdue_check_interval INTEGER DEFAULT 60,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '08:00',
    
    -- Email preferences
    daily_digest BOOLEAN DEFAULT FALSE,
    weekly_digest BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Project Templates
CREATE TABLE public.project_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task Templates (for project templates)
CREATE TABLE public.task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.project_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    estimated_duration INTEGER,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Statistics
CREATE TABLE public.user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    total_journal_entries INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    total_areas INTEGER DEFAULT 0,
    total_projects INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    courses_enrolled INTEGER DEFAULT 0,
    courses_completed INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id)
);

-- Password Reset Tokens (for transition period)
CREATE TABLE public.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_pillars_user_id ON public.pillars(user_id);
CREATE INDEX idx_areas_user_id ON public.areas(user_id);
CREATE INDEX idx_areas_pillar_id ON public.areas(pillar_id);
CREATE INDEX idx_projects_user_id ON public.projects(user_id);
CREATE INDEX idx_projects_area_id ON public.projects(area_id);
CREATE INDEX idx_tasks_user_id ON public.tasks(user_id);
CREATE INDEX idx_tasks_project_id ON public.tasks(project_id);
CREATE INDEX idx_tasks_due_date ON public.tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_status ON public.tasks(status);
CREATE INDEX idx_journal_entries_user_id ON public.journal_entries(user_id);
CREATE INDEX idx_journal_entries_created_at ON public.journal_entries(created_at);
CREATE INDEX idx_resources_user_id ON public.resources(user_id);
CREATE INDEX idx_resources_parent ON public.resources(parent_type, parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_unread ON public.notifications(user_id, is_read) WHERE is_read = FALSE;

-- Enable Row Level Security (RLS)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pillars ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journal_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Users can only access their own data
CREATE POLICY "Users can manage their own profile" ON public.user_profiles FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users can manage their own pillars" ON public.pillars FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own areas" ON public.areas FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own projects" ON public.projects FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own tasks" ON public.tasks FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own journal templates" ON public.journal_templates FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own journal entries" ON public.journal_entries FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own resources" ON public.resources FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own notifications" ON public.notifications FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own notification preferences" ON public.notification_preferences FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own project templates" ON public.project_templates FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view task templates for their project templates" ON public.task_templates FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.project_templates pt WHERE pt.id = template_id AND pt.user_id = auth.uid())
);
CREATE POLICY "Users can manage their own user stats" ON public.user_stats FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can manage their own password reset tokens" ON public.password_reset_tokens FOR ALL USING (auth.uid() = user_id);

-- Functions and Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all relevant tables
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pillars_updated_at BEFORE UPDATE ON public.pillars FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_areas_updated_at BEFORE UPDATE ON public.areas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_journal_templates_updated_at BEFORE UPDATE ON public.journal_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON public.journal_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_resources_updated_at BEFORE UPDATE ON public.resources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_preferences_updated_at BEFORE UPDATE ON public.notification_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_templates_updated_at BEFORE UPDATE ON public.project_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_stats_updated_at BEFORE UPDATE ON public.user_stats FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();