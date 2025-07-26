-- Add missing archived column to tasks table
ALTER TABLE public.tasks ADD COLUMN archived BOOLEAN DEFAULT FALSE;