#!/usr/bin/env python3
"""
Manual Analytics Migration Script
Execute SQL statements one by one for better control
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_supabase_client():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)

def create_analytics_tables():
    """Create analytics tables step by step"""
    supabase = get_supabase_client()
    
    logger.info("🔧 Creating User Analytics Preferences table...")
    try:
        # User Analytics Preferences Table
        supabase.table('user_analytics_preferences').select('*').limit(1).execute()
        logger.info("✅ user_analytics_preferences table already exists")
    except:
        # Create table using direct SQL
        create_preferences_sql = """
        CREATE TABLE user_analytics_preferences (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            analytics_consent BOOLEAN DEFAULT true,
            ai_behavior_tracking BOOLEAN DEFAULT true,
            performance_tracking BOOLEAN DEFAULT true,
            error_reporting BOOLEAN DEFAULT true,
            data_retention_days INTEGER DEFAULT 365,
            anonymize_after_days INTEGER DEFAULT 90,
            track_ai_insights_usage BOOLEAN DEFAULT true,
            track_ai_actions_usage BOOLEAN DEFAULT true,
            track_goal_planner_usage BOOLEAN DEFAULT true,
            track_navigation_patterns BOOLEAN DEFAULT true,
            track_search_queries BOOLEAN DEFAULT false,
            share_anonymous_stats BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # You'll need to execute this in Supabase SQL Editor
        print("\n" + "="*80)
        print("STEP 1: Execute this SQL in your Supabase SQL Editor:")
        print("="*80)
        print(create_preferences_sql)
        
    logger.info("🔧 Creating User Sessions table...")
    try:
        supabase.table('user_sessions').select('*').limit(1).execute()
        logger.info("✅ user_sessions table already exists")
    except:
        create_sessions_sql = """
        CREATE TABLE user_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            session_id TEXT NOT NULL,
            start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            end_time TIMESTAMP WITH TIME ZONE,
            duration_ms INTEGER,
            is_active BOOLEAN DEFAULT true,
            entry_page TEXT,
            exit_page TEXT,
            page_views INTEGER DEFAULT 0,
            ai_interactions INTEGER DEFAULT 0,
            feature_usages INTEGER DEFAULT 0,
            user_agent TEXT,
            screen_resolution TEXT,
            timezone TEXT,
            device_type TEXT,
            consent_given BOOLEAN DEFAULT true,
            is_anonymized BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        print("\n" + "="*80)
        print("STEP 2: Execute this SQL in your Supabase SQL Editor:")
        print("="*80)
        print(create_sessions_sql)
        
    logger.info("🔧 Creating User Behavior Events table...")
    try:
        supabase.table('user_behavior_events').select('*').limit(1).execute()
        logger.info("✅ user_behavior_events table already exists")
    except:
        create_events_sql = """
        CREATE TABLE user_behavior_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            session_id TEXT NOT NULL,
            action_type TEXT NOT NULL CHECK (action_type IN ('page_view', 'ai_interaction', 'feature_usage', 'task_action', 'project_action', 'navigation', 'search', 'insight_feedback')),
            feature_name TEXT NOT NULL,
            ai_feature_type TEXT CHECK (ai_feature_type IN ('my_ai_insights', 'ai_quick_actions', 'goal_planner', 'semantic_search', 'hrm_analysis')),
            event_data JSONB DEFAULT '{}',
            duration_ms INTEGER,
            success BOOLEAN DEFAULT true,
            error_message TEXT,
            page_url TEXT,
            referrer_url TEXT,
            user_agent TEXT,
            screen_resolution TEXT,
            timezone TEXT,
            is_anonymized BOOLEAN DEFAULT false,
            consent_given BOOLEAN DEFAULT true,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            client_timestamp TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        print("\n" + "="*80)
        print("STEP 3: Execute this SQL in your Supabase SQL Editor:")
        print("="*80)
        print(create_events_sql)
    
    # Create indexes
    indexes_sql = """
    -- Indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id);
    CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions (session_id);
    CREATE INDEX IF NOT EXISTS idx_behavior_events_user_id ON user_behavior_events (user_id);
    CREATE INDEX IF NOT EXISTS idx_behavior_events_session_id ON user_behavior_events (session_id);
    CREATE INDEX IF NOT EXISTS idx_behavior_events_timestamp ON user_behavior_events (timestamp);
    CREATE INDEX IF NOT EXISTS idx_behavior_events_ai_feature ON user_behavior_events (ai_feature_type) WHERE ai_feature_type IS NOT NULL;
    """
    
    print("\n" + "="*80)
    print("STEP 4: Execute these indexes in your Supabase SQL Editor:")
    print("="*80)
    print(indexes_sql)
    
    # RLS Policies
    rls_sql = """
    -- Enable Row Level Security
    ALTER TABLE user_analytics_preferences ENABLE ROW LEVEL SECURITY;
    ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;  
    ALTER TABLE user_behavior_events ENABLE ROW LEVEL SECURITY;
    
    -- RLS Policies for user_analytics_preferences
    CREATE POLICY "Users can manage their own analytics preferences" 
    ON user_analytics_preferences FOR ALL 
    USING (auth.uid() = user_id);
    
    -- RLS Policies for user_sessions
    CREATE POLICY "Users can manage their own sessions" 
    ON user_sessions FOR ALL 
    USING (auth.uid() = user_id);
    
    -- RLS Policies for user_behavior_events  
    CREATE POLICY "Users can manage their own behavior events" 
    ON user_behavior_events FOR ALL 
    USING (auth.uid() = user_id);
    """
    
    print("\n" + "="*80)
    print("STEP 5: Execute RLS policies in your Supabase SQL Editor:")
    print("="*80)
    print(rls_sql)
    
    print("\n" + "="*80)
    print("🎉 MANUAL MIGRATION INSTRUCTIONS COMPLETE!")
    print("Execute all 5 SQL blocks in your Supabase SQL Editor")
    print("="*80)

if __name__ == "__main__":
    create_analytics_tables()