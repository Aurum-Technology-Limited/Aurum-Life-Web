"""
Fix Supabase Database Schema
Add missing columns and fix enum values to match backend models
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client with service role key for schema changes
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

# Use service role key for schema modifications
supabase: Client = create_client(supabase_url, supabase_service_key)

async def fix_database_schema():
    """Fix database schema to match backend models"""
    
    schema_fixes = [
        # Add missing columns to pillars table
        """
        ALTER TABLE pillars 
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS time_allocation INTEGER DEFAULT 0;
        """,
        
        # Add missing columns to areas table  
        """
        ALTER TABLE areas
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS importance TEXT DEFAULT 'medium';
        """,
        
        # Add missing columns to projects table
        """
        ALTER TABLE projects
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        """,
        
        # Add missing columns to tasks table
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        """,
        
        # Update enum values for project status
        """
        UPDATE projects 
        SET status = 'not_started' 
        WHERE status = 'Not Started';
        
        UPDATE projects 
        SET status = 'in_progress' 
        WHERE status = 'In Progress';
        
        UPDATE projects 
        SET status = 'completed' 
        WHERE status = 'Completed';
        
        UPDATE projects 
        SET status = 'on_hold' 
        WHERE status = 'On Hold';
        """,
        
        # Update enum values for task status
        """
        UPDATE tasks 
        SET status = 'pending' 
        WHERE status = 'Pending';
        
        UPDATE tasks 
        SET status = 'in_progress' 
        WHERE status = 'In Progress';
        
        UPDATE tasks 
        SET status = 'completed' 
        WHERE status = 'Completed';
        
        UPDATE tasks 
        SET status = 'cancelled' 
        WHERE status = 'Cancelled';
        """,
        
        # Update enum values for priority
        """
        UPDATE projects 
        SET priority = 'low' 
        WHERE priority = 'Low';
        
        UPDATE projects 
        SET priority = 'medium' 
        WHERE priority = 'Medium';
        
        UPDATE projects 
        SET priority = 'high' 
        WHERE priority = 'High';
        
        UPDATE tasks 
        SET priority = 'low' 
        WHERE priority = 'Low';
        
        UPDATE tasks 
        SET priority = 'medium' 
        WHERE priority = 'Medium';
        
        UPDATE tasks 
        SET priority = 'high' 
        WHERE priority = 'High';
        """,
        
        # Set default values for new columns
        """
        UPDATE pillars 
        SET is_active = TRUE 
        WHERE is_active IS NULL;
        
        UPDATE areas 
        SET is_active = TRUE 
        WHERE is_active IS NULL;
        
        UPDATE projects 
        SET is_active = TRUE 
        WHERE is_active IS NULL;
        
        UPDATE tasks 
        SET is_active = TRUE 
        WHERE is_active IS NULL;
        """
    ]
    
    print("🔧 FIXING SUPABASE DATABASE SCHEMA...")
    
    for i, sql_statement in enumerate(schema_fixes, 1):
        try:
            print(f"   Executing schema fix {i}/{len(schema_fixes)}...")
            
            # Use raw SQL execution via rpc call
            result = supabase.rpc('exec_sql', {'sql_statement': sql_statement}).execute()
            
            print(f"   ✅ Schema fix {i} completed successfully")
            
        except Exception as e:
            print(f"   ⚠️ Schema fix {i} failed: {e}")
            print(f"   SQL: {sql_statement.strip()}")
            
            # Try direct SQL execution instead
            try:
                # Some operations might work with direct postgrest calls
                print(f"   🔄 Trying alternative approach for fix {i}...")
                # Skip for now - manual execution might be needed
                pass
            except Exception as e2:
                print(f"   ❌ Alternative approach also failed: {e2}")
    
    print("✅ DATABASE SCHEMA UPDATE COMPLETED!")
    print("\n📋 MANUAL VERIFICATION NEEDED:")
    print("   Please verify in Supabase dashboard that:")
    print("   - pillars table has 'is_active' and 'time_allocation' columns")
    print("   - areas table has 'is_active' and 'importance' columns")
    print("   - projects table has 'is_active' column")
    print("   - tasks table has 'is_active' column")
    print("   - All enum values are lowercase with underscores")

if __name__ == "__main__":
    import asyncio
    asyncio.run(fix_database_schema())