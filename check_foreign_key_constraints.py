#!/usr/bin/env python3
"""
Check database foreign key constraints to identify the mismatch
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

from supabase_client import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_foreign_key_constraints():
    """Check which tables have wrong foreign key constraints"""
    try:
        supabase = await get_supabase_client()
        
        print("🔍 Checking foreign key constraints...")
        
        # SQL query to get foreign key constraints
        constraint_query = """
        SELECT 
            tc.table_name,
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public'
            AND kcu.column_name = 'user_id'
        ORDER BY tc.table_name;
        """
        
        try:
            # Execute raw SQL query
            result = supabase.rpc('exec_sql', {'sql': constraint_query}).execute()
            print("✅ Foreign key constraint query executed")
            print("📊 Results:")
            
            # The result should contain constraint information
            for row in result.data:
                table_name = row.get('table_name')
                constraint_name = row.get('constraint_name')
                foreign_table = row.get('foreign_table_name')
                
                status = "❌ WRONG" if foreign_table == 'users' else "✅ CORRECT"
                print(f"   {status} {table_name}.user_id -> {foreign_table}.id ({constraint_name})")
                
        except Exception as e:
            print(f"⚠️ Cannot execute raw SQL query: {e}")
            
            # Alternative approach: Try to infer from error messages
            print("\n🔍 Alternative approach - testing table constraints...")
            
            test_tables = ['pillars', 'areas', 'projects', 'tasks', 'journal_entries', 'resources']
            test_user_id = "00000000-0000-0000-0000-000000000000"  # Non-existent user ID
            
            for table in test_tables:
                try:
                    # Try to insert with non-existent user_id to trigger foreign key error
                    test_data = {
                        'id': test_user_id,
                        'user_id': test_user_id,
                        'name': 'test'
                    }
                    
                    supabase.table(table).insert(test_data).execute()
                    print(f"   ⚠️ {table}: No foreign key constraint (unexpected)")
                    
                except Exception as e:
                    error_msg = str(e)
                    if 'not present in table "users"' in error_msg:
                        print(f"   ❌ {table}: References legacy 'users' table")
                    elif 'not present in table "auth"' in error_msg or 'violates foreign key constraint' in error_msg:
                        print(f"   ✅ {table}: References correct 'auth.users' table")
                    else:
                        print(f"   ❓ {table}: Unknown constraint ({error_msg[:50]}...)")
        
        # Check specific cases we know about
        print("\n🔍 Checking specific known issues...")
        
        # Check what user IDs are in each table
        users_sample = supabase.table('users').select('id').limit(1).execute()
        profiles_sample = supabase.table('user_profiles').select('id').limit(1).execute()
        
        if users_sample.data and profiles_sample.data:
            legacy_user_id = users_sample.data[0]['id']
            auth_user_id = profiles_sample.data[0]['id']
            
            print(f"📋 Legacy user ID (from users table): {legacy_user_id}")
            print(f"📋 Auth user ID (from user_profiles): {auth_user_id}")
            
            # Test which ID works for each table
            test_tables = ['pillars', 'areas', 'projects']
            
            for table in test_tables:
                print(f"\n🧪 Testing {table} table:")
                
                # Test with legacy user ID
                try:
                    count = supabase.table(table).select('id', count='exact').eq('user_id', legacy_user_id).execute()
                    print(f"   ✅ Legacy user ID works: {count.count} records")
                except Exception as e:
                    print(f"   ❌ Legacy user ID fails: {e}")
                
                # Test with auth user ID
                try:
                    count = supabase.table(table).select('id', count='exact').eq('user_id', auth_user_id).execute()
                    print(f"   ✅ Auth user ID works: {count.count} records")
                except Exception as e:
                    print(f"   ❌ Auth user ID fails: {e}")
        
        print("\n✅ Foreign key constraint analysis completed!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_foreign_key_constraints())