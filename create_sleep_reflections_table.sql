-- Create sleep_reflections table for morning sleep tracking
CREATE TABLE IF NOT EXISTS sleep_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sleep_quality INTEGER NOT NULL CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
    feeling VARCHAR(50) NOT NULL,
    sleep_hours VARCHAR(50) NOT NULL,
    sleep_influences TEXT,
    today_intention TEXT,
    type VARCHAR(50) DEFAULT 'morning_sleep_reflection',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id and date for fast lookups
CREATE INDEX IF NOT EXISTS idx_sleep_reflections_user_date ON sleep_reflections(user_id, date DESC);

-- Create index on user_id for user queries
CREATE INDEX IF NOT EXISTS idx_sleep_reflections_user_id ON sleep_reflections(user_id);

-- Add RLS policies for sleep_reflections
ALTER TABLE sleep_reflections ENABLE ROW LEVEL SECURITY;

-- Users can only access their own sleep reflections
CREATE POLICY "Users can view their own sleep reflections" ON sleep_reflections
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own sleep reflections" ON sleep_reflections
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own sleep reflections" ON sleep_reflections
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own sleep reflections" ON sleep_reflections
    FOR DELETE USING (auth.uid() = user_id);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_sleep_reflections_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sleep_reflections_updated_at
    BEFORE UPDATE ON sleep_reflections
    FOR EACH ROW
    EXECUTE FUNCTION update_sleep_reflections_updated_at();