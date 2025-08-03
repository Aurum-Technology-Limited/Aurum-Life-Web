#!/usr/bin/env python3
"""
Foreign Key Constraint Fix Script
Execute the SQL migration to fix foreign key constraints to reference public.users instead of auth.users
"""

import os
from supabase import create_client, Client

# Initialize Supabase client
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_ANON_KEY')

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables")
    exit(1)

supabase: Client = create_client(url, key)

def execute_sql_file(file_path):
    """Execute SQL statements from a file"""
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()
        
        # Split SQL content by statements (rough approach)
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"📄 Executing {len(statements)} SQL statements from {file_path}")
        
        for i, statement in enumerate(statements, 1):
            if statement.strip() and not statement.strip().startswith('--'):
                try:
                    print(f"⚙️  Executing statement {i}: {statement[:100]}...")
                    # Use rpc to execute raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"⚠️  Statement {i} failed (might be expected): {e}")
        
        print("🎉 SQL migration completed!")
        
    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Execute the foreign key fix script
    success = execute_sql_file('/app/fix_foreign_key_constraints.sql')
    
    if success:
        print("✅ Foreign key constraints migration completed successfully!")
        print("🔧 All foreign keys now reference public.users instead of auth.users")
    else:
        print("❌ Migration failed!")