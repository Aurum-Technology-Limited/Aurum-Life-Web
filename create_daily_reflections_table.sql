-- Daily Reflections Table Creation for Aurum Life
-- This table supports the Daily Reflection feature of the AI Coach MVP

-- Create daily_reflections table
CREATE TABLE IF NOT EXISTS daily_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    reflection_date DATE NOT NULL DEFAULT CURRENT_DATE,
    reflection_text TEXT NOT NULL,
    completion_score INTEGER CHECK (completion_score >= 1 AND completion_score <= 10),
    mood VARCHAR(50),
    biggest_accomplishment TEXT,
    challenges_faced TEXT,
    tomorrow_focus TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add unique constraint to prevent multiple reflections per user per day
ALTER TABLE daily_reflections 
ADD CONSTRAINT unique_user_date UNIQUE (user_id, reflection_date);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_daily_reflections_user_date 
ON daily_reflections (user_id, reflection_date DESC);

CREATE INDEX IF NOT EXISTS idx_daily_reflections_date 
ON daily_reflections (reflection_date DESC);

-- Add daily_streak column to user_profiles table if it doesn't exist
-- This will track consecutive daily reflection streak
DO $$ 
BEGIN
    -- Check if daily_streak column exists in user_profiles table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_profiles' 
        AND column_name = 'daily_streak'
    ) THEN
        ALTER TABLE user_profiles 
        ADD COLUMN daily_streak INTEGER DEFAULT 0;
        
        -- Create index for daily_streak
        CREATE INDEX IF NOT EXISTS idx_user_profiles_daily_streak 
        ON user_profiles (daily_streak DESC);
    END IF;
END $$;

-- Add RLS (Row Level Security) policies for daily_reflections
ALTER TABLE daily_reflections ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own reflections
CREATE POLICY "Users can view own reflections" ON daily_reflections
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can only insert their own reflections
CREATE POLICY "Users can insert own reflections" ON daily_reflections
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can only update their own reflections
CREATE POLICY "Users can update own reflections" ON daily_reflections
    FOR UPDATE USING (auth.uid() = user_id);

-- Policy: Users can only delete their own reflections
CREATE POLICY "Users can delete own reflections" ON daily_reflections
    FOR DELETE USING (auth.uid() = user_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_daily_reflections_updated_at 
    BEFORE UPDATE ON daily_reflections 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert comment for documentation
COMMENT ON TABLE daily_reflections IS 'Stores daily reflection entries for AI Coach MVP feature';
COMMENT ON COLUMN daily_reflections.completion_score IS 'Daily completion score from 1-10';
COMMENT ON COLUMN daily_reflections.mood IS 'User mood description (e.g., optimistic, reflective, challenging)';
COMMENT ON COLUMN daily_reflections.reflection_date IS 'Date of the reflection (allows for backdated entries)';

-- Success message
SELECT 'Daily reflections table and related structures created successfully!' as result;