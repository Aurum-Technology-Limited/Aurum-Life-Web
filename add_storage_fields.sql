-- Add Supabase Storage fields to resources table
-- Migration to support file storage in Supabase Storage instead of base64

-- Add storage fields
ALTER TABLE public.resources 
ADD COLUMN IF NOT EXISTS storage_bucket TEXT,
ADD COLUMN IF NOT EXISTS storage_path TEXT,
ADD COLUMN IF NOT EXISTS file_url TEXT;

-- Make file_content optional (for backward compatibility during migration)
ALTER TABLE public.resources 
ALTER COLUMN file_content DROP NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN public.resources.storage_bucket IS 'Supabase Storage bucket name';
COMMENT ON COLUMN public.resources.storage_path IS 'File path in Supabase Storage';
COMMENT ON COLUMN public.resources.file_url IS 'Public or signed URL for file access';
COMMENT ON COLUMN public.resources.file_content IS 'Legacy base64 content - being phased out';