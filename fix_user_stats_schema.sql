-- Add missing updated_at column to user_stats table
ALTER TABLE public.user_stats 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();