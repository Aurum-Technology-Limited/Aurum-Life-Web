-- HRM Phase 3: Rules Engine Table
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.2

CREATE TABLE IF NOT EXISTS public.hrm_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Rule Identity
    rule_code TEXT UNIQUE NOT NULL, -- e.g., 'PILLAR_ALIGNMENT_001'
    rule_name TEXT NOT NULL,
    description TEXT NOT NULL,
    
    -- Hierarchy Configuration
    hierarchy_level TEXT NOT NULL CHECK (hierarchy_level IN ('pillar', 'area', 'project', 'task', 'cross_level')),
    applies_to_entity_types TEXT[] NOT NULL, -- Which entities this rule evaluates
    
    -- Rule Logic
    rule_type TEXT NOT NULL CHECK (rule_type IN (
        'scoring',           -- Affects priority scores
        'filtering',         -- Filters entities
        'relationship',      -- Analyzes relationships
        'temporal',          -- Time-based rules
        'constraint',        -- Enforces constraints
        'pattern_matching'   -- Pattern detection
    )),
    
    -- Configuration
    rule_config JSONB NOT NULL,
    
    -- Weights and Scoring
    base_weight DECIMAL(3,2) DEFAULT 0.5 CHECK (base_weight >= 0 AND base_weight <= 1),
    user_adjustable BOOLEAN DEFAULT false,
    
    -- LLM Integration
    requires_llm BOOLEAN DEFAULT false,
    llm_prompt_template TEXT,
    
    -- Management
    is_active BOOLEAN DEFAULT true,
    is_system_rule BOOLEAN DEFAULT true, -- System rules can't be deleted
    created_by TEXT DEFAULT 'system',
    
    -- Versioning
    version INTEGER DEFAULT 1,
    changelog JSONB DEFAULT '[]'::JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_hrm_rules_active ON hrm_rules(is_active, hierarchy_level);
CREATE INDEX IF NOT EXISTS idx_hrm_rules_entity_types ON hrm_rules USING GIN (applies_to_entity_types);

-- Row Level Security (system-wide readable, admin-only writable)
ALTER TABLE hrm_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can read HRM rules" 
ON hrm_rules FOR SELECT USING (true);
CREATE POLICY "Only system can manage HRM rules" 
ON hrm_rules FOR ALL USING (false);