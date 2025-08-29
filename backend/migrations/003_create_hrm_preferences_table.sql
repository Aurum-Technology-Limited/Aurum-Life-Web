-- HRM Phase 3: User Preferences Table
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.3

CREATE TABLE IF NOT EXISTS public.hrm_user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Rule Weight Overrides
    rule_weight_overrides JSONB DEFAULT '{}'::JSONB,
    
    -- AI Interaction Preferences
    explanation_detail_level TEXT DEFAULT 'balanced' CHECK (explanation_detail_level IN ('minimal', 'balanced', 'detailed')),
    show_confidence_scores BOOLEAN DEFAULT true,
    show_reasoning_path BOOLEAN DEFAULT true,
    ai_personality TEXT DEFAULT 'coach' CHECK (ai_personality IN ('coach', 'assistant', 'strategist', 'motivator')),
    ai_communication_style TEXT DEFAULT 'encouraging' CHECK (ai_communication_style IN ('direct', 'encouraging', 'analytical', 'socratic')),
    
    -- Optimization Preferences
    primary_optimization TEXT DEFAULT 'balance' CHECK (primary_optimization IN (
        'balance', 'focus', 'exploration', 'efficiency', 'wellbeing'
    )),
    
    -- Time and Energy Patterns
    preferred_work_hours JSONB DEFAULT '{"start": "09:00", "end": "17:00"}'::JSONB,
    energy_pattern TEXT DEFAULT 'steady' CHECK (energy_pattern IN ('morning_peak', 'afternoon_peak', 'evening_peak', 'steady')),
    
    -- Learning and Privacy
    enable_ai_learning BOOLEAN DEFAULT true,
    share_anonymous_insights BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_hrm_preferences_user ON hrm_user_preferences(user_id);

-- Row Level Security
ALTER TABLE hrm_user_preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own HRM preferences" 
ON hrm_user_preferences FOR ALL USING (auth.uid() = user_id);