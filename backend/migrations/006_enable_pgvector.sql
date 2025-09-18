-- HRM Phase 3: Enable pgvector for RAG Implementation
-- Reference: RAG_IMPLEMENTATION_GUIDE.md

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding columns to existing tables for RAG
ALTER TABLE public.journal_entries 
ADD COLUMN IF NOT EXISTS content_embedding vector(1536),
ADD COLUMN IF NOT EXISTS title_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.daily_reflections
ADD COLUMN IF NOT EXISTS reflection_embedding vector(1536),
ADD COLUMN IF NOT EXISTS accomplishment_embedding vector(1536),
ADD COLUMN IF NOT EXISTS challenges_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.tasks
ADD COLUMN IF NOT EXISTS description_embedding vector(1536),
ADD COLUMN IF NOT EXISTS name_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE public.projects
ADD COLUMN IF NOT EXISTS combined_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

-- Create HNSW indexes for fast similarity search
CREATE INDEX IF NOT EXISTS idx_journal_content_embedding 
ON public.journal_entries 
USING hnsw (content_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_reflection_embedding 
ON public.daily_reflections 
USING hnsw (reflection_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_task_description_embedding 
ON public.tasks 
USING hnsw (description_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
WHERE description IS NOT NULL AND description != '';

CREATE INDEX IF NOT EXISTS idx_project_embedding 
ON public.projects 
USING hnsw (combined_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);