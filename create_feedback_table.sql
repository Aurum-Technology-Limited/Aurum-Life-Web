-- Create feedback table for user feedback and support system
-- This table stores all user feedback, support requests, and bug reports

CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    user_email TEXT NOT NULL,
    user_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('suggestion', 'bug_report', 'feature_request', 'question', 'complaint', 'compliment')),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    
    -- Status tracking
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    admin_response TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT,
    
    -- Email tracking
    email_sent BOOLEAN DEFAULT FALSE,
    email_sent_at TIMESTAMPTZ,
    email_error TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
CREATE INDEX IF NOT EXISTS idx_feedback_priority ON feedback(priority);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);

-- Create updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_feedback_updated_at ON feedback;
CREATE TRIGGER update_feedback_updated_at 
    BEFORE UPDATE ON feedback 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for multi-tenant isolation
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own feedback
CREATE POLICY "Users can view their own feedback" ON feedback
    FOR SELECT USING (auth.uid()::TEXT = user_id::TEXT);

-- Users can only create feedback with their own user_id
CREATE POLICY "Users can create their own feedback" ON feedback
    FOR INSERT WITH CHECK (auth.uid()::TEXT = user_id::TEXT);

-- Users can update their own feedback (for status updates)
CREATE POLICY "Users can update their own feedback" ON feedback
    FOR UPDATE USING (auth.uid()::TEXT = user_id::TEXT);

-- Admin policy would be added separately with service role access
-- Admins (using service role) can view and update all feedback
-- This is handled through the service role key in the backend

COMMENT ON TABLE feedback IS 'Stores user feedback, support requests, and bug reports with email notification tracking';
COMMENT ON COLUMN feedback.category IS 'Type of feedback: suggestion, bug_report, feature_request, question, complaint, compliment';
COMMENT ON COLUMN feedback.priority IS 'Priority level: low, medium, high, urgent';
COMMENT ON COLUMN feedback.status IS 'Current status: open, in_progress, resolved, closed';
COMMENT ON COLUMN feedback.email_sent IS 'Whether notification email was successfully sent';
COMMENT ON COLUMN feedback.email_error IS 'Error message if email sending failed';