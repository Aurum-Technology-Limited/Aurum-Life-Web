-- HRM Phase 3: Enhance Existing Tables with HRM Fields
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.2

-- Add HRM fields to tasks table
ALTER TABLE public.tasks 
ADD COLUMN IF NOT EXISTS hrm_priority_score DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS hrm_reasoning_summary TEXT,
ADD COLUMN IF NOT EXISTS hrm_last_analyzed TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS ai_suggested_timeblock TEXT,
ADD COLUMN IF NOT EXISTS obstacle_risk TEXT CHECK (obstacle_risk IN ('low', 'medium', 'high'));

-- Performance index for HRM task queries
CREATE INDEX IF NOT EXISTS idx_tasks_hrm_priority 
ON tasks(user_id, completed, hrm_priority_score DESC NULLS LAST) 
WHERE completed = false;

-- Add HRM fields to projects table
ALTER TABLE public.projects 
ADD COLUMN IF NOT EXISTS hrm_health_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS hrm_predicted_completion DATE,
ADD COLUMN IF NOT EXISTS hrm_risk_factors JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS goal_coherence_score DECIMAL(3,2);

-- Add HRM fields to areas table
ALTER TABLE public.areas 
ADD COLUMN IF NOT EXISTS time_allocation_actual DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS time_allocation_recommended DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS balance_score DECIMAL(3,2);

-- Add HRM fields to pillars table
ALTER TABLE public.pillars 
ADD COLUMN IF NOT EXISTS vision_statement TEXT,
ADD COLUMN IF NOT EXISTS success_metrics JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS alignment_strength DECIMAL(3,2);

-- Add indexes for enhanced queries
CREATE INDEX IF NOT EXISTS idx_projects_health_score ON projects(user_id, hrm_health_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_areas_balance_score ON areas(user_id, balance_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_pillars_alignment ON pillars(user_id, alignment_strength DESC NULLS LAST);