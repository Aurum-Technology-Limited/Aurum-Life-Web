# Aurum Life MVP Web App - Execution PRD for AI-Enhanced Architecture

**Version:** 2.1  
**Date:** January 2025  
**Document Type:** Production Implementation Status  
**Status:** ✅ MVP Deployed - Production Ready  

---

## 📋 Executive Summary

**✅ PRODUCTION STATUS UPDATE (January 2025)**

Aurum Life MVP has been successfully deployed to production with a modern React + Supabase + Vercel architecture. The application is live at https://aurum-life-web.vercel.app with full authentication, real-time synchronization, and core productivity features.

**Current Implementation Status:**
- ✅ **Frontend**: React 18 with Tailwind CSS deployed on Vercel
- ✅ **Backend**: Supabase Edge Functions with TypeScript
- ✅ **Database**: PostgreSQL with Row Level Security
- ✅ **Authentication**: Supabase Auth with Google OAuth
- ✅ **Real-time**: Live data synchronization
- ✅ **AI Integration**: OpenAI and Gemini API integration
- ✅ **Mobile**: Responsive design for all devices

This document now serves as a reference for the implemented MVP and future enhancement roadmap.

**Key Documents Referenced:**
- `/workspace/Aurum Architecture and Strategy/aurum_life_hrm_phase3_prd.md` - Complete HRM technical specifications
- `/workspace/Aurum Architecture and Strategy/aurum_life_hrm_ui_epics_user_stories.md` - UI/UX requirements
- `/workspace/Aurum Architecture and Strategy/aurum_life_new_screens_specification.md` - New screen designs
- `/workspace/Aurum Architecture and Strategy/aurum_life_wireframes_web.md` - Web wireframes
- `/workspace/Aurum Architecture and Strategy/aurum_life_wireframes_mobile.md` - Mobile wireframes

---

## 🎯 Implementation Scope

### Core Objectives
1. **Implement HRM Architecture** - Transform from rule-based to LLM-augmented reasoning
2. **Create Blackboard System** - Centralized insights repository with pub/sub capabilities
3. **Build New UI Components** - AI-powered interfaces for insights and interaction
4. **Maintain Existing Features** - Ensure backward compatibility with current functionality
5. **Optimize Performance** - Implement caching and efficient data patterns

### Out of Scope for MVP
- Mobile native app (web-responsive only)
- Voice assistant integration
- AR features
- Third-party calendar sync
- Team collaboration features

---

## 🏗️ Technical Architecture Requirements

### 1. Database Schema Updates

**Location:** Create migration files in `/workspace/backend/migrations/`

#### 1.1 New Tables Required

```sql
-- File: 001_create_insights_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.1
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

-- Create indexes for performance
CREATE INDEX idx_insights_user_entity ON insights(user_id, entity_type, entity_id);
CREATE INDEX idx_insights_active ON insights(user_id, is_active, created_at DESC);
CREATE INDEX idx_insights_type ON insights(user_id, insight_type, created_at DESC);
CREATE INDEX idx_insights_expiry ON insights(expires_at) WHERE expires_at IS NOT NULL;
```

```sql
-- File: 002_create_hrm_rules_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.2
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
    created_by TEXT DEFAULT 'system',
    version INTEGER DEFAULT 1,
    changelog JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

```sql
-- File: 003_create_hrm_preferences_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.3
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

```sql
-- File: 004_create_feedback_log_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.4
CREATE TABLE public.hrm_feedback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_id UUID REFERENCES public.insights(id) ON DELETE SET NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'insight_helpful', 'insight_not_helpful',
        'priority_correct', 'priority_incorrect',
        'reasoning_clear', 'reasoning_unclear',
        'recommendation_followed', 'recommendation_ignored'
    )),
    entity_type TEXT,
    entity_id UUID,
    original_score DECIMAL(5,2),
    user_adjusted_score DECIMAL(5,2),
    feedback_text TEXT,
    suggested_improvement TEXT,
    applied_rules JSONB,
    reasoning_snapshot JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.2 Existing Table Modifications

```sql
-- File: 005_modify_existing_tables.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.2
-- Add HRM fields to tasks table
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_priority_score DECIMAL(5,2);
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_reasoning_summary TEXT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_last_analyzed TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS ai_suggested_timeblock TEXT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS obstacle_risk TEXT CHECK (obstacle_risk IN ('low', 'medium', 'high'));
CREATE INDEX idx_tasks_hrm_priority ON tasks(user_id, completed, hrm_priority_score DESC) WHERE completed = false;

-- Add HRM fields to projects table
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_health_score DECIMAL(3,2);
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_predicted_completion DATE;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_risk_factors JSONB DEFAULT '[]'::JSONB;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS goal_coherence_score DECIMAL(3,2);

-- Add HRM fields to areas table
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS time_allocation_actual DECIMAL(5,2);
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS time_allocation_recommended DECIMAL(5,2);
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS balance_score DECIMAL(3,2);

-- Add HRM fields to pillars table
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS vision_statement TEXT;
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS success_metrics JSONB DEFAULT '[]'::JSONB;
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS alignment_strength DECIMAL(3,2);
```

#### 1.3 Data Migration

```sql
-- File: 006_migrate_ai_interactions.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.3
-- Migrate existing ai_interactions data to insights table
INSERT INTO public.insights (
    user_id, entity_type, insight_type, title, summary, 
    detailed_reasoning, confidence_score, created_at
)
SELECT 
    user_id,
    'global' as entity_type,
    'pattern_recognition' as insight_type,
    interaction_type as title,
    'Historical AI interaction' as summary,
    jsonb_build_object('type', interaction_type, 'context_size', context_size) as detailed_reasoning,
    0.75 as confidence_score,
    created_at
FROM public.ai_interactions
WHERE EXISTS (SELECT 1 FROM public.ai_interactions LIMIT 1);

-- Drop the old table after verification
-- DROP TABLE IF EXISTS public.ai_interactions CASCADE;
```

```sql
-- File: 007_enable_pgvector.sql
-- Reference: RAG_IMPLEMENTATION_GUIDE.md
-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding columns to existing tables
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
USING hnsw (reflection_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_task_description_embedding 
ON public.tasks 
USING hnsw (description_embedding vector_cosine_ops)
WHERE description IS NOT NULL AND description != '';

CREATE INDEX IF NOT EXISTS idx_project_embedding 
ON public.projects 
USING hnsw (combined_embedding vector_cosine_ops);
```

```sql
-- File: 008_create_ai_conversation_memory.sql
-- Reference: RAG_IMPLEMENTATION_GUIDE.md
-- Store AI conversation history with embeddings
CREATE TABLE IF NOT EXISTS public.ai_conversation_memory (
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

CREATE INDEX idx_conversation_embedding 
ON ai_conversation_memory 
USING hnsw (message_embedding vector_cosine_ops);

CREATE INDEX idx_conversation_user_date 
ON ai_conversation_memory (user_id, conversation_date DESC);

-- Enable RLS
ALTER TABLE ai_conversation_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own AI conversations" 
ON ai_conversation_memory FOR ALL USING (auth.uid() = user_id);
```

```sql
-- File: 009_create_rag_functions.sql
-- Reference: RAG_IMPLEMENTATION_GUIDE.md
-- Create helper functions for semantic search

-- Find similar journal entries
CREATE OR REPLACE FUNCTION find_similar_journal_entries(
    query_embedding vector(1536),
    match_count INT DEFAULT 5,
    user_id_filter UUID DEFAULT NULL
)
RETURNS TABLE(
    id UUID,
    title TEXT,
    content TEXT,
    similarity FLOAT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        je.id,
        je.title,
        je.content,
        1 - (je.content_embedding <=> query_embedding) as similarity,
        je.created_at
    FROM journal_entries je
    WHERE 
        je.content_embedding IS NOT NULL
        AND (user_id_filter IS NULL OR je.user_id = user_id_filter)
    ORDER BY je.content_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Multi-table semantic search for RAG
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
    RETURN QUERY
    WITH combined_results AS (
        -- Journal entries
        SELECT 
            'journal_entry' as entity_type,
            id as entity_id,
            title,
            content,
            1 - (content_embedding <=> query_embedding) as similarity,
            created_at,
            jsonb_build_object('mood', mood, 'tags', tags) as metadata
        FROM journal_entries
        WHERE 
            user_id = user_id_filter
            AND content_embedding IS NOT NULL
            AND (date_range_days IS NULL OR created_at >= NOW() - INTERVAL '1 day' * date_range_days)
        
        UNION ALL
        
        -- Daily reflections
        SELECT 
            'daily_reflection' as entity_type,
            id as entity_id,
            'Daily Reflection - ' || reflection_date::TEXT as title,
            reflection_text as content,
            1 - (reflection_embedding <=> query_embedding) as similarity,
            created_at,
            jsonb_build_object(
                'completion_score', completion_score,
                'mood', mood,
                'date', reflection_date
            ) as metadata
        FROM daily_reflections
        WHERE 
            user_id = user_id_filter
            AND reflection_embedding IS NOT NULL
            AND (date_range_days IS NULL OR created_at >= NOW() - INTERVAL '1 day' * date_range_days)
        
        UNION ALL
        
        -- Tasks with descriptions
        SELECT 
            'task' as entity_type,
            t.id as entity_id,
            t.name as title,
            t.description as content,
            1 - (t.description_embedding <=> query_embedding) as similarity,
            t.created_at,
            jsonb_build_object(
                'status', t.status,
                'priority', t.priority,
                'project_id', t.project_id,
                'due_date', t.due_date
            ) as metadata
        FROM tasks t
        WHERE 
            t.user_id = user_id_filter
            AND t.description_embedding IS NOT NULL
            AND t.description != ''
            AND (date_range_days IS NULL OR t.created_at >= NOW() - INTERVAL '1 day' * date_range_days)
    )
    SELECT * FROM combined_results
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

```sql
-- File: 010_seed_hrm_rules.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 6.1
INSERT INTO public.hrm_rules (rule_code, rule_name, description, hierarchy_level, applies_to_entity_types, rule_type, rule_config, base_weight, requires_llm) VALUES
('TEMPORAL_URGENCY_001', 'Task Deadline Urgency', 'Scores tasks based on deadline proximity', 'task', ARRAY['task'], 'temporal', 
 '{"conditions": {"due_date_proximity": "24h", "has_dependencies": false}, "actions": {"priority_boost": 0.3, "add_tag": "urgent"}}'::jsonb, 
 0.7, false),
 
('PILLAR_ALIGNMENT_001', 'Pillar Alignment Scoring', 'Scores entities based on pillar importance and time allocation', 'cross_level', ARRAY['task', 'project', 'area'], 'scoring',
 '{"factors": ["pillar_time_allocation", "area_importance", "project_priority"], "aggregation": "weighted_average"}'::jsonb,
 0.8, false),
 
('ENERGY_PATTERN_001', 'Energy-Based Task Matching', 'Matches tasks to user energy patterns', 'task', ARRAY['task'], 'temporal',
 '{"energy_mapping": {"deep_work": ["morning_peak"], "admin": ["afternoon"], "creative": ["evening_peak"]}}'::jsonb,
 0.5, true),
 
('DEPENDENCY_CHECK_001', 'Task Dependency Analysis', 'Analyzes and scores based on dependency status', 'task', ARRAY['task'], 'constraint',
 '{"blocking_penalty": 0.8, "ready_boost": 0.2}'::jsonb,
 0.6, false);
```

### 2. Backend Service Implementation

#### 2.1 Core HRM Service

**File:** `/workspace/backend/hrm_service.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.1.1

```python
# Implementation structure based on PRD specifications
# Full implementation details in aurum_life_hrm_phase3_prd.md - Section 3.1.1

class HierarchicalReasoningModel:
    """
    LLM-Augmented Hierarchical Reasoning Model
    Provides intelligent reasoning across the PAPT hierarchy
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = get_supabase_client()
        self.llm = self._initialize_llm()
        self._context_cache = {}
        
    async def analyze_entity(self, entity_type: str, entity_id: Optional[str] = None, analysis_depth: str = "balanced") -> HRMInsight:
        """
        Perform hierarchical reasoning on an entity
        Reference: aurum_life_hrm_phase3_prd.md - analyze_entity method
        """
        # Implementation as specified in PRD
        pass
```

#### 2.2 Blackboard Service

**File:** `/workspace/backend/blackboard_service.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.1.2

```python
# Implementation structure based on PRD specifications
# Full implementation details in aurum_life_hrm_phase3_prd.md - Section 3.1.2

class BlackboardService:
    """
    Centralized insight repository with pub/sub capabilities
    Implements the Blackboard architectural pattern for AI systems
    """
    
    async def store_insight(self, user_id: str, insight: Dict[str, Any], notify_subscribers: bool = True) -> str:
        """
        Store an insight and optionally notify subscribers
        Reference: aurum_life_hrm_phase3_prd.md - store_insight method
        """
        # Implementation as specified in PRD
        pass
```

#### 2.3 Rules Engine

**File:** `/workspace/backend/hrm_rules_engine.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.1.3

```python
# Implementation structure based on PRD specifications
# Full implementation details in aurum_life_hrm_phase3_prd.md - Section 3.1.3

class HRMRulesEngine:
    """
    Main rules engine for HRM
    Manages and executes hierarchical rules for the reasoning model
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self._rule_registry = {
            'TEMPORAL_URGENCY': TemporalUrgencyRule,
            'PILLAR_ALIGNMENT': PillarAlignmentRule,
            'ENERGY_PATTERN': EnergyPatternRule,
            'DEPENDENCY_CHECK': DependencyRule
        }
        self._rules_cache = {}
```

#### 2.4 API Endpoint Updates

**File:** `/workspace/backend/server.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.2.2

Add these new endpoints:

```python
# New imports
from hrm_service import HierarchicalReasoningModel
from blackboard_service import BlackboardService
from hrm_rules_engine import HRMRulesEngine

# Service initialization
blackboard_service = BlackboardService()
hrm_rules_engine = HRMRulesEngine()

# New endpoints as specified in PRD Section 5.1
@api_router.get("/insights/{entity_type}/{entity_id}")
async def get_entity_insights(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get HRM insights for any entity"""
    # Implementation as specified in PRD
    pass

@api_router.post("/insights/{entity_type}/{entity_id}/analyze")
async def analyze_entity(
    entity_type: str,
    entity_id: str,
    analysis_depth: str = Query("balanced", regex="^(minimal|balanced|detailed)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger HRM analysis for an entity"""
    # Implementation as specified in PRD
    pass
```

#### 2.5 RAG Implementation with pgvector

**Reference:** `/workspace/Aurum Architecture and Strategy/Technical Documents/RAG_IMPLEMENTATION_GUIDE.md`

##### 2.5.1 Embedding Service

**File:** `/workspace/backend/ai/embedding_service.py`

```python
import openai
from typing import List, Dict, Optional
import asyncio
from supabase import create_client
import numpy as np

class EmbeddingService:
    """
    Service for generating and managing vector embeddings for RAG
    Enables semantic search across user content
    """
    
    def __init__(self):
        self.model = "text-embedding-3-small"  # 1536 dimensions, cost-effective
        self.batch_size = 100
        self.supabase = get_supabase_client()
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = await openai.Embedding.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def update_journal_embeddings(self, user_id: str):
        """Update embeddings for user's journal entries"""
        # Batch process journal entries without embeddings
        entries = await self.supabase.from_('journal_entries')\
            .select('id, title, content')\
            .eq('user_id', user_id)\
            .is_('content_embedding', None)\
            .execute()
        
        if entries.data:
            await self._batch_update_embeddings('journal_entries', entries.data)
    
    async def update_task_embeddings(self, user_id: str):
        """Update embeddings for tasks with descriptions"""
        tasks = await self.supabase.from_('tasks')\
            .select('id, name, description')\
            .eq('user_id', user_id)\
            .neq('description', '')\
            .is_('description_embedding', None)\
            .execute()
        
        if tasks.data:
            await self._batch_update_embeddings('tasks', tasks.data)
```

##### 2.5.2 RAG Service

**File:** `/workspace/backend/ai/rag_service.py`

```python
from typing import Dict, List, Optional
from embedding_service import EmbeddingService

class RAGService:
    """
    Retrieval-Augmented Generation service
    Provides contextual information from user's history for AI responses
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.context_window = 5  # Number of relevant documents
        self.supabase = get_supabase_client()
        
    async def retrieve_context(self, query: str, user_id: str, 
                             entity_filter: Optional[Dict] = None) -> Dict:
        """
        Retrieve relevant context for a query
        Returns formatted context and source documents
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Search across multiple tables using rag_search function
        results = await self.supabase.rpc('rag_search', {
            'query_embedding': query_embedding,
            'user_id_filter': user_id,
            'match_count': self.context_window,
            'date_range_days': 90  # Focus on recent 3 months
        }).execute()
        
        # Format context for LLM
        context = self._format_context(results.data)
        return {
            'context': context,
            'sources': results.data,
            'embedding_used': query_embedding[:5]  # First 5 for debugging
        }
    
    async def find_similar_tasks(self, task_description: str, user_id: str) -> List[Dict]:
        """Find similar completed tasks to help with estimation and approach"""
        embedding = await self.embedding_service.generate_embedding(task_description)
        
        results = await self.supabase.rpc('find_similar_tasks', {
            'query_embedding': embedding,
            'user_id_filter': user_id,
            'match_count': 3,
            'include_completed': True
        }).execute()
        
        return results.data
```

##### 2.5.3 Enhanced HRM Service with RAG

**File:** Update `/workspace/backend/hrm_service.py`

```python
# Add to existing HRM service
from ai.rag_service import RAGService

class HierarchicalReasoningModel:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = get_supabase_client()
        self.llm = self._initialize_llm()
        self.rag_service = RAGService()  # NEW: Add RAG service
        self._context_cache = {}
        
    async def analyze_entity(self, entity_type: str, entity_id: Optional[str] = None, 
                           analysis_depth: str = "balanced", use_rag: bool = True) -> HRMInsight:
        """
        Enhanced entity analysis with RAG context
        """
        # Get entity details
        entity = await self._get_entity(entity_type, entity_id)
        
        # NEW: Retrieve relevant historical context
        rag_context = None
        if use_rag:
            query = self._build_rag_query(entity_type, entity)
            rag_context = await self.rag_service.retrieve_context(
                query=query,
                user_id=self.user_id
            )
        
        # Build enhanced prompt with RAG context
        prompt = self._build_analysis_prompt(
            entity_type, entity, analysis_depth, rag_context
        )
        
        # Generate insight with LLM
        insight = await self._generate_insight(prompt, entity_type, entity_id)
        
        # Store RAG sources in insight metadata
        if rag_context:
            insight.llm_context['rag_sources'] = rag_context['sources']
        
        return insight
```

#### 2.6 AI Model Router Implementation

**Reference:** `/workspace/Aurum Architecture and Strategy/Technical Documents/SYSTEM_ARCHITECTURE.md` - AI Architecture section

##### 2.6.1 AI Router Service

**File:** `/workspace/backend/ai/router.py`

```python
from enum import Enum
from typing import Dict, Any, Optional
import openai
import google.generativeai as genai

class ModelType(Enum):
    STRATEGIC = "strategic"  # GPT-4 Turbo for complex reasoning
    EXECUTION = "execution"  # Gemini 1.5 Flash for CRUD operations

class ComplexityAnalyzer:
    """Analyzes request complexity to determine appropriate model"""
    
    STRATEGIC_KEYWORDS = {
        'analyze', 'strategy', 'plan', 'align', 'optimize', 
        'recommend', 'insight', 'pattern', 'trend'
    }
    
    EXECUTION_KEYWORDS = {
        'create', 'update', 'delete', 'list', 'fetch', 
        'get', 'set', 'add', 'remove', 'modify'
    }
    
    async def analyze(self, request: Dict[str, Any]) -> float:
        """
        Returns complexity score 0-10
        0-3: Simple CRUD operations
        4-7: Moderate complexity
        8-10: Complex reasoning required
        """
        content = request.get('content', '').lower()
        
        # Check for strategic keywords
        strategic_score = sum(
            2 for keyword in self.STRATEGIC_KEYWORDS 
            if keyword in content
        )
        
        # Check for execution keywords
        execution_score = sum(
            1 for keyword in self.EXECUTION_KEYWORDS 
            if keyword in content
        )
        
        # Multi-entity operations add complexity
        if request.get('cross_entity', False):
            strategic_score += 3
            
        # Long-form analysis requests
        if len(content) > 200:
            strategic_score += 2
            
        complexity = min(10, strategic_score - (execution_score * 0.5))
        return max(0, complexity)

class AIRouter:
    """
    Routes AI requests to appropriate models based on complexity and type
    Optimizes for cost and performance
    """
    
    def __init__(self):
        self.strategic_model = OpenAIClient(model="gpt-4-turbo")
        self.execution_model = GeminiClient(model="gemini-1.5-flash")
        self.complexity_analyzer = ComplexityAnalyzer()
        self.usage_tracker = UsageTracker()
        
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate model"""
        # Check user's tier and quotas
        user_tier = request.get('user_tier', 'standard')
        monthly_usage = await self.usage_tracker.get_monthly_usage(
            request['user_id']
        )
        
        # Analyze complexity
        complexity_score = await self.complexity_analyzer.analyze(request)
        
        # Determine model based on complexity and quotas
        if complexity_score > 7 or request.get('requires_reasoning', False):
            # Check if user has quota for strategic model
            if monthly_usage['strategic_tokens'] < STRATEGIC_QUOTA_LIMIT:
                model_type = ModelType.STRATEGIC
            else:
                # Fallback to execution model with enhanced prompt
                model_type = ModelType.EXECUTION
                request['enhanced_prompt'] = True
        else:
            model_type = ModelType.EXECUTION
        
        # Process request with selected model
        if model_type == ModelType.STRATEGIC:
            response = await self.strategic_model.process(request)
        else:
            response = await self.execution_model.process(request)
        
        # Track usage
        await self.usage_tracker.track_usage(
            user_id=request['user_id'],
            model_type=model_type,
            tokens_used=response['usage']['total_tokens']
        )
        
        response['model_used'] = model_type.value
        response['complexity_score'] = complexity_score
        
        return response
```

#### 2.7 Speech API Implementation

**Reference:** `/workspace/Aurum Architecture and Strategy/Technical Documents/SYSTEM_ARCHITECTURE.md` - Speech API Architecture section

##### 2.7.1 Speech Service

**File:** `/workspace/backend/ai/speech_service.py`

```python
import openai
from typing import Optional, BinaryIO
import asyncio
import io

class SpeechService:
    """
    Handles speech-to-text and text-to-speech conversions
    Enables voice interactions with Aurum AI
    """
    
    def __init__(self):
        # Speech-to-Text
        self.stt_model = "whisper-1"
        
        # Text-to-Speech
        self.tts_model = "tts-1"
        self.tts_voice_standard = "alloy"  # Natural, balanced voice
        self.tts_voice_premium = None  # For future ElevenLabs integration
        
    async def transcribe_audio(self, audio_file: BinaryIO, 
                             language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio to text using Whisper
        Supports 99+ languages with automatic detection
        """
        try:
            # OpenAI Whisper API
            response = await openai.Audio.atranscribe(
                model=self.stt_model,
                file=audio_file,
                language=language,  # Optional language hint
                response_format="verbose_json"  # Get timestamps
            )
            
            return {
                'text': response.text,
                'language': response.language,
                'duration': response.duration,
                'segments': response.segments  # Word-level timestamps
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    async def synthesize_speech(self, text: str, user_tier: str = "standard",
                              voice: Optional[str] = None) -> bytes:
        """
        Convert text to speech
        Returns audio bytes in MP3 format
        """
        try:
            # Select voice based on user tier
            if user_tier == "premium" and self.tts_voice_premium:
                # Future: Use ElevenLabs for premium users
                return await self._synthesize_premium(text, voice)
            else:
                # Use OpenAI TTS for standard users
                voice = voice or self.tts_voice_standard
                
                response = await openai.Audio.speech.create(
                    model=self.tts_model,
                    voice=voice,
                    input=text,
                    response_format="mp3",
                    speed=1.0  # Normal speed
                )
                
                return response.content
                
        except Exception as e:
            raise Exception(f"Speech synthesis failed: {str(e)}")
    
    async def process_voice_conversation(self, audio_file: BinaryIO, 
                                       user_id: str, user_tier: str = "standard") -> Dict[str, Any]:
        """
        Complete voice conversation pipeline
        Audio → Text → AI Processing → Speech
        """
        # Step 1: Transcribe audio
        transcription = await self.transcribe_audio(audio_file)
        
        # Step 2: Process with AI (using existing router)
        from ai.router import AIRouter
        ai_router = AIRouter()
        
        ai_response = await ai_router.route_request({
            'content': transcription['text'],
            'user_id': user_id,
            'user_tier': user_tier,
            'input_type': 'voice'
        })
        
        # Step 3: Convert response to speech
        audio_response = await self.synthesize_speech(
            ai_response['content'],
            user_tier
        )
        
        return {
            'transcription': transcription['text'],
            'ai_response': ai_response['content'],
            'audio_response': audio_response,
            'language': transcription['language'],
            'model_used': ai_response['model_used']
        }
```

##### 2.7.2 Voice API Endpoints

**File:** Add to `/workspace/backend/server.py`

```python
from ai.speech_service import SpeechService
from fastapi import UploadFile, File

speech_service = SpeechService()

@api_router.post("/voice/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Transcribe audio to text"""
    audio_bytes = await audio.read()
    audio_file = io.BytesIO(audio_bytes)
    
    result = await speech_service.transcribe_audio(audio_file, language)
    
    # Store in conversation memory
    await store_conversation_memory(
        user_id=current_user.id,
        role="user",
        content=result['text'],
        metadata={'audio_duration': result['duration']}
    )
    
    return result

@api_router.post("/voice/synthesize")
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Convert text to speech"""
    audio_bytes = await speech_service.synthesize_speech(
        text=request.text,
        user_tier=current_user.tier,
        voice=request.voice
    )
    
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "attachment; filename=speech.mp3"
        }
    )

@api_router.post("/voice/conversation")
async def voice_conversation(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Complete voice conversation with AI"""
    audio_bytes = await audio.read()
    audio_file = io.BytesIO(audio_bytes)
    
    result = await speech_service.process_voice_conversation(
        audio_file=audio_file,
        user_id=current_user.id,
        user_tier=current_user.tier
    )
    
    # Return both text and audio responses
    return {
        'transcription': result['transcription'],
        'ai_response': result['ai_response'],
        'audio_url': f"/api/voice/audio/{store_temp_audio(result['audio_response'])}",
        'model_used': result['model_used']
    }
```

### 3. Frontend Implementation

#### 3.1 New Components Required

**Reference:** `aurum_life_wireframes_web.md` for detailed specifications

##### 3.1.1 AI Command Center Component

**File:** `/workspace/frontend/src/components/AICommandCenter.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 1

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { Command } from 'lucide-react';
import { useHotkeys } from 'react-hotkeys-hook';

const AICommandCenter = () => {
  // Implementation based on wireframe specifications
  // Styling: Background #1F2937, Border #374151, etc.
  return (
    <div className="fixed inset-0 z-50 bg-black/70">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

##### 3.1.2 HRM Insight Card Component

**File:** `/workspace/frontend/src/components/HRMInsightCard.jsx`
**Reference:** `aurum_life_hrm_ui_epics_user_stories.md` - Section "New Components Needed"

```jsx
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Brain, TrendingUp, AlertTriangle } from 'lucide-react';

const HRMInsightCard = ({ insight, onFeedback }) => {
  // Implementation based on UI specifications
  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700">
      {/* Implementation as specified in user stories */}
    </div>
  );
};
```

##### 3.1.3 AI Insights Dashboard

**File:** `/workspace/frontend/src/components/AIInsightsDashboard.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 2

```jsx
import React, { useState, useEffect } from 'react';
import { Brain, Settings, RefreshCw } from 'lucide-react';
import HRMInsightCard from './HRMInsightCard';
import { api } from '../services/api';

const AIInsightsDashboard = () => {
  // Implementation based on wireframe specifications
  // Stats cards, filter system, insights list
  return (
    <div className="p-6 bg-[#0B0D14]">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

##### 3.1.4 Focus Mode Component

**File:** `/workspace/frontend/src/components/FocusMode.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 3

```jsx
import React, { useState, useEffect } from 'react';
import { Pause, Check, X } from 'lucide-react';

const FocusMode = ({ task, onComplete, onExit }) => {
  // Implementation based on wireframe specifications
  // Timer, progress ring, AI coaching
  return (
    <div className="fixed inset-0 bg-[#0B0D14] flex items-center justify-center">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

##### 3.1.5 Daily Planning Ritual

**File:** `/workspace/frontend/src/components/DailyPlanningRitual.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 4

```jsx
import React, { useState } from 'react';
import { Sun } from 'lucide-react';

const DailyPlanningRitual = ({ onComplete, onSkip }) => {
  const [energy, setEnergy] = useState(null);
  const [schedule, setSchedule] = useState([]);
  
  // Implementation based on wireframe specifications
  return (
    <div className="max-w-4xl mx-auto p-8">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

#### 3.2 Component Integration

##### 3.2.1 Update App.js

**File:** `/workspace/frontend/src/App.js`

Add new routes and lazy imports:

```jsx
// Add to lazy imports section
const AIInsightsDashboard = lazy(() => import('./components/AIInsightsDashboard'));
const FocusMode = lazy(() => import('./components/FocusMode'));

// Add to navigation cases in renderActiveSection()
case 'ai-insights':
  return <AIInsightsDashboard {...props} />;
case 'focus':
  return <FocusMode {...props} />;
```

##### 3.2.2 Update Navigation

**File:** `/workspace/frontend/src/components/SimpleLayout.jsx`

Add new navigation items:

```jsx
const navigation = useMemo(() => [
  // ... existing items ...
  { name: 'AI Insights', key: 'ai-insights', icon: Brain },
  // ... rest of items ...
], []);
```

##### 3.2.3 Update Today Component

**File:** `/workspace/frontend/src/components/Today.jsx`
**Reference:** `aurum_life_hrm_ui_epics_user_stories.md` - Story 2.1

Modify to include HRM analysis:

```jsx
// Add HRM insight display to task cards
import HRMInsightCard from './HRMInsightCard';

// In the task rendering section:
{showHrmAnalysis && task.hrm_analysis && (
  <div className="ml-4 mt-2">
    <HRMInsightCard
      insight={{
        id: `task-${task.id}-analysis`,
        title: 'Priority Analysis',
        summary: task.hrm_reasoning_summary,
        confidence_score: task.hrm_priority_score / 100,
        detailed_reasoning: task.hrm_analysis
      }}
    />
  </div>
)}
```

### 4. API Integration Updates

#### 4.1 Update API Service

**File:** `/workspace/frontend/src/services/api.js`

Add new API endpoints:

```javascript
// HRM Insights API
export const insightsAPI = {
  getInsights: (entityType, entityId) => 
    api.get(`/api/insights/${entityType}/${entityId}`),
    
  analyzeEntity: (entityType, entityId, depth = 'balanced') =>
    api.post(`/api/insights/${entityType}/${entityId}/analyze?analysis_depth=${depth}`),
    
  submitFeedback: (insightId, feedback, details = null) =>
    api.post(`/api/insights/${insightId}/feedback?feedback=${feedback}`, details),
    
  getPatterns: (lookbackDays = 30) =>
    api.get(`/api/insights/patterns/me?lookback_days=${lookbackDays}`)
};

// HRM Preferences API
export const hrmAPI = {
  getPreferences: () => api.get('/api/hrm/preferences'),
  updatePreferences: (preferences) => api.put('/api/hrm/preferences', preferences)
};

// Update Today API to include HRM parameter
export const todayAPI = {
  getTodayTasks: (coachingTopN = 3, useHrm = true) => 
    api.get(`/api/today?coaching_top_n=${coachingTopN}&use_hrm=${useHrm}`),
  // ... rest of methods
};
```

### 5. Design System Updates

#### 5.1 Add AI-Specific Styles

**File:** `/workspace/frontend/src/index.css`

Add new design tokens:

```css
/* AI-specific colors */
:root {
  --ai-primary: #3B82F6;
  --ai-secondary: #8B5CF6;
  --ai-success: #10B981;
  --ai-warning: #F59E0B;
  --ai-danger: #EF4444;
  --ai-surface: #1E293B;
  --ai-surface-light: #334155;
}

/* AI-specific utilities */
@layer utilities {
  .ai-glow {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
  }
  
  .ai-border {
    border-color: var(--ai-primary);
  }
  
  .confidence-high {
    color: var(--ai-success);
  }
  
  .confidence-medium {
    color: var(--ai-warning);
  }
  
  .confidence-low {
    color: var(--ai-danger);
  }
}
```

### 6. Performance Optimizations

#### 6.1 Caching Strategy

**File:** `/workspace/backend/cache_service.py`

Add HRM-specific caching:

```python
def cache_hrm_insight(user_id: str, entity_type: str, entity_id: str, ttl: int = 21600):
    """Cache HRM insights for 6 hours by default"""
    cache_key = f"hrm_insight:{user_id}:{entity_type}:{entity_id}"
    return cache_result(cache_key, ttl_seconds=ttl)

def cache_reasoning_path(user_id: str, task_id: str, ttl: int = 3600):
    """Cache reasoning paths for 1 hour"""
    cache_key = f"reasoning_path:{user_id}:{task_id}"
    return cache_result(cache_key, ttl_seconds=ttl)
```

#### 6.2 Query Optimization

**Reference:** `aurum_life_hrm_phase3_prd.md` - Performance sections

- Implement parallel fetching for hierarchy data
- Use database views for complex reasoning paths
- Batch API calls where possible
- Implement progressive loading for insights

### 7. Testing Requirements

#### 7.1 Backend Tests

**Directory:** `/workspace/backend/tests/`

Create test files:

1. `test_hrm_service.py` - Test HRM analysis functionality
2. `test_blackboard_service.py` - Test insight storage and retrieval
3. `test_hrm_rules_engine.py` - Test rule execution
4. `test_hrm_endpoints.py` - Test new API endpoints

#### 7.2 Frontend Tests

**Directory:** `/workspace/frontend/src/__tests__/`

Create test files:

1. `AICommandCenter.test.jsx` - Test command parsing and suggestions
2. `HRMInsightCard.test.jsx` - Test insight display and feedback
3. `AIInsightsDashboard.test.jsx` - Test dashboard functionality
4. `FocusMode.test.jsx` - Test timer and controls

### 8. Deployment Checklist

#### 8.1 Environment Variables

Add to `.env`:

```bash
# Existing variables remain unchanged

# AI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here  # Optional for premium TTS

# Model Selection
AI_STRATEGIC_MODEL=gpt-4-turbo
AI_EXECUTION_MODEL=gemini-1.5-flash
AI_EMBEDDING_MODEL=text-embedding-3-small

# AI Cost Control
AI_MONTHLY_BUDGET_PER_USER=0.50  # USD
AI_STRATEGIC_TOKEN_LIMIT=100000  # Monthly limit per user
AI_EXECUTION_TOKEN_LIMIT=1000000  # Monthly limit per user

# HRM-specific configuration
HRM_ENABLED=true
HRM_DEFAULT_ANALYSIS_DEPTH=balanced
HRM_CACHE_TTL=21600
HRM_MAX_INSIGHTS_PER_USER=1000
HRM_USE_RAG=true  # Enable RAG for contextual responses

# RAG Configuration
RAG_CONTEXT_WINDOW=5
RAG_DATE_RANGE_DAYS=90
RAG_EMBEDDING_BATCH_SIZE=100

# Speech API Configuration
SPEECH_STT_MODEL=whisper-1
SPEECH_TTS_MODEL=tts-1
SPEECH_TTS_VOICE_STANDARD=alloy
SPEECH_ENABLE_PREMIUM_TTS=false
```

#### 8.2 Database Migrations

1. Run all migration scripts in order (001-010):
   - 001-006: Core HRM tables and modifications
   - 007: Enable pgvector extension and add embeddings
   - 008: Create AI conversation memory table
   - 009: Create RAG search functions
   - 010: Seed HRM rules
2. Verify pgvector extension is enabled
3. Verify data migration from ai_interactions table
4. Create database backup before migrations
5. Test rollback procedures
6. Generate initial embeddings for existing content (background job)

#### 8.3 Feature Flags

Implement feature flag for gradual rollout:

```python
# In backend/server.py
HRM_ENABLED = os.environ.get('HRM_ENABLED', 'true').lower() == 'true'

# Use throughout code
if HRM_ENABLED:
    # Use HRM system
else:
    # Use legacy system
```

### 9. MVP Success Criteria

1. **Functional Requirements**
   - [ ] HRM analyzes tasks with reasoning paths
   - [ ] Insights are stored and retrievable
   - [ ] Users can provide feedback on insights
   - [ ] AI Command Center is accessible via Cmd+K
   - [ ] Daily planning ritual generates schedules
   - [ ] Focus mode tracks time with AI coaching

2. **Performance Requirements**
   - [ ] Insight generation < 3 seconds
   - [ ] Command center response < 500ms
   - [ ] Page load times < 2 seconds
   - [ ] Smooth animations at 60fps

3. **Quality Requirements**
   - [ ] 90% test coverage for new code
   - [ ] No regression in existing features
   - [ ] Accessibility compliance (WCAG 2.1 AA)
   - [ ] Mobile responsive design

### 10. Implementation Order

**Week 1: Foundation**
1. Database migrations and schema updates
2. Backend HRM service implementation
3. Blackboard service implementation
4. Basic API endpoints

**Week 2: Core Features**
1. AI Command Center component
2. HRM Insight Card component  
3. Update Today view with HRM
4. Implement caching layer

**Week 3: Advanced Features**
1. AI Insights Dashboard
2. Focus Mode implementation
3. Daily Planning Ritual
4. Rules engine completion

**Week 4: Polish & Testing**
1. Performance optimization
2. Comprehensive testing
3. Bug fixes and refinements
4. Documentation updates

---

## 📚 Additional References

- **Technical Architecture:** Review existing codebase structure in `/workspace/backend/` and `/workspace/frontend/`
- **Design System:** Maintain consistency with current dark theme (#0B0D14 background, #F59E0B primary)
- **AI Integration:** Leverage existing Gemini integration in `ai_coach_service.py`
- **Performance:** Follow patterns in `ultra_performance_services.py`

## 🚨 Important Notes

1. **Backward Compatibility:** All existing features must continue working during implementation
2. **Data Integrity:** Implement comprehensive data validation and error handling
3. **Security:** Follow existing authentication patterns and add rate limiting for AI endpoints
4. **Monitoring:** Add logging for all HRM decisions for debugging and improvement

### 11. AI Performance & Cost Monitoring

#### 11.1 Cost Tracking Dashboard

Implement real-time cost monitoring for AI usage:

```python
# backend/ai/usage_tracker.py
class UsageTracker:
    async def get_usage_summary(self, user_id: str, period: str = "month") -> Dict:
        """Get AI usage and cost summary for user"""
        return {
            "period": period,
            "strategic_model": {
                "requests": 245,
                "tokens": 98500,
                "cost": 2.46  # USD
            },
            "execution_model": {
                "requests": 1820,
                "tokens": 485000,
                "cost": 0.48  # USD
            },
            "embeddings": {
                "requests": 150,
                "vectors": 1500,
                "cost": 0.02  # USD
            },
            "speech": {
                "stt_minutes": 45,
                "tts_characters": 125000,
                "cost": 2.14  # USD
            },
            "total_cost": 5.10,  # USD
            "budget_remaining": 4.90,  # USD (from $10 monthly)
            "projected_monthly": 7.65  # USD
        }
```

#### 11.2 Key Performance Metrics

Monitor these AI-specific metrics:

1. **Response Quality**
   - User feedback rate on insights
   - Insight application rate
   - Task completion improvement

2. **Cost Efficiency**
   - Cost per active user
   - Model routing accuracy
   - Cache hit rate for embeddings

3. **Performance Metrics**
   - Average response time by model
   - RAG retrieval relevance scores
   - Speech recognition accuracy

4. **Usage Patterns**
   - Peak usage hours
   - Most common query types
   - Feature adoption rates

#### 11.3 Cost Optimization Alerts

Set up automated alerts for:
- User approaching monthly budget (80%)
- Unusual spike in strategic model usage
- Low cache hit rates
- High error rates in speech processing

#### 11.4 Expected Cost Projections

Based on the multi-model architecture:

| Users | Monthly AI Cost | Revenue Needed* |
|-------|----------------|-----------------|
| 100   | $21            | $42             |
| 1,000 | $210           | $420            |
| 10,000| $1,900         | $3,800          |

*Assuming 50% margin on AI costs

This PRD provides a complete blueprint for implementing the enhanced AI architecture with cost-optimized multi-model routing, RAG capabilities, and voice interaction support. Reference the linked documents for detailed specifications, wireframes, and user stories.