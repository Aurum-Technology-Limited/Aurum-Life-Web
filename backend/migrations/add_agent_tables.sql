-- Multi-Agent System Tables for Aurum Life
-- Add support for agent orchestration and workflow management

-- Validation Results table for Market Validation Agent
CREATE TABLE IF NOT EXISTS public.validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis TEXT NOT NULL,
    status TEXT CHECK (status IN ('validated', 'invalidated', 'needs_more_data')),
    confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
    evidence JSONB DEFAULT '[]'::jsonb,
    insights JSONB DEFAULT '[]'::jsonb,
    next_steps JSONB DEFAULT '[]'::jsonb,
    validation_method TEXT,
    full_analysis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Registry table
CREATE TABLE IF NOT EXISTS public.agent_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT UNIQUE NOT NULL,
    agent_type TEXT NOT NULL,
    agent_state TEXT DEFAULT 'initializing',
    capabilities JSONB DEFAULT '[]'::jsonb,
    configuration JSONB DEFAULT '{}'::jsonb,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Messages table for audit trail
CREATE TABLE IF NOT EXISTS public.agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id TEXT UNIQUE NOT NULL,
    source_agent TEXT NOT NULL,
    target_agent TEXT,
    message_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    correlation_id TEXT,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'pending',
    error_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Workflow Definitions table
CREATE TABLE IF NOT EXISTS public.workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    agent_sequence JSONB NOT NULL, -- Array of agent IDs in order
    configuration JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow Executions table
CREATE TABLE IF NOT EXISTS public.workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL REFERENCES public.workflow_definitions(workflow_id),
    execution_id TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'started',
    current_agent TEXT,
    input_data JSONB,
    output_data JSONB,
    error_details TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER
);

-- Agent Performance Metrics table
CREATE TABLE IF NOT EXISTS public.agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    metric_value DECIMAL,
    metadata JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_validation_results_hypothesis ON public.validation_results(hypothesis);
CREATE INDEX idx_validation_results_status ON public.validation_results(status);
CREATE INDEX idx_validation_results_created_at ON public.validation_results(created_at);

CREATE INDEX idx_agent_registry_agent_id ON public.agent_registry(agent_id);
CREATE INDEX idx_agent_registry_agent_type ON public.agent_registry(agent_type);
CREATE INDEX idx_agent_registry_agent_state ON public.agent_registry(agent_state);

CREATE INDEX idx_agent_messages_source_agent ON public.agent_messages(source_agent);
CREATE INDEX idx_agent_messages_target_agent ON public.agent_messages(target_agent);
CREATE INDEX idx_agent_messages_correlation_id ON public.agent_messages(correlation_id);
CREATE INDEX idx_agent_messages_created_at ON public.agent_messages(created_at);

CREATE INDEX idx_workflow_executions_workflow_id ON public.workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_status ON public.workflow_executions(status);
CREATE INDEX idx_workflow_executions_started_at ON public.workflow_executions(started_at);

CREATE INDEX idx_agent_metrics_agent_id ON public.agent_metrics(agent_id);
CREATE INDEX idx_agent_metrics_metric_type ON public.agent_metrics(metric_type);
CREATE INDEX idx_agent_metrics_recorded_at ON public.agent_metrics(recorded_at);

-- Add RLS policies
ALTER TABLE public.validation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_metrics ENABLE ROW LEVEL SECURITY;

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_validation_results_updated_at BEFORE UPDATE ON public.validation_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_agent_registry_updated_at BEFORE UPDATE ON public.agent_registry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_workflow_definitions_updated_at BEFORE UPDATE ON public.workflow_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();