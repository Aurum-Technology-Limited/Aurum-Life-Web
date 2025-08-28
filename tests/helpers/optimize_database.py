#!/usr/bin/env python3
"""
Database optimization script - Add indexes for better performance
"""

import asyncio
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('.env')

async def create_performance_indexes():
    """Create database indexes for better query performance"""
    
    try:
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not service_key:
            print("❌ Supabase credentials not found")
            return
            
        supabase: Client = create_client(url, service_key)
        
        # Create indexes for better performance
        index_queries = [
            # User-based indexes for fast lookups
            "CREATE INDEX IF NOT EXISTS idx_pillars_user_id ON public.pillars(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_areas_user_id ON public.areas(user_id);", 
            "CREATE INDEX IF NOT EXISTS idx_projects_user_id ON public.projects(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON public.tasks(user_id);",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON public.tasks(user_id, completed);",
            "CREATE INDEX IF NOT EXISTS idx_areas_user_archived ON public.areas(user_id, archived);",
            "CREATE INDEX IF NOT EXISTS idx_projects_user_archived ON public.projects(user_id, archived);",
            "CREATE INDEX IF NOT EXISTS idx_pillars_user_archived ON public.pillars(user_id, archived);",
            
            # Indexes for joins
            "CREATE INDEX IF NOT EXISTS idx_areas_pillar_id ON public.areas(pillar_id);",
            "CREATE INDEX IF NOT EXISTS idx_projects_area_id ON public.projects(area_id);",
            "CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON public.tasks(project_id);",
        ]
        
        print("🚀 Creating database indexes for performance optimization...")
        
        for query in index_queries:
            try:
                result = supabase.rpc('exec_sql', {'sql': query}).execute()
                index_name = query.split('idx_')[1].split(' ')[0] if 'idx_' in query else 'unknown'
                print(f"✅ Created index: {index_name}")
            except Exception as e:
                print(f"⚠️ Index creation skipped (may already exist): {e}")
        
        print("🚀 Database optimization completed!")
        
    except Exception as e:
        print(f"❌ Database optimization failed: {e}")

if __name__ == "__main__":
    asyncio.run(create_performance_indexes())