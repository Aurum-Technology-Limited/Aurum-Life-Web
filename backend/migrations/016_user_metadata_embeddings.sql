-- Migration 016: User Metadata Embeddings for RAG System
-- Implements vector-based semantic search across user's PAPT hierarchy
-- Reference: aurum-life-impl-plan.md

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table for RAG system
CREATE TABLE IF NOT EXISTS public.user_metadata_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  domain_tag TEXT NOT NULL, -- e.g., 'pillar', 'area', 'project', 'task'
  entity_id UUID,         -- references specific entity
  text_snippet TEXT NOT NULL,
  embedding VECTOR(1536) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_metadata_embeddings_hnsw
ON public.user_metadata_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Standard index for filtering by user and domain
CREATE INDEX IF NOT EXISTS idx_metadata_embeddings_user_domain 
ON public.user_metadata_embeddings (user_id, domain_tag);

-- Index for entity lookups
CREATE INDEX IF NOT EXISTS idx_metadata_embeddings_entity 
ON public.user_metadata_embeddings (entity_id, domain_tag);

-- Enable Row Level Security
ALTER TABLE public.user_metadata_embeddings ENABLE ROW LEVEL SECURITY;

-- RLS policy for user data isolation
CREATE POLICY "Users can access their embeddings"
ON public.user_metadata_embeddings FOR ALL
USING (auth.uid() = user_id);

-- Grant permissions
GRANT ALL ON public.user_metadata_embeddings TO authenticated;
GRANT ALL ON public.user_metadata_embeddings TO service_role;

-- Add comments for documentation
COMMENT ON TABLE public.user_metadata_embeddings IS 'Stores semantic embeddings of user PAPT hierarchy for RAG-based AI interactions';
COMMENT ON COLUMN public.user_metadata_embeddings.domain_tag IS 'PAPT layer: pillar, area, project, task, or journal_entry';
COMMENT ON COLUMN public.user_metadata_embeddings.entity_id IS 'References the specific entity (pillar_id, area_id, etc.)';
COMMENT ON COLUMN public.user_metadata_embeddings.text_snippet IS 'The text that was embedded (name + description)';
COMMENT ON COLUMN public.user_metadata_embeddings.embedding IS 'OpenAI text-embedding-ada-002 vector (1536 dimensions)';