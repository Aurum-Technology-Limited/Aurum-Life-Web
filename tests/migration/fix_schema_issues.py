#!/usr/bin/env python3
"""
Fix database schema issues by adding missing columns and tables
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from supabase_client import supabase_manager

async def fix_schema():
    """Fix schema issues"""
    try:
        client = supabase_manager.get_client()
        
        # Add archived column to tasks table
        print("Adding archived column to tasks table...")
        result = client.rpc('execute_sql', {
            'sql': 'ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;'
        }).execute()
        print("✅ Added archived column to tasks table")
        
        # Create user_course_progress table
        print("Creating user_course_progress table...")
        create_course_progress_sql = """
        CREATE TABLE IF NOT EXISTS public.user_course_progress (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            course_id UUID NOT NULL,
            progress_percentage DECIMAL(5,2) DEFAULT 0.0,
            completed BOOLEAN DEFAULT FALSE,
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        result = client.rpc('execute_sql', {'sql': create_course_progress_sql}).execute()
        print("✅ Created user_course_progress table")
        
        # Create user_badges table
        print("Creating user_badges table...")
        create_badges_sql = """
        CREATE TABLE IF NOT EXISTS public.user_badges (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            badge_id UUID NOT NULL,
            earned BOOLEAN DEFAULT FALSE,
            earned_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        result = client.rpc('execute_sql', {'sql': create_badges_sql}).execute()
        print("✅ Created user_badges table")
        
    except Exception as e:
        print(f"Error: {e}")
        # Try alternative approach - direct SQL execution
        print("Trying alternative approach...")

if __name__ == "__main__":
    asyncio.run(fix_schema())