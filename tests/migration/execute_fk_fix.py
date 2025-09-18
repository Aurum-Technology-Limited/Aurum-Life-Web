#!/usr/bin/env python3
"""
Foreign Key Constraint Fix Script
Execute the SQL migration to fix foreign key constraints to reference public.users instead of auth.users
"""

import os
import sys
sys.path.append('/app/backend')

from supabase import create_client, Client

# Initialize Supabase client with service role key for full access
url = "https://sftppbnqlsumjlrgyzgo.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzUxNjA5OSwiZXhwIjoyMDY5MDkyMDk5fQ.yG2lyX7WEnbRc8u3z8n3JQSQ72EqmO7hn4Or64NvKGo"

supabase: Client = create_client(url, service_role_key)

def execute_sql_statements():
    """Execute the foreign key constraint fix statements"""
    
    # List of SQL statements to execute
    statements = [
        # Drop existing constraints
        "ALTER TABLE public.pillars DROP CONSTRAINT IF EXISTS pillars_user_id_fkey;",
        "ALTER TABLE public.areas DROP CONSTRAINT IF EXISTS areas_user_id_fkey;", 
        "ALTER TABLE public.projects DROP CONSTRAINT IF EXISTS projects_user_id_fkey;",
        "ALTER TABLE public.tasks DROP CONSTRAINT IF EXISTS tasks_user_id_fkey;",
        "ALTER TABLE public.daily_reflections DROP CONSTRAINT IF EXISTS daily_reflections_user_id_fkey;",
        "ALTER TABLE public.sleep_reflections DROP CONSTRAINT IF EXISTS sleep_reflections_user_id_fkey;",
        "ALTER TABLE public.journals DROP CONSTRAINT IF EXISTS journals_user_id_fkey;",
        "ALTER TABLE public.ai_interactions DROP CONSTRAINT IF EXISTS ai_interactions_user_id_fkey;",
        "ALTER TABLE public.user_points DROP CONSTRAINT IF EXISTS user_points_user_id_fkey;",
        "ALTER TABLE public.achievements DROP CONSTRAINT IF EXISTS achievements_user_id_fkey;",
        "ALTER TABLE public.alignment_scores DROP CONSTRAINT IF EXISTS alignment_scores_user_id_fkey;",
        "ALTER TABLE public.username_change_records DROP CONSTRAINT IF EXISTS username_change_records_user_id_fkey;",
        
        # Add new constraints referencing public.users
        "ALTER TABLE public.pillars ADD CONSTRAINT pillars_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.areas ADD CONSTRAINT areas_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.projects ADD CONSTRAINT projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.tasks ADD CONSTRAINT tasks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.daily_reflections ADD CONSTRAINT daily_reflections_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.sleep_reflections ADD CONSTRAINT sleep_reflections_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.journals ADD CONSTRAINT journals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.ai_interactions ADD CONSTRAINT ai_interactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.user_points ADD CONSTRAINT user_points_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.achievements ADD CONSTRAINT achievements_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.alignment_scores ADD CONSTRAINT alignment_scores_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;",
        "ALTER TABLE public.username_change_records ADD CONSTRAINT username_change_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;"
    ]
    
    print(f"🚀 Starting foreign key constraint migration with {len(statements)} statements...")
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        try:
            print(f"⚙️  Executing statement {i}: {statement[:80]}...")
            
            # Execute the raw SQL using postgrest
            response = supabase.postgrest.rpc('exec_sql', {'sql': statement}).execute()
            
            print(f"✅ Statement {i} executed successfully")
            success_count += 1
            
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower():
                print(f"ℹ️  Statement {i} - constraint does not exist (expected): {error_msg}")
                success_count += 1
            elif "already exists" in error_msg.lower():
                print(f"ℹ️  Statement {i} - constraint already exists (expected): {error_msg}")
                success_count += 1
            else:
                print(f"❌ Statement {i} failed: {error_msg}")
                error_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Errors: {error_count}")
    
    if error_count == 0:
        print("🎉 Foreign key constraint migration completed successfully!")
        print("🔧 All foreign keys now reference public.users instead of auth.users")
        return True
    else:
        print("⚠️  Migration completed with some errors")
        return False

if __name__ == "__main__":
    success = execute_sql_statements()
    
    if success:
        print("\n✅ MIGRATION COMPLETE - Ready to test pillar creation!")
    else:
        print("\n⚠️  Migration had issues - manual verification needed")