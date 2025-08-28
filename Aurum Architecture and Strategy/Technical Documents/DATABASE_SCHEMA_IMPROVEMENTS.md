# Database Schema Improvements for Aurum Life MVP

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Proposed Changes for MVP Implementation

---

## 📋 Overview

This document outlines the database schema improvements required to transform the current Aurum Life database into an AI-enhanced system capable of supporting the HRM (Hierarchical Reasoning Model) and RAG (Retrieval-Augmented Generation) features.

## 🎯 Improvement Categories

### 1. AI Infrastructure Enhancements

#### 1.1 Enable pgvector Extension

```sql
-- Enable vector support for semantic search
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 1.2 Add Embedding Columns to Existing Tables

**journal_entries table improvements:**
```sql
ALTER TABLE public.journal_entries 
ADD COLUMN content_embedding vector(1536),
ADD COLUMN title_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN ai_insights_generated BOOLEAN DEFAULT FALSE,
ADD COLUMN sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1);

-- Create index for vector similarity search
CREATE INDEX idx_journal_content_embedding 
ON public.journal_entries 
USING hnsw (content_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**tasks table improvements:**
```sql
ALTER TABLE public.tasks 
-- AI and embedding fields
ADD COLUMN description_embedding vector(1536),
ADD COLUMN name_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE,
-- HRM scoring fields
ADD COLUMN hrm_priority_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_priority_score >= 0 AND hrm_priority_score <= 1),
ADD COLUMN hrm_alignment_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_alignment_score >= 0 AND hrm_alignment_score <= 1),
ADD COLUMN hrm_reasoning_summary TEXT,
ADD COLUMN hrm_last_analyzed TIMESTAMP WITH TIME ZONE,
ADD COLUMN ai_suggested_timeblock TEXT,
ADD COLUMN obstacle_risk TEXT CHECK (obstacle_risk IN ('low', 'medium', 'high')),
-- Behavior tracking fields
ADD COLUMN actual_duration INTEGER,
ADD COLUMN actual_start_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN actual_end_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN focus_time_minutes INTEGER DEFAULT 0,
ADD COLUMN interruption_count INTEGER DEFAULT 0,
ADD COLUMN context_switches INTEGER DEFAULT 0,
ADD COLUMN energy_level_at_start TEXT CHECK (energy_level_at_start IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
ADD COLUMN energy_level_at_completion TEXT CHECK (energy_level_at_completion IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
-- Denormalized hierarchy fields for performance
ADD COLUMN area_id UUID REFERENCES public.areas(id),
ADD COLUMN pillar_id UUID REFERENCES public.pillars(id);

-- Create indexes
CREATE INDEX idx_task_description_embedding 
ON public.tasks 
USING hnsw (description_embedding vector_cosine_ops)
WHERE description IS NOT NULL AND description != '';

CREATE INDEX idx_tasks_hierarchy ON public.tasks(user_id, pillar_id, area_id, project_id);
CREATE INDEX idx_tasks_hrm_priority ON public.tasks(user_id, completed, hrm_priority_score DESC) WHERE completed = false;
```

**projects table improvements:**
```sql
ALTER TABLE public.projects 
-- AI and embedding fields
ADD COLUMN combined_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE,
-- HRM analysis fields
ADD COLUMN hrm_coherence_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_coherence_score >= 0 AND hrm_coherence_score <= 1),
ADD COLUMN hrm_risk_assessment TEXT,
ADD COLUMN hrm_suggested_adjustments JSONB,
ADD COLUMN hrm_health_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_health_score >= 0 AND hrm_health_score <= 1),
-- Time tracking
ADD COLUMN estimated_hours INTEGER,
ADD COLUMN actual_hours_spent DECIMAL(6,2) DEFAULT 0,
ADD COLUMN last_activity_date TIMESTAMP WITH TIME ZONE,
-- Denormalized field
ADD COLUMN pillar_id UUID REFERENCES public.pillars(id);

CREATE INDEX idx_project_embedding 
ON public.projects 
USING hnsw (combined_embedding vector_cosine_ops);

CREATE INDEX idx_projects_hierarchy ON public.projects(user_id, pillar_id, area_id);
```

### 2. New Tables for AI Functionality

#### 2.1 Insights Table
```sql
CREATE TABLE public.insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('pillar', 'area', 'project', 'task', 'global')),
    entity_id UUID,
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'priority_reasoning', 'alignment_analysis', 'pattern_recognition',
        'recommendation', 'goal_coherence', 'time_allocation',
        'progress_prediction', 'obstacle_identification', 'optimization_suggestion'
    )),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    detailed_reasoning JSONB NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0 AND impact_score <= 1),
    reasoning_path JSONB NOT NULL DEFAULT '[]'::JSONB,
    supporting_data JSONB DEFAULT '{}',
    llm_session_id TEXT,
    llm_context JSONB,
    llm_model_used TEXT DEFAULT 'gemini-1.5-flash',
    user_feedback TEXT CHECK (user_feedback IN ('accepted', 'rejected', 'modified', 'ignored')),
    feedback_details JSONB,
    application_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    is_pinned BOOLEAN DEFAULT false,
    expires_at TIMESTAMP WITH TIME ZONE,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    version INTEGER DEFAULT 1,
    previous_version_id UUID REFERENCES public.insights(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_insights_user_entity ON public.insights(user_id, entity_type, entity_id);
CREATE INDEX idx_insights_active ON public.insights(user_id, is_active, created_at DESC);
CREATE INDEX idx_insights_type ON public.insights(user_id, insight_type, created_at DESC);
CREATE INDEX idx_insights_expiry ON public.insights(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_insights_feedback ON public.insights(user_id, user_feedback) WHERE user_feedback IS NOT NULL;
```

#### 2.2 Daily Reflections Table
```sql
CREATE TABLE public.daily_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    reflection_date DATE NOT NULL DEFAULT CURRENT_DATE,
    reflection_text TEXT NOT NULL,
    completion_score INTEGER CHECK (completion_score >= 1 AND completion_score <= 10),
    mood VARCHAR(50) CHECK (mood IN (
        'excited', 'happy', 'content', 'neutral', 'frustrated', 'sad', 'anxious', 'overwhelmed'
    )),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    biggest_accomplishment TEXT,
    challenges_faced TEXT,
    tomorrow_focus TEXT,
    gratitude_notes TEXT,
    lessons_learned TEXT,
    -- Metrics
    tasks_completed_count INTEGER DEFAULT 0,
    focus_time_minutes INTEGER DEFAULT 0,
    productivity_score INTEGER CHECK (productivity_score >= 1 AND productivity_score <= 10),
    alignment_score DECIMAL(3,2) CHECK (alignment_score >= 0 AND alignment_score <= 1),
    -- Embeddings for AI
    reflection_embedding vector(1536),
    accomplishment_embedding vector(1536),
    challenges_embedding vector(1536),
    embedding_model TEXT DEFAULT 'text-embedding-3-small',
    embedding_updated_at TIMESTAMP WITH TIME ZONE,
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_date UNIQUE (user_id, reflection_date)
);

CREATE INDEX idx_daily_reflections_user_date ON public.daily_reflections(user_id, reflection_date DESC);
CREATE INDEX idx_daily_reflections_mood ON public.daily_reflections(user_id, mood, reflection_date DESC);
CREATE INDEX idx_reflection_embedding 
ON public.daily_reflections 
USING hnsw (reflection_embedding vector_cosine_ops);
```

#### 2.3 AI Conversation Memory
```sql
CREATE TABLE public.ai_conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    session_id UUID NOT NULL DEFAULT gen_random_uuid(),
    message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
    message_content TEXT NOT NULL,
    message_embedding vector(1536),
    context_entities JSONB DEFAULT '{}', -- {tasks: [], projects: [], areas: [], pillars: []}
    tokens_used INTEGER DEFAULT 0,
    model_used TEXT,
    response_time_ms INTEGER,
    was_helpful BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversation_embedding 
ON public.ai_conversation_memory 
USING hnsw (message_embedding vector_cosine_ops);

CREATE INDEX idx_conversation_user_session 
ON public.ai_conversation_memory(user_id, session_id, created_at);
```

### 3. Behavioral Tracking Improvements

#### 3.1 Time Tracking Table
```sql
CREATE TABLE public.time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('task', 'project', 'area', 'pillar')),
    entity_id UUID NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER GENERATED ALWAYS AS (
        CASE 
            WHEN end_time IS NOT NULL 
            THEN EXTRACT(EPOCH FROM (end_time - start_time)) / 60
            ELSE NULL
        END
    ) STORED,
    is_active BOOLEAN DEFAULT true,
    activity_type TEXT CHECK (activity_type IN ('focused', 'collaborative', 'meeting', 'break', 'planning')),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    productivity_rating INTEGER CHECK (productivity_rating >= 1 AND productivity_rating <= 10),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_time_entries_user_date ON public.time_entries(user_id, start_time DESC);
CREATE INDEX idx_time_entries_active ON public.time_entries(user_id, is_active) WHERE is_active = true;
CREATE INDEX idx_time_entries_entity ON public.time_entries(entity_type, entity_id);
```

#### 3.2 User Behavior Patterns
```sql
CREATE TABLE public.user_behavior_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    pattern_type TEXT NOT NULL CHECK (pattern_type IN (
        'peak_productivity_hours', 'task_completion_time', 'procrastination_triggers',
        'energy_patterns', 'focus_duration', 'break_frequency'
    )),
    pattern_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    sample_size INTEGER NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_behavior_patterns_user_type ON public.user_behavior_patterns(user_id, pattern_type, is_active);
```

### 4. Enhanced User Tables

#### 4.1 User Profiles Enhancements
```sql
ALTER TABLE public.user_profiles 
ADD COLUMN user_tier TEXT DEFAULT 'standard' CHECK (user_tier IN ('standard', 'premium', 'enterprise')),
ADD COLUMN longest_streak INTEGER DEFAULT 0,
ADD COLUMN total_focus_hours DECIMAL(8,2) DEFAULT 0,
ADD COLUMN average_daily_completion_rate DECIMAL(3,2) DEFAULT 0,
ADD COLUMN preferred_working_hours JSONB DEFAULT '{"start": "09:00", "end": "17:00"}',
ADD COLUMN timezone TEXT DEFAULT 'UTC',
ADD COLUMN ai_onboarding_completed BOOLEAN DEFAULT false,
ADD COLUMN ai_features_enabled BOOLEAN DEFAULT true,
ADD COLUMN last_activity_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX idx_user_profiles_activity ON public.user_profiles(last_activity_at DESC);
```

#### 4.2 Enhanced User Stats
```sql
ALTER TABLE public.user_stats 
ADD COLUMN total_ai_interactions INTEGER DEFAULT 0,
ADD COLUMN insights_generated INTEGER DEFAULT 0,
ADD COLUMN insights_applied INTEGER DEFAULT 0,
ADD COLUMN ai_satisfaction_score DECIMAL(3,2) CHECK (ai_satisfaction_score >= 0 AND ai_satisfaction_score <= 5),
ADD COLUMN total_focus_time_minutes INTEGER DEFAULT 0,
ADD COLUMN average_task_completion_time INTEGER,
ADD COLUMN task_estimation_accuracy DECIMAL(3,2),
ADD COLUMN weekly_active_days INTEGER DEFAULT 0,
ADD COLUMN current_momentum_score DECIMAL(3,2) DEFAULT 0.5;
```

### 5. Data Quality Improvements

#### 5.1 Standardize Soft Delete
```sql
-- Add consistent archival columns where missing
ALTER TABLE public.journal_entries 
DROP COLUMN IF EXISTS deleted,
DROP COLUMN IF EXISTS deleted_at,
ADD COLUMN archived BOOLEAN DEFAULT FALSE,
ADD COLUMN archived_at TIMESTAMP WITH TIME ZONE;

-- Update all tables to use consistent pattern
UPDATE public.journal_entries SET archived = true, archived_at = NOW() WHERE deleted = true;
```

#### 5.2 Add Missing Constraints
```sql
-- Add CHECK constraints for all enum fields
ALTER TABLE public.tasks 
ADD CONSTRAINT chk_task_status CHECK (status IN ('todo', 'in_progress', 'review', 'completed', 'cancelled')),
ADD CONSTRAINT chk_task_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent'));

ALTER TABLE public.projects 
ADD CONSTRAINT chk_project_status CHECK (status IN ('not_started', 'in_progress', 'completed', 'on_hold', 'cancelled')),
ADD CONSTRAINT chk_project_priority CHECK (priority IN ('low', 'medium', 'high'));

-- Add range constraints
ALTER TABLE public.areas 
ADD CONSTRAINT chk_area_importance CHECK (importance >= 1 AND importance <= 5);

ALTER TABLE public.projects 
ADD CONSTRAINT chk_project_importance CHECK (importance >= 1 AND importance <= 5),
ADD CONSTRAINT chk_completion_percentage CHECK (completion_percentage >= 0 AND completion_percentage <= 100);
```

### 6. Performance Optimization

#### 6.1 Materialized Views for Hierarchy
```sql
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

CREATE INDEX idx_hierarchy_view_user ON hierarchy_view(user_id);
CREATE INDEX idx_hierarchy_view_pillar ON hierarchy_view(user_id, pillar_id);
```

#### 6.2 Summary Statistics Cache
```sql
CREATE TABLE public.user_statistics_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    stat_type TEXT NOT NULL CHECK (stat_type IN ('daily', 'weekly', 'monthly')),
    pillar_stats JSONB DEFAULT '{}',
    area_stats JSONB DEFAULT '{}',
    project_stats JSONB DEFAULT '{}',
    task_stats JSONB DEFAULT '{}',
    time_allocation JSONB DEFAULT '{}',
    productivity_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_stat_date UNIQUE (user_id, stat_date, stat_type)
);

CREATE INDEX idx_stats_cache_user_date ON public.user_statistics_cache(user_id, stat_date DESC, stat_type);
```

### 7. Audit and Compliance

#### 7.1 Audit Log
```sql
CREATE TABLE public.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('create', 'update', 'delete', 'archive', 'restore')),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON public.audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_log_entity ON public.audit_log(entity_type, entity_id, created_at DESC);
```

## 🚀 Implementation Order

### Phase 1: Foundation (Week 1)
1. Enable pgvector extension
2. Create core AI tables (insights, ai_conversation_memory)
3. Add embedding columns to content tables
4. Create daily_reflections table

### Phase 2: Behavior Tracking (Week 1-2)
1. Add behavior tracking fields to tasks
2. Create time_entries table
3. Create user_behavior_patterns table
4. Enhance user_profiles and user_stats

### Phase 3: Data Quality (Week 2)
1. Standardize soft delete across all tables
2. Add missing constraints
3. Fix denormalization issues
4. Create audit_log table

### Phase 4: Performance (Week 2-3)
1. Create vector indexes
2. Build materialized views
3. Implement statistics cache
4. Add missing indexes

### Phase 5: Migration & Testing (Week 3-4)
1. Migrate existing data
2. Generate initial embeddings
3. Test performance
4. Validate data integrity

## 📊 Monitoring & Maintenance

### Key Metrics to Track
1. **Embedding Generation**: Time to generate, backlog size
2. **Vector Search Performance**: Query time, relevance scores
3. **Storage Growth**: Table sizes, index sizes
4. **Cache Hit Rates**: Statistics cache effectiveness
5. **User Engagement**: Daily reflections completion, AI interaction frequency

### Maintenance Tasks
1. **Daily**: Refresh materialized views, update statistics cache
2. **Weekly**: Analyze query performance, optimize slow queries
3. **Monthly**: Review storage usage, archive old conversations
4. **Quarterly**: Re-evaluate embedding model, retrain patterns

## 🎯 Success Criteria

1. **Performance**
   - Hierarchy queries < 100ms
   - Vector similarity search < 500ms
   - Statistics generation < 1 second

2. **Data Quality**
   - 100% constraint compliance
   - < 0.1% data inconsistency
   - 95%+ embedding coverage

3. **User Experience**
   - AI response time < 2 seconds
   - 90%+ relevance for RAG results
   - 80%+ daily reflection completion

This comprehensive schema improvement plan transforms the Aurum Life database into an AI-ready platform while maintaining data integrity and performance.