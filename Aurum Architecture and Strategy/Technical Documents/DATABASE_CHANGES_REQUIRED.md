# Database Changes Required for AI Architecture

## Current State Analysis

Based on the existing Supabase tables and the planned AI architecture with pgvector RAG implementation, here are the required database changes:

## 📊 Tables to Add

### 1. **public.insights** (NEW)
**Purpose**: Store AI-generated insights and reasoning from the HRM system
```sql
CREATE TABLE public.insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('pillar', 'area', 'project', 'task', 'global')),
    entity_id UUID,
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'priority_reasoning', 'alignment_analysis', 'pattern_recognition',
        'recommendation', 'goal_coherence', 'time_allocation',
        'progress_prediction', 'obstacle_identification'
    )),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    detailed_reasoning JSONB NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0 AND impact_score <= 1),
    reasoning_path JSONB NOT NULL DEFAULT '[]'::JSONB,
    llm_session_id TEXT,
    llm_context JSONB,
    llm_model_used TEXT DEFAULT 'gemini-2.0-flash',
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
```

### 2. **public.hrm_rules** (NEW)
**Purpose**: Define rules for the Hierarchical Reasoning Model
```sql
CREATE TABLE public.hrm_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code TEXT UNIQUE NOT NULL,
    rule_name TEXT NOT NULL,
    description TEXT NOT NULL,
    hierarchy_level TEXT NOT NULL CHECK (hierarchy_level IN ('pillar', 'area', 'project', 'task', 'cross_level')),
    applies_to_entity_types TEXT[] NOT NULL,
    rule_type TEXT NOT NULL CHECK (rule_type IN (
        'scoring', 'filtering', 'relationship',
        'temporal', 'constraint', 'pattern_matching'
    )),
    rule_config JSONB NOT NULL,
    base_weight DECIMAL(3,2) DEFAULT 0.5 CHECK (base_weight >= 0 AND base_weight <= 1),
    user_adjustable BOOLEAN DEFAULT false,
    requires_llm BOOLEAN DEFAULT false,
    llm_prompt_template TEXT,
    is_active BOOLEAN DEFAULT true,
    is_system_rule BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. **public.hrm_user_preferences** (NEW)
**Purpose**: Store user-specific HRM preferences and configurations
```sql
CREATE TABLE public.hrm_user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    rule_weight_overrides JSONB DEFAULT '{}'::JSONB,
    explanation_detail_level TEXT DEFAULT 'balanced' CHECK (explanation_detail_level IN ('minimal', 'balanced', 'detailed')),
    show_confidence_scores BOOLEAN DEFAULT true,
    show_reasoning_path BOOLEAN DEFAULT true,
    ai_personality TEXT DEFAULT 'coach' CHECK (ai_personality IN ('coach', 'assistant', 'strategist', 'motivator')),
    ai_communication_style TEXT DEFAULT 'encouraging' CHECK (ai_communication_style IN ('direct', 'encouraging', 'analytical', 'socratic')),
    primary_optimization TEXT DEFAULT 'balance' CHECK (primary_optimization IN (
        'balance', 'focus', 'exploration', 'efficiency', 'wellbeing'
    )),
    preferred_work_hours JSONB DEFAULT '{"start": "09:00", "end": "17:00"}'::JSONB,
    energy_pattern TEXT DEFAULT 'steady' CHECK (energy_pattern IN ('morning_peak', 'afternoon_peak', 'evening_peak', 'steady')),
    enable_ai_learning BOOLEAN DEFAULT true,
    share_anonymous_insights BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. **public.hrm_feedback_log** (NEW)
**Purpose**: Track user feedback on AI suggestions for improvement
```sql
CREATE TABLE public.hrm_feedback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_id UUID REFERENCES public.insights(id) ON DELETE SET NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN ('positive', 'negative', 'correction', 'suggestion')),
    feedback_text TEXT,
    context JSONB,
    applied_to_future BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 5. **public.ai_conversation_memory** (NEW)
**Purpose**: Store conversation history with embeddings for RAG
```sql
CREATE TABLE public.ai_conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
    message_content TEXT NOT NULL,
    message_embedding vector(1536),
    context_window JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    model_used TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 6. **public.ai_model_usage** (NEW)
**Purpose**: Track AI model usage for cost monitoring and optimization
```sql
CREATE TABLE public.ai_model_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    model_type TEXT NOT NULL CHECK (model_type IN ('strategic', 'execution', 'embedding', 'stt', 'tts')),
    model_name TEXT NOT NULL,
    request_type TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    response_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT false,
    error_code TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 7. **public.daily_reflections** (NEW)
**Purpose**: Store daily reflection entries
```sql
CREATE TABLE public.daily_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    reflection_date DATE NOT NULL DEFAULT CURRENT_DATE,
    reflection_text TEXT NOT NULL,
    completion_score INTEGER CHECK (completion_score >= 1 AND completion_score <= 10),
    mood VARCHAR(50),
    biggest_accomplishment TEXT,
    challenges_faced TEXT,
    tomorrow_focus TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_date UNIQUE (user_id, reflection_date)
);
```

### 8. **public.sleep_reflections** (NEW)
**Purpose**: Track sleep quality and patterns
```sql
CREATE TABLE public.sleep_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    sleep_date DATE NOT NULL,
    sleep_quality INTEGER CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
    sleep_duration_hours DECIMAL(3,1),
    factors_affecting_sleep TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_sleep_date UNIQUE (user_id, sleep_date)
);
```

### 9. **public.feedback** (NEW)
**Purpose**: General user feedback table
```sql
CREATE TABLE public.feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) CHECK (type IN ('bug', 'feature_request', 'general', 'complaint', 'praise')),
    category VARCHAR(100),
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'in_review', 'in_progress', 'resolved', 'closed')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 📝 Tables to Modify

### 1. **public.journal_entries** (MODIFY)
**Changes**: Add vector embeddings for RAG
```sql
ALTER TABLE public.journal_entries 
ADD COLUMN content_embedding vector(1536),
ADD COLUMN title_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE;
```

### 2. **public.tasks** (MODIFY)
**Changes**: Add HRM-specific fields and embeddings
```sql
ALTER TABLE public.tasks 
-- HRM fields
ADD COLUMN hrm_priority_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_priority_score >= 0 AND hrm_priority_score <= 1),
ADD COLUMN hrm_alignment_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_alignment_score >= 0 AND hrm_alignment_score <= 1),
ADD COLUMN hrm_reasoning_summary TEXT,
ADD COLUMN hrm_last_analyzed TIMESTAMP WITH TIME ZONE,
ADD COLUMN ai_suggested_timeblock TEXT,
ADD COLUMN obstacle_risk TEXT CHECK (obstacle_risk IN ('low', 'medium', 'high')),
-- Embedding fields
ADD COLUMN description_embedding vector(1536),
ADD COLUMN name_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE;
```

### 3. **public.projects** (MODIFY)
**Changes**: Add HRM fields and embeddings
```sql
ALTER TABLE public.projects 
-- HRM fields
ADD COLUMN hrm_coherence_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_coherence_score >= 0 AND hrm_coherence_score <= 1),
ADD COLUMN hrm_risk_assessment TEXT,
ADD COLUMN hrm_suggested_adjustments JSONB,
-- Embedding fields
ADD COLUMN combined_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE;
```

### 4. **public.areas** (MODIFY)
**Changes**: Add HRM analysis fields
```sql
ALTER TABLE public.areas 
ADD COLUMN hrm_balance_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_balance_score >= 0 AND hrm_balance_score <= 1),
ADD COLUMN hrm_last_rebalanced TIMESTAMP WITH TIME ZONE;
```

### 5. **public.pillars** (MODIFY)
**Changes**: Add time allocation tracking
```sql
ALTER TABLE public.pillars 
ADD COLUMN time_allocation_percentage DECIMAL(5,2) CHECK (time_allocation_percentage >= 0 AND time_allocation_percentage <= 100),
ADD COLUMN hrm_health_score DECIMAL(3,2) DEFAULT 0.5 CHECK (hrm_health_score >= 0 AND hrm_health_score <= 1);
```

### 6. **public.user_profiles** (MODIFY)
**Changes**: Add user tier and daily streak
```sql
ALTER TABLE public.user_profiles 
ADD COLUMN user_tier TEXT DEFAULT 'standard' CHECK (user_tier IN ('standard', 'premium', 'enterprise')),
ADD COLUMN daily_streak INTEGER DEFAULT 0,
ADD COLUMN longest_streak INTEGER DEFAULT 0,
ADD COLUMN ai_onboarding_completed BOOLEAN DEFAULT false;
```

### 7. **public.user_stats** (MODIFY)
**Changes**: Add AI-related statistics
```sql
ALTER TABLE public.user_stats 
ADD COLUMN total_ai_interactions INTEGER DEFAULT 0,
ADD COLUMN insights_generated INTEGER DEFAULT 0,
ADD COLUMN insights_applied INTEGER DEFAULT 0,
ADD COLUMN ai_satisfaction_score DECIMAL(3,2) CHECK (ai_satisfaction_score >= 0 AND ai_satisfaction_score <= 5);
```

### 8. **public.daily_reflections** (IF EXISTS - MODIFY)
**Changes**: Add embeddings
```sql
ALTER TABLE public.daily_reflections
ADD COLUMN reflection_embedding vector(1536),
ADD COLUMN accomplishment_embedding vector(1536),
ADD COLUMN challenges_embedding vector(1536),
ADD COLUMN embedding_model TEXT DEFAULT 'text-embedding-3-small',
ADD COLUMN embedding_updated_at TIMESTAMP WITH TIME ZONE;
```

## 🗑️ Tables to Remove/Deprecate

### 1. **public.ai_interactions** (REMOVE)
**Reason**: Replaced by more comprehensive tables (insights, ai_conversation_memory, ai_model_usage)
**Migration**: Data should be migrated to the new insights table before removal
```sql
-- Migrate data first
INSERT INTO public.insights (user_id, entity_type, insight_type, title, summary, detailed_reasoning, confidence_score, created_at)
SELECT 
    user_id,
    'global' as entity_type,
    'pattern_recognition' as insight_type,
    interaction_type as title,
    'Historical AI interaction' as summary,
    jsonb_build_object('type', interaction_type, 'context_size', context_size) as detailed_reasoning,
    0.75 as confidence_score,
    created_at
FROM public.ai_interactions;

-- Then drop the table
DROP TABLE IF EXISTS public.ai_interactions CASCADE;
```

## 🔧 Additional Database Setup

### 1. **Enable pgvector Extension**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. **Create Vector Indexes**
```sql
-- Journal entries
CREATE INDEX idx_journal_content_embedding 
ON public.journal_entries 
USING hnsw (content_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Tasks
CREATE INDEX idx_task_description_embedding 
ON public.tasks 
USING hnsw (description_embedding vector_cosine_ops)
WHERE description IS NOT NULL AND description != '';

-- Projects
CREATE INDEX idx_project_embedding 
ON public.projects 
USING hnsw (combined_embedding vector_cosine_ops);

-- Daily reflections
CREATE INDEX idx_reflection_embedding 
ON public.daily_reflections 
USING hnsw (reflection_embedding vector_cosine_ops);

-- AI conversation memory
CREATE INDEX idx_conversation_embedding 
ON public.ai_conversation_memory 
USING hnsw (message_embedding vector_cosine_ops);
```

### 3. **Create RAG Search Functions**
```sql
-- Multi-table semantic search function
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
    -- Implementation as provided in pgvector_rag_schema.sql
END;
$$;
```

### 4. **Enable Row Level Security (RLS)**
```sql
-- New tables
ALTER TABLE public.insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hrm_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hrm_user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hrm_feedback_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_conversation_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_model_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sleep_reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for each table
CREATE POLICY "Users can manage their own insights" ON public.insights FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view active HRM rules" ON public.hrm_rules FOR SELECT USING (is_active = true);
CREATE POLICY "Users can manage their own preferences" ON public.hrm_user_preferences FOR ALL USING (auth.uid() = user_id);
-- ... etc for all new tables
```

## 📊 Migration Order

1. **Phase 1: Extension and Core Tables**
   - Enable pgvector extension
   - Create insights table
   - Create hrm_rules table
   - Create hrm_user_preferences table

2. **Phase 2: Modify Existing Tables**
   - Add HRM fields to tasks, projects, areas, pillars
   - Add embedding columns to journal_entries, tasks, projects
   - Update user_profiles and user_stats

3. **Phase 3: RAG Infrastructure**
   - Create ai_conversation_memory table
   - Create vector indexes
   - Create search functions

4. **Phase 4: Supporting Tables**
   - Create hrm_feedback_log
   - Create ai_model_usage
   - Create daily_reflections (if not exists)
   - Create sleep_reflections
   - Create feedback

5. **Phase 5: Cleanup**
   - Migrate data from ai_interactions
   - Remove deprecated tables

## 🔍 Key Considerations

1. **Performance**: Vector indexes can be large. Monitor index size and query performance.
2. **Costs**: Storing embeddings increases storage costs. Consider retention policies.
3. **Backups**: Ensure backup strategy handles vector data efficiently.
4. **Security**: All new tables must have appropriate RLS policies.
5. **Monitoring**: Set up monitoring for vector search performance and AI usage.

This comprehensive set of changes will enable the full AI architecture with RAG capabilities while maintaining data integrity and security.