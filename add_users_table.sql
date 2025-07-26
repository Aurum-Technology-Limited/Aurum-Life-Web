-- Add users table to Supabase for compatibility with existing auth system
-- This allows the current authentication to work while we migrate to full Supabase Auth

CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT DEFAULT '',
    last_name TEXT DEFAULT '',
    password_hash TEXT,
    google_id TEXT,
    profile_picture TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    level INTEGER DEFAULT 1,
    total_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "Users can manage their own data" ON public.users FOR ALL USING (auth.uid() = id);

-- Index for performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_username ON public.users(username);