-- HRM Phase 3: Core Insights Table
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.1

CREATE TABLE IF NOT EXISTS public.insights (
    -- Primary Fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Entity Reference
    entity_type TEXT NOT NULL CHECK (entity_type IN ('pillar', 'area', 'project', 'task', 'global')),
    entity_id UUID, -- NULL for global insights
    
    -- Insight Details
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'priority_reasoning',      -- Why something is prioritized
        'alignment_analysis',      -- How entities align with goals
        'pattern_recognition',     -- Detected patterns
        'recommendation',          -- Action recommendations
        'goal_coherence',         -- Goal conflict/alignment analysis
        'time_allocation',        -- Time distribution insights
        'progress_prediction',    -- Future state predictions
        'obstacle_identification' -- Blocker analysis
    )),
    
    -- Core Content
    title TEXT NOT NULL,
    summary TEXT NOT NULL,        -- Human-readable summary
    detailed_reasoning JSONB NOT NULL, -- Full HRM reasoning trace
    
    -- HRM Specific Fields
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0 AND impact_score <= 1),
    
    -- Reasoning Path (shows hierarchical thinking)
    reasoning_path JSONB NOT NULL DEFAULT '[]'::JSONB,
    
    -- LLM Context Preservation
    llm_session_id TEXT,
    llm_context JSONB, -- Preserved context for conversation continuity
    llm_model_used TEXT DEFAULT 'gemini-2.0-flash',
    
    -- User Interaction
    user_feedback TEXT CHECK (user_feedback IN ('accepted', 'rejected', 'modified', 'ignored')),
    feedback_details JSONB,
    application_count INTEGER DEFAULT 0, -- Times user applied this insight
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    is_pinned BOOLEAN DEFAULT false, -- User can pin important insights
    expires_at TIMESTAMP WITH TIME ZONE, -- Auto-expire time-sensitive insights
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Versioning
    version INTEGER DEFAULT 1,
    previous_version_id UUID REFERENCES public.insights(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_insights_user_entity ON insights(user_id, entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_insights_active ON insights(user_id, is_active, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(user_id, insight_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_insights_expiry ON insights(expires_at) WHERE expires_at IS NOT NULL;

-- Row Level Security
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own insights" 
ON insights FOR ALL USING (auth.uid() = user_id);