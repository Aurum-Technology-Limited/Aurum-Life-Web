# Database Migration Plan for Aurum Life MVP

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Estimated Duration:** 3-4 weeks  
**Risk Level:** Medium

---

## 📋 Migration Overview

This document provides a detailed, step-by-step plan for migrating the current Aurum Life database to support AI-enhanced features. The migration will be performed in phases to minimize risk and ensure data integrity.

## 🚦 Pre-Migration Checklist

### Technical Prerequisites
- [ ] PostgreSQL version 15+ with pgvector support
- [ ] Supabase project with vector extension available
- [ ] Backup strategy implemented and tested
- [ ] Development/staging environment ready
- [ ] Monitoring tools configured
- [ ] Migration scripts reviewed and tested

### Team Readiness
- [ ] Database administrator assigned
- [ ] Backend developers briefed on changes
- [ ] Rollback procedures documented
- [ ] Communication plan for users established
- [ ] Support team prepared for potential issues

## 📊 Migration Phases

### Phase 1: Foundation Setup (Day 1-3)

#### 1.1 Create Full Backup
```bash
# Export complete database backup
pg_dump -h your-db-host -U postgres -d your-db-name > aurum_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup integrity
pg_restore --list aurum_backup_*.sql
```

#### 1.2 Enable pgvector Extension
```sql
-- Migration: 001_enable_pgvector.sql
BEGIN;

-- Check if extension exists
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT vector_version();

COMMIT;
```

#### 1.3 Create Core AI Tables
```sql
-- Migration: 002_create_ai_core_tables.sql
BEGIN;

-- Create insights table
CREATE TABLE public.insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    -- ... (full schema from improvements document)
);

-- Create indexes
CREATE INDEX idx_insights_user_entity ON public.insights(user_id, entity_type, entity_id);
-- ... (other indexes)

-- Enable RLS
ALTER TABLE public.insights ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can manage their own insights" 
ON public.insights FOR ALL 
USING (auth.uid() = user_id);

COMMIT;
```

### Phase 2: Enhance Existing Tables (Day 4-7)

#### 2.1 Add Embedding Columns
```sql
-- Migration: 003_add_embedding_columns.sql
BEGIN;

-- Add to journal_entries
ALTER TABLE public.journal_entries 
ADD COLUMN IF NOT EXISTS content_embedding vector(1536),
ADD COLUMN IF NOT EXISTS title_embedding vector(1536),
ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP WITH TIME ZONE;

-- Add to tasks
ALTER TABLE public.tasks 
ADD COLUMN IF NOT EXISTS description_embedding vector(1536),
ADD COLUMN IF NOT EXISTS name_embedding vector(1536),
-- ... (other columns)

-- Verification
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
AND column_name LIKE '%embedding%';

COMMIT;
```

#### 2.2 Add Behavioral Tracking Fields
```sql
-- Migration: 004_add_behavioral_tracking.sql
BEGIN;

-- Enhance tasks table
ALTER TABLE public.tasks 
ADD COLUMN IF NOT EXISTS actual_duration INTEGER,
ADD COLUMN IF NOT EXISTS actual_start_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS actual_end_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS focus_time_minutes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS interruption_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS context_switches INTEGER DEFAULT 0;

-- Add constraints
ALTER TABLE public.tasks 
ADD CONSTRAINT chk_actual_duration CHECK (actual_duration >= 0),
ADD CONSTRAINT chk_focus_time CHECK (focus_time_minutes >= 0),
ADD CONSTRAINT chk_interruptions CHECK (interruption_count >= 0);

COMMIT;
```

### Phase 3: Data Quality Improvements (Day 8-10)

#### 3.1 Standardize Soft Delete
```sql
-- Migration: 005_standardize_soft_delete.sql
BEGIN;

-- Backup affected data
CREATE TEMP TABLE journal_entries_deleted_backup AS
SELECT id, deleted, deleted_at 
FROM public.journal_entries 
WHERE deleted = true;

-- Update journal_entries
ALTER TABLE public.journal_entries 
ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;

-- Migrate data
UPDATE public.journal_entries 
SET archived = true, 
    archived_at = COALESCE(deleted_at, NOW())
WHERE deleted = true;

-- Remove old columns (after verification)
ALTER TABLE public.journal_entries 
DROP COLUMN IF EXISTS deleted,
DROP COLUMN IF EXISTS deleted_at;

-- Add index
CREATE INDEX idx_journal_entries_archived 
ON public.journal_entries(user_id, archived) 
WHERE archived = false;

COMMIT;
```

#### 3.2 Add Missing Constraints
```sql
-- Migration: 006_add_constraints.sql
BEGIN;

-- Tasks constraints
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_task_status'
    ) THEN
        ALTER TABLE public.tasks 
        ADD CONSTRAINT chk_task_status 
        CHECK (status IN ('todo', 'in_progress', 'review', 'completed', 'cancelled'));
    END IF;
END $$;

-- Projects constraints
ALTER TABLE public.projects 
DROP CONSTRAINT IF EXISTS chk_project_status,
ADD CONSTRAINT chk_project_status 
CHECK (status IN ('not_started', 'in_progress', 'completed', 'on_hold', 'cancelled'));

-- Verify constraints
SELECT 
    conname,
    conrelid::regclass,
    pg_get_constraintdef(oid)
FROM pg_constraint
WHERE contype = 'c'
AND connamespace = 'public'::regnamespace;

COMMIT;
```

### Phase 4: Create Vector Indexes (Day 11-12)

#### 4.1 Create HNSW Indexes
```sql
-- Migration: 007_create_vector_indexes.sql
BEGIN;

-- Journal entries index (this may take time for large tables)
CREATE INDEX CONCURRENTLY idx_journal_content_embedding 
ON public.journal_entries 
USING hnsw (content_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64)
WHERE content_embedding IS NOT NULL;

-- Tasks index
CREATE INDEX CONCURRENTLY idx_task_description_embedding 
ON public.tasks 
USING hnsw (description_embedding vector_cosine_ops)
WHERE description IS NOT NULL 
AND description != ''
AND description_embedding IS NOT NULL;

-- Monitor progress
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%';

COMMIT;
```

### Phase 5: Performance Optimizations (Day 13-15)

#### 5.1 Create Materialized Views
```sql
-- Migration: 008_create_materialized_views.sql
BEGIN;

-- Hierarchy view
CREATE MATERIALIZED VIEW hierarchy_view AS
SELECT 
    t.id as task_id,
    t.name as task_name,
    t.user_id,
    p.id as project_id,
    p.name as project_name,
    a.id as area_id,
    a.name as area_name,
    pi.id as pillar_id,
    pi.name as pillar_name,
    t.status as task_status,
    t.priority as task_priority,
    t.due_date,
    t.hrm_priority_score,
    t.hrm_alignment_score
FROM tasks t
JOIN projects p ON t.project_id = p.id
JOIN areas a ON p.area_id = a.id
LEFT JOIN pillars pi ON a.pillar_id = pi.id;

-- Create indexes on materialized view
CREATE INDEX idx_hierarchy_view_user ON hierarchy_view(user_id);
CREATE INDEX idx_hierarchy_view_pillar ON hierarchy_view(user_id, pillar_id);

-- Create refresh function
CREATE OR REPLACE FUNCTION refresh_hierarchy_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY hierarchy_view;
END;
$$ LANGUAGE plpgsql;

COMMIT;
```

#### 5.2 Create Statistics Cache
```sql
-- Migration: 009_create_statistics_cache.sql
BEGIN;

CREATE TABLE public.user_statistics_cache (
    -- ... (schema from improvements document)
);

-- Create update trigger
CREATE OR REPLACE FUNCTION update_user_statistics_cache()
RETURNS TRIGGER AS $$
BEGIN
    -- Mark cache as stale
    UPDATE user_statistics_cache 
    SET updated_at = NOW() - INTERVAL '1 day'
    WHERE user_id = COALESCE(NEW.user_id, OLD.user_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Attach triggers to relevant tables
CREATE TRIGGER trigger_update_stats_on_task_change
AFTER INSERT OR UPDATE OR DELETE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_user_statistics_cache();

COMMIT;
```

### Phase 6: Data Migration (Day 16-18)

#### 6.1 Migrate Historical Data
```sql
-- Migration: 010_migrate_historical_data.sql
BEGIN;

-- Populate denormalized fields in tasks
UPDATE tasks t
SET area_id = p.area_id,
    pillar_id = a.pillar_id
FROM projects p
JOIN areas a ON p.area_id = a.id
WHERE t.project_id = p.id
AND t.area_id IS NULL;

-- Initialize HRM scores with defaults
UPDATE tasks 
SET hrm_priority_score = 0.5,
    hrm_alignment_score = 0.5
WHERE hrm_priority_score IS NULL;

-- Create initial daily reflections from journal entries
INSERT INTO daily_reflections (
    user_id,
    reflection_date,
    reflection_text,
    mood,
    created_at
)
SELECT DISTINCT ON (user_id, created_at::date)
    user_id,
    created_at::date,
    content,
    mood,
    created_at
FROM journal_entries
WHERE template_type = 'daily_reflection'
ORDER BY user_id, created_at::date, created_at DESC
ON CONFLICT (user_id, reflection_date) DO NOTHING;

COMMIT;
```

### Phase 7: Create Search Functions (Day 19-20)

#### 7.1 RAG Search Functions
```sql
-- Migration: 011_create_search_functions.sql
BEGIN;

-- Multi-table semantic search
CREATE OR REPLACE FUNCTION rag_search(
    query_embedding vector(1536),
    user_id_filter UUID,
    match_count INT DEFAULT 10,
    date_range_days INT DEFAULT NULL
)
RETURNS TABLE(
    entity_type TEXT,
    entity_id UUID,
    title TEXT,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- ... (implementation from improvements document)
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION rag_search TO authenticated;

COMMIT;
```

### Phase 8: Post-Migration Tasks (Day 21)

#### 8.1 Generate Initial Embeddings
```python
# Python script to generate embeddings
import asyncio
from supabase import create_client
import openai

async def generate_initial_embeddings():
    # Process in batches of 100
    batch_size = 100
    
    # Get all journal entries without embeddings
    entries = await supabase.from_('journal_entries')\
        .select('id, title, content')\
        .is_('content_embedding', None)\
        .limit(batch_size)\
        .execute()
    
    for entry in entries.data:
        # Generate embedding
        embedding = await generate_embedding(f"{entry['title']}\n{entry['content']}")
        
        # Update database
        await supabase.from_('journal_entries')\
            .update({
                'content_embedding': embedding,
                'embedding_updated_at': 'now()'
            })\
            .eq('id', entry['id'])\
            .execute()
```

#### 8.2 Verify Migration Success
```sql
-- Verification queries
-- Check table modifications
SELECT 
    table_name,
    COUNT(*) as new_columns
FROM information_schema.columns
WHERE table_schema = 'public'
AND column_name IN ('content_embedding', 'hrm_priority_score', 'archived')
GROUP BY table_name;

-- Check indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND indexname LIKE '%embedding%';

-- Check constraints
SELECT 
    conname,
    conrelid::regclass
FROM pg_constraint
WHERE contype = 'c'
AND connamespace = 'public'::regnamespace
ORDER BY conrelid::regclass::text;
```

## 🔄 Rollback Procedures

### Rollback Script Template
```sql
-- Rollback for each migration
-- 001_rollback_pgvector.sql
DROP EXTENSION IF EXISTS vector CASCADE;

-- 002_rollback_ai_tables.sql
DROP TABLE IF EXISTS public.insights CASCADE;
DROP TABLE IF EXISTS public.ai_conversation_memory CASCADE;
-- etc.

-- Restore from backup if needed
psql -h your-db-host -U postgres -d your-db-name < aurum_backup_timestamp.sql
```

## 📊 Post-Migration Monitoring

### Key Metrics to Monitor
1. **Query Performance**
   ```sql
   SELECT 
       query,
       calls,
       mean_exec_time,
       max_exec_time
   FROM pg_stat_statements
   WHERE query LIKE '%embedding%'
   ORDER BY mean_exec_time DESC;
   ```

2. **Table Sizes**
   ```sql
   SELECT 
       schemaname,
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

3. **Index Usage**
   ```sql
   SELECT 
       schemaname,
       tablename,
       indexname,
       idx_scan,
       idx_tup_read,
       idx_tup_fetch
   FROM pg_stat_user_indexes
   ORDER BY idx_scan DESC;
   ```

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

1. **pgvector extension fails to install**
   - Verify PostgreSQL version (15+)
   - Check Supabase plan supports extensions
   - Contact Supabase support if needed

2. **Vector index creation times out**
   - Use CONCURRENTLY option
   - Process in smaller batches
   - Increase maintenance_work_mem temporarily

3. **Constraint violations during migration**
   - Identify violating records
   - Clean data before adding constraints
   - Consider temporary relaxation of constraints

4. **Performance degradation**
   - Analyze query plans
   - Update table statistics
   - Consider adjusting index parameters

## ✅ Sign-off Checklist

- [ ] All migrations completed successfully
- [ ] Data integrity verified
- [ ] Performance benchmarks met
- [ ] Rollback procedures tested
- [ ] Documentation updated
- [ ] Team trained on new schema
- [ ] Monitoring alerts configured
- [ ] Backup retention verified

This migration plan ensures a smooth transition to the AI-enhanced database schema while minimizing risk and downtime.