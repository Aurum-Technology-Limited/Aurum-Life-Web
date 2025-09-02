
-- Execute this SQL in your Supabase SQL Editor for Sentiment Analysis:

-- Add sentiment analysis columns to journal_entries table
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS sentiment_category TEXT CHECK (sentiment_category IN ('very_positive', 'positive', 'neutral', 'negative', 'very_negative'));
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS sentiment_confidence DECIMAL(3,2) CHECK (sentiment_confidence >= 0 AND sentiment_confidence <= 1);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS emotional_keywords JSONB DEFAULT '[]';
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS emotional_themes JSONB DEFAULT '[]';
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS dominant_emotions JSONB DEFAULT '[]';
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS emotional_intensity DECIMAL(3,2) CHECK (emotional_intensity >= 0 AND emotional_intensity <= 1);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS sentiment_analysis_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS sentiment_analysis_version TEXT DEFAULT '1.0';

-- Create indexes for sentiment queries
CREATE INDEX IF NOT EXISTS idx_journal_entries_sentiment_score ON journal_entries (sentiment_score) WHERE sentiment_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_journal_entries_sentiment_category ON journal_entries (sentiment_category) WHERE sentiment_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_sentiment ON journal_entries (user_id, sentiment_score, created_at) WHERE sentiment_score IS NOT NULL;

-- Create sentiment utility functions
CREATE OR REPLACE FUNCTION get_sentiment_emoji(category TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN CASE category
        WHEN 'very_positive' THEN '😄'
        WHEN 'positive' THEN '😊'
        WHEN 'neutral' THEN '😐'
        WHEN 'negative' THEN '😞'
        WHEN 'very_negative' THEN '😢'
        ELSE '😐'
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

GRANT EXECUTE ON FUNCTION get_sentiment_emoji(TEXT) TO authenticated;

