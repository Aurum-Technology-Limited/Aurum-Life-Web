-- Migration 017: Behavioral Metrics Enhancement
-- Adds time-series behavioral data to pillars and areas
-- Reference: aurum-life-impl-plan.md

-- Add JSONB fields to store time-series behavioral metrics
ALTER TABLE public.pillars
  ADD COLUMN IF NOT EXISTS behavior_metrics JSONB DEFAULT '[]'::JSONB;

ALTER TABLE public.areas
  ADD COLUMN IF NOT EXISTS behavior_metrics JSONB DEFAULT '[]'::JSONB;

-- Add task metadata tracking
ALTER TABLE public.tasks
  ADD COLUMN IF NOT EXISTS task_metadata JSONB DEFAULT '{}'::JSONB;

-- Extend user_behavior_events for flow state tracking
ALTER TABLE public.user_behavior_events
  ADD COLUMN IF NOT EXISTS flow_state_event BOOLEAN DEFAULT FALSE;

-- Update existing event_data column if it doesn't exist
-- (Note: This column might already exist in newer schema versions)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_behavior_events' AND column_name='event_data') THEN
        ALTER TABLE public.user_behavior_events ADD COLUMN event_data JSONB DEFAULT '{}'::JSONB;
    END IF;
END $$;

-- Create indexes for JSONB behavioral metrics
CREATE INDEX IF NOT EXISTS idx_pillars_behavior_metrics
ON public.pillars USING GIN (behavior_metrics);

CREATE INDEX IF NOT EXISTS idx_areas_behavior_metrics
ON public.areas USING GIN (behavior_metrics);

CREATE INDEX IF NOT EXISTS idx_tasks_metadata
ON public.tasks USING GIN (task_metadata);

CREATE INDEX IF NOT EXISTS idx_behavior_events_flow_state
ON public.user_behavior_events (user_id, flow_state_event, timestamp)
WHERE flow_state_event = true;

-- Add comments for documentation
COMMENT ON COLUMN public.pillars.behavior_metrics IS 'Time-series behavioral data: [{timestamp, alignment_score, sentiment, habit_strength, energy_level}]';
COMMENT ON COLUMN public.areas.behavior_metrics IS 'Time-series behavioral data: [{timestamp, alignment_score, sentiment, habit_strength, focus_time}]';
COMMENT ON COLUMN public.tasks.task_metadata IS 'Context metadata: {energy_requirement, context_tags, switching_delays, cognitive_load}';
COMMENT ON COLUMN public.user_behavior_events.flow_state_event IS 'Indicates if this event represents flow state entry/exit';
COMMENT ON COLUMN public.user_behavior_events.event_data IS 'Event-specific data: flow states, procrastination triggers, context switches';