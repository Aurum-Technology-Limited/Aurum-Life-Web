#!/usr/bin/env python3
"""
Run journal templates schema fix migration
"""
import os
import sys
sys.path.append('/app/backend')

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the journal templates schema fix migration"""
    try:
        # Initialize Supabase client with service role key for admin operations
        supabase_url = os.getenv('SUPABASE_URL')
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not service_role_key:
            print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment")
            return False
            
        supabase: Client = create_client(supabase_url, service_role_key)
        
        # Read the migration SQL
        migration_file = '/app/backend/migrations/013_fix_journal_templates_schema.sql'
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("🔧 Running journal templates schema fix migration...")
        print(f"📁 Migration file: {migration_file}")
        
        # Execute the migration
        result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        if result.data:
            print("✅ Migration completed successfully!")
            print("📋 Migration details:")
            for item in result.data:
                if item.get('notice'):
                    print(f"   ℹ️  {item['notice']}")
        else:
            print("✅ Migration completed (no output)")
            
        # Verify the table structure
        print("\n🔍 Verifying journal_templates table structure...")
        
        # Check if table exists and get column information
        verify_result = supabase.rpc('exec_sql', {
            'sql': """
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'journal_templates' 
            ORDER BY ordinal_position;
            """
        }).execute()
        
        if verify_result.data:
            print("✅ journal_templates table structure:")
            for col in verify_result.data:
                print(f"   📝 {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        print("\n🎉 Journal templates schema fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🚀 Journal templates functionality is now fully operational!")
        sys.exit(0)
    else:
        print("\n💥 Migration failed. Please check the errors above.")
        sys.exit(1)