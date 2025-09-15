-- Migration 018: Analytics Preferences Extension
-- Extends user analytics preferences with new RAG and behavioral tracking options
-- Reference: aurum-life-impl-plan.md

-- Extend user_analytics_preferences with new behavioral tracking options
ALTER TABLE public.user_analytics_preferences
  ADD COLUMN IF NOT EXISTS track_pillar_metrics BOOLEAN DEFAULT true,
  ADD COLUMN IF NOT EXISTS record_rag_snippets BOOLEAN DEFAULT true,
  ADD COLUMN IF NOT EXISTS store_task_context BOOLEAN DEFAULT true,
  ADD COLUMN IF NOT EXISTS track_flow_states BOOLEAN DEFAULT true,
  ADD COLUMN IF NOT EXISTS store_behavioral_embeddings BOOLEAN DEFAULT true;

-- Add comments for new columns
COMMENT ON COLUMN public.user_analytics_preferences.track_pillar_metrics IS 'Allow collection of pillar-level behavioral metrics';
COMMENT ON COLUMN public.user_analytics_preferences.record_rag_snippets IS 'Allow storage of text snippets for RAG embedding generation';
COMMENT ON COLUMN public.user_analytics_preferences.store_task_context IS 'Allow storage of task context metadata for AI insights';
COMMENT ON COLUMN public.user_analytics_preferences.track_flow_states IS 'Allow tracking of flow state entry/exit events';
COMMENT ON COLUMN public.user_analytics_preferences.store_behavioral_embeddings IS 'Allow creation and storage of behavioral embeddings for personalization';