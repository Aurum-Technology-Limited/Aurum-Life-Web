-- HRM Phase 3: User Feedback Tracking Table
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.4

CREATE TABLE IF NOT EXISTS public.hrm_feedback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_id UUID REFERENCES public.insights(id) ON DELETE SET NULL,
    
    -- Feedback Classification
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'insight_helpful', 'insight_not_helpful',
        'priority_correct', 'priority_incorrect',
        'reasoning_clear', 'reasoning_unclear',
        'recommendation_followed', 'recommendation_ignored'
    )),
    
    -- Context
    entity_type TEXT,
    entity_id UUID,
    
    -- Score Adjustments
    original_score DECIMAL(5,2),
    user_adjusted_score DECIMAL(5,2),
    
    -- Qualitative Feedback
    feedback_text TEXT,
    suggested_improvement TEXT,
    
    -- System State Snapshot
    applied_rules JSONB,
    reasoning_snapshot JSONB,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_feedback_log_user ON hrm_feedback_log(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_log_insight ON hrm_feedback_log(insight_id);
CREATE INDEX IF NOT EXISTS idx_feedback_log_type ON hrm_feedback_log(feedback_type, created_at DESC);

-- Row Level Security
ALTER TABLE hrm_feedback_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own feedback log" 
ON hrm_feedback_log FOR ALL USING (auth.uid() = user_id);