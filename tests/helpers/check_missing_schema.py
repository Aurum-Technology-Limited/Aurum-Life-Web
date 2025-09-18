#!/usr/bin/env python3
"""
Add missing tables and fix schema issues
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from supabase_client import supabase_manager

async def create_missing_tables():
    """Create missing tables that are referenced in the code"""
    try:
        client = supabase_manager.get_client()
        
        # Check if user_course_progress table exists
        try:
            result = client.table('user_course_progress').select('*').limit(1).execute()
            print("✅ user_course_progress table already exists")
        except Exception:
            print("Creating user_course_progress table...")
            # Since we can't execute DDL directly, create it through data insertion approach
            # This table is referenced in the code but doesn't exist
            print("❌ Cannot create table - need manual schema update")
        
        # Check if user_badges table exists  
        try:
            result = client.table('user_badges').select('*').limit(1).execute()
            print("✅ user_badges table already exists")
        except Exception:
            print("Creating user_badges table...")
            print("❌ Cannot create table - need manual schema update")
            
        # Check if tasks table has archived column
        try:
            result = client.table('tasks').select('archived').limit(1).execute()
            print("✅ tasks.archived column exists")
        except Exception as e:
            print(f"❌ tasks.archived column missing: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_missing_tables())