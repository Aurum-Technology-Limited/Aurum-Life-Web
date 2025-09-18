-- HRM Phase 3: Seed Initial HRM Rules
-- Reference: aurum_life_hrm_phase3_prd.md - Section 6.1

INSERT INTO public.hrm_rules (rule_code, rule_name, description, hierarchy_level, applies_to_entity_types, rule_type, rule_config, base_weight, requires_llm) VALUES

-- Temporal Rules
('TEMPORAL_URGENCY_001', 'Task Deadline Urgency', 'Scores tasks based on deadline proximity with exponential scaling for overdue items', 'task', ARRAY['task'], 'temporal', 
 '{"conditions": {"overdue_multiplier": 2.0, "due_today_boost": 0.8, "due_tomorrow_boost": 0.4}, "thresholds": {"critical_hours": 6, "urgent_hours": 24}}'::jsonb, 
 0.8, false),

('TEMPORAL_MORNING_PEAK_001', 'Morning Energy Optimization', 'Boosts complex tasks during user morning peak hours', 'task', ARRAY['task'], 'temporal',
 '{"time_windows": {"peak_start": "07:00", "peak_end": "10:00"}, "task_types": {"deep_work": 0.3, "creative": 0.25, "planning": 0.2}}'::jsonb,
 0.5, false),

-- Alignment Rules  
('PILLAR_ALIGNMENT_001', 'Pillar Importance Scoring', 'Scores entities based on pillar alignment and time allocation preferences', 'cross_level', ARRAY['task', 'project', 'area'], 'scoring',
 '{"factors": ["pillar_time_allocation", "area_importance", "project_priority"], "aggregation": "weighted_average", "time_allocation_weight": 0.4}'::jsonb,
 0.9, false),

('GOAL_COHERENCE_001', 'Goal Coherence Analysis', 'Analyzes conflicts and synergies between goals across hierarchy', 'cross_level', ARRAY['project', 'area'], 'relationship',
 '{"conflict_penalty": -0.3, "synergy_boost": 0.2, "coherence_threshold": 0.7}'::jsonb,
 0.6, true),

-- Dependency and Constraint Rules
('DEPENDENCY_CHECK_001', 'Task Dependency Analysis', 'Analyzes and scores based on dependency status and blocking relationships', 'task', ARRAY['task'], 'constraint',
 '{"blocking_penalty": -0.8, "ready_boost": 0.3, "cascade_analysis": true}'::jsonb,
 0.7, false),

('PROGRESS_MOMENTUM_001', 'Project Progress Momentum', 'Boosts tasks in projects showing good momentum, penalizes stalled projects', 'project', ARRAY['task', 'project'], 'pattern_matching',
 '{"momentum_factors": ["recent_completions", "timeline_adherence", "team_velocity"], "boost_threshold": 0.75, "stall_penalty": -0.4}'::jsonb,
 0.5, true),

-- Energy and Context Rules
('ENERGY_PATTERN_001', 'Energy-Based Task Matching', 'Matches task complexity to user energy patterns throughout the day', 'task', ARRAY['task'], 'temporal',
 '{"energy_mapping": {"deep_work": ["morning_peak"], "admin": ["afternoon"], "creative": ["evening_peak"], "routine": ["any"]}, "complexity_analysis": true}'::jsonb,
 0.6, true),

('CONTEXT_SWITCHING_001', 'Context Switch Penalty', 'Applies penalty for frequent context switching between different areas', 'cross_level', ARRAY['task'], 'scoring',
 '{"switch_penalty": -0.2, "focus_bonus": 0.15, "area_grouping_preferred": true}'::jsonb,
 0.4, false),

-- Wellbeing Rules
('WORKLIFE_BALANCE_001', 'Work-Life Balance Monitor', 'Monitors and adjusts for healthy work-life balance', 'cross_level', ARRAY['area', 'project'], 'pattern_matching',
 '{"balance_targets": {"work": 0.6, "health": 0.2, "relationships": 0.15, "personal": 0.05}, "imbalance_penalty": -0.5}'::jsonb,
 0.5, true),

-- Learning Rules
('SKILL_DEVELOPMENT_001', 'Skill Development Priority', 'Prioritizes tasks that develop important skills', 'task', ARRAY['task', 'project'], 'scoring',
 '{"skill_categories": ["technical", "leadership", "communication", "domain_knowledge"], "development_boost": 0.25}'::jsonb,
 0.4, true)

ON CONFLICT (rule_code) DO UPDATE SET
    rule_name = EXCLUDED.rule_name,
    description = EXCLUDED.description,
    rule_config = EXCLUDED.rule_config,
    base_weight = EXCLUDED.base_weight,
    requires_llm = EXCLUDED.requires_llm,
    updated_at = NOW();