-- Create table for tracking username changes
CREATE TABLE IF NOT EXISTS username_change_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    old_username TEXT NOT NULL DEFAULT '',
    new_username TEXT NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_username_change_records_user_id ON username_change_records(user_id);
CREATE INDEX IF NOT EXISTS idx_username_change_records_changed_at ON username_change_records(changed_at);
CREATE INDEX IF NOT EXISTS idx_username_change_records_user_changed_at ON username_change_records(user_id, changed_at);

-- Add Row Level Security (RLS)
ALTER TABLE username_change_records ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own username change records
CREATE POLICY "Users can view their own username changes" ON username_change_records
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Policy: System can insert username change records (no user policy for INSERT to allow backend service to work)
CREATE POLICY "System can insert username changes" ON username_change_records
    FOR INSERT WITH CHECK (true);

-- Grant necessary permissions
GRANT SELECT, INSERT ON username_change_records TO authenticated;
GRANT SELECT, INSERT ON username_change_records TO service_role;

-- Add a comment to explain the table's purpose
COMMENT ON TABLE username_change_records IS 'Tracks username changes to enforce 7-day rate limiting';
COMMENT ON COLUMN username_change_records.user_id IS 'Reference to the user who changed their username';
COMMENT ON COLUMN username_change_records.old_username IS 'The previous username before the change';
COMMENT ON COLUMN username_change_records.new_username IS 'The new username after the change';
COMMENT ON COLUMN username_change_records.changed_at IS 'Timestamp when the username was changed';
COMMENT ON COLUMN username_change_records.ip_address IS 'IP address from which the change was made (optional)';