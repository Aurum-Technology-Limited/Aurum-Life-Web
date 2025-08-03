-- AI Interactions Tracking Table
-- Tracks AI Coach interactions for quota management

CREATE TABLE IF NOT EXISTS ai_interactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('goal_decomposition', 'weekly_review', 'obstacle_analysis')),
    context_size INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_id ON ai_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_created_at ON ai_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_month ON ai_interactions(user_id, created_at);

-- Enable RLS (Row Level Security)
ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY;

-- Create RLS policy - users can only access their own AI interaction records
CREATE POLICY "Users can view their own AI interactions" ON ai_interactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own AI interactions" ON ai_interactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_interactions_updated_at 
    BEFORE UPDATE ON ai_interactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();