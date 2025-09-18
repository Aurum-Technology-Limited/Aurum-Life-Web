-- Sentiment Analysis Enhancement Migration
-- Migration: 012_add_sentiment_analysis.sql
-- Adds sentiment analysis fields to journal entries and daily reflections

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

-- Add sentiment analysis columns to daily_reflections table (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'daily_reflections') THEN
        ALTER TABLE daily_reflections ADD COLUMN IF NOT EXISTS sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1);
        ALTER TABLE daily_reflections ADD COLUMN IF NOT EXISTS sentiment_category TEXT CHECK (sentiment_category IN ('very_positive', 'positive', 'neutral', 'negative', 'very_negative'));
        ALTER TABLE daily_reflections ADD COLUMN IF NOT EXISTS sentiment_confidence DECIMAL(3,2) CHECK (sentiment_confidence >= 0 AND sentiment_confidence <= 1);
        ALTER TABLE daily_reflections ADD COLUMN IF NOT EXISTS emotional_keywords JSONB DEFAULT '[]';
        ALTER TABLE daily_reflections ADD COLUMN IF NOT EXISTS emotional_themes JSONB DEFAULT '[]';
        ALTER TABLE daily_reflections ADD COLUMN IF NOT EXISTS sentiment_analysis_date TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Create emotional insights tracking table
CREATE TABLE IF NOT EXISTS emotional_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    insight_type TEXT NOT NULL CHECK (insight_type IN ('trend_analysis', 'activity_correlation', 'emotional_pattern', 'mood_prediction', 'wellness_alert')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    insight_data JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    date_range_start TIMESTAMP WITH TIME ZONE NOT NULL,
    date_range_end TIMESTAMP WITH TIME ZONE NOT NULL,
    related_entries JSONB DEFAULT '[]',  -- Array of journal entry IDs
    actionable_suggestions JSONB DEFAULT '[]',  -- Array of suggestion strings
    is_active BOOLEAN DEFAULT true,
    created_by_system BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_emotional_insights_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create activity sentiment correlation tracking table
CREATE TABLE IF NOT EXISTS activity_sentiment_correlations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('pillar', 'area', 'project', 'task')),
    activity_id UUID NOT NULL,
    activity_name TEXT NOT NULL,
    average_sentiment DECIMAL(3,2) CHECK (average_sentiment >= -1 AND average_sentiment <= 1),
    entry_count INTEGER DEFAULT 0,
    sentiment_trend JSONB DEFAULT '[]',  -- Array of recent sentiment scores
    emotional_impact_score DECIMAL(3,2) CHECK (emotional_impact_score >= 0 AND emotional_impact_score <= 1),
    insights JSONB DEFAULT '[]',  -- Array of insight strings
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_activity_correlations_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Unique constraint - one correlation per user-activity combination
    UNIQUE(user_id, activity_type, activity_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_journal_entries_sentiment_score ON journal_entries (sentiment_score) WHERE sentiment_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_journal_entries_sentiment_category ON journal_entries (sentiment_category) WHERE sentiment_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_journal_entries_sentiment_analysis_date ON journal_entries (sentiment_analysis_date) WHERE sentiment_analysis_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_sentiment ON journal_entries (user_id, sentiment_score, created_at) WHERE sentiment_score IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_emotional_insights_user ON emotional_insights (user_id);
CREATE INDEX IF NOT EXISTS idx_emotional_insights_type ON emotional_insights (insight_type);
CREATE INDEX IF NOT EXISTS idx_emotional_insights_date_range ON emotional_insights (date_range_start, date_range_end);
CREATE INDEX IF NOT EXISTS idx_emotional_insights_active ON emotional_insights (is_active);

CREATE INDEX IF NOT EXISTS idx_activity_correlations_user ON activity_sentiment_correlations (user_id);
CREATE INDEX IF NOT EXISTS idx_activity_correlations_activity ON activity_sentiment_correlations (activity_type, activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_correlations_impact ON activity_sentiment_correlations (emotional_impact_score DESC);

-- Create view for sentiment analytics
CREATE VIEW sentiment_analytics AS
SELECT 
    je.user_id,
    DATE(je.created_at) as entry_date,
    COUNT(*) as entries_count,
    AVG(je.sentiment_score) as avg_sentiment,
    AVG(je.sentiment_confidence) as avg_confidence,
    AVG(je.emotional_intensity) as avg_intensity,
    MODE() WITHIN GROUP (ORDER BY je.sentiment_category) as dominant_category,
    STRING_AGG(DISTINCT unnested_keywords.keyword, ', ') as common_keywords
FROM journal_entries je
LEFT JOIN LATERAL jsonb_array_elements_text(je.emotional_keywords) as unnested_keywords(keyword) ON true
WHERE je.sentiment_score IS NOT NULL
  AND je.deleted = false
GROUP BY je.user_id, DATE(je.created_at);

-- Create view for emotional wellness tracking
CREATE VIEW emotional_wellness_dashboard AS
SELECT 
    je.user_id,
    COUNT(DISTINCT DATE(je.created_at)) as active_days,
    COUNT(*) as total_analyzed_entries,
    AVG(je.sentiment_score) as average_sentiment,
    STDDEV(je.sentiment_score) as sentiment_variability,
    COUNT(*) FILTER (WHERE je.sentiment_category IN ('positive', 'very_positive'))::FLOAT / COUNT(*) as positive_ratio,
    COUNT(*) FILTER (WHERE je.sentiment_category IN ('negative', 'very_negative'))::FLOAT / COUNT(*) as negative_ratio,
    AVG(je.emotional_intensity) as average_emotional_intensity,
    MAX(je.created_at) as last_entry_date,
    MIN(je.created_at) as first_analyzed_entry
FROM journal_entries je
WHERE je.sentiment_score IS NOT NULL
  AND je.deleted = false
  AND je.created_at >= NOW() - INTERVAL '90 days'  -- Last 3 months
GROUP BY je.user_id;

-- Enable Row Level Security for new tables
ALTER TABLE emotional_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_sentiment_correlations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for emotional_insights
CREATE POLICY "Users can manage their own emotional insights" 
ON emotional_insights FOR ALL 
USING (auth.uid() = user_id);

-- RLS Policies for activity_sentiment_correlations  
CREATE POLICY "Users can manage their own activity correlations" 
ON activity_sentiment_correlations FOR ALL 
USING (auth.uid() = user_id);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON emotional_insights TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON activity_sentiment_correlations TO authenticated;
GRANT SELECT ON sentiment_analytics TO authenticated;
GRANT SELECT ON emotional_wellness_dashboard TO authenticated;

-- Add update triggers for updated_at columns
CREATE TRIGGER update_emotional_insights_updated_at 
    BEFORE UPDATE ON emotional_insights 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activity_correlations_updated_at 
    BEFORE UPDATE ON activity_sentiment_correlations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE emotional_insights IS 'AI-generated emotional insights based on sentiment analysis patterns';
COMMENT ON TABLE activity_sentiment_correlations IS 'Correlations between user activities and emotional outcomes';
COMMENT ON VIEW sentiment_analytics IS 'Daily aggregated sentiment analytics for dashboard reporting';
COMMENT ON VIEW emotional_wellness_dashboard IS 'Comprehensive emotional wellness metrics for users';

COMMENT ON COLUMN journal_entries.sentiment_score IS 'AI-generated sentiment score from -1 (very negative) to 1 (very positive)';
COMMENT ON COLUMN journal_entries.sentiment_category IS 'Human-readable sentiment category for UI display';
COMMENT ON COLUMN journal_entries.emotional_keywords IS 'Key emotional words detected by AI analysis';
COMMENT ON COLUMN journal_entries.emotional_themes IS 'Major emotional themes identified in the entry';
COMMENT ON COLUMN journal_entries.emotional_intensity IS 'Intensity of emotional expression (0-1)';

-- Create function to get sentiment emoji
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

-- Create function to get sentiment color
CREATE OR REPLACE FUNCTION get_sentiment_color(category TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN CASE category
        WHEN 'very_positive' THEN '#10B981'
        WHEN 'positive' THEN '#34D399'
        WHEN 'neutral' THEN '#6B7280'
        WHEN 'negative' THEN '#F59E0B'
        WHEN 'very_negative' THEN '#EF4444'
        ELSE '#6B7280'
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION get_sentiment_emoji(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_sentiment_color(TEXT) TO authenticated;