-- Supabase Storage Bucket Configuration
-- Run this in your Supabase SQL Editor to set up CDN-optimized buckets

-- ========================================
-- 1. CREATE STORAGE BUCKETS
-- ========================================

-- Create avatars bucket (public)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('avatars', 'avatars', true, 5242880, ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif'])
ON CONFLICT (id) DO UPDATE
SET 
  public = true,
  file_size_limit = 5242880,
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif'];

-- Create images bucket (public)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('images', 'images', true, 10485760, ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml'])
ON CONFLICT (id) DO UPDATE
SET 
  public = true,
  file_size_limit = 10485760,
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml'];

-- Create documents bucket (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('documents', 'documents', false, 52428800, ARRAY['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'])
ON CONFLICT (id) DO UPDATE
SET 
  public = false,
  file_size_limit = 52428800,
  allowed_mime_types = ARRAY['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];

-- Create assets bucket (public, for logos, icons, etc.)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('assets', 'assets', true, 2097152, ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml', 'image/x-icon'])
ON CONFLICT (id) DO UPDATE
SET 
  public = true,
  file_size_limit = 2097152,
  allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/svg+xml', 'image/x-icon'];

-- ========================================
-- 2. STORAGE POLICIES (RLS)
-- ========================================

-- Enable RLS on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Avatar images are publicly accessible" ON storage.objects;
DROP POLICY IF EXISTS "Users can upload their own avatar" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own avatar" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own avatar" ON storage.objects;
DROP POLICY IF EXISTS "Public images are accessible to everyone" ON storage.objects;
DROP POLICY IF EXISTS "Authenticated users can upload images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own images" ON storage.objects;
DROP POLICY IF EXISTS "Users can view their own documents" ON storage.objects;
DROP POLICY IF EXISTS "Users can upload their own documents" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own documents" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own documents" ON storage.objects;
DROP POLICY IF EXISTS "Assets are publicly accessible" ON storage.objects;

-- AVATARS BUCKET POLICIES
-- Public read access
CREATE POLICY "Avatar images are publicly accessible"
ON storage.objects FOR SELECT
USING (bucket_id = 'avatars');

-- Authenticated users can upload their own avatar
CREATE POLICY "Users can upload their own avatar"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can update their own avatar
CREATE POLICY "Users can update their own avatar"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can delete their own avatar
CREATE POLICY "Users can delete their own avatar"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'avatars' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- IMAGES BUCKET POLICIES
-- Public read access
CREATE POLICY "Public images are accessible to everyone"
ON storage.objects FOR SELECT
USING (bucket_id = 'images');

-- Authenticated users can upload images
CREATE POLICY "Authenticated users can upload images"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'images' 
  AND auth.role() = 'authenticated'
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can update their own images
CREATE POLICY "Users can update their own images"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can delete their own images
CREATE POLICY "Users can delete their own images"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- DOCUMENTS BUCKET POLICIES (Private)
-- Users can only view their own documents
CREATE POLICY "Users can view their own documents"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can upload their own documents
CREATE POLICY "Users can upload their own documents"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can update their own documents
CREATE POLICY "Users can update their own documents"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Users can delete their own documents
CREATE POLICY "Users can delete their own documents"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- ASSETS BUCKET POLICIES
-- Public read access for assets
CREATE POLICY "Assets are publicly accessible"
ON storage.objects FOR SELECT
USING (bucket_id = 'assets');

-- ========================================
-- 3. HELPER FUNCTIONS
-- ========================================

-- Function to get storage usage for a user
CREATE OR REPLACE FUNCTION get_user_storage_usage(user_id uuid)
RETURNS TABLE (
  bucket_name text,
  file_count bigint,
  total_size_bytes bigint,
  total_size_mb numeric
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    bucket_id::text as bucket_name,
    COUNT(*)::bigint as file_count,
    COALESCE(SUM(metadata->>'size')::bigint, 0) as total_size_bytes,
    ROUND(COALESCE(SUM(metadata->>'size')::numeric, 0) / 1048576, 2) as total_size_mb
  FROM storage.objects
  WHERE owner = user_id
  GROUP BY bucket_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up old uploads (older than 30 days in temp folders)
CREATE OR REPLACE FUNCTION cleanup_old_temp_uploads()
RETURNS integer AS $$
DECLARE
  deleted_count integer;
BEGIN
  DELETE FROM storage.objects
  WHERE 
    bucket_id IN ('images', 'documents')
    AND name LIKE '%/temp/%'
    AND created_at < NOW() - INTERVAL '30 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- 4. OPTIMIZATION SETTINGS
-- ========================================

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_storage_objects_owner 
ON storage.objects(owner);

CREATE INDEX IF NOT EXISTS idx_storage_objects_bucket_owner 
ON storage.objects(bucket_id, owner);

CREATE INDEX IF NOT EXISTS idx_storage_objects_created_at 
ON storage.objects(created_at);

-- ========================================
-- 5. CDN CONFIGURATION NOTES
-- ========================================

/*
CDN Configuration for Production:

1. Supabase automatically provides CDN for public buckets
2. URLs follow pattern: https://[project-ref].supabase.co/storage/v1/object/public/[bucket]/[path]

3. Image transformations are available via URL parameters:
   - width: Target width in pixels
   - height: Target height in pixels
   - resize: 'cover' | 'contain' | 'fill'
   - quality: 1-100 (default 80)
   - format: 'origin' | 'webp' (auto-conversion)

4. Example transformation URL:
   https://[project-ref].supabase.co/storage/v1/object/public/images/photo.jpg?width=800&height=600&resize=cover&quality=85

5. Headers automatically set by Supabase:
   - Cache-Control: public, max-age=3600
   - Content-Type: [detected mime type]
   - Accept-Ranges: bytes (for partial content)

6. For better performance:
   - Use WebP format when possible (?format=webp)
   - Implement responsive images with multiple sizes
   - Use appropriate cache headers
   - Consider using a custom domain with Cloudflare

7. Storage limits (configurable):
   - avatars: 5MB per file
   - images: 10MB per file
   - documents: 50MB per file
   - assets: 2MB per file
*/

-- ========================================
-- 6. MONITORING QUERIES
-- ========================================

-- Query to check bucket configuration
SELECT 
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types,
  created_at,
  updated_at
FROM storage.buckets
ORDER BY name;

-- Query to check storage usage by bucket
SELECT 
  bucket_id,
  COUNT(*) as file_count,
  ROUND(SUM((metadata->>'size')::numeric) / 1048576, 2) as total_size_mb,
  ROUND(AVG((metadata->>'size')::numeric) / 1024, 2) as avg_size_kb
FROM storage.objects
GROUP BY bucket_id
ORDER BY total_size_mb DESC;

-- Query to find large files
SELECT 
  bucket_id,
  name,
  ROUND((metadata->>'size')::numeric / 1048576, 2) as size_mb,
  created_at,
  metadata->>'mimetype' as mime_type
FROM storage.objects
WHERE (metadata->>'size')::numeric > 5242880 -- Files larger than 5MB
ORDER BY (metadata->>'size')::numeric DESC
LIMIT 20;